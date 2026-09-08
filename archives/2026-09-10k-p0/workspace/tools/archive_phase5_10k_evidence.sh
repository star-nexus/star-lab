#!/usr/bin/env bash
set -Eeuo pipefail

# Mirror Phase-5 10K experiment evidence from sibling star-main -> star-lab.
#
# Ownership rule:
#   A owns:
#     - Phase-5 formal baseline        20260906-030632
#     - Phase-5.1 attribution          20260906-033723
#     - Optimization-A production A/B 20260906-041532
#   B owns:
#     - Optimization-B negative result 20260906-120822
#     - It references A's Optimization-A baseline instead of duplicating it.
#   C1 owns:
#     - Vision geometry-hit attribution 20260906-124920
#
# Safe to rerun: rsync updates identical destinations without deleting unrelated files.

SCENARIO="chibi-144k-scale-10000"

CASE_A="2026-09-10k-movement-system-lookup"
CASE_B="2026-09-10k-spatial-index-move-specialization"
CASE_C1="2026-09-10k-vision-geometry-hit-path"

STAR_MAIN_ROOT="${STAR_MAIN_ROOT:-$(git rev-parse --show-toplevel)}"
PARENT_DIR="$(dirname "$STAR_MAIN_ROOT")"
STAR_LAB_ROOT="${STAR_LAB_ROOT:-$PARENT_DIR/star-lab}"

if [[ ! -d "$STAR_MAIN_ROOT/.git" ]]; then
    echo "ERROR: STAR main repo not found: $STAR_MAIN_ROOT" >&2
    exit 2
fi

if [[ ! -d "$STAR_LAB_ROOT/.git" ]]; then
    echo "ERROR: sibling STAR Lab repo not found: $STAR_LAB_ROOT" >&2
    echo "Set STAR_LAB_ROOT=/path/to/star-lab if needed." >&2
    exit 2
fi

if ! command -v rsync >/dev/null 2>&1; then
    echo "ERROR: rsync is required." >&2
    exit 2
fi

echo "STAR main: $STAR_MAIN_ROOT"
echo "STAR Lab : $STAR_LAB_ROOT"
echo

assert_manifest_sha() {
    local src="$1"
    local expected_sha="$2"
    local manifest="$src/manifest.txt"

    if [[ ! -f "$manifest" ]]; then
        echo "ERROR: missing manifest: $manifest" >&2
        exit 3
    fi

    local actual_sha
    actual_sha="$(awk -F= '$1=="git_sha"{print $2; exit}' "$manifest")"

    if [[ -z "$actual_sha" ]]; then
        echo "ERROR: git_sha missing from $manifest" >&2
        exit 3
    fi

    if [[ "$actual_sha" != "$expected_sha" ]]; then
        echo "ERROR: source identity mismatch" >&2
        echo "  manifest : $manifest" >&2
        echo "  expected : $expected_sha" >&2
        echo "  actual   : $actual_sha" >&2
        exit 3
    fi
}

copy_run() {
    local family="$1"
    local run_id="$2"
    local case_id="$3"
    local expected_sha="$4"

    local src="$STAR_MAIN_ROOT/results/$family/$SCENARIO/$run_id"
    local dst="$STAR_LAB_ROOT/experiments/$case_id/results/raw/$family/$SCENARIO/$run_id"

    if [[ ! -d "$src" ]]; then
        echo "ERROR: source run not found: $src" >&2
        exit 4
    fi

    assert_manifest_sha "$src" "$expected_sha"

    echo "COPY $family/$run_id"
    echo "  -> experiments/$case_id/results/raw/$family/$SCENARIO/$run_id"

    mkdir -p "$dst"
    rsync -a "$src/" "$dst/"
}

write_raw_checksums() {
    local case_id="$1"
    local case_root="$STAR_LAB_ROOT/experiments/$case_id"
    local raw_root="$case_root/results/raw"
    local checksum_file="$case_root/artifacts/RAW_SHA256SUMS"

    mkdir -p "$case_root/artifacts"

    if [[ ! -d "$raw_root" ]]; then
        echo "ERROR: raw evidence root missing: $raw_root" >&2
        exit 5
    fi

    python3 - "$case_root" "$raw_root" "$checksum_file" <<'PY'
from pathlib import Path
import hashlib
import sys

case_root = Path(sys.argv[1]).resolve()
raw_root = Path(sys.argv[2]).resolve()
out = Path(sys.argv[3])

rows = []
for path in sorted(p for p in raw_root.rglob("*") if p.is_file()):
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    rel = path.resolve().relative_to(case_root)
    rows.append(f"{h.hexdigest()}  {rel.as_posix()}")

out.write_text("\n".join(rows) + "\n", encoding="utf-8")
print(f"  checksummed {len(rows)} files -> {out}")
PY
}

echo "== Optimization A evidence =="
copy_run \
    "phase5-10k-core" \
    "20260906-030632" \
    "$CASE_A" \
    "82054c554d359516fe3d9cf0fa80cfd81bc222a3"

copy_run \
    "phase5-10k-attribution" \
    "20260906-033723" \
    "$CASE_A" \
    "497ca6ce7113cb4883359fb0821b4022538255a6"

copy_run \
    "phase5-10k-core" \
    "20260906-041532" \
    "$CASE_A" \
    "b9e0bb92b546b3283cb5c1d30a9a510d0c006ec2"

write_raw_checksums "$CASE_A"

echo
echo "== Optimization B evidence =="
copy_run \
    "phase5-10k-core" \
    "20260906-120822" \
    "$CASE_B" \
    "73a2f7f33067dfd39e7aaf1c07a4c08eafc021ba"

write_raw_checksums "$CASE_B"

echo
echo "== Optimization C1 attribution evidence =="
copy_run \
    "phase5-vision-hit-attribution" \
    "20260906-124920" \
    "$CASE_C1" \
    "ebf2dc5cfb74c16b83272b6e9cf23f29017efe88"

write_raw_checksums "$CASE_C1"

echo
echo "============================================================"
echo "Evidence mirror complete."
echo "============================================================"
echo
echo "Review:"
echo "  cd \"$STAR_LAB_ROOT\""
echo "  git status --short"
echo
echo "Sizes:"
du -sh \
    "$STAR_LAB_ROOT/experiments/$CASE_A" \
    "$STAR_LAB_ROOT/experiments/$CASE_B" \
    "$STAR_LAB_ROOT/experiments/$CASE_C1" \
    2>/dev/null || true
