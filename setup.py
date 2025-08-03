from setuptools import setup, find_packages

setup(
    name="pjapp",
    version="0.1.2",
    packages=find_packages(),
    install_requires=[
        "requests"
    ],
    entry_points={
        "console_scripts": [
            "pjapp=practicejapanese.main:main"
        ]
    },
    include_package_data=True,
)