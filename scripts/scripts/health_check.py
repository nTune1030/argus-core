#!/usr/bin/env python3
import shutil
import psutil
import socket
import os
import sys

# --- CONFIGURATION ---
# (No email config needed! Orchestrator handles it)
HOME_DIR = os.path.expanduser("~")
SD_CARD_PATH = os.path.join(HOME_DIR, "nas_storage")

# --- THRESHOLDS ---
CPU_LIMIT = 80        
DISK_MIN_FREE = 20    
SD_MIN_FREE = 10      
MEM_MIN_MB = 100      

def check_cpu_usage():
    return psutil.cpu_percent(interval=1) > CPU_LIMIT

def check_disk_usage():
    du = shutil.disk_usage("/")
    return (du.free / du.total) * 100 < DISK_MIN_FREE

def check_sd_usage():
    try:
        du = shutil.disk_usage(SD_CARD_PATH)
        return (du.free / du.total) * 100 < SD_MIN_FREE
    except FileNotFoundError:
        return True 

def check_memory_usage():
    limit = MEM_MIN_MB * 1024 * 1024 
    return psutil.virtual_memory().available < limit

def check_localhost():
    try:
        return socket.gethostbyname('localhost') != "127.0.0.1"
    except:
        return True

def main():
    checks = [
        (check_cpu_usage, "CPU usage is over 80%"),
        (check_disk_usage, "OS Drive Space Low (< 20%)"),
        (check_sd_usage, "SD Card Storage Low/Missing"),
        (check_memory_usage, "Low Memory (< 100MB)"),
        (check_localhost, "Localhost resolution failed")
    ]

    issues_found = False

    for check_func, message in checks:
        if check_func():
            # The Orchestrator will capture this print and email it
            print(f"⚠️ CRITICAL: {message}")
            issues_found = True

    # If we found issues, exit with error code 1 so Orchestrator knows it failed
    if issues_found:
        sys.exit(1)

if __name__ == "__main__":
    main()