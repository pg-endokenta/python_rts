import os
import shutil
import subprocess
import time
import signal
import pytest


def is_port_open(port, host='localhost'):
    import socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex((host, port)) == 0


def wait_port(port, timeout=10):
    start = time.time()
    while time.time() - start < timeout:
        if is_port_open(port):
            return True
        time.sleep(0.5)
    return False


@pytest.mark.skipif(shutil.which("npm") is None, reason="npm is required")
def test_frontend_serves_page(tmp_path):
    # install dependencies
    subprocess.run("npm install", shell=True, cwd="frontend", check=True)

    port = int(os.environ.get("BACKEND_PORT", "8000"))
    backend = subprocess.Popen(
        f"uvicorn backend.webarena:app --reload --port {port}",
        shell=True,
        start_new_session=True,
    )
    try:
        assert wait_port(port)
        env = os.environ.copy()
        env["VITE_API_URL"] = f"http://localhost:{port}"
        frontend = subprocess.Popen(
            "npm run dev -- --host",
            shell=True,
            cwd="frontend",
            env=env,
            start_new_session=True,
        )
        try:
            assert wait_port(5173)
            # fetch page
            out = subprocess.check_output(
                "curl -s http://localhost:5173", shell=True
            ).decode()
            assert "<div id=\"root\"></div>" in out
        finally:
            os.killpg(frontend.pid, signal.SIGTERM)
            frontend.wait(timeout=5)
    finally:
        os.killpg(backend.pid, signal.SIGTERM)
        backend.wait(timeout=5)
