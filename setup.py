"""
Setup configuration for Nays Framework package.
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read the README file
readme_file = Path(__file__).parent / "README.md"
long_description = ""
if readme_file.exists():
    long_description = readme_file.read_text(encoding="utf-8")

# Read requirements
requirements_file = Path(__file__).parent / "requirements.txt"
install_requires = []
if requirements_file.exists():
    with open(requirements_file) as f:
        install_requires = [line.strip() for line in f if line.strip() and not line.startswith("#")]

setup(
    name="nays",
    version="1.0.0",
    author="Nays Contributors",
    description="A NestJS-like Python modular framework with PySide6 UI support",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/codersidprogrammer/nays",
    packages=find_packages(exclude=["test", "tests", "*.tests"]),
    python_requires=">=3.8",
    install_requires=install_requires,
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Application Frameworks",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
    ],
    keywords="framework module router dependency-injection pyside6 ui",
    project_urls={
        "Bug Reports": "https://github.com/codersidprogrammer/nays/issues",
        "Source": "https://github.com/codersidprogrammer/nays",
    },
)
