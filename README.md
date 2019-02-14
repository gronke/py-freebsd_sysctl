# py-freebsd_sysctl

> A native Python module for FreeBSD sysctl.

This Python 3 interface for FreeBSD sysctl has no third party dependency and does not require a compile step to install.
It is meant for performant (read) access to sysctls, their type, value and description.


```python3
>>> from freebsd_sysctl import Sysctl
>>> Sysctl("security.jail.enforce_statfs").value
2
>>> Sysctl("security.jail.enforce_statfs").ctl_type
<class 'freebsd_sysctl.IntType'>
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
