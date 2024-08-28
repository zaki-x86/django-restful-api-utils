python3 -m build --sdist .
python3 -m build --wheel .
twine upload dist/*
