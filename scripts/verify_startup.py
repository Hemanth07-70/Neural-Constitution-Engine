"""Script to verify backend startup, /health, and /openapi.json endpoints."""
import subprocess
import sys
import time

import requests


def main():
    print("Starting uvicorn server in subprocess...")
    proc = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "backend.api.app:app", "--host", "127.0.0.1", "--port", "8005"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    try:
        time.sleep(3)
        # Check /health
        resp = requests.get("http://127.0.0.1:8005/health", timeout=5)
        if resp.status_code == 200:
            print(f"✅ /health returned 200: {resp.json()}")
        else:
            print(f"❌ /health returned {resp.status_code}")
            sys.exit(1)

        # Check /openapi.json
        resp_openapi = requests.get("http://127.0.0.1:8005/openapi.json", timeout=5)
        if resp_openapi.status_code == 200:
            print("✅ /openapi.json returned 200 (schema loaded)")
        else:
            print(f"❌ /openapi.json returned {resp_openapi.status_code}")
            sys.exit(1)

        print("🎉 Startup verification PASSED.")
    finally:
        proc.terminate()
        proc.wait()


if __name__ == "__main__":
    main()
