#!/usr/bin/env bash
set -Eeuo pipefail

# ============================================================
# STAR Phase 5 — 10K Core Runtime
#
# Formal points:
#   10K resident /   0% moving
#   10K resident /  50% moving
#   10K resident / 100% moving
#
# Canonical gate:
#   controlled_work_frame_ms.p99 <= 33.33 ms
#
# Engineering signal:
#   controlled_work_frame_ms.p99 <= 16.67 ms
#
# Each point runs in a FRESH STAR process.
# ============================================================


# -----------------------------
# Configuration
# -----------------------------

SCENARIO="${SCENARIO:-chibi-144k-scale-10000}"

SEED="${SEED:-42}"
PHASE_SEED="${PHASE_SEED:-42}"
ROUTE_STEPS="${ROUTE_STEPS:-12}"

DURATION="${DURATION:-20}"
WARMUP="${WARMUP:-5}"
SAMPLE_AFTER="${SAMPLE_AFTER:-7}"

READY_TIMEOUT="${READY_TIMEOUT:-120}"
COMMAND_TIMEOUT="${COMMAND_TIMEOUT:-120}"

RESULTS_ROOT="${RESULTS_ROOT:-results/phase5-10k-core}"

RUN_ID="${RUN_ID:-$(date +%Y%m%d-%H%M%S)}"


# -----------------------------
# Repository sanity
# -----------------------------

REPO_ROOT="$(git rev-parse --show-toplevel)"
cd "$REPO_ROOT"

SCENARIO_FILE="rotk_env/maps/${SCENARIO}.json"

if [[ ! -f "$SCENARIO_FILE" ]]; then
    echo "ERROR: scenario not found:"
    echo "  $SCENARIO_FILE"
    exit 2
fi

RUN_DIR="${RESULTS_ROOT}/${SCENARIO}/${RUN_ID}"
mkdir -p "$RUN_DIR"

GIT_SHA="$(git rev-parse HEAD)"
GIT_BRANCH="$(git branch --show-current)"

echo
echo "============================================================"
echo "STAR Phase 5 — 10K Core Runtime"
echo "============================================================"
echo "Scenario : $SCENARIO"
echo "Branch   : $GIT_BRANCH"
echo "SHA      : $GIT_SHA"
echo "Results  : $RUN_DIR"
echo "============================================================"
echo


# -----------------------------
# Run-level evidence
# -----------------------------

{
    echo "experiment=Phase 5 — 10K Core Runtime"
    echo "run_id=$RUN_ID"
    echo "created_at_utc=$(date -u '+%Y-%m-%dT%H:%M:%SZ')"

    echo "git_branch=$GIT_BRANCH"
    echo "git_sha=$GIT_SHA"

    echo "scenario=$SCENARIO"
    echo "scenario_file=$SCENARIO_FILE"
    echo "scenario_sha256=$(shasum -a 256 "$SCENARIO_FILE" | awk '{print $1}')"

    echo "seed=$SEED"
    echo "phase_seed=$PHASE_SEED"
    echo "route_steps=$ROUTE_STEPS"

    echo "motion_phase=staggered"
    echo "gc_policy=realtime_defer"

    echo "duration_seconds=$DURATION"
    echo "warmup_seconds=$WARMUP"
    echo "sample_after_seconds=$SAMPLE_AFTER"

    echo "fog=ON (validated by driver guard)"
    echo "minimap_dynamic_units=OFF"
    echo "render=uncapped"
    echo "hub=offline"
    echo "mock_ai=off"

    echo "canonical_30hz_gate_ms=33.33"
    echo "engineering_60hz_gate_ms=16.67"

    echo
    echo "uname=$(uname -a)"

    if command -v sw_vers >/dev/null 2>&1; then
        echo "macos_product=$(sw_vers -productName)"
        echo "macos_version=$(sw_vers -productVersion)"
        echo "macos_build=$(sw_vers -buildVersion)"
    fi
} > "$RUN_DIR/manifest.txt"

git status --short > "$RUN_DIR/git-status.txt"
git diff --stat > "$RUN_DIR/git-diff-stat.txt"


# -----------------------------
# Process cleanup
# -----------------------------

ENV_PID=""
CURRENT_SOCKET=""

cleanup_env() {
    if [[ -n "${ENV_PID:-}" ]] && kill -0 "$ENV_PID" 2>/dev/null; then
        kill -TERM "$ENV_PID" 2>/dev/null || true

        # Give STAR a short graceful shutdown window.
        for _ in {1..25}; do
            if ! kill -0 "$ENV_PID" 2>/dev/null; then
                break
            fi
            sleep 0.2
        done

        if kill -0 "$ENV_PID" 2>/dev/null; then
            kill -KILL "$ENV_PID" 2>/dev/null || true
        fi

        wait "$ENV_PID" 2>/dev/null || true
    fi

    if [[ -n "${CURRENT_SOCKET:-}" ]]; then
        rm -f "$CURRENT_SOCKET"
    fi

    ENV_PID=""
    CURRENT_SOCKET=""
}

