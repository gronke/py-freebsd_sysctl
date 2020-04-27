#!/usr/bin/env python
import os
import os.path


def read_first_line(relative_filename: str) -> str:
    __dirname = os.path.dirname(__file__)
    absolute_path = os.path.join(__dirname, "../", relative_filename)
    with open(absolute_path, "r", encoding="UTF-8") as f:
        return f.readline().strip()


try:
    VERSION = read_first_line("VERSION")
except Exception:
    # last git commit SHA is the version
    line = read_first_line(".git/HEAD")
    if line.startswith("ref: ") is False:
        VERSION = line
    else:
        ref = line[5:]
        VERSION = read_first_line(f".git/{ref}")

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
