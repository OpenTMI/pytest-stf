#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
:copyright: (c) 2021 by Jussi Vatjus-Anttila
:license: MIT, see LICENSE for more details.
"""
from setuptools import setup


setup(
    name="pytest-stf",
    use_scm_version=True,
    description="pytest plugin for openSTF",
    long_description=open("README.md").read(),
    long_description_content_type='text/markdown',
    author="Jussi Vatjus-Anttila",
    author_email="jussiva@gmail.com",
    url="https://github.com/opentmi/pytest-stf",
    packages=["pytest_stf"],
    entry_points={"pytest11": ["stf = pytest_stf.plugin"]},
    setup_requires=["setuptools_scm"],
    install_requires=[
        "pytest>=5.0",
        "pytest-metadata",
        "stf-appium-client==0.9.4",
        "pytest-lockable==0.9.1"],
    # List additional groups of dependencies here (e.g. development
    # dependencies). Users will be able to install these using the "extras"
    # syntax, for example:
    #
    #   $ pip install .[dev]
    #
    # Similar to `install_requires` above, these must be valid existing
    # projects.
    extras_require={  # Optional
        'dev': ['pytest-cov', 'mock', 'flake8', 'pylint', 'pyinstaller']
    },
    license="Mozilla Public License 2.0 (MPL 2.0)",
    keywords="py.test pytest openstf android phone",
    python_requires=">=3.9",
    classifiers=[
        # "Development Status :: 5 - Production/Stable",
        "Framework :: Pytest",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Mozilla Public License 2.0 (MPL 2.0)",
        "Operating System :: POSIX",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: MacOS :: MacOS X",
        "Topic :: Software Development :: Quality Assurance",
        "Topic :: Software Development :: Testing",
        "Topic :: Utilities",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3 :: Only",
    ],
)
