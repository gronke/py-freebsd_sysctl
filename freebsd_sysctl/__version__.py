#!/usr/bin/env python3
import os
import os.path
import re

# When a RELEASE file exists, the version is read from this file.
# Otherwise the latest version from CHANGELOG.md is suffixed with -dev and
# a git commit hash (if available).

__dirname = os.path.dirname(__file__)
__module_dir = os.path.join(__dirname, "..")
__changelog_file = os.path.join(__module_dir, "CHANGELOG.md")
__release_version_file = os.path.join(__dirname, ".version")


def __read_first_line(relative_filename: str) -> str:
    absolute_path = os.path.join(__module_dir, relative_filename)
    with open(absolute_path, "r", encoding="UTF-8") as f:
        return f.readline().strip()


COMMIT = None
if os.path.isfile(__release_version_file) is True:
    __version__ = __read_first_line(__release_version_file)
else:
    # get latest semver from CHANGELOG.md
    __version_pattern = re.compile(r"## \[([0-9]+\.[0-9]+\.[0-9]+)\]")
    with open(__changelog_file, "r", encoding="UTF-8") as f:
        __version__ = __version_pattern.findall(f.read())[0]

    # dev version
    __version__ += "-dev"

    # append current git commit
    if os.path.isfile(".git/HEAD") is True:
        line = __read_first_line(".git/HEAD")
        __version__ += "-"
        if line.startswith("ref: ") is False:
            COMMIT = line
            __version__ += line[:8]
        else:
            ref = line[5:]
            COMMIT = __read_first_line(f".git/{ref}")
            __version__ += COMMIT[:8]

if __name__ == "__main__":
    print(VERSION)
    exit(0)

try:
    major, minor, patch = tuple(VERSION.split("."))
    commit = None
    __version__ = VERSION
except ValueError:
    major = minor = patch = None
    commit = VERSION

__version__ = VERSION
