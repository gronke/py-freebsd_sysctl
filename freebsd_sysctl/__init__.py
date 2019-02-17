# Copyright (c) 2019, Stefan Grönke
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted providing that the following conditions
# are met:
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE AUTHOR ``AS IS'' AND ANY EXPRESS OR
# IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED.  IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS
# OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
# HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT,
# STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING
# IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
import typing
import ctypes
import struct
import enum
import freebsd_sysctl.libc
import freebsd_sysctl.types
import freebsd_sysctl.flags

NULL_BYTES = b"\x00"
CTL_MAXNAME = ctypes.c_uint(24)
T_OID = (ctypes.c_int * 2)
BUFSIZ = 1024 # see /include/stdio.h#L209


class Sysctl:

    _name: typing.Optional[str]
    _oid: typing.Optional[typing.List[int]]
    _kind: typing.Optional[int]
    _fmt = typing.Optional[bytes]
    _size: typing.Optional[int]
    _value: typing.Optional[str]
    _description: typing.Optional[str]

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
        self._description = None

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
            self._name = self.oid2name(self.oid)
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
            self._size = self.query_size(self.oid, self.ctl_type)
        return self._size

    @property
    def raw_value(self) -> int:
        if self._value is None:
            self._value = self.qurty_value(self.oid, self.size, self.ctl_type)
        return self._value

    @property
    def value(self) -> int:
        return self.raw_value.value

    @property
    def description(self) -> int:
        if self._description is None:
            self._description = self.query_description(self.oid)
        return self._description

    @property
    def next(self):
        return self.__class__(oid=self.query_next(self.oid))

    @property
    def children(self) -> typing.Iterator['Sysctl']:
        if self.ctl_type != freebsd_sysctl.types.NODE:
            return
        current = self.next
        while self.oid == current.oid[:len(self.oid)]:
            yield current
            current = current.next

    def __query_kind_and_fmt(self) -> None:
        self._kind, self._fmt = self.query_fmt(self.oid)

    @staticmethod
    def name2oid(name: str) -> typing.List[int]:
        p_name = ctypes.c_char_p(name.encode() + NULL_BYTES)
        oid = T_OID(0, 3)
        p_oid = ctypes.POINTER(T_OID)(oid)

        length = ctypes.c_int(CTL_MAXNAME.value * ctypes.sizeof(ctypes.c_int))
        p_length = ctypes.POINTER(ctypes.c_int)(length)

        Res = ctypes.c_int*length.value
        res = (Res)()

        freebsd_sysctl.libc.dll.sysctl(
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
    def oid2name(oid: typing.List[int]) -> str:
        qoid_len = (2 + len(oid))
        qoid_type = ctypes.c_int * qoid_len
        qoid = (qoid_type)(*([0, 1] + oid))
        p_qoid = ctypes.POINTER(qoid_type)(qoid)

        buf = ctypes.create_string_buffer(BUFSIZ)
        buf_void = ctypes.cast(buf, ctypes.c_void_p)

        buf_length = ctypes.sizeof(buf)
        p_buf_length = ctypes.POINTER(ctypes.c_int)(ctypes.c_int(buf_length))

        freebsd_sysctl.libc.dll.sysctl(
            p_qoid,
            qoid_len,
            buf_void,
            p_buf_length,
            0,
            0
        )
        return buf.value.decode()

    @staticmethod
    def query_fmt(oid: typing.List[int]) -> bytes:

        qoid_len = (2 + len(oid))
        qoid_type = ctypes.c_int * qoid_len
        qoid = (qoid_type)(*([0, 4] + oid))
        p_qoid = ctypes.POINTER(qoid_type)(qoid)

        buf_type = ctypes.c_char * BUFSIZ
        buf = buf_type()
        p_buf = ctypes.POINTER(buf_type)(buf)
        buf_void = ctypes.cast(p_buf, ctypes.c_void_p)

        buf_length = ctypes.sizeof(buf)
        p_buf_length = ctypes.POINTER(ctypes.c_int)(ctypes.c_int(buf_length))

        freebsd_sysctl.libc.dll.sysctl(
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
    def query_size(
        oid: typing.List[int],
        ctl_type: freebsd_sysctl.types.CtlType
    ) -> bytes:

        oid_type = ctypes.c_int * len(oid)
        _oid = (oid_type)(*oid)
        p_oid = ctypes.POINTER(oid_type)(_oid)

        length = ctypes.c_int()
        p_length = ctypes.POINTER(ctypes.c_int)(length)

        freebsd_sysctl.libc.dll.sysctl(
            p_oid,
            len(oid),
            None,
            p_length,
            0
        )

        return max(length.value, ctl_type.min_size)

    @staticmethod
    def qurty_value(
        oid: typing.List[int],
        size: int,
        ctl_type: freebsd_sysctl.types.CtlType
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

        freebsd_sysctl.libc.dll.sysctl(
            p_oid,
            ctypes.c_uint32(len(oid)),
            p_buf_void,
            p_buf_length,
            None,
            0
        )

        return ctl_type(buf, size)

    @staticmethod
    def query_description(
        oid: typing.List[int]
    ) -> str:

        qoid_len = (2 + len(oid))
        qoid_type = ctypes.c_int * qoid_len
        qoid = (qoid_type)(*([0, 5] + oid))
        p_qoid = ctypes.POINTER(qoid_type)(qoid)

        buf_type = ctypes.c_char * BUFSIZ
        buf = buf_type()
        p_buf = ctypes.POINTER(buf_type)(buf)
        buf_void = ctypes.cast(p_buf, ctypes.c_void_p)

        buf_length = ctypes.sizeof(buf)
        p_buf_length = ctypes.POINTER(ctypes.c_int)(ctypes.c_int(buf_length))

        freebsd_sysctl.libc.dll.sysctl(
            p_qoid,
            qoid_len,
            buf_void,
            p_buf_length,
            0,
            0
        )

        return buf.value.decode()

    @staticmethod
    def query_next(oid: typing.List[int]) -> bytes:

        qoid_len = (2 + len(oid))
        qoid_type = ctypes.c_int * qoid_len
        qoid = (qoid_type)(*([0, 2] + oid))
        p_qoid = ctypes.POINTER(qoid_type)(qoid)

        buf_type = ctypes.c_int * CTL_MAXNAME.value
        buf = buf_type()
        p_buf = ctypes.POINTER(buf_type)(buf)
        buf_void = ctypes.cast(p_buf, ctypes.c_void_p)

        buf_length = ctypes.sizeof(buf)
        p_buf_length = ctypes.POINTER(ctypes.c_int)(ctypes.c_int(buf_length))

        freebsd_sysctl.libc.dll.sysctl(
            p_qoid,
            qoid_len,
            buf_void,
            p_buf_length,
            0,
            0
        )

        oid_length = int(
            p_buf_length.contents.value / ctypes.sizeof(ctypes.c_int)
        )
        return buf[0:oid_length]

    @property
    def ctl_type(self) -> freebsd_sysctl.types.CtlType:
        return self.get_ctl_type(self.kind, self.fmt)

    @staticmethod
    def get_ctl_type(
        kind: int,
        fmt: bytes
    ) -> freebsd_sysctl.types.CtlType:
        return freebsd_sysctl.types.identify_type(kind, fmt)

    def has_flag(self, flag: int) -> bool:
        """Return is the sysctl has a certain flag."""
        return (self.kind & flag == flag) is True
