"""Sandboxed execution of student Python code.

Primary path (the capstone claim): a fresh Docker container per run with
--network none, CPU/memory/pids limits, read-only rootfs, non-root user,
and a hard wall-clock timeout. Student code is NEVER executed on the host
in the default configuration.

Local fallback: only when CODEKITA_ALLOW_LOCAL_SANDBOX=1 is explicitly set.
It exists so unit tests can run on machines/CI without Docker (like this
build VM). It applies a timeout + rlimits and an isolated tmp cwd, but it
cannot disable networking — DO NOT use it for a public demo. The API
reports which sandbox actually ran in every response.
"""
from __future__ import annotations

import os
import resource
import subprocess
import sys
import tempfile
from dataclasses import dataclass

TIME_LIMIT_S = 2
MEMORY_LIMIT_MB = 128
MAX_OUTPUT_CHARS = 10_000
SANDBOX_IMAGE = os.environ.get("CODEKITA_SANDBOX_IMAGE", "codekita-sandbox:latest")
ALLOW_LOCAL = os.environ.get("CODEKITA_ALLOW_LOCAL_SANDBOX") == "1"


@dataclass
class RunResult:
    stdout: str
    timed_out: bool
    error: str | None  # internal/log only — never shown raw to students
    sandbox: str  # "docker" | "local-dev"


def docker_available() -> bool:
    try:
        r = subprocess.run(["docker", "info"], capture_output=True, timeout=5)
        return r.returncode == 0
    except Exception:
        return False


def _run_docker(code: str, stdin: str) -> RunResult:
    cmd = [
        "docker", "run", "--rm", "-i",
        "--network", "none",
        "--cpus", "0.5",
        "--memory", f"{MEMORY_LIMIT_MB}m",
        "--pids-limit", "64",
        "--read-only", "--tmpfs", "/tmp:size=16m",
        "--user", "nobody",
        SANDBOX_IMAGE, "python", "-I", "-c", code,
    ]
    try:
        p = subprocess.run(cmd, input=stdin, capture_output=True, text=True,
                           timeout=TIME_LIMIT_S + 2)
        return RunResult((p.stdout or "")[:MAX_OUTPUT_CHARS], False,
                         (p.stderr or None) if p.returncode else None, "docker")
    except subprocess.TimeoutExpired:
        subprocess.run(["docker", "kill", "codekita-run"], capture_output=True)
        return RunResult("", True, "timeout (docker)", "docker")


def _limits():
    resource.setrlimit(resource.RLIMIT_CPU, (TIME_LIMIT_S, TIME_LIMIT_S + 1))
    resource.setrlimit(resource.RLIMIT_AS,
                       (MEMORY_LIMIT_MB * 4 * 1024 * 1024,) * 2)
    resource.setrlimit(resource.RLIMIT_FSIZE, (1_000_000, 1_000_000))


def _run_local(code: str, stdin: str) -> RunResult:
    with tempfile.TemporaryDirectory() as td:
        try:
            p = subprocess.run(
                [sys.executable, "-I", "-c", code], input=stdin,
                capture_output=True, text=True, timeout=TIME_LIMIT_S,
                cwd=td, preexec_fn=_limits,
                env={"PATH": "/usr/bin:/bin", "HOME": td})
            return RunResult((p.stdout or "")[:MAX_OUTPUT_CHARS], False,
                             (p.stderr or None) if p.returncode else None,
                             "local-dev")
        except subprocess.TimeoutExpired:
            return RunResult("", True, "timeout (local-dev)", "local-dev")


def run_code(code: str, stdin: str = "") -> RunResult:
    if docker_available():
        return _run_docker(code, stdin)
    if ALLOW_LOCAL:
        return _run_local(code, stdin)
    return RunResult("", False,
                     "Docker unavailable and local sandbox not enabled. "
                     "Install Docker or set CODEKITA_ALLOW_LOCAL_SANDBOX=1 for dev tests only.",
                     "none")
