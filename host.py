"""
Host Launcher for Apex RiskEngine:
Starts the Uvicorn web server and connects a secure public Cloudflare Tunnel.
Outputs the public HTTPS live link accessible immediately by judges.
"""
import subprocess
import time
import re
import os
import sys

if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

CLOUDFLARED_PATHS = [
    r"C:\Program Files (x86)\cloudflared\cloudflared.exe",
    r"C:\Program Files\cloudflared\cloudflared.exe",
    "cloudflared"
]

def find_cloudflared():
    for p in CLOUDFLARED_PATHS:
        if os.path.exists(p):
            return p
    return "cloudflared"

def start_hosting():
    print("=" * 70)
    print("APEX RISKENGINE - LIVE CLOUD HOSTING")
    print("=" * 70)
    
    # 1. Start uvicorn server
    print("[1/2] Starting local FastAPI server on http://127.0.0.1:8000 ...")
    server_cmd = [sys.executable, "-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", "8000"]
    server_proc = subprocess.Popen(server_cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding='utf-8', errors='ignore')

    time.sleep(2)

    # 2. Start cloudflared tunnel
    cf_bin = find_cloudflared()
    print(f"[2/2] Launching Cloudflare edge tunnel using {cf_bin} ...")
    tunnel_cmd = [cf_bin, "tunnel", "--url", "http://127.0.0.1:8000"]
    tunnel_proc = subprocess.Popen(tunnel_cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding='utf-8', errors='ignore')

    public_url = None
    url_pattern = re.compile(r"https://[a-zA-Z0-9-]+\.trycloudflare\.com")

    start_time = time.time()
    while time.time() - start_time < 30:
        line = tunnel_proc.stdout.readline()
        if not line:
            break
        match = url_pattern.search(line)
        if match:
            public_url = match.group(0)
            break

    if public_url:
        print("\n" + "*" * 70)
        print("[SUCCESS] LIVE HOSTED SOLUTION ACTIVE & ACCESSIBLE WORLDWIDE!")
        print(f"PUBLIC JUDGE LINK: {public_url}")
        print("LOCALHOST LINK:    http://127.0.0.1:8000")
        print("*" * 70 + "\n")
        
        with open("LIVE_HOSTED_URL.txt", "w", encoding="utf-8") as f:
            f.write(public_url + "\n")
            f.write(f"Generated at: {time.ctime()}\n")
            
        print("Public link saved to LIVE_HOSTED_URL.txt")
        return public_url, server_proc, tunnel_proc
    else:
        print("[WARNING] Could not detect trycloudflare.com URL within 30 seconds.")
        return None, server_proc, tunnel_proc

if __name__ == "__main__":
    url, s_proc, t_proc = start_hosting()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping hosting...")
        if s_proc: s_proc.terminate()
        if t_proc: t_proc.terminate()
