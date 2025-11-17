#!/bin/bash
set -euo pipefail
TAG_VERSION="${1:-}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

python3 - "$SCRIPT_DIR" "$TAG_VERSION" << 'PY'
import sys
import re
from pathlib import Path

# args: sys.argv[1] = script_dir, sys.argv[2] = tag
script_dir = Path(sys.argv[1])
tag = sys.argv[2] if len(sys.argv) > 2 else ""

def get_version_from_init(path: Path) -> str:
    init_path = script_dir.joinpath("OpenCtrl","__init__.py")
    print(init_path)
    with open(init_path,'r') as f:
        for line in f:
            if line.startswith('__version__'):
                delim = '"' if '"' in line else "'"
                return(line.split(delim)[1])

version = get_version_from_init(script_dir)
print(version)
if tag == version:
    print(f"Version Consistent: {tag} == {version}")
    sys.exit(0)
else:
    print(f"Version Inconsistent: {tag} != {version}")
    sys.exit(1)
PY
exit $?