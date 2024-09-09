import subprocess
from pathlib import Path


# Get root path
BASE_DIR = Path(__file__).resolve().parent.parent

print(BASE_DIR)

"""
Run the following commands:
python3 -m build --sdist .
python3 -m build --wheel .
twine upload dist/*
"""

subprocess.call(["python", "-m", "build", "--sdist", "."])
subprocess.call(["python", "-m", "build", "--wheel", "."])
subprocess.call(["twine", "upload", "dist/*"])