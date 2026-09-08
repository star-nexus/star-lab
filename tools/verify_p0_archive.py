#!/usr/bin/env python3
"""Verify P0 package hashes and every migrated source/result archive locator."""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
import zipfile

ROOT = Path(__file__).resolve().parents[1]
ARCHIVE = ROOT / "archives/2026-09-10k-p0"


def main():
    package_count = 0
    for line in (ARCHIVE / "SHA256SUMS").read_text().splitlines():
        digest, name = line.split("  ", 1)
        path = ARCHIVE / name
        if hashlib.sha256(path.read_bytes()).hexdigest() != digest:
            raise ValueError(f"Package checksum mismatch: {path}")
        package_count += 1
    migrated = 0
    archives = {}
    try:
        for name in ("workspace-migration.json", "results-migration.json"):
            for record in json.loads((ARCHIVE / name).read_text())["files"]:
                locator = record["archive"]
                path = ROOT / locator["path"]
                if "member" in locator:
                    if path not in archives:
                        archives[path] = zipfile.ZipFile(path)
                    data = archives[path].read(locator["member"])
                else:
                    data = path.read_bytes()
                if len(data) != record["size"] or hashlib.sha256(data).hexdigest() != record["sha256"]:
                    raise ValueError(f"Migration checksum mismatch: {record['source']}")
                migrated += 1
    finally:
        for archive in archives.values():
            archive.close()
    print(f"PASS: {package_count} package files and {migrated} migrated file locators")


if __name__ == "__main__":
    main()
