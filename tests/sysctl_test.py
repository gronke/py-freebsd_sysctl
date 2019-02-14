import os.path
import pytest
import subprocess
import sys

project_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, project_path)

import sysctl


@pytest.fixture
def sysctl_types():
	stdout = subprocess.check_output(["/sbin/sysctl", "-a", "-t"])
	lines = stdout.decode().strip().split("\n")
	
	return dict(filter(
		lambda x: not x[0].endswith("."),
		[x.split(": ", maxsplit=1) for x in lines]
	))


def map_sysctl_type(ctl_type: sysctl.CtlType) -> str:
	if ctl_type == sysctl.NodeType:
		return "node"
	elif ctl_type == sysctl.IntType:
		return "integer"
	elif ctl_type == sysctl.StringType:
		return "string"
	elif ctl_type == sysctl.Int64Type:
		return "int64_t"
	elif ctl_type == sysctl.OpaqueType:
		return "opaque"
	elif ctl_type == sysctl.UIntType:
		return "unsigned integer"
	elif ctl_type == sysctl.LongType:
		return "long integer"
	elif ctl_type == sysctl.ULongType:
		return "unsigned long"
	elif ctl_type == sysctl.UInt64Type:
		return "uint64_t"
	elif ctl_type == sysctl.UInt8Type:
		return "uint8_t"
	elif ctl_type == sysctl.UInt16Type:
		return "uint16_t"
	elif ctl_type == sysctl.Int8Type:
		return "int8_t"
	elif ctl_type == sysctl.Int16Type:
		return "int16_t"
	elif ctl_type == sysctl.Int32Type:
		return "int32_t"
	elif ctl_type == sysctl.UInt32Type:
		return "uint32_t"
	raise Exception(f"Unknown CtlType: {ctl_type}")


def test_sysctl_names(sysctl_types):
	for sysctl_name, sysctl_type in sysctl_types.items():
		current_sysctl = sysctl.Sysctl(sysctl_name)
		assert sysctl_name == current_sysctl.name


def test_sysctl_types(sysctl_types):
	for sysctl_name, sysctl_type in sysctl_types.items():
		current_sysctl = sysctl.Sysctl(sysctl_name)
		assert sysctl_type == map_sysctl_type(current_sysctl.ctl_type)


def test_sysctl_values(sysctl_types):
	for sysctl_name, sysctl_type in sysctl_types.items():
		current_sysctl = sysctl.Sysctl(sysctl_name)

		stdout = subprocess.check_output([
			"/sbin/sysctl",
			"-n",
			sysctl_name
		]).strip().decode()

		if isinstance(current_sysctl.raw_value, sysctl.OpaqueType):
			continue
		elif isinstance(current_sysctl.raw_value, sysctl.NodeType):
			continue
		else:
			assert stdout == str(current_sysctl.value).strip()


def test_sysctl_descriptions(sysctl_types):
	for sysctl_name, sysctl_type in sysctl_types.items():
		current_sysctl = sysctl.Sysctl(sysctl_name)

		stdout = subprocess.check_output([
			"/sbin/sysctl",
			"-d",
			"-n",
			sysctl_name
		]).strip().decode()

		assert stdout == str(current_sysctl.description).strip()
