from setuptools import setup, find_packages
import os
import re

def read_version(): 
    init_path = os.path.join(os.path.dirname(__file__), "practicejapanese", "__init__.py")
    with open(init_path, "r") as f:
        content = f.read()
    match = re.search(r'__version__\s*=\s*[\'"]([^\'"]+)[\'"]', content)
    return match.group(1) if match else "0.0.0"

def read_requirements():
    req_path = os.path.join(os.path.dirname(__file__), "requirements.txt")
    with open(req_path, "r") as f:
        lines = f.readlines()
    return [line.strip() for line in lines if line.strip() and not line.startswith('#')]

setup(
    name="pjapp",
    version=read_version(),
    packages=find_packages(),
    install_requires=read_requirements(),
    entry_points={
        "console_scripts": [
            "pjapp=practicejapanese.main:main"
        ]
    },
    include_package_data=True,
)