# see https://wiki.freebsd.org/AlfonsoSiciliano/sysctlmibinfo

import typing
import ctypes
import sysctl.libc

NULL_BYTES = b"\x00"
CTL_MAXNAME = ctypes.c_uint(24)
T_OID = (ctypes.c_int * 2)


class Sysctl:

    name: str
    oid: typing.List[int]
    fmt = bytes

    def __init__(self, name: str) -> None:
        self.name = name
        self.oid = self.name2oid(self.name)
        self.fmt = self.oidfmt(self.oid)

    def name2oid(self, name: str) -> typing.List[int]:
        p_name = ctypes.c_char_p(name.encode() + NULL_BYTES)
        oid = T_OID(0, 3)
        p_oid = ctypes.POINTER(T_OID)(oid)

        length = ctypes.c_int(CTL_MAXNAME.value * ctypes.sizeof(ctypes.c_int))
        p_length = ctypes.POINTER(ctypes.c_int)(length)

        Res = ctypes.c_int*length.value
        res = (Res)()

        sysctl.libc.dll.sysctl(
            p_oid,
            2,
            ctypes.POINTER(Res)(res),
            p_length,
            p_name,
            len(p_name.value)
        )

        oid_length = int(length.value / ctypes.sizeof(ctypes.c_int))
        return res[:oid_length]

    def oidfmt(self, oid: typing.List[int]) -> bytes:
        qoid_len = (2 + len(oid))
        qoid_type = ctypes.c_int * qoid_len
        qoid = (qoid_type)(*([0, 4] + oid))
        p_qoid = ctypes.POINTER(qoid_type)(qoid)

        buf = ctypes.create_string_buffer(2048)
        buf_void = ctypes.cast(buf, ctypes.c_void_p)

        length = ctypes.sizeof(buf)
        p_length = ctypes.POINTER(ctypes.c_int)(ctypes.c_int(length))

        sysctl.libc.dll.sysctl(
            p_qoid,
            qoid_len,
            buf_void,
            p_length,
            0,
            0
        )

        print(self.name)
        print(self.oid)
        print(buf.value)

        return buf.value


Sysctl("security.jail.enforce_statfs")
Sysctl("security.jail.param.host.hostuuid")
Sysctl("security.jail.param.path")
Sysctl("security.jail.param.osrelease")
Sysctl("security.jail.param.children.max")