# see https://wiki.freebsd.org/AlfonsoSiciliano/sysctlmibinfo

import typing
import ctypes
import struct
import enum
import sysctl.libc

NULL_BYTES = b"\x00"
CTL_MAXNAME = ctypes.c_uint(24)
T_OID = (ctypes.c_int * 2)


class Sysctl:

    _name: typing.Optional[str]
    _oid: typing.Optional[typing.List[int]]
    _kind: typing.Optional[int]
    _fmt = typing.Optional[bytes]

    def __init__(
        self,
        name: typing.Optional[str]=None,
        oid: typing.Optional[typing.List[int]]=None
    ) -> None:
        self._name = name
        self._oid = oid
        self._kind = None
        self._fmt = None

    @property
    def oid(self) -> typing.List[int]:
        if self._oid is None:
            if self.name is None:
                raise ValueError("Name or OID required")
            self._oid = self.name2oid(self.name)
        return self._oid

    @property
    def name(self) -> str:
        if self._name is None:
            if self.oid is None:
                raise ValueError("Name or OID required")
            raise NotImplementedError("Missing oid2name resolution") 
        return self._name

    @property
    def kind(self) -> int:
        if self._kind is None:
            self.__query_kind_and_fmt()
        return self._kind

    @property
    def fmt(self) -> int:
        if self._fmt is None:
            self.__query_kind_and_fmt()
        return self._fmt

    def __query_kind_and_fmt(self) -> None:
        self._kind, self._fmt = self.oidfmt(self.oid)

    @staticmethod
    def name2oid(name: str) -> typing.List[int]:
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

    @staticmethod
    def oidfmt(oid: typing.List[int]) -> bytes:

        qoid_len = (2 + len(oid))
        qoid_type = ctypes.c_int * qoid_len
        qoid = (qoid_type)(*([0, 4] + oid))
        p_qoid = ctypes.POINTER(qoid_type)(qoid)

        buf_type = ctypes.c_char * 1024
        buf = buf_type()
        p_buf = ctypes.POINTER(buf_type)(buf)
        buf_void = ctypes.cast(p_buf, ctypes.c_void_p)

        buf_length = ctypes.sizeof(buf)
        p_buf_length = ctypes.POINTER(ctypes.c_int)(ctypes.c_int(buf_length))

        sysctl.libc.dll.sysctl(
            p_qoid,
            qoid_len,
            buf_void,
            p_buf_length,
            0,
            0
        )

        assert len(buf) >= 4
        result = buf[:buf_length]
        kind, = struct.unpack("<I", result[:4])
        fmt = result[4:]
        return (kind, fmt)

    @property
    def ctl_type(self) -> str:
        return self.get_ctl_type(self.kind, self.fmt)

    @staticmethod
    def get_ctl_type(kind: int, fmt: bytes) -> str:
        ctl_types = [
            "node",
            "int",
            "string",
            "s64",
            ("struct", "opaque",),
            "uint",
            "long",
            "ulong",
            "u64",
            "u8",
            "u16",
            "s8",
            "s16",
            "s32",
            "u32"
        ]
        ctl_type = kind & 0xF
        assert ctl_type != 0

        if ctl_type == 5:
            return "struct" if (fmt[0:1] == b"S") else "opaque"
        else:
            return ctl_types[ctl_type-1]


# Sysctl("security.jail.enforce_statfs")
# Sysctl("security.jail.param.host.hostuuid")
# Sysctl("security.jail.param.path")
# Sysctl("security.jail.param.osrelease")
# Sysctl("security.jail.param.children.max")

