#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 2 || $# -gt 3 ]]; then
  echo "Usage: $0 <managed-solution.zip> <xform.xml> [baseline-bridge-import.json]" >&2
  exit 2
fi

project_dir="$(cd "$(dirname "$0")" && pwd)"
solution_path="$(realpath "$1")"
xform_path="$(realpath "$2")"
baseline_path="${3:-}"
if [[ -n "$baseline_path" ]]; then
  baseline_path="$(realpath "$baseline_path")"
fi
solution_hash="99e5e030d7c7257d8415aa90d93c4068e44019c198bcc19bdc472523580e4a04"
xform_hash="1fa53c3517f63dac748c777616c322a9be4da8b70b89e5e3a21a61d6619d8b51"

verify_hash() {
  local expected="$1"
  local path="$2"
  local actual
  actual="$(sha256sum "$path" | awk '{print $1}')"
  if [[ "$actual" != "$expected" ]]; then
    echo "SHA-256 mismatch for $path" >&2
    echo "Expected: $expected" >&2
    echo "Actual:   $actual" >&2
    exit 1
  fi
}

verify_hash "$solution_hash" "$solution_path"
verify_hash "$xform_hash" "$xform_path"

solution_stage="$(mktemp)"
cp "$solution_path" "$solution_stage"
baseline_stage=""
if [[ -n "$baseline_path" ]]; then
  baseline_stage="$(mktemp)"
  cp "$baseline_path" "$baseline_stage"
fi

find "$project_dir/DeploymentAssets/Solutions" -maxdepth 1 -type f -name '*.zip' -delete
find "$project_dir/PkgAssets/Content" -maxdepth 1 -type f -name '*.xml' -delete
find "$project_dir/PkgAssets/Content" -maxdepth 1 -type f -name '*.json' -delete
cp "$solution_stage" "$project_dir/DeploymentAssets/Solutions/$(basename "$solution_path")"
rm -f "$solution_stage"
cp "$xform_path" "$project_dir/PkgAssets/Content/tacatdp_impact_evaluation-2608130924.xml"
if [[ -n "$baseline_stage" ]]; then
  cp "$baseline_stage" "$project_dir/PkgAssets/Content/tacatdp-baseline-bridge-import.json"
  rm -f "$baseline_stage"
fi

dotnet publish "$project_dir/Tacatdp.DeploymentPackage.csproj" -c Release

package_path="$project_dir/bin/Release/Tacatdp.DeploymentPackage.1.0.3.pdpkg.zip"
python3 "$project_dir/../../scripts/validate-deployment-package.py" "$package_path"
echo "$package_path"
