#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os.path
from setuptools import find_packages, setup

__dirname = os.path.abspath(os.path.dirname(__file__))

about = {}
with open(os.path.join(__dirname, "freebsd_sysctl", '__version__.py')) as f:
    VERSION = exec(f.read(), about)

setup(
	name="freebsd_sysctl",
	version=about['__version__'],
	description="A native Python module for FreeBSD sysctl.",
	url="https://github.com/gronke/py-freebsd_sysctl",
	author="Stefan Grönke",
	author_email="stefan@gronke.net",
	python_requires=">=3.6",
	tests_require=["pytest"],
	packages=find_packages(exclude=('tests',))
)