#!/usr/bin/python3

# Finds the content of the first markdown h2 section
# Stops at the next h2 heading or the end of the file.
import sys
from _Changelog import Changelog

changelog = Changelog()

args = sys.argv[1:]
percent_encoded = ("--percent-encode" in args)
bump_version = ("--bump-version" in args)
show_version_only = ("--version-only" in args)

if "--version" in args:
    if bump_version is True:
        print("--version cannot be used with --bump-version")
        exit(1)
    _index = args.index("--version")
    version = args[_index + 1]
elif bump_version is True:
    try:
        version = changelog.bump()
    except Exception as e:
        print(str(e).strip("\""), file=sys.stderr)
        exit(1)
else:
    version = "UNRELEASED"

try:
    if str(version) == "latest":
        section = changelog.sections[0]
    else:
        section = changelog.get_section(version)
except KeyError as e:
    print(str(e).strip("\""), file=sys.stderr)
    exit(1)

if section is None:
    exit(1)
else:
    if show_version_only is True:
        print(str(section.version))
    elif percent_encoded is True:
        print(section.percent_encoded)
    else:
        print(str(section))
