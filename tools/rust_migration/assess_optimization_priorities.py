"""Read-only cost reassessment from canonical E2/E3 evidence; no new benchmark."""

import argparse
import gzip
import hashlib
import json
import math
from pathlib import Path
import subprocess
import zipfile


E2_SHA = "62c5e73a2356334fc0fa85e3b5f4054a46f5f759ad7cb6c9fcef41dcd7b190ba"
E3_SHA = "c3e347b145fcc5edfda304bb35030d3d3d9320861f116a5507d2b92cbd9b6abd"
AUDIT_SHA = "3b167b151c3bc32e1d54f6015d0f15d2c3dd6a74"
SOURCE_FILES = (
    "framework/ecs/world.py", "framework/engine/renders.py",
    "rotk_env/runtime/world_presentation.py", "rotk_env/runtime/session.py",
    "rotk_env/systems/window_unit_render_system.py",
    "rotk_env/systems/window_render_systems_base.py",
    "rotk_env/systems/optimized_render_systems.py",
    "rotk_env/systems/fog_surface_presenter.py",
    "native/rotk/src/runtime.rs", "native/rotk/src/statistics.rs",
    "native/rotk/src/vision.rs", "native/rotk/src/observation.rs",
    "native/rotk/src/spatial.rs", "native/core/src/world.rs",
)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def canonical_zip(path, expected):
    assert digest(path.read_bytes()) == expected, f"archive mismatch: {path}"
    archive = zipfile.ZipFile(path)
    checks = {}
    for line in archive.read("SHA256SUMS").decode().splitlines():
        sha, name = line.split(maxsplit=1)
        checks[name.lstrip("*")] = sha
    return archive, checks


def member(archive, checks, name):
    data = archive.read(name)
    assert digest(data) == checks[name], f"member mismatch: {name}"
    return data


def mean(values):
    return math.fsum(values) / len(values)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[2]
    e2 = root / "experiments/2026-09-rust-statistics-compute"
    e3 = root / "experiments/2026-10-rust-internal-system-candidates"
    comparison_path = e2 / "results/capacity-comparison.json"
    comparison = json.loads(comparison_path.read_text())
    archive2, checks2 = canonical_zip(e2 / "artifacts/statistics-compute-raw.zip", E2_SHA)
    live = []
    fields = ("native_step_ms", "delta_ms", "presentation_apply_ms", "inputs_ms", "display_systems_ms")
    for row in comparison["rows"]:
        name = "results/" + row["raw"]["path"]
        data = member(archive2, checks2, name)
        assert len(data) == row["raw"]["size"] and digest(data) == row["raw"]["sha256"]
        raw = json.loads(data)
        frames = [f for f in raw["frames"] if 30 <= f["t"] < 330]
        assert len(frames) == row["frame"]["count"]
        frame_mean = mean([f["work_ms"] for f in frames])
        assert abs(frame_mean - row["frame"]["avg"]) < 1e-8
        phases = {key: mean([f[key] for f in frames]) for key in fields}
        for key in fields:
            assert abs(phases[key] - row["native_phases"][key]["avg"]) < 1e-8
        remainder = [f["update_work_ms"] - f["agent_ms"] - sum(f[k] for k in fields) for f in frames]
        live.append({
            "run": row["run"], "source_sha": row["source"]["sha"],
            "raw_member": name, "raw_sha256": digest(data), "frames": len(frames),
            "frame_mean_ms": frame_mean, "frame_p99_ms": row["frame"]["p99"],
            "phase_mean_ms": phases, "agent_mean_ms": row["agent_ms"]["avg"],
            "unattributed_update_mean_ms": mean(remainder),
            "native_step_fraction_pct": 100 * phases["native_step_ms"] / frame_mean,
            "display_systems_fraction_pct": 100 * phases["display_systems_ms"] / frame_mean,
            "presentation_apply_fraction_pct": 100 * phases["presentation_apply_ms"] / frame_mean,
            "observation_service": row["service"],
            "observation_queue": row["observation_queue"], "action_queue": row["action_queue"],
        })
    archive2.close()
    archive3, checks3 = canonical_zip(e3 / "artifacts/system-candidates-raw.zip", E3_SHA)
    budgets = []
    for threads in (1, 2, 4):
        name = f"replays/candidate-t{threads}.timings.json.gz"
        data = member(archive3, checks3, name)
        ticks = json.loads(gzip.decompress(data))
        assert len(ticks) == 9880
        assert len({t["seq"] for t in ticks}) == len(ticks)
        native = mean([t["native_ns"] for t in ticks])
        overlap = mean([min(t["statistics"]["kernel_wall_ns"], t["phases_ns"].get("movement", 0)) for t in ticks])
        budgets.append({
            "threads": threads, "ticks": len(ticks), "member": name, "sha256": digest(data),
            "native_diagnostic_mean_us": native / 1000,
            "statistics_kernel_movement_ideal_mean_us": overlap / 1000,
            "ideal_fraction_pct": 100 * overlap / native,
            "statistics_trim_diagnostic_mean_us": mean([t["statistics"]["trim_ns"] for t in ticks]) / 1000,
        })
    archive3.close()
    sources = {}
    for path in SOURCE_FILES:
        stored = subprocess.check_output(["git", "show", f"{AUDIT_SHA}:{path}"], cwd=args.source)
        current = (args.source / path).read_bytes()
        assert stored == current, f"audit source changed: {path}"
        sources[path] = digest(current)
    result = {
        "status": "planning_assessment_from_existing_evidence",
        "audited_source_sha": AUDIT_SHA, "tool_sha256": digest(Path(__file__).read_bytes()),
        "source_file_sha256": sources,
        "e2_archive_sha256": E2_SHA, "e3_archive_sha256": E3_SHA,
        "capacity_comparison_sha256": digest(comparison_path.read_bytes()),
        "live_window": "E2 native4: 30s warmup + 300s measurement, source 2bc57d5; not E5 live",
        "notes": [
            "No new workload executed. Existing raw slow samples retained.",
            "Per-frame means and per-request latency have different denominators.",
            "Unattributed update remainder is not proven rendering or GC cost.",
            "E3 overlap is diagnostic zero-cost upper bound, not implemented speedup.",
            "No new capacity, Frontier, policy or GAP closure.",
        ],
        "live": live, "statistics_movement_ideal": budgets,
    }
    encoded = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.write_text(encoded)
    else:
        print(encoded, end="")


if __name__ == "__main__":
    main()
