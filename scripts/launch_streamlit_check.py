"""Launch Streamlit twice, assert HTTP 200, capture logs/HTML."""

from __future__ import annotations

import argparse
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path


def wait_http(url: str, proc: subprocess.Popen, timeout: float = 45.0) -> tuple[int, bytes, str | None]:
    deadline = time.time() + timeout
    last_err = None
    while time.time() < deadline:
        if proc.poll() is not None:
            return -1, b"", f"process exited {proc.returncode} before HTTP ready"
        try:
            with urllib.request.urlopen(url, timeout=3) as resp:
                body = resp.read()
                return resp.status, body, None
        except Exception as exc:  # noqa: BLE001 — probe until timeout
            last_err = str(exc)
            time.sleep(0.5)
    return -1, b"", last_err or "timeout"


def run_once(n: int, port: int, app: Path, streamlit: Path, out: Path) -> dict:
    log_path = out / f"streamlit_{n}.log"
    html_path = out / f"page_{n}.html"
    log_f = log_path.open("w", encoding="utf-8", errors="replace")
    cmd = [
        str(streamlit),
        "run",
        str(app),
        "--server.headless=true",
        f"--server.port={port}",
        "--server.address=127.0.0.1",
        "--browser.gatherUsageStats=false",
        "--server.enableCORS=false",
        "--server.enableXsrfProtection=false",
    ]
    proc = subprocess.Popen(
        cmd,
        cwd=str(app.parent),
        stdout=log_f,
        stderr=subprocess.STDOUT,
        text=True,
    )
    url = f"http://127.0.0.1:{port}/"
    status, body, err = wait_http(url, proc)
    html_path.write_bytes(body)
    log_f.flush()
    log_text = log_path.read_text(encoding="utf-8", errors="replace")
    traceback = "Traceback" in log_text or "traceback" in log_text
    alive = proc.poll() is None
    proc.terminate()
    try:
        proc.wait(timeout=12)
    except subprocess.TimeoutExpired:
        proc.kill()
        proc.wait(timeout=5)
    log_f.close()
    return {
        "n": n,
        "port": port,
        "status": status,
        "bytes": len(body),
        "err": err,
        "traceback": traceback,
        "alive_before_stop": alive,
        "html_has_streamlit": b"streamlit" in body.lower() or b"Streamlit" in body,
        "log_has_tutor": ("相图" in log_text) or ("phase" in log_text.lower()) or ("You can now view" in log_text),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", required=True)
    parser.add_argument("--port1", type=int, default=8765)
    parser.add_argument("--port2", type=int, default=8766)
    args = parser.parse_args()
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    root = Path(__file__).resolve().parents[1]
    app = root / "app.py"
    streamlit = root / ".venv" / "Scripts" / "streamlit.exe"
    if not streamlit.exists():
        streamlit = Path(sys.executable).with_name("streamlit.exe")
    results = []
    try:
        results.append(run_once(1, args.port1, app, streamlit, out))
        time.sleep(1.0)
        results.append(run_once(2, args.port2, app, streamlit, out))
    except OSError as exc:
        (out / "streamlit_launch_error.txt").write_text(str(exc), encoding="utf-8")
        print("LAUNCH_ERROR", exc)
        return 2
    report = out / "streamlit_check.txt"
    lines = [str(r) for r in results]
    report.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))
    ok = all(r["status"] == 200 and r["alive_before_stop"] and not r["traceback"] for r in results)
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
