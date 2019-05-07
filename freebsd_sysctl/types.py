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
import ctypes
import typing
import struct


class CtlType:
    min_size = 0
    data: bytes
    ctype: typing.Optional[type] = None
    unpack_format: typing.Optional[str] = None

    def __init__(self, data: bytes, size: int) -> None:
        self.data = data
        self.size = size

    @property
    def amount(self):
        if self.min_size == 0:
            return 1
        return int(self.size / self.min_size)

    @property
    def value(self) -> typing.Any:
        if self.unpack_format is None:
            return self.data.value
        values = list(struct.unpack(
            f"<{self.unpack_format * self.amount}",
            self.data
        ))
        if len(values) == 1:
            return values[0]
        return values

    def __str__(self) -> str:
        if self.amount == 1:
            return self.__tostring(self.value)
        return " ".join([self.__tostring(x) for x in self.value])

    @staticmethod
    def __tostring(value: typing.Any) -> str:
        if isinstance(value, bytes) is True:
            return value.decode()
        return str(value)


class NODE(CtlType):
    ctype = ctypes.c_uint
    min_size = ctypes.sizeof(ctypes.c_uint)
    unpack_format = "I"


class INT(CtlType):
    ctype = ctypes.c_int
    min_size = ctypes.sizeof(ctypes.c_int)
    unpack_format = "i"


class STRING(CtlType):

    @property
    def value(self) -> str:
        return self.data.value.decode()


class S64(CtlType):
    ctype = ctypes.c_int64
    min_size = ctypes.sizeof(ctypes.c_int64)
    unpack_format = "q"


class STRUCT(CtlType):
    pass


class OPAQUE(CtlType):
    pass


class UINT(CtlType):
    ctype = ctypes.c_uint
    min_size = ctypes.sizeof(ctypes.c_uint)
    unpack_format = "I"


class LONG(CtlType):
    ctype = ctypes.c_long
    min_size = ctypes.sizeof(ctypes.c_long)
    unpack_format = "q"


class ULONG(CtlType):
    ctype = ctypes.c_ulong
    min_size = ctypes.sizeof(ctypes.c_ulong)
    unpack_format = "Q"


class U64(CtlType):
    ctype = ctypes.c_uint64
    min_size = ctypes.sizeof(ctypes.c_uint64)
    unpack_format = "Q"


class U8(CtlType):
    ctype = ctypes.c_uint8
    min_size = ctypes.sizeof(ctypes.c_uint8)
    unpack_format = "B"


class U16(CtlType):
    ctype = ctypes.c_uint16
    min_size = ctypes.sizeof(ctypes.c_uint16)
    unpack_format = "H"


class S8(CtlType):
    ctype = ctypes.c_int8
    min_size = ctypes.sizeof(ctypes.c_int8)
    unpack_format = "b"


class S16(CtlType):
    ctype = ctypes.c_int16
    min_size = ctypes.sizeof(ctypes.c_int16)
    unpack_format = "h"


class S32(CtlType):
    ctype = ctypes.c_int32
    min_size = ctypes.sizeof(ctypes.c_int32)
    unpack_format = "i"


class U32(CtlType):
    ctype = ctypes.c_uint32
    min_size = ctypes.sizeof(ctypes.c_uint32)
    unpack_format = "I"


def identify_type(kind: int, fmt: bytes) -> CtlType:
    ctl_type = kind & 0xF
    if ctl_type == 1:
        return NODE
    elif ctl_type == 2:
        return INT
    elif ctl_type == 3:
        return STRING
    elif ctl_type == 4:
        return S64
    elif ctl_type == 5:
        # return STRUCT if (fmt[0:1] == b"S") else OPAQUE
        return OPAQUE
    elif ctl_type == 6:
        return UINT
    elif ctl_type == 7:
        return LONG
    elif ctl_type == 8:
        return ULONG
    elif ctl_type == 9:
        return U64
    elif ctl_type == 10:
        return U8
    elif ctl_type == 11:
        return U16
    elif ctl_type == 12:
        return S8
    elif ctl_type == 13:
        return S16
    elif ctl_type == 14:
        return S32
    elif ctl_type == 15:
        return U32
    else:
        raise Exception(f"Invalid ctl_type: {ctl_type}")
