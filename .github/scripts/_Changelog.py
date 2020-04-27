#!/usr/bin/env python
import typing
import os
import os.path
import re
import datetime
import urllib.parse

# MyPy
_SemverTuple = typing.Tuple[int, int, int]


class Date(datetime.datetime):

    __date_format = "%Y-%m-%d"

    def __str__(self) -> None:
        return format(self, self.__date_format)

    @staticmethod
    def strptime(value):
        date = datetime.datetime.strptime(value, Date.__date_format)
        return Date(date.year, date.month, date.day)


class Semver:

    __major: typing.Optional[int]
    __minor: typing.Optional[int]
    __patch: typing.Optional[int]

    def __init__(self, *args: typing.Union[str, _SemverTuple]) -> None:
        self.__major = None
        self.__minor = None
        self.__patch = None
        self.set_version(*args)

    def set_version(self, *args: typing.Union[str, _SemverTuple]) -> None:
        major = minor = patch = None
        if len(args) == 1 and isinstance(args[0], str):
            if (args[0] == "UNRELEASED"):
                major = minor = patch = None
            else:
                major, minor, patch = self.__parse_version_string(args[0])
        elif (len(args) == 3):
            major, minor, patch = args

        self.__major = major
        self.__minor = minor
        self.__patch = patch

    def __parse_version_string(self, value: str) -> _SemverTuple:
        major, minor, patch = [int(v) for v in value.split(".")]
        return (major, minor, patch,)

    @property
    def major(self) -> int:
        return self.__major

    @property
    def minor(self) -> int:
        return self.__minor

    @property
    def patch(self) -> int:
        return self.__patch

    def __str__(self) -> str:
        if self.__major == self.__minor == self.__patch == None:
            return "UNRELEASED"
        return f"{self.major}.{self.minor}.{self.patch}"

    def __repr__(self) -> str:
        return self.__str__()

    def __hash__(self) -> hash:
        return hash((self.major, self.minor, self.patch,))

    def __eq__(self, other: 'Semver') -> bool:
        major = (self.major == other.major)
        minor = (self.minor == other.minor)
        patch = (self.patch == other.patch)
        return (major and minor and patch)


class ChangelogSection:

    __date: Date
    __version: Semver
    text: str

    categories = [
        "Added",
        "Changed",
        "Deprecated",
        "Fixed",
        "Removed",
        "Breaking",
        "Security",
        "Chores"
    ]

    # vocabulary in older PRs might differ, but can be mapped on import
    _category_synonyms = [
        ["Added", "Features"],
        ["Changed", "Enhancement"],
        ["Fixed", "Bugs", "Fixes"],
        ["Chores", "Chore"]
    ]

    # categories that cause minor version bumps instead of patch versions
    _minor_version_triggers = [
        "Removed",
        "Breaking"
    ]

    __PATTERN = re.compile(
        (
            r"## \[(?P<version>UNRELEASED|\d+\.\d+\.\d+)\]"
            r"(?: - (?P<date>[0-9]{4}-[0-9]{2}-[0-9]{2}))?"
            r"\n*"
            r"(?P<text>.*?)"
            r"\n*$"
        ),
        re.DOTALL
    )

    @staticmethod
    def parse(section_body: str) -> typing.Any:
        match = ChangelogSection.__PATTERN.match(section_body)
        return ChangelogSection(
            version=match.group("version"),
            date=match.group("date"),
            text=match.group("text")
        )

    def __init__(
        self,
        version: typing.Union[str, _SemverTuple, Semver],
        text: str,
        date: typing.Optional[typing.Union[str, Date]]=None
    ) -> None:
        self.version = version
        self.date = date
        self.text = text.strip()

    @property
    def version(self) -> Semver:
        return self.__version

    @version.setter
    def version(self, value: typing.Union[str, _SemverTuple, Semver]) -> None:
        if isinstance(value, Semver):
            self.__version = value
        else:
            self.__version = Semver(value)

    @property
    def date(self) -> Date:
        return self.__date

    @date.setter
    def date(
        self,
        value: typing.Optional[
            typing.Union[str, datetime.datetime, Date]
        ]
    ) -> None:
        if isinstance(value, str) is True:
            self.__date = Date.strptime(value)
        elif value is None:
            self.__date = None
        else:
            self.__date = Date(value.year, value.month, value.day)

    @property
    def breaking(self) -> bool:
        """Return True if the changes were breaking."""
        keywords = self._minor_version_triggers
        text = self.text.upper()
        return any([(f"\n### {kw.upper()}" in text) for kw in keywords])

    def __str__(self) -> None:

        heading = f"[{str(self.version)}]"
        if self.date is not None:
            heading += f" - {str(self.date)}"
        text = self.text
        body = f"\n\n{text}" if (text != "") else ""
        return f"## {heading}{body}"

    @property
    def percent_encoded(self) -> str:
        """Return percent encoded string."""
        return urllib.parse.quote(self.__str__())

    def __repr__(self) -> str:
        return f'<Changes version="{self.version}" date="{self.date}">'


