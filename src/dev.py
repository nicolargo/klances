#!/usr/bin/env python3
"""
Klances development launcher.

Starts both the Vite frontend watcher and the FastAPI server in parallel.
Access the application at http://localhost:8000/frontend/
"""

import os
import signal
import subprocess
import sys
import time

_SRC_DIR = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_SRC_DIR)
FRONTEND_DIR = os.path.join(_SRC_DIR, "frontend")
VENV_BIN = os.path.join(_ROOT, "venv", "bin")
UVICORN = os.path.join(VENV_BIN, "uvicorn")


def _terminate_all(procs: list) -> None:
    for p in procs:
        if p.poll() is None:
            p.terminate()
    for p in procs:
        try:
            p.wait(timeout=5)
        except subprocess.TimeoutExpired:
            p.kill()


def main() -> None:
    procs: list[subprocess.Popen] = []

    # Initial frontend build (so FastAPI has something to serve immediately)
    print("[klances] Building frontend...")
    result = subprocess.run(["npm", "run", "build"], cwd=FRONTEND_DIR)
    if result.returncode != 0:
        print(
            "[klances] Frontend build failed — check npm output above.", file=sys.stderr
        )
        sys.exit(1)

    # Vite watch mode: rebuilds src/frontend/dist/ on every file change
    vite = subprocess.Popen(
        ["npx", "vite", "build", "--watch"],
        cwd=FRONTEND_DIR,
    )
    procs.append(vite)

    # FastAPI + uvicorn with auto-reload on Python file changes
    uvicorn = subprocess.Popen(
        [
            UVICORN,
            "api.main:app",
            "--reload",
            "--host",
            "0.0.0.0",
            "--port",
            "8000",
            "--no-access-log",
        ],
        cwd=_ROOT,
    )
    procs.append(uvicorn)

    print("[klances] Running at http://localhost:8000/frontend/")
    print("[klances] API docs at http://localhost:8000/api/1/docs")
    print("[klances] Press Ctrl+C to stop.\n")

    def _cleanup(sig=None, frame=None) -> None:
        print("\n[klances] Shutting down...")
        _terminate_all(procs)
        sys.exit(0)

    signal.signal(signal.SIGINT, _cleanup)
    signal.signal(signal.SIGTERM, _cleanup)

    while True:
        for p in procs:
            if p.poll() is not None:
                print(
                    f"[klances] Subprocess exited (pid={p.pid}). Stopping."
                )
                _cleanup()
        time.sleep(0.5)


if __name__ == "__main__":
    main()
