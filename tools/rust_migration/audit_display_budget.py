"""Read-only E6 budget audit used by the E7 planning record; no new benchmark."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import statistics
import zipfile
from pathlib import Path


CASE = "experiments/2026-10-rust-presentation-cache"
ZIP_SHA = "accdac58f19704c943083006be4f15d1fc44bb88fb1d6a91ec75bce791d6e620"
RAW_MEMBER = "raw/live-diagnostic-baseline.raw.json"
RAW_SHA = "794a98934b65c57db9161c87b488e85e219cc32e210ae507feff6491aecba854"
META_MEMBER = "raw/live-diagnostic-baseline.json"
META_SHA = "8b6da40fc54384da53545675519bad2c2749fde11d9f11b410a15b9a5261ed24"
CORE = (
    "core_screen_fill_ms", "core_input_system_ms", "core_scene_update_ms",
    "core_render_engine_ms", "core_display_present_ms",
)


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def audit(root: Path) -> dict:
    archive = root / CASE / "artifacts/presentation-cache-raw.zip"
    archive_bytes = archive.read_bytes()
    if sha(archive_bytes) != ZIP_SHA:
        raise ValueError("Canonical E6 archive checksum differs")
    with zipfile.ZipFile(archive) as packed:
        raw_bytes = packed.read(RAW_MEMBER)
        meta_bytes = packed.read(META_MEMBER)
    if sha(raw_bytes) != RAW_SHA or sha(meta_bytes) != META_SHA:
        raise ValueError("Canonical diagnostic member checksum differs")
    raw, meta = json.loads(raw_bytes), json.loads(meta_bytes)
    workload = meta["workload"]
    if (workload["warmup"], workload["seconds"], workload["native_threads"],
            workload["presentation_research_mode"]) != (30.0, 60.0, 4, "baseline"):
        raise ValueError("Unexpected diagnostic workload")
    indexed = [(i, row) for i, row in enumerate(raw["frames"])
               if 30.0 <= row["t"] < 90.0]
    rows = [row for _, row in indexed]
    if len(rows) != 1800:
        raise ValueError("Measured-frame count differs")
    fields = ("work_ms", "update_work_ms", "agent_ms") + CORE
    if any(key not in row or not math.isfinite(row[key])
           for row in rows for key in fields):
        raise ValueError("Missing or nonfinite frame field")
    means = {key: statistics.mean(row[key] for row in rows) for key in fields}
    old_residual = statistics.mean(
        row["update_work_ms"] - sum(row[key] for key in CORE) for row in rows)
    corrected = statistics.mean(
        row["update_work_ms"] - row["agent_ms"] - sum(row[key] for key in CORE)
        for row in rows)
    cost_path = root / CASE / "results/cost-attribution-complete.json"
    cost_bytes = cost_path.read_bytes()
    published = json.loads(cost_bytes)["live_diagnostic"]
    for key in ("work_ms", "update_work_ms") + CORE:
        if not math.isclose(means[key], published["means_ms"][key], abs_tol=1e-12):
            raise ValueError(f"Published mean differs: {key}")
    if not math.isclose(old_residual, published["unattributed_update_ms"], abs_tol=1e-12):
        raise ValueError("Published residual differs")
    return {
        "status": "existing_diagnostic_reanalysis_only",
        "new_experiment": False,
        "source": meta["source"], "tooling": meta["tooling"],
        "hardware": meta["hardware"], "workload": workload,
        "evidence": {
            "archive": str(archive.relative_to(root)), "archive_sha256": ZIP_SHA,
            "raw_member": RAW_MEMBER, "raw_member_sha256": RAW_SHA,
            "metadata_member": META_MEMBER, "metadata_member_sha256": META_SHA,
            "published_cost": str(cost_path.relative_to(root)),
            "published_cost_sha256": sha(cost_bytes),
            "audit_tool": "tools/rust_migration/audit_display_budget.py",
            "audit_tool_sha256": sha(Path(__file__).read_bytes()),
        },
        "selection": {
            "predicate": "30.0 <= frame['t'] < 90.0", "samples": len(rows),
            "first_raw_index": indexed[0][0], "last_raw_index": indexed[-1][0],
            "first_t": rows[0]["t"], "last_t": rows[-1]["t"],
        },
        "means_ms": means,
        "five_core_mean_ms": statistics.mean(sum(row[key] for key in CORE) for row in rows),
        "old_residual_mean_ms": old_residual,
        "agent_share_of_old_residual_pct": 100 * means["agent_ms"] / old_residual,
        "corrected_residual_mean_ms": corrected,
        "frame_loop_outside_update_mean_ms": statistics.mean(
            row["work_ms"] - row["update_work_ms"] for row in rows),
        "corrected_formula": "mean(update_work_ms - agent_ms - sum(five_core_fields))",
        "nested_contract": [
            "update_work_ms already includes agent_ms; do not add agent_ms again",
            "scene_update includes inputs/native/delta/apply/display",
            "five_core_fields partition the original GameEngine._update scopes",
            "work_ms includes the wrapper update plus outer frame-loop work, excluding cap wait",
            "corrected residual still includes harness census/recording/wrapper overhead",
            "all values include diagnostic overhead and are not predicted optimization gains",
        ],
        "published_means_reproduced": True,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--lab-root", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = audit(args.lab_root.resolve())
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print(f"Verified {result['selection']['samples']} canonical diagnostic frames; "
          f"corrected residual {result['corrected_residual_mean_ms']:.9f} ms")


if __name__ == "__main__":
    main()
