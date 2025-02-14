import tkinter as tk
import time
import threading

root = tk.Tk()
root.geometry("200x100")
progress = tk.Label(root, text="0%")
progress.pack()

def long_running_task():
    for i in range(1, 101):
        time.sleep(0.1)  # 긴 작업을 시뮬레이션
        progress.config(text=f"{i}%")
        root.update_idletasks()  # 진행률 표시줄 업데이트

def start_long_running_task():
    # 긴 작업을 새로운 스레드에서 실행
    threading.Thread(target=long_running_task, daemon=True).start()

tk.Button(root, text="Start", command=start_long_running_task).pack()
root.mainloop()
