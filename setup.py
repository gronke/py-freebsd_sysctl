#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import os.path
import sys
from setuptools import find_packages, setup

cwd = os.getcwd()

about = {}
version_file = os.path.join(os.getcwd(), "freebsd_sysctl", '__version__.py')
with open(version_file, encoding="utf-8") as f:
    VERSION = exec(f.read(), about)

with open(os.path.join(cwd, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()


setup(
	name="freebsd_sysctl",
	version=about['__version__'],
	description="A native Python module for FreeBSD sysctl.",
	long_description=long_description,
	long_description_content_type="text/markdown",
	url="https://github.com/gronke/py-freebsd_sysctl",
	author="Stefan Grönke",
	author_email="stefan@gronke.net",
	python_requires=">=3.6",
	setup_requires=["pytest-runner"],
	tests_require=["pytest"],
	packages=find_packages(exclude=('tests',))
)
