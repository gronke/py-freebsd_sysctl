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
"""sysctl flags decoded from fmt."""
RD = 0x80000000                     # Allow reads of variable
WR = 0x40000000                     # Allow writes to the variable
RW = (RD | WR)
DORMANT = 0x20000000                # This sysctl is not active yet
ANYBODY = 0x10000000                # All users can set this var
SECURE = 0x08000000                 # Permit set only if securelevel<=0
PRISON = 0x04000000                 # Prisoned roots can fiddle
DYN = 0x02000000                    # Dynamic oid - can be freed
SKIP = 0x01000000                   # Skip this sysctl when listing
SECURE = 0x00F00000                 # Secure level
TUN = 0x00080000                    # Default value is loaded from getenv()
RDTUN = (RD | TUN)
RWTUN = (RW | TUN)
MPSAFE = 0x00040000                 # Handler is MP safe
VNET = 0x00020000                   # Prisons with vnet can fiddle
DYING = 0x00010000                  # Oid is being removed
CAPRD = 0x00008000                  # Can be read in capability mode
CAPWR = 0x00004000                  # Can be written in capability mode
STATS = 0x00002000                  # Statistics, not a tuneable
NOFETCH = 0x00001000                # Don't fetch tunable from getenv()
CAPRW = (CAPRD | CAPWR)