trap cleanup_env EXIT INT TERM


# -----------------------------
# One formal density point
# -----------------------------

run_point() {
    local density="$1"
    local label="$2"

    local point_dir="${RUN_DIR}/${label}"
    mkdir -p "$point_dir"

    CURRENT_SOCKET="/tmp/star-10k-${$}-${label}.sock"
    rm -f "$CURRENT_SOCKET"

    echo
    echo "============================================================"
    echo "Phase 5 point: $label"
    echo "execution density: $density"
    echo "============================================================"

    {
        echo "density=$density"
        echo "label=$label"
        echo "git_sha=$GIT_SHA"
        echo "scenario=$SCENARIO"
        echo "socket=$CURRENT_SOCKET"
    } > "$point_dir/config.txt"


    # --------------------------------------------------------
    # Fresh production STAR ENV
    #
    # Important:
    # STAR_SCALE_MINIMAP_UNITS=off disables ONLY the dynamic
    # MiniMap unit-dot layer. Normal map/viewport presentation
    # remains intact.
    # --------------------------------------------------------

    STAR_SCALE_MINIMAP_UNITS=off \
    uv run python -m rotk_env.main \
        --skip-start \
        --mode real_time \
        --scenario "$SCENARIO" \
        --players human_vs_two_ai \
        --no-hub \
        --seed "$SEED" \
        --uncapped \
        --scale-harness-socket "$CURRENT_SOCKET" \
        > "$point_dir/env.log" 2>&1 &

    ENV_PID=$!

    echo "STAR ENV PID: $ENV_PID"


    # --------------------------------------------------------
    # Formal Phase-5 density point
    # --------------------------------------------------------

    set +e

    uv run python tools/scale_driver.py \
        --socket "$CURRENT_SOCKET" \
        --command-timeout "$COMMAND_TIMEOUT" \
        density-point \
        --density "$density" \
        --phase staggered \
        --seed "$SEED" \
        --phase-seed "$PHASE_SEED" \
        --route-steps "$ROUTE_STEPS" \
        --duration "$DURATION" \
        --warmup "$WARMUP" \
        --sample-after "$SAMPLE_AFTER" \
        --ready-timeout "$READY_TIMEOUT" \
        --gc-policy realtime_defer \
        --profile "$point_dir/profile.json" \
        --output "$point_dir/point.json" \
        2>&1 | tee "$point_dir/driver.log"

    DRIVER_RC="${PIPESTATUS[0]}"

    set -e

    echo "$DRIVER_RC" > "$point_dir/driver-exit-code.txt"


    # Kill this STAR instance before starting the next point.
    cleanup_env


    # --------------------------------------------------------
    # Produce concise classification
    # --------------------------------------------------------

    if [[ -f "$point_dir/point.json" && -f "$point_dir/profile.json" ]]; then

        uv run python - \
            "$point_dir/point.json" \
            "$point_dir/profile.json" \
            "$point_dir/summary.json" \
            "$density" \
            "$label" \
            "$DRIVER_RC" <<'PY'
import json
import sys
from pathlib import Path

point_path = Path(sys.argv[1])
profile_path = Path(sys.argv[2])
summary_path = Path(sys.argv[3])

density = float(sys.argv[4])
label = sys.argv[5]
driver_rc = int(sys.argv[6])

point = json.loads(point_path.read_text())
profile = json.loads(profile_path.read_text())

controlled = profile.get("controlled_work_frame_ms") or {}
metadata = profile.get("metadata") or {}
status = point.get("status") or {}
guards = point.get("guards") or {}

p99 = controlled.get("p99")
p95 = controlled.get("p95")
avg = controlled.get("avg")
maximum = controlled.get("max")

resident = int(status.get("living_units") or 0)
moving = int(status.get("active_moving_units") or 0)

actual_density = moving / resident if resident else None

minimap_off = (
    metadata.get("minimap_unit_layer_enabled") is False
    and metadata.get("minimap_unit_layer_override") == "off"
)

driver_guards_ok = bool(point.get("ok"))
valid = driver_guards_ok and minimap_off and p99 is not None

if not valid:
    canonical = "INVALID"
    stress60 = "INVALID"
else:
    canonical = "PASS" if float(p99) <= 33.33 else "FAIL"
    stress60 = "PASS" if float(p99) <= 16.67 else "FAIL"

summary = {
    "label": label,
    "requested_density": density,
    "resident_units": resident,
    "active_moving_units": moving,
    "actual_density": actual_density,

    "valid_evidence": valid,
    "driver_exit_code": driver_rc,
    "driver_guards_ok": driver_guards_ok,

    "minimap_unit_layer_enabled":
        metadata.get("minimap_unit_layer_enabled"),
    "minimap_unit_layer_override":
        metadata.get("minimap_unit_layer_override"),

    "controlled_work_frame_ms": {
        "avg": avg,
        "p95": p95,
        "p99": p99,
        "max": maximum,
    },

    "canonical_30hz": {
        "criterion_ms": 33.33,
        "classification": canonical,
    },

    "engineering_60hz": {
        "criterion_ms": 16.67,
        "classification": stress60,
    },

    "guards": guards,
}

summary_path.write_text(
    json.dumps(summary, indent=2, sort_keys=True) + "\n"
)

print()
print("------------------------------------------------------------")
print(f"{label}")
print("------------------------------------------------------------")
print(f"resident              : {resident}")
print(f"moving                : {moving}")
print(f"actual density        : {actual_density}")
print(f"driver guards         : {'PASS' if driver_guards_ok else 'FAIL'}")
print(f"MiniMap dynamic units : {'OFF' if minimap_off else 'INVALID'}")
print(f"controlled avg        : {avg} ms")
print(f"controlled p95        : {p95} ms")
print(f"controlled p99        : {p99} ms")
print(f"controlled max        : {maximum} ms")
print(f"30 Hz canonical       : {canonical}")
print(f"60 Hz engineering     : {stress60}")
print("------------------------------------------------------------")
PY

    else
        cat > "$point_dir/summary.json" <<EOF
{
  "label": "$label",
  "requested_density": $density,
  "valid_evidence": false,
  "driver_exit_code": $DRIVER_RC,
  "error": "point.json and/or profile.json missing; inspect env.log and driver.log"
}
EOF

        echo
        echo "WARNING: $label did not produce complete evidence."
        echo "Inspect:"
        echo "  $point_dir/env.log"
        echo "  $point_dir/driver.log"
    fi
}


