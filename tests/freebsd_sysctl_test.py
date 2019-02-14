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

project_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, project_path)

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
		assert sysctl_name == current_sysctl.name


def test_sysctl_types(sysctl_types):
	for sysctl_name, sysctl_type in sysctl_types.items():
		current_sysctl = freebsd_sysctl.Sysctl(sysctl_name)
		current_mapped_type = map_sysctl_type(current_sysctl.ctl_type)
		assert sysctl_type == current_mapped_type, sysctl_name


def test_sysctl_values(sysctl_types):
	for sysctl_name, sysctl_type in sysctl_types.items():
		current_sysctl = freebsd_sysctl.Sysctl(sysctl_name)

		stdout = subprocess.check_output([
			"/sbin/sysctl",
			"-n",
			sysctl_name
		]).strip().decode()

		if isinstance(current_sysctl.raw_value, freebsd_sysctl.OPAQUE):
			continue
		elif isinstance(current_sysctl.raw_value, freebsd_sysctl.NODE):
			continue
		else:
			current_value = str(current_sysctl.value).strip()
			assert current_value == stdout, sysctl_name


def test_sysctl_descriptions(sysctl_types):
	for sysctl_name, sysctl_type in sysctl_types.items():
		current_sysctl = freebsd_sysctl.Sysctl(sysctl_name)

		stdout = subprocess.check_output([
			"/sbin/sysctl",
			"-d",
			"-n",
			sysctl_name
		]).strip().decode()

		current_description = str(current_sysctl.description).strip()
		assert stdout == current_description, sysctl_name
