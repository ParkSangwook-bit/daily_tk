
import psutil
import subprocess

# PSUTIL 리스트 출력
def list_psutil_processes():
    print("=== psutil Processes ===")
    for proc in psutil.process_iter(attrs=['pid', 'name']):
        try:
            print(f"PID: {proc.info['pid']}, Name: {proc.info['name']}")
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    print("========================")

# TASKLIST 명령 출력
def list_tasklist_processes():
    print("=== tasklist Processes ===")
    result = subprocess.run("tasklist", shell=True, capture_output=True, text=True)
    print(result.stdout)
    print("========================")

