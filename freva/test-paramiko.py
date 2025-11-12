import paramiko
from paramiko_jump import MultiFactorAuthHandler, SSHJumpClient

USERNAME = "mbergemann"
HOST = "casper.hpc.ucar.edu"
PASSWORD = "x9i$D4et?K~Y^*+"  # your NCAR password
DUO = "push"  # or "1" / 6-digit code
import os
import socket
from typing import Tuple

handler = MultiFactorAuthHandler()
handler.add(PASSWORD)
# handler.add("1")
with SSHJumpClient(auth_handler=handler) as jumper:
    jumper.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    jumper.connect(
        hostname=HOST,
        username=USERNAME,
        look_for_keys=False,
        allow_agent=30,
    )
stdin, stdout, stderr = jumper.exec_command("uptime")
output = stdout.readlines()
print(output)
