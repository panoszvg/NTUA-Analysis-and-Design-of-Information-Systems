import os
import pathlib

from setuptools import setup, find_packages

NAME = "rhea"
VERSION = "0.0.2"
DESCRIPTION = "Real-time processing simulation package"
URL = "https://github.com/panoszvg/NTUA-Analysis-and-Design-of-Information-Systems"
AUTHOR = "Rhea"
REQUIRES_PYTHON = ">=3.7.0"

REQUIRED = [
    "pika>=1.2",
    "pyspark>=3.2"
]

repo_root = str(pathlib.Path(__file__).resolve().parent)

README_FILE = os.path.join(repo_root, "README.md")
with open(README_FILE, "r", encoding="utf8") as f:
    LONG_DESCRIPTION = f.read()

setup(
    name=NAME,
    version=VERSION,
    author=AUTHOR,
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    python_requires=REQUIRES_PYTHON,
    platforms="Linux, Mac OS X, Windows",
    url=URL,
    packages=find_packages(exclude=("examples",)),
    install_requires=REQUIRED,
    license="MIT",
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
    ],
)