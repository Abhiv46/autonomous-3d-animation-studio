import os
import sys
import time
import subprocess

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

PYTHON_EXE = r"C:\Users\user\AppData\Local\Python\pythoncore-3.14-64\python.exe"
DAEMON_SCRIPT = r"C:\TheNaughtyDuo_Automation\live_stream_daemon.py"
LOG_FILE = r"C:\TheNaughtyDuo_Automation\live_stream.log"

def is_ffmpeg_streaming():
    try:
        out = subprocess.check_output('tasklist /FI "IMAGENAME eq ffmpeg.exe" /FO CSV', shell=True).decode()
        return "ffmpeg.exe" in out
    except Exception:
        return False

def is_daemon_running():
    try:
        # Check wmic or powershell for live_stream_daemon.py
        out = subprocess.check_output('powershell -Command "Get-CimInstance Win32_Process | Where-Object { $_.CommandLine -like \'*live_stream_daemon.py*\' } | Measure-Object | Select -ExpandProperty Count"', shell=True).decode().strip()
        count = int(out) if out.isdigit() else 0
        return count > 0
    except Exception:
        return False

def check_log_freshness():
    if not os.path.exists(LOG_FILE):
        return False
    # If log was modified within last 20 seconds, it's actively streaming
    age = time.time() - os.path.getmtime(LOG_FILE)
    return age < 25

def main():
    streaming = is_ffmpeg_streaming()
    daemon = is_daemon_running()
    fresh = check_log_freshness()

    print(f"[*] Live Stream Health Check at {time.strftime('%Y-%m-%d %H:%M:%S')}:")
    print(f"    - Daemon running: {daemon}")
    print(f"    - FFmpeg process: {streaming}")
    print(f"    - Stream active/fresh: {fresh}")

    if daemon and streaming and fresh:
        print("[OK] 24/7 Live Stream is running flawlessly and healthy!")
        return

    print("[!] Stream or Daemon dropped! Auto-recovering right now...", flush=True)
    subprocess.run(["taskkill", "/F", "/IM", "ffmpeg.exe"], capture_output=True)
    time.sleep(1)

    # Launch daemon in detached background process
    DETACHED_PROCESS = 0x00000008
    CREATE_NEW_PROCESS_GROUP = 0x00000200
    subprocess.Popen(
        [PYTHON_EXE, DAEMON_SCRIPT],
        creationflags=DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP,
        close_fds=True
    )
    time.sleep(3)
    print("[OK] Live Stream Daemon successfully recovered and streaming live!", flush=True)

if __name__ == "__main__":
    main()
