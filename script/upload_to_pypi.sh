#!/usr/bin/env sh

set -eu

SCRIPT_DIR="$(dirname "$0")"
cd "$(dirname "$SCRIPT_DIR")"

# Use venv Python if available, otherwise fall back to system python3
if [ -f .venv/bin/python ]; then
  PYTHON=.venv/bin/python
else
  PYTHON=python3
fi

if ! command -v "$PYTHON" >/dev/null 2>&1; then
  echo "Error: Python interpreter not found at $PYTHON." >&2
  exit 1
fi

if ! $PYTHON -m build --help >/dev/null 2>&1; then
  echo "Error: build package is not installed. Install with '$PYTHON -m pip install build'." >&2
  exit 1
fi

if ! $PYTHON -m twine --help >/dev/null 2>&1; then
  echo "Error: twine is not installed. Install with '$PYTHON -m pip install twine'." >&2
  exit 1
fi

# Auto-increment version
printf "Auto-incrementing version...\n"
$PYTHON -c "
import re
with open('source/__init__.py', 'r') as f:
    content = f.read()

match = re.search(r'__version__\s*=\s*[\"\'](.*?)[\"\']', content)
if match:
    version = match.group(1)
    parts = version.split('.')
    parts[-1] = str(int(parts[-1]) + 1)
    new_version = '.'.join(parts)
    new_content = re.sub(
        r'__version__\s*=\s*[\"\'](.*?)[\"\']',
        f'__version__ = \"{new_version}\"',
        content
    )
    with open('source/__init__.py', 'w') as f:
        f.write(new_content)
    print(f'{version} -> {new_version}')
"

REPOSITORY="pypi"
TWINE_ARGS=""

# Parse arguments
for arg in "$@"; do
  case "$arg" in
    --verbose)
      TWINE_ARGS="$TWINE_ARGS --verbose"
      ;;
    --skip-existing)
      TWINE_ARGS="$TWINE_ARGS --skip-existing"
      ;;
    testpypi)
      REPOSITORY="testpypi"
      ;;
    -*)
      # Pass other flags to twine
      TWINE_ARGS="$TWINE_ARGS $arg"
      ;;
    *)
      REPOSITORY="$arg"
      ;;
  esac
done

printf "Removing previous build artifacts...\n"
rm -rf build dist *.egg-info

printf "Building source and wheel distributions...\n"
$PYTHON -m build

printf "Uploading distributions to %s...\n" "$REPOSITORY"
$PYTHON -m twine upload --repository "$REPOSITORY" $TWINE_ARGS dist/*

printf "Cleaning up build artifacts...\n"
rm -rf build dist *.egg-info

printf "Upload complete.\n"