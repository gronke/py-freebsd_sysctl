# py-freebsd_sysctl

> Native Python wrapper for FreeBSD sysctls using libc.

This Python 3 interface for FreeBSD sysctl has no third party dependency and does not require a compile step to install.
It is meant for performant (read) access to sysctls, their type, value and description.


```python3
>>> from freebsd_sysctl import Sysctl
>>> Sysctl("security.jail.enforce_statfs").value
2
>>> Sysctl("security.jail.enforce_statfs").ctl_type
<class 'freebsd_sysctl.types.INT'>
>>> Sysctl("security.jail.enforce_statfs").description
'Processes in jail cannot see all mounted file systems (deprecated)'
```

With either a sysctl `name` or `oid` the other properties provide memoized access to lazy-loaded properties.

## Properties

### Read/Write

| Property Name | Description |
| ------------- | ----------- |
| `name`        | String identifier of the sysctl. |
| `oid`         | List of Integer values identifying the sysctl. |

### Read-Only

| Read Property Name | Description |
| ------------- | ----------- |
| `value`       | Value of a sysctl. `sysctl <name>` |
| `ctl_type`    | sysctl type class. `sysctl -t <name>` |
| `description` | Text description of the sysctl. `sysctl -d <name>` |

---

This project is heavily inspired by [johalun/sysctl-rs](https://github.com/johalun/sysctl-rs).
Kudos to @fabianfreyer for untiring support and debugging.

It is developed and maintained by Stefan Grönke ([@gronke](https://github.com/gronke)) and published under [BSD 2-Clause License](LICENSE.txt).

## Development

### Unit Tests

Unit tests may run on FreeBSD or HardenedBSD.

### Static Code Analysis

The project enforces PEP-8 code style and MyPy strong typing via flake8, that is required to pass before merging any changes.
Together with Bandit checks for common security issues the static code analysis can be ran on Linux and BSD code execution.

```
make install-dev
make check
```

### Releases

We try to *manually* keep a [Changelog](CHANGELOG.md), following the style on [changelog.md](https://changelog.md).
New releases are tagged according to [Semver](https://semver.org/), released on [PyPi](https://pypi.org/project/libioc/), and published as [port](https://github.com/bsdci/ports).

To get a port published, we need to [create a Bugzilla Issue in the Ports category](https://bugs.freebsd.org/bugzilla/enter_bug.cgi?component=Individual%20Port%28s%29&product=Ports%20%26%20Packages)
