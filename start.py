import os
import re
import subprocess
import sys
import threading
import time

PYTHON_EXEC = sys.executable
UVICORN_EXEC = [PYTHON_EXEC, "-m", "uvicorn"]
BACKEND_PORT = 8000
FRONTEND_PORT = 8090
TARGET_PORTS = [BACKEND_PORT, FRONTEND_PORT, 8080]


def get_listening_pids(port: int) -> list[int]:
    try:
        output = subprocess.check_output(
            ["netstat", "-ano"],
            text=True,
            encoding="utf-8",
            errors="ignore",
        )
    except Exception:
        return []

    pids: set[int] = set()
    pattern = re.compile(rf"^\s*TCP\s+\S+:{port}\s+\S+\s+LISTENING\s+(\d+)\s*$", re.IGNORECASE)
    for line in output.splitlines():
        match = pattern.match(line)
        if match:
            try:
                pid = int(match.group(1))
                if pid != os.getpid():
                    pids.add(pid)
            except ValueError:
                pass
    return sorted(pids)


def kill_pid(pid: int) -> None:
    try:
        subprocess.run(
            ["taskkill", "/F", "/PID", str(pid)],
            check=False,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    except Exception:
        pass


def cleanup_ports() -> None:
    print("[INFO] Verification des ports 8000/8080...")
    for port in TARGET_PORTS:
        pids = get_listening_pids(port)
        if not pids:
            continue
        print(f"[INFO] Port {port} occupe par PID(s): {pids}. Nettoyage...")
        for pid in pids:
            kill_pid(pid)
        time.sleep(0.3)


def run_backend() -> None:
    base_dir = os.path.dirname(os.path.abspath(__file__))
    backend_dir = os.path.join(base_dir, "backend")
    try:
        subprocess.run(
            [*UVICORN_EXEC, "main:app", "--reload", "--host", "127.0.0.1", "--port", str(BACKEND_PORT)],
            cwd=backend_dir,
            check=True,
        )
    except Exception as exc:
        print(f"[ERREUR] Backend: {exc}")


def run_frontend() -> None:
    base_dir = os.path.dirname(os.path.abspath(__file__))
    frontend_dir = os.path.join(base_dir, "FRONTend")
    try:
        subprocess.run(
            [
                PYTHON_EXEC,
                "-m",
                "http.server",
                str(FRONTEND_PORT),
                "--bind",
                "127.0.0.1",
                "--directory",
                frontend_dir,
            ],
            check=True,
        )
    except Exception as exc:
        print(f"[ERREUR] Frontend: {exc}")


if __name__ == "__main__":
    print("[INFO] Demarrage de GameStore...")
    cleanup_ports()

    backend = threading.Thread(target=run_backend, daemon=True)
    frontend = threading.Thread(target=run_frontend, daemon=True)
    backend.start()
    frontend.start()

    time.sleep(2)
    cache_bust = int(time.time())
    print(f"[INFO] Frontend: http://localhost:{FRONTEND_PORT}/index.html?v={cache_bust}")
    print(f"[INFO] Backend : http://127.0.0.1:{BACKEND_PORT}/docs")

    backend.join()
    frontend.join()
