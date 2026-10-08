"""
Dedicated tunnel runner with live log capture.
"""
import subprocess
import time
import re
import os

cf = r"C:\Program Files (x86)\cloudflared\cloudflared.exe"
log_path = "tunnel.log"

with open(log_path, "w", encoding="utf-8") as f:
    pass

proc = subprocess.Popen(
    [cf, "tunnel", "--url", "http://127.0.0.1:8000"],
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    text=True,
    encoding="utf-8",
    errors="ignore"
)

pattern = re.compile(r"https://[a-zA-Z0-9-]+\.trycloudflare\.com")
found_url = None

start = time.time()
with open(log_path, "a", encoding="utf-8") as log_file:
    while time.time() - start < 20:
        line = proc.stdout.readline()
        if not line:
            break
        log_file.write(line)
        log_file.flush()
        m = pattern.search(line)
        if m and not found_url:
            found_url = m.group(0)
            print("FOUND_LIVE_URL:", found_url)
            with open("LIVE_HOSTED_URL.txt", "w", encoding="utf-8") as url_file:
                url_file.write(found_url + "\n")
            break

# Keep running
try:
    while True:
        line = proc.stdout.readline()
        if line:
            with open(log_path, "a", encoding="utf-8") as log_file:
                log_file.write(line)
                log_file.flush()
        time.sleep(0.1)
except Exception:
    proc.terminate()
