"""
Apex RiskEngine - Bulletproof High-Availability Host Daemon
Features:
- Runs FastAPI (Uvicorn) backend on port 8000
- Launches Cloudflare Edge Tunnel with --protocol http2 (prevents UDP/QUIC ISP dropouts)
- Automatically monitors & restarts services if they disconnect
- Writes current public URL to LIVE_HOSTED_URL.txt
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

def log(msg):
    timestamp = time.strftime("[%Y-%m-%d %H:%M:%S]")
    line = f"{timestamp} {msg}"
    print(line, flush=True)
    try:
        with open("host_daemon.log", "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except Exception:
        pass

def run_daemon():
    work_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(work_dir)
    
    log("=" * 65)
    log("APEX RISKENGINE - STARTING PERMANENT HOST DAEMON")
    log("=" * 65)

    cf_bin = find_cloudflared()
    log(f"Using Cloudflared binary: {cf_bin}")

    server_proc = None
    tunnel_proc = None
    url_pattern = re.compile(r"https://[a-zA-Z0-9-]+\.trycloudflare\.com")
    
    while True:
        try:
            # 1. Ensure Uvicorn Server is Running
            if server_proc is None or server_proc.poll() is not None:
                log("Starting FastAPI Backend (uvicorn app.main:app) on http://127.0.0.1:8000 ...")
                server_cmd = [sys.executable, "-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", "8000"]
                server_proc = subprocess.Popen(server_cmd, cwd=work_dir)
                time.sleep(2)

            # 2. Ensure Cloudflare Tunnel is Running with HTTP/2 (stable TCP)
            if tunnel_proc is None or tunnel_proc.poll() is not None:
                log("Launching Cloudflare Edge Tunnel with HTTP/2 protocol...")
                log_file = os.path.join(work_dir, "tunnel.log")
                if os.path.exists(log_file):
                    try: os.remove(log_file)
                    except Exception: pass

                # Using --protocol http2 is critical to avoid QUIC UDP timeouts on home networks
                tunnel_cmd = [
                    cf_bin, "tunnel",
                    "--url", "http://127.0.0.1:8000",
                    "--protocol", "http2",
                    "--logfile", log_file
                ]
                tunnel_proc = subprocess.Popen(tunnel_cmd, cwd=work_dir)

                # Wait for assigned public URL
                public_url = None
                for _ in range(25):
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
                    log("*" * 65)
                    log(f"LIVE URL READY: {public_url}")
                    log("*" * 65)
                    with open("LIVE_HOSTED_URL.txt", "w", encoding="utf-8") as f:
                        f.write(public_url + "\n")
                        f.write(f"Updated at: {time.ctime()}\n")
                else:
                    log("Warning: Could not detect tunnel URL within 25 seconds.")

            time.sleep(3)

        except KeyboardInterrupt:
            log("Stopping daemon...")
            if server_proc: server_proc.terminate()
            if tunnel_proc: tunnel_proc.terminate()
            break
        except Exception as e:
            log(f"Unexpected error in daemon loop: {e}")
            time.sleep(3)

if __name__ == "__main__":
    run_daemon()