class Changelog(list):

    encoding = "UTF-8"
    file: str
    __sections: typing.List[ChangelogSection]

    def __init__(self, file: str="CHANGELOG.md") -> None:
        self.file = file
        self.__sections = []
        super().__init__()
        self.load()

    @property
    def sections(self):
        return self.__sections

    @property
    def next_version(self):
        latest = list(self)[1]
        current = latest.version
        if self.need_minor_bump is True:
            return Semver(current.major, current.minor+1, 0)
        else:
            return Semver(current.major, current.minor, current.patch+1)

    def get_section(
        self,
        version: typing.Union[str, _SemverTuple, Semver]
    ) -> ChangelogSection:
        if isinstance(version, Semver) is True:
            _version = version
        elif isinstance(version, str) is True:
            _version = Semver(version)
        else:
            _version = Semver(*version)

        for section in self.__sections:
            if section.version == _version:
                return section
        raise KeyError(f"Version '{version}' not found.")

    @property
    def need_minor_bump(self) -> bool:
        return any([section.breaking for section in self.__sections])

    def bump(self) -> Semver:

        if str(self.__sections[0].version) != "UNRELEASED":
            raise Exception(f"No unreleased changes found in {self.file}")

        next_version = self.next_version
        self.__sections[0].version = next_version
        self.__sections[0].date = datetime.datetime.now()

        self.__write(self.file)
        return next_version

    def load(self, file: typing.Optional[str]=None) -> None:
        _file = self.file if (file is None) else file
        data = self.__read(_file)
        if file is not None:
            self.file = file

        self.clear()

        for section in [f"## {x}" for x in data.split("\n## ")[1:]]:
            self.__sections.append(ChangelogSection.parse(section))

    def __get_absolute_path(self, file: str) -> str:
        return os.path.join(
            os.path.dirname(__file__),
            "../../",
            file
        )

    def __read(self, file: str) -> str:
        _file = self.__get_absolute_path(file)
        with open(_file, "r", encoding=self.encoding) as f:
            return f.read().strip()

    def __write(self, file: str) -> None:
        _file = self.__get_absolute_path(file)
        with open(_file, "w", encoding=self.encoding) as f:
            f.write(str(self))
            f.truncate()
        
    def clear(self) -> None:
        self.__sections.clear()

    def __setitem__(self, key: str, section: ChangelogSection) -> None:
        self.__sections[key] = section

    def __getitem__(self, key: str) -> ChangelogSection:
        return self.__sections[key]

    def __iter__(self):
        return self.__sections.__iter__()

    def __str__(self) -> str:
        sections = '\n\n'.join(
            [str(section) + "\n" for section in self.sections]
        )
        return f"# Changelog\n\n{sections}"