# ============================================================
# Run formal Phase-5 points
# ============================================================

run_point 0.0 "00pct-moving"
run_point 0.5 "50pct-moving"
run_point 1.0 "100pct-moving"


# -----------------------------
# Aggregate report
# -----------------------------

uv run python - "$RUN_DIR" <<'PY'
import json
import sys
from pathlib import Path

run_dir = Path(sys.argv[1])

labels = [
    "00pct-moving",
    "50pct-moving",
    "100pct-moving",
]

rows = []

for label in labels:
    path = run_dir / label / "summary.json"

    if not path.exists():
        rows.append({
            "label": label,
            "valid_evidence": False,
            "canonical": "INVALID",
            "stress60": "INVALID",
        })
        continue

    data = json.loads(path.read_text())

    c = data.get("controlled_work_frame_ms") or {}

    rows.append({
        "label": label,
        "resident": data.get("resident_units"),
        "moving": data.get("active_moving_units"),
        "density": data.get("actual_density"),
        "p99_ms": c.get("p99"),
        "valid_evidence": data.get("valid_evidence", False),
        "canonical": (
            data.get("canonical_30hz") or {}
        ).get("classification", "INVALID"),
        "stress60": (
            data.get("engineering_60hz") or {}
        ).get("classification", "INVALID"),
    })

(run_dir / "summary.json").write_text(
    json.dumps(rows, indent=2) + "\n"
)

with (run_dir / "summary.tsv").open("w") as f:
    f.write(
        "point\tresident\tmoving\tdensity\t"
        "controlled_p99_ms\tvalid\t30hz\t60hz\n"
    )

    for r in rows:
        f.write(
            f"{r.get('label')}\t"
            f"{r.get('resident')}\t"
            f"{r.get('moving')}\t"
            f"{r.get('density')}\t"
            f"{r.get('p99_ms')}\t"
            f"{r.get('valid_evidence')}\t"
            f"{r.get('canonical')}\t"
            f"{r.get('stress60')}\n"
        )

print()
print("======================================================================")
print("Phase 5 — 10K Core Runtime Summary")
print("======================================================================")
print(
    f"{'POINT':<16}"
    f"{'RESIDENT':>10}"
    f"{'MOVING':>10}"
    f"{'P99(ms)':>12}"
    f"{'VALID':>9}"
    f"{'30Hz':>9}"
    f"{'60Hz':>9}"
)

for r in rows:
    print(
        f"{r.get('label', ''):<16}"
        f"{str(r.get('resident')):>10}"
        f"{str(r.get('moving')):>10}"
        f"{str(r.get('p99_ms')):>12}"
        f"{str(r.get('valid_evidence')):>9}"
        f"{str(r.get('canonical')):>9}"
        f"{str(r.get('stress60')):>9}"
    )

print("======================================================================")
print(f"Results: {run_dir}")
PY


echo
echo "Phase 5 three-point run completed."
echo
echo "Results:"
echo "  $RUN_DIR"
echo
