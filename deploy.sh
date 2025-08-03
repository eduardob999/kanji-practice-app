rm -rf dist/ build/ pjapp.egg-info/
python3 -m build
twine upload dist/*