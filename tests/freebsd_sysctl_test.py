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
import os.path
import pytest
import subprocess
import sys

import freebsd_sysctl


@pytest.fixture
def sysctl_types():
    stdout = subprocess.check_output(["/sbin/sysctl", "-a", "-t"])
    lines = stdout.decode().strip().split("\n")
    
    return dict(filter(
        lambda x: not x[0].endswith("."),
        [x.split(": ", maxsplit=1) for x in lines]
    ))


def map_sysctl_type(ctl_type: freebsd_sysctl.types.CtlType) -> str:
    if ctl_type == freebsd_sysctl.types.NODE:
        return "node"
    elif ctl_type == freebsd_sysctl.types.INT:
        return "integer"
    elif ctl_type == freebsd_sysctl.types.STRING:
        return "string"
    elif ctl_type == freebsd_sysctl.types.S64:
        return "int64_t"
    elif ctl_type == freebsd_sysctl.types.OPAQUE:
        return "opaque"
    elif ctl_type == freebsd_sysctl.types.UINT:
        return "unsigned integer"
    elif ctl_type == freebsd_sysctl.types.LONG:
        return "long integer"
    elif ctl_type == freebsd_sysctl.types.ULONG:
        return "unsigned long"
    elif ctl_type == freebsd_sysctl.types.U64:
        return "uint64_t"
    elif ctl_type == freebsd_sysctl.types.U8:
        return "uint8_t"
    elif ctl_type == freebsd_sysctl.types.U16:
        return "uint16_t"
    elif ctl_type == freebsd_sysctl.types.S8:
        return "int8_t"
    elif ctl_type == freebsd_sysctl.types.S16:
        return "int16_t"
    elif ctl_type == freebsd_sysctl.types.S32:
        return "int32_t"
    elif ctl_type == freebsd_sysctl.types.U32:
        return "uint32_t"
    raise Exception(f"Unknown CtlType: {ctl_type}")


def test_sysctl_names(sysctl_types):
    for sysctl_name, sysctl_type in sysctl_types.items():
        current_sysctl = freebsd_sysctl.Sysctl(sysctl_name)
        resolved_sysctl = freebsd_sysctl.Sysctl(oid=current_sysctl.oid)
        assert sysctl_name == resolved_sysctl.name


def test_sysctl_types(sysctl_types):
    for sysctl_name, sysctl_type in sysctl_types.items():
        current_sysctl = freebsd_sysctl.Sysctl(sysctl_name)
        current_mapped_type = map_sysctl_type(current_sysctl.ctl_type)
        assert sysctl_type == current_mapped_type, sysctl_name


def test_sysctl_values(benchmark, sysctl_types):

    dynamic_sysctl_names = [
        "kern.ipc.pipekva",
        "kern.lastpid",
        "kern.openfiles",
        "kern.cp_time",
        "kern.cp_times",
        "kern.ipc.numopensockets",
        "kern.msgbuf",
        "vm.phys_free",
        "net.inet.tcp.hostcache.list",
        "net.inet.tcp.functions_available"
    ]

    def lookup_values(sysctl_types):
        for sysctl_name, sysctl_type in sysctl_types.items():
            yield sysctl_name, freebsd_sysctl.Sysctl(sysctl_name).raw_value

    raw_values = dict(benchmark(lookup_values, sysctl_types))

    for sysctl_name, sysctl_type in sysctl_types.items():
        raw_value = raw_values[sysctl_name]

        if any([
            isinstance(raw_value, freebsd_sysctl.types.OPAQUE),
            isinstance(raw_value, freebsd_sysctl.types.NODE),
            sysctl_name.endswith("counter"),
            sysctl_name.startswith("vm."),
            sysctl_name.startswith("hw."),
            sysctl_name.startswith("vfs."),
            sysctl_name.startswith("kstat."),
            sysctl_name.startswith("dev."),
            sysctl_name.startswith("kern.timecounter."),
            sysctl_name.startswith("kern.tty_"),
            sysctl_name.startswith("kern.epoch.stats."),
            sysctl_name.startswith("debug"),
            (sysctl_name in dynamic_sysctl_names)
        ]):
            continue

        stdout = subprocess.check_output([
            "/sbin/sysctl",
            "-n",
            sysctl_name
        ]).strip().decode()

        current_value = str(raw_value).strip()
        assert current_value == stdout, sysctl_name


def test_sysctl_descriptions(benchmark, sysctl_types):

    def lookup_descriptions(sysctl_types):
        for sysctl_name, sysctl_type in sysctl_types.items():
            yield sysctl_name, freebsd_sysctl.Sysctl(sysctl_name).description

    descriptions = dict(benchmark(lookup_descriptions, sysctl_types))

    for sysctl_name, sysctl_type in sysctl_types.items():
        if sysctl_type.upper() == "NODE":
            # skip NODE types because /sbin/sysctl returns multiple results
            continue
        stdout = subprocess.check_output([
            "/sbin/sysctl",
            "-d",
            "-n",
            sysctl_name
        ]).decode().strip("\n")

        assert stdout == descriptions[sysctl_name], sysctl_name


def test_security_jail_param_list(benchmark):
    test_node_name = "security.jail.param"
    stdout = subprocess.check_output([
        "/sbin/sysctl",
         "-o",
        test_node_name
    ]).strip().decode()
    child_names = [n.split(": ")[0] for n in stdout.split("\n")]
    assert len(child_names) > 0, "test pre-condition"

    def get_children(test_node_sysctl):
        return list(test_node_sysctl.children)

    test_node_children = benchmark(
        get_children,
        freebsd_sysctl.Sysctl(test_node_name)
    )

    assert len(test_node_children) == len(child_names), (
        "different number of children reported"
    )

    test_node_child_names = [c.name for c in test_node_children]
    assert all([a == b for a, b in zip(test_node_child_names, child_names)]), (
        "the order of children or their names differed"
    )
