#!/usr/bin/env bash
set -euo pipefail

# Locate sibling repositories automatically.
STAR_ROOT="$(git rev-parse --show-toplevel)"
PARENT_DIR="$(dirname "$STAR_ROOT")"
LAB_ROOT="$PARENT_DIR/star-lab"

SRC="$STAR_ROOT/results/phase4"
CASE_REL="experiments/2026-09-minimap-unit-layer-tail"
CASE_ROOT="$LAB_ROOT/$CASE_REL"
DST="$CASE_ROOT/results"
ARTIFACTS="$CASE_ROOT/artifacts"

echo "STAR root : $STAR_ROOT"
echo "STAR Lab  : $LAB_ROOT"
echo "Case      : $CASE_ROOT"
echo

if [[ ! -d "$LAB_ROOT/.git" ]]; then
  echo "ERROR: sibling star-lab repository not found at:"
  echo "  $LAB_ROOT"
  exit 1
fi

if [[ ! -d "$SRC" ]]; then
  echo "ERROR: Phase-4 result directory not found:"
  echo "  $SRC"
  exit 1
fi

mkdir -p "$DST" "$ARTIFACTS"

# ----------------------------------------------------------------------
# Canonical formal evidence
#
# Keep this deliberately small. These are exactly the raw artifacts
# currently declared formal_pending in STAR Lab manifest.yaml.
# ----------------------------------------------------------------------

declare -a COPY_MAP=(

  # 25% crossing-cost diagnostic
  "density-025-crossing-correlation.json|density-025-crossing-correlation.json"
  "density-025-crossing-correlation-profile.json|density-025-crossing-correlation-profile.json"

  # 25% same-code MiniMap unit-layer A/B
  "density-025-minimap-units-on.json|density-025-minimap-units-on.json"
  "density-025-minimap-units-on-profile.json|density-025-minimap-units-on-profile.json"

  "density-025-minimap-units-off.json|density-025-minimap-units-off.json"
  "density-025-minimap-units-off-profile.json|density-025-minimap-units-off-profile.json"

  # 50% Core 60Hz three fresh-process runs
  # Run 1 was originally saved without the explicit "run1" suffix,
  # so normalize its canonical archive name here.
  "density-050-core-60hz.json|density-050-core-60hz-run1.json"
  "density-050-core-60hz-profile.json|density-050-core-60hz-run1-profile.json"

  "density-050-core-60hz-run2.json|density-050-core-60hz-run2.json"
  "density-050-core-60hz-run2-profile.json|density-050-core-60hz-run2-profile.json"

  "density-050-core-60hz-run3.json|density-050-core-60hz-run3.json"
  "density-050-core-60hz-run3-profile.json|density-050-core-60hz-run3-profile.json"
)

echo "== Checking source artifacts =="

for mapping in "${COPY_MAP[@]}"; do
  src_name="${mapping%%|*}"

  if [[ ! -f "$SRC/$src_name" ]]; then
    echo "ERROR: missing source artifact:"
    echo "  $SRC/$src_name"
    exit 1
  fi
done

echo "All 12 source artifacts exist."
echo

echo "== Validating JSON =="

for mapping in "${COPY_MAP[@]}"; do
  src_name="${mapping%%|*}"
  python3 -m json.tool "$SRC/$src_name" >/dev/null
  echo "OK  $src_name"
done

echo
echo "== Copying canonical artifacts =="

for mapping in "${COPY_MAP[@]}"; do
  src_name="${mapping%%|*}"
  dst_name="${mapping#*|}"

  cp -p "$SRC/$src_name" "$DST/$dst_name"

  # Byte-for-byte verification after copy.
  if ! cmp -s "$SRC/$src_name" "$DST/$dst_name"; then
    echo "ERROR: copied artifact differs from source:"
    echo "  $src_name -> $dst_name"
    exit 1
  fi

  echo "$src_name"
  echo "  -> $dst_name"
done

echo
echo "== Generating SHA256SUMS =="

cd "$CASE_ROOT"

cat > artifacts/SHA256SUMS.tmp <<'EOF'
EOF

# Generate checksums using paths relative to the experiment root,
# as required by STAR Lab PROTOCOL.md.
FORMAL_FILES=(
  "results/density-025-crossing-correlation.json"
  "results/density-025-crossing-correlation-profile.json"
  "results/density-025-minimap-units-on.json"
  "results/density-025-minimap-units-on-profile.json"
  "results/density-025-minimap-units-off.json"
  "results/density-025-minimap-units-off-profile.json"
  "results/density-050-core-60hz-run1.json"
  "results/density-050-core-60hz-run1-profile.json"
  "results/density-050-core-60hz-run2.json"
  "results/density-050-core-60hz-run2-profile.json"
  "results/density-050-core-60hz-run3.json"
  "results/density-050-core-60hz-run3-profile.json"
)

: > artifacts/SHA256SUMS

for file in "${FORMAL_FILES[@]}"; do
  shasum -a 256 "$file" >> artifacts/SHA256SUMS
done

rm -f artifacts/SHA256SUMS.tmp

echo
cat artifacts/SHA256SUMS

echo
echo "== Verifying SHA256 integrity =="

shasum -a 256 -c artifacts/SHA256SUMS

echo
echo "== Archive contents =="

find results -maxdepth 1 -type f -print | sort
echo
find artifacts -maxdepth 1 -type f -print | sort

echo
echo "== Git status =="

git -C "$LAB_ROOT" status --short "$CASE_REL"

echo
echo "DONE."
echo
echo "Next:"
echo "  cd \"$LAB_ROOT\""
echo "  git add \"$CASE_REL\""
echo "  git status"
echo
echo "Review the diff, then commit/push when satisfied."
