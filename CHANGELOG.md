## 0.11.0 - 2020-04-23

### Added

- [This changelog!](https://github.com/gronke/py-freebsd_sysctl/pull/6)
- [Test automation on Travis and Cirrus CI](https://github.com/gronke/py-freebsd_sysctl/pull/5)

### Changed

- bumped version to 0.11.0, because of all the changes
- [speedup loading of C library](https://github.com/gronke/py-freebsd_sysctl/pull/4)

### Fixed

- We're now ignoring the entire `debug.` space, because it was causing a lot of trouble with parsing
