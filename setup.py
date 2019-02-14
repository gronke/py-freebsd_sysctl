#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import os.path
import sys
from setuptools import find_packages, setup


about = {}
with open(os.path.join(os.getcwd(), "freebsd_sysctl", '__version__.py')) as f:
    VERSION = exec(f.read(), about)


setup(
	name="freebsd_sysctl",
	version=about['__version__'],
	description="A native Python module for FreeBSD sysctl.",
	url="https://github.com/gronke/py-freebsd_sysctl",
	author="Stefan Grönke",
	author_email="stefan@gronke.net",
	python_requires=">=3.6",
	setup_requires=["pytest-runner"],
	tests_require=["pytest"],
	packages=find_packages(exclude=('tests',))
)