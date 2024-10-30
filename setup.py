from setuptools import find_packages, setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="kore",
    version="0.1.0",
    author="lowg0d",
    author_email="",
    description="",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
    python_requires=">=3.12",
    install_requires=["PySide6", "PySideSix-Frameless-Window", "click"],
    entry_points={
        "console_scripts": [
            "kore=kore.cli.cli:main",
        ],
    },
)
