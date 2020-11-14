#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import os.path
from freebsd_sysctl.__version__ import __version__
from setuptools import setup
from setuptools.command.build_py import build_py
from setuptools.command.sdist import sdist
import distutils.log


class BuildCommand(build_py):

    def run(self):
        super().run()

        self.announce(
            f"Tagging version {__version__}",
            level=distutils.log.INFO
        )
        if not self.dry_run:
            # generate .version files
            for package in self.distribution.packages:
                target = os.path.join(
                    self.build_lib,
                    package,
                    ".version"
                )
                with open(target, "w", encoding="UTF-8") as f:
                    f.write(__version__)
                    f.truncate()


class SdistCommand(sdist):

    def run(self):
        self.announce(
            f"Bundling Source Distribution of Release {__version__}",
            level=distutils.log.INFO
        )
        created_release_files = set()

        if not self.dry_run:
            # generate temporary RELEASE files
            for package in self.distribution.packages:
                release_file = os.path.join(
                    os.path.dirname(os.path.abspath(__file__)),
                    package,
                    ".version"
                )
                if os.path.isfile(release_file) is False:
                    created_release_files.add(release_file)
                    with open(release_file, "w", encoding="UTF-8") as f:
                        f.write(__version__)
                        f.truncate()
        try:
            pass
            super().run()
        finally:
            if not self.dry_run:
                for release_file in created_release_files:
                    os.remove(release_file)


if __name__ == "__main__":
    setup(
        cmdclass=dict(
            build_py=BuildCommand,
            sdist=SdistCommand
        )
    )
