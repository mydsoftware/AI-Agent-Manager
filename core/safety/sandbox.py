"""Isolated execution of Python/shell (and optional Node) with a structured result."""

from __future__ import annotations

import logging
import os
import shutil
import subprocess
import tempfile
import time
from dataclasses import dataclass
from pathlib import Path

logger = logging.getLogger(__name__)

DANGEROUS_PATTERNS = (
    "rm -rf /",
    "mkfs",
    ":(){",
    "dd if=",
    "shutdown",
    "reboot",
    "fork bomb",
    "curl | sh",
    "wget | sh",
    "chmod 777 /",
)


@dataclass
class ExecutionResult:
    success: bool
    stdout: str = ""
    stderr: str = ""
    exit_code: int = 0
    execution_time: float = 0.0
    timed_out: bool = False
    error: str | None = None
    blocked: bool = False
    backend: str = "subprocess"


class Sandbox:
    """Prefer Docker when explicitly enabled; otherwise restricted subprocess."""

    def __init__(
        self,
        backend: str = "subprocess",
        timeout_seconds: float = 30.0,
        network: bool = False,
        allow_docker: bool = False,
        workdir: str | None = None,
    ) -> None:
        self.backend = backend if backend in {"subprocess", "docker"} else "subprocess"
        self.timeout_seconds = timeout_seconds
        self.network = network
        self.allow_docker = allow_docker
        self.workdir = workdir

    def _blocked(self, command: str) -> str | None:
        lowered = command.lower()
        for pat in DANGEROUS_PATTERNS:
            if pat.lower() in lowered:
                return pat
        return None

    def run_python(self, code: str, extra_files: dict[str, str] | None = None) -> ExecutionResult:
        return self._run_in_workspace(["python3", "main.py"], {"main.py": code, **(extra_files or {})})

    def run_shell(self, command: str, extra_files: dict[str, str] | None = None) -> ExecutionResult:
        blocked = self._blocked(command)
        if blocked:
            logger.warning("blocked dangerous command pattern=%s", blocked)
            return ExecutionResult(
                success=False,
                stderr=f"blocked dangerous command: {blocked}",
                exit_code=126,
                error="blocked",
                blocked=True,
            )
        return self._run_in_workspace(["bash", "-lc", command], extra_files or {})

    def run_node(self, code: str) -> ExecutionResult:
        return self._run_in_workspace(["node", "main.js"], {"main.js": code})

    def _run_in_workspace(self, argv: list[str], files: dict[str, str]) -> ExecutionResult:
        tmp = tempfile.mkdtemp(prefix="aam-sandbox-")
        try:
            for name, content in files.items():
                dest = Path(tmp) / name
                dest.parent.mkdir(parents=True, exist_ok=True)
                dest.write_text(content, encoding="utf-8")
            if self.backend == "docker" and self.allow_docker and shutil.which("docker"):
                return self._docker(argv, tmp)
            return self._subprocess(argv, tmp)
        finally:
            shutil.rmtree(tmp, ignore_errors=True)

    def _subprocess(self, argv: list[str], cwd: str) -> ExecutionResult:
        env = os.environ.copy()
        env["PYTHONDONTWRITEBYTECODE"] = "1"
        start = time.time()
        try:
            proc = subprocess.run(
                argv,
                cwd=cwd,
                capture_output=True,
                text=True,
                timeout=self.timeout_seconds,
                env=env,
            )
            elapsed = time.time() - start
            return ExecutionResult(
                success=proc.returncode == 0,
                stdout=proc.stdout[-20_000:],
                stderr=proc.stderr[-20_000:],
                exit_code=proc.returncode,
                execution_time=elapsed,
                backend="subprocess",
            )
        except subprocess.TimeoutExpired as exc:
            return ExecutionResult(
                success=False,
                stdout=(exc.stdout or "")[-20_000:] if isinstance(exc.stdout, str) else "",
                stderr=(exc.stderr or "")[-20_000:] if isinstance(exc.stderr, str) else "",
                exit_code=124,
                execution_time=time.time() - start,
                timed_out=True,
                error="timeout",
                backend="subprocess",
            )
        except Exception as exc:
            return ExecutionResult(
                success=False,
                exit_code=1,
                execution_time=time.time() - start,
                error=str(exc),
                backend="subprocess",
            )

    def _docker(self, argv: list[str], cwd: str) -> ExecutionResult:
        net = ["--network", "none"] if not self.network else []
        docker_argv = [
            "docker", "run", "--rm", "--pids-limit", "64", "--memory", "256m", "--cpus", "1",
            *net, "-v", f"{cwd}:/work", "-w", "/work", "python:3.12-slim", *argv,
        ]
        start = time.time()
        try:
            proc = subprocess.run(docker_argv, capture_output=True, text=True, timeout=self.timeout_seconds + 15)
            return ExecutionResult(
                success=proc.returncode == 0,
                stdout=proc.stdout[-20_000:],
                stderr=proc.stderr[-20_000:],
                exit_code=proc.returncode,
                execution_time=time.time() - start,
                backend="docker",
            )
        except subprocess.TimeoutExpired:
            return ExecutionResult(success=False, exit_code=124, timed_out=True, error="timeout", execution_time=time.time() - start, backend="docker")
        except Exception as exc:
            logger.info("docker failed, falling back: %s", exc)
            return self._subprocess(argv, cwd)
