#!/usr/bin/env python3
import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="djhtml",
    version="0.0.2",
    author="Jaap Joris Vens",
    author_email="jj@rtts.eu",
    description="Django template indenter",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/rtts/djhtml",
    packages=setuptools.find_packages(),
    entry_points={
        "console_scripts": ["djhtml=djhtml.__main__:main"],
    },
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
)
