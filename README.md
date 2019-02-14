# py-systl

Native Python 3 module for FreeBSD sysctl.

```python3
>>> import sysctl
>>> sysctl.Sysctl("security.jail.enforce_statfs").value
2
>>> sysctl.Sysctl("security.jail.enforce_statfs").ctl_type
<class 'sysctl.IntType'>
```