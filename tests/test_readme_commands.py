import subprocess
import sys
import time
from pathlib import Path
import shutil


README = Path(__file__).resolve().parents[1] / "README.md"


def extract_commands():
    commands = []
    in_block = False
    current = ""
    for line in README.read_text().splitlines():
        if line.startswith("```bash"):
            in_block = True
            continue
        if in_block:
            if line.startswith("```"):
                if current:
                    commands.append(current.strip())
                    current = ""
                in_block = False
                continue
            line = line.rstrip()
            if line.endswith("\\"):
                current += line[:-1] + " "
            else:
                current += line
                commands.append(current.strip())
                current = ""
    return commands


def run(cmd, cwd=None, timeout=30):
    proc = subprocess.Popen(cmd, shell=True, cwd=cwd)
    try:
        proc.communicate(timeout=timeout)
    except subprocess.TimeoutExpired:
        proc.terminate()
        try:
            proc.communicate(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.communicate()
    return proc.returncode == 0


def test_readme_commands():
    commands = extract_commands()
    for cmd in commands:
        if "path/to/bots" in cmd:
            cmd = cmd.replace("path/to/bots", "bots")

        if cmd.startswith("docker ") or cmd.startswith("docker-compose"):
            if shutil.which("docker") is None:
                # Skip docker commands when docker is unavailable
                continue
            assert run(cmd, timeout=120)
            continue

        if cmd.startswith("curl"):
            server = subprocess.Popen(
                "uvicorn webarena:app --reload", shell=True
            )
            time.sleep(2)
            try:
                assert run(cmd, timeout=5)
            finally:
                server.terminate()
                server.wait(timeout=5)
            continue

        if cmd.startswith("uvicorn webarena:app --reload"):
            proc = subprocess.Popen(cmd, shell=True)
            time.sleep(2)
            proc.terminate()
            proc.wait(timeout=5)
            continue

        if cmd.startswith("npm install"):
            assert run(cmd, cwd="frontend", timeout=120)
            continue

        if cmd.startswith("npm run dev"):
            proc = subprocess.Popen(cmd, shell=True, cwd="frontend")
            time.sleep(2)
            proc.terminate()
            proc.wait(timeout=5)
            continue

        assert run(cmd)

