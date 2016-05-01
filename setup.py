#!/usr/bin/env python

import codecs
import os

from setuptools import setup


MY_DIR = os.path.dirname(os.path.realpath(__file__))

setup(
    name="pacmimi",
    use_scm_version={
        "write_to": os.path.join(MY_DIR, "pacmimi", "app_version.py")
    },
    description="Arch Linux Pacman mirrorlist merging utility",
    # Read the long description from our README.rst file, as UTF-8.
    long_description=codecs.open(
        os.path.join(MY_DIR, "README.rst"),
        "rb",
        "utf-8"
    ).read(),
    author="Tilman Blumenbach",
    author_email="tilman+pypi@ax86.net",
    entry_points={
        "console_scripts": [
            "pacmimi = pacmimi.main:main"
        ]
    },
    license="BSD 3-Clause License",
    url="https://github.com/Tblue/pacmimi",
    packages=["pacmimi"],
    setup_requires=["setuptools_scm ~= 1.10"],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Console",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: BSD License",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.2",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3 :: Only",
        "Topic :: System :: Systems Administration",
        "Topic :: Utilities"
    ]
)
