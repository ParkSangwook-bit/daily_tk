import customtkinter as ctk
import time

root = ctk.CTk()
root.geometry("400x200")

# indeterminate 모드로 프로그레스 바 생성
progress_bar = ctk.CTkProgressBar(master=root, mode="indeterminate", width=300)
progress_bar.pack(pady=20)

# 버튼 클릭 시 애니메이션 시작 함수
def start_progress():
    progress_bar.start()  # 프로그레스 바의 애니메이션 시작

# 버튼 클릭 시 애니메이션 정지 함수
def stop_progress():
    progress_bar.stop()  # 프로그레스 바의 애니메이션 멈춤

# 시작 및 정지 버튼 생성
start_button = ctk.CTkButton(master=root, text="Start Animation", command=start_progress)
stop_button = ctk.CTkButton(master=root, text="Stop Animation", command=stop_progress)
start_button.pack(pady=10)
stop_button.pack(pady=10)

root.mainloop()
