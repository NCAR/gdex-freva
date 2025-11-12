import os
import socket
from typing import Tuple

import paramiko
import pexpect

USERNAME = "mbergemann"
HOST = "casper.hpc.ucar.edu"
PASSWORD = "x9i$D4et?K~Y^*+"  # your NCAR password

import getpass
import os
from typing import List, Optional, Tuple

import pexpect


def ssh_login_sequence(
    host: str,
    username: str,
    sequence: List[str],  # ["Password:", "secret", "ncar-two-factor:", "1", ...]
    command: str,
    timeout: int = 120,
) -> Tuple[int, str, str]:
    """
    Run `command` on remote host using explicit prompt/answer pairs.
    Returns (rc, stdout, stderr).
    """
    # Force password/keyboard-interactive only; disable hostkey checking & keys/certs/agent/GSSAPI
    ssh_opts = [
        "-tt",
        "-o",
        "StrictHostKeyChecking=no",
        "-o",
        "UserKnownHostsFile=/dev/null",
        "-o",
        "PreferredAuthentications=keyboard-interactive,password",
        "-o",
        "PubkeyAuthentication=no",
        "-o",
        "PasswordAuthentication=yes",
        "-o",
        "KbdInteractiveAuthentication=yes",
        "-o",
        "GSSAPIAuthentication=no",
        "-o",
        "BatchMode=no",
        "-o",
        "IdentitiesOnly=yes",
    ]

    # Prefix stdout/stderr on the *remote* so we can split them, and print an RC marker
    remote = (
        f"bash -lc '{{ {command} ; rc=$?; }} "
        f'> >(sed -u "s/^/__STDOUT__/" ) '
        f'2> >(sed -u "s/^/__STDERR__/" >&2 ); '
        f'printf "__RC__%d\\n" "$rc"\''
    )

    # cmd = f"ssh {' '.join(ssh_opts)} {username}@{host} {remote}"
    cmd = f"ssh {username}@{host} {command}"

    child = pexpect.spawn(cmd, encoding="utf-8", timeout=timeout)

    # Turn your flat list into prompt/answer pairs
    if len(sequence) % 2 != 0:
        raise ValueError(
            "sequence must have an even number of items: [prompt, answer, ...]"
        )
    pairs = list(zip(sequence[0::2], sequence[1::2]))

    # Minimal failure patterns we’ll watch for during auth
    fail_patterns = [
        pexpect.TIMEOUT,
        pexpect.EOF,
        r"(?i)permission denied",
        r"(?i)authentication failed",
        r"(?i)too many authentication failures",
    ]

    # Drive the login sequence
    for prompt, answer in pairs:
        i = child.expect([prompt] + fail_patterns)
        if i == 0:
            # matched your prompt — send the answer (can be empty string)
            child.sendline(answer)
        else:
            # hit a failure pattern
            why = [
                "TIMEOUT",
                "EOF",
                "Permission denied",
                "Auth failed",
                "Too many auths",
            ][i - 1]
            child.close(force=True)
            raise RuntimeError(f"Login failed: {why}")
    child.interact()
    # After auth, read until we see the RC marker from the remote command
    # We collect everything then split out stdout/stderr by our prefixes.
    buf = ""
    try:
        child.expect(r"__RC__\d+", timeout=timeout)
        buf += child.before or ""
        rc_marker = child.after or ""
    except pexpect.TIMEOUT:
        child.close(force=True)
        raise TimeoutError(
            "Timed out waiting for command to finish (no RC marker)."
        )

    # Parse exit code
    try:
        rc = int(rc_marker.split("__RC__")[-1].strip())
    except Exception:
        rc = 0  # fallback

    # Drain any remaining output (should be minimal)
    try:
        child.read_nonblocking(size=4096, timeout=1)
    except Exception:
        pass
    finally:
        try:
            child.close()
        except Exception:
            pass

    # Split stdout/stderr using our prefixes
    stdout_lines, stderr_lines = [], []
    for line in buf.splitlines():
        if line.startswith("__STDOUT__"):
            stdout_lines.append(line[len("__STDOUT__") :])
        elif line.startswith("__STDERR__"):
            stderr_lines.append(line[len("__STDERR__") :])
        # ignore the RC marker if present in buf

    stdout = "\n".join(stdout_lines)
    stderr = "\n".join(stderr_lines)
    return rc, stdout, stderr


if __name__ == "__main__":
    rc, out, err = ssh_login_sequence(
        host=HOST,
        username=USERNAME,
        sequence=["(?i)ncar-two-factor:", PASSWORD, "1", ""],
        command="hostname && whoami",
    )
    print("RC:", rc)
    print("STDOUT:", out)
    print("STDERR:", err)

    ssh_login_sequence(
        host="levante.dkrz.de",
        username="k204230",
        sequence=["Password", "Schw4r!zk0pff"],
        command="hostname && whoami",
    )

    # print("RC:", rc)
    # print("STDOUT:", out)
    # print("STDERR:", err)
