# see https://wiki.freebsd.org/AlfonsoSiciliano/sysctlmibinfo

import typing
import ctypes
import struct
import enum
import sysctl.libc

NULL_BYTES = b"\x00"
CTL_MAXNAME = ctypes.c_uint(24)
T_OID = (ctypes.c_int * 2)


class CtlType:
    min_size = 0
    data: bytes
    ctype: typing.Optional[type] = None
    unpack_format: typing.Optional[str] = None

    def __init__(self, data: bytes) -> None:
        self.data = data

    @property
    def value(self) -> typing.Any:
        if self.unpack_format is None:
            return self.data.value
        value, = struct.unpack(f"<{self.unpack_format}", self.data)
        return value

    def __str__(self) -> str:
        value = self.value
        if isinstance(value, bytes) is True:
            return value.decode()
        return str(value)


class NodeType(CtlType):
    pass


class IntType(CtlType):
    ctype = ctypes.c_int
    min_size = ctypes.sizeof(ctypes.c_int)
    unpack_format = "i"


class StringType(CtlType):
    pass


class Int64Type(CtlType):
    ctype = ctypes.c_int64
    min_size = ctypes.sizeof(ctypes.c_int64)
    unpack_format = "q"


class StructType(CtlType):
    pass


class OpaqueType(CtlType):
    pass


class UIntType(CtlType):
    ctype = ctypes.c_uint
    min_size = ctypes.sizeof(ctypes.c_uint)
    unpack_format = "I"


class LongType(CtlType):
    ctype = ctypes.c_long
    min_size = ctypes.sizeof(ctypes.c_long)
    unpack_format = "q"


class ULongType(CtlType):
    ctype = ctypes.c_ulong
    min_size = ctypes.sizeof(ctypes.c_ulong)
    unpack_format = "Q"


class UInt64Type(CtlType):
    ctype = ctypes.c_uint64
    min_size = ctypes.sizeof(ctypes.c_uint64)
    unpack_format = "Q"


class UInt8Type(CtlType):
    ctype = ctypes.c_uint8
    min_size = ctypes.sizeof(ctypes.c_uint8)
    unpack_format = "B"


class UInt16Type(CtlType):
    ctype = ctypes.c_uint16
    min_size = ctypes.sizeof(ctypes.c_uint16)
    unpack_format = "H"


class Int8Type(CtlType):
    ctype = ctypes.c_int8
    min_size = ctypes.sizeof(ctypes.c_int8)
    unpack_format = "b"


class Int16Type(CtlType):
    ctype = ctypes.c_int16
    min_size = ctypes.sizeof(ctypes.c_int16)
    unpack_format = "h"


class Int32Type(CtlType):
    ctype = ctypes.c_int32
    min_size = ctypes.sizeof(ctypes.c_int32)
    unpack_format = "i"


class UInt32Type(CtlType):
    ctype = ctypes.c_uint32
    min_size = ctypes.sizeof(ctypes.c_uint32)
    unpack_format = "I"


def identify_type(kind: int, fmt: bytes) -> CtlType:
    ctl_type = kind & 0xF
    if ctl_type == 1:
        return NodeType
    elif ctl_type == 2:
        return IntType
    elif ctl_type == 3:
        return StringType
    elif ctl_type == 4:
        return Int64Type
    elif ctl_type == 5:
        # return StructType if (fmt[0:1] == b"S") else OpaqueType
        return OpaqueType
    elif ctl_type == 6:
        return UIntType
    elif ctl_type == 7:
        return LongType
    elif ctl_type == 8:
        return ULongType
    elif ctl_type == 9:
        return UInt64Type
    elif ctl_type == 10:
        return UInt8Type
    elif ctl_type == 11:
        return UInt16Type
    elif ctl_type == 12:
        return Int16Type
    elif ctl_type == 13:
        return Int16Type
    elif ctl_type == 14:
        return Int32Type
    elif ctl_type == 15:
        return UInt32Type
    else:
        raise Exception(f"Invalid ctl_type: {ctl_type}")


class Sysctl:

    _name: typing.Optional[str]
    _oid: typing.Optional[typing.List[int]]
    _kind: typing.Optional[int]
    _fmt = typing.Optional[bytes]
    _size: typing.Optional[int]
    _value: typing.Optional[str]

    def __init__(
        self,
        name: typing.Optional[str]=None,
        oid: typing.Optional[typing.List[int]]=None
    ) -> None:
        self._name = name
        self._oid = oid
        self._kind = None
        self._fmt = None
        self._size = None
        self._value = None

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

    @property
    def size(self) -> int:
        if self._size is None:
            self._size = self.oidsize(self.oid, self.ctl_type)
        return self._size

    @property
    def value(self) -> int:
        if self._value is None:
            self._value = self.oidvalue(self.oid, self.size, self.ctl_type)
        return self._value

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

        if len(buf) < 4:
            raise Exception("response buffer too small")
        result = buf[:buf_length]
        kind, = struct.unpack("<I", result[:4])
        fmt = result[4:]
        return (kind, fmt)

    @staticmethod
    def oidsize(oid: typing.List[int], ctl_type: CtlType) -> bytes:

        oid_type = ctypes.c_int * len(oid)
        _oid = (oid_type)(*oid)
        p_oid = ctypes.POINTER(oid_type)(_oid)

        length = ctypes.c_int()
        p_length = ctypes.POINTER(ctypes.c_int)(length)

        sysctl.libc.dll.sysctl(
            p_oid,
            len(oid),
            None,
            p_length,
            0
        )

        return max(length.value, ctl_type.min_size)

    @staticmethod
    def oidvalue(
        oid: typing.List[int],
        size: int,
        ctl_type: CtlType
    ) -> bytes:

        # ToDo: check if value is readable

        oid_type = ctypes.c_int * len(oid)
        _oid = (oid_type)(*oid)
        p_oid = ctypes.POINTER(oid_type)(_oid)

        buf_type = ctypes.c_char * size
        buf = buf_type()
        p_buf = ctypes.POINTER(buf_type)(buf)
        p_buf_void = ctypes.cast(p_buf, ctypes.c_void_p)

        buf_length = ctypes.sizeof(buf)
        p_buf_length = ctypes.POINTER(ctypes.c_int)(ctypes.c_int(buf_length))

        sysctl.libc.dll.sysctl(
            p_oid,
            ctypes.c_uint32(len(oid)),
            p_buf_void,
            p_buf_length,
            None,
            0
        )

        return ctl_type(buf)

    @property
    def ctl_type(self) -> CtlType:
        return self.get_ctl_type(self.kind, self.fmt)

    @staticmethod
    def get_ctl_type(kind: int, fmt: bytes) -> CtlType:
        return identify_type(kind, fmt)
