#!/bin/bash
# This script automates the build and upload process for the PracticeJapanese package.
rm -rf dist/ build/ pjapp.egg-info/

# Bump version number
version_file="practicejapanese/__init__.py"
current_version=$(grep -Po "(?<=__version__ = \")([0-9]+\.[0-9]+\.[0-9]+)" "$version_file")

IFS='.' read -r major minor patch <<< "$current_version"

patch=$((patch + 1))
if (( patch >= 10 )); then
  patch=0
  minor=$((minor + 1))
fi
if (( minor >= 10 )); then
  minor=0
  major=$((major + 1))
fi

new_version="${major}.${minor}.${patch}"

sed -i "s/__version__ = \".*\"/__version__ = \"${new_version}\"/" "$version_file"
echo "Version bumped to $new_version"

# Reset all scores before build/upload
python3 -c "from practicejapanese.core.utils import reset_scores; reset_scores()"

# Build and upload the package
python3 -m build
twine upload dist/*