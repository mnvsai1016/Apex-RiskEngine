"""
Host Launcher for Apex RiskEngine:
Starts Uvicorn web server and connects a secure public Cloudflare Tunnel.
Outputs the public HTTPS live link accessible immediately worldwide.
"""
import subprocess
import time
import re
import os
import sys

def find_cloudflared():
    paths = [
        r"C:\Program Files (x86)\cloudflared\cloudflared.exe",
        r"C:\Program Files\cloudflared\cloudflared.exe",
        "cloudflared"
    ]
    for p in paths:
        if os.path.exists(p):
            return p
    return "cloudflared"

def start_hosting():
    print("=" * 70, flush=True)
    print("APEX RISKENGINE - LIVE CLOUD HOSTING", flush=True)
    print("=" * 70, flush=True)
    
    work_dir = os.path.dirname(os.path.abspath(__file__))
    log_file = os.path.join(work_dir, "tunnel.log")
    if os.path.exists(log_file):
        try:
            os.remove(log_file)
        except Exception:
            pass

    # 1. Start uvicorn server
    print("[1/2] Starting local FastAPI server on http://127.0.0.1:8000 ...", flush=True)
    server_cmd = [sys.executable, "-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", "8000"]
    server_proc = subprocess.Popen(server_cmd, cwd=work_dir)

    time.sleep(2)

    # 2. Start cloudflared tunnel writing to logfile
    cf_bin = find_cloudflared()
    print(f"[2/2] Launching Cloudflare edge tunnel using {cf_bin} ...", flush=True)
    tunnel_cmd = [cf_bin, "tunnel", "--url", "http://127.0.0.1:8000", "--logfile", log_file]
    tunnel_proc = subprocess.Popen(tunnel_cmd, cwd=work_dir)

    public_url = None
    url_pattern = re.compile(r"https://[a-zA-Z0-9-]+\.trycloudflare\.com")

    start_time = time.time()
    while time.time() - start_time < 30:
        time.sleep(1)
        if os.path.exists(log_file):
            try:
                with open(log_file, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()
                matches = url_pattern.findall(content)
                if matches:
                    public_url = matches[0]
                    break
            except Exception:
                pass

    if public_url:
        print("\n" + "*" * 70, flush=True)
        print("[SUCCESS] LIVE HOSTED SOLUTION ACTIVE & ACCESSIBLE WORLDWIDE!", flush=True)
        print(f"PUBLIC JUDGE LINK: {public_url}", flush=True)
        print("LOCALHOST LINK:    http://127.0.0.1:8000", flush=True)
        print("*" * 70 + "\n", flush=True)
        
        url_file = os.path.join(work_dir, "LIVE_HOSTED_URL.txt")
        with open(url_file, "w", encoding="utf-8") as f:
            f.write(public_url + "\n")
            f.write(f"Generated at: {time.ctime()}\n")
            
        print("Public link saved to LIVE_HOSTED_URL.txt", flush=True)
    else:
        print("[WARNING] Could not detect trycloudflare.com URL within 30 seconds.", flush=True)

    try:
        while True:
            # Check if processes are alive
            if server_proc.poll() is not None:
                print("Server exited unexpectedly!", flush=True)
                break
            if tunnel_proc.poll() is not None:
                print("Tunnel exited unexpectedly!", flush=True)
                break
            time.sleep(2)
    except KeyboardInterrupt:
        print("\nStopping hosting...", flush=True)
    finally:
        if server_proc: server_proc.terminate()
        if tunnel_proc: tunnel_proc.terminate()

if __name__ == "__main__":
    start_hosting()
