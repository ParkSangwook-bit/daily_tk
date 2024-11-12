import customtkinter as ctk
import time

root = ctk.CTk()
root.geometry("500x300")
root.title("Adaptive Progress Bar Example")

# 프레임 생성 (모든 UI 요소를 포함하는 프레임)
main_frame = ctk.CTkFrame(master=root)
main_frame.pack(pady=20, padx=20, fill="both", expand=True)

# determinate 모드의 프로그레스 바
determinate_bar = ctk.CTkProgressBar(master=main_frame, width=400, height=30)
determinate_bar.grid(row=0, column=0, pady=(0, 10))
determinate_bar.set(0.0)

# indeterminate 모드의 프로그레스 바 (기본적으로 숨김)
indeterminate_bar = ctk.CTkProgressBar(master=main_frame, width=400, height=30, mode="indeterminate")
indeterminate_bar.grid(row=0, column=0, pady=(0, 10))
indeterminate_bar.grid_remove()  # 초기에는 숨겨둠

# 상태 메시지 라벨
status_label = ctk.CTkLabel(master=main_frame, text="작업 대기 중...")
status_label.grid(row=1, column=0, pady=10)
 
# 작업 상태 관리 변수
is_task_running = False
current_task_index = 0
task_count = 10

# 작업 단계 진행 함수
def run_task():
    global is_task_running, current_task_index
    is_task_running = True

    # determinate 바의 진행률 업데이트
    progress = current_task_index / task_count
    determinate_bar.set(progress)

    # 3초 후에 indeterminate로 전환 (아직 작업이 끝나지 않은 경우)
    root.after(3000, set_to_indeterminate)

    # 작업 단계 시뮬레이션 (2초 동안 지연)
    status_label.configure(text=f"작업 {current_task_index + 1}/{task_count} 진행 중...")
    root.after(2000, complete_task)  # 2초 후에 다음 단계로 넘어감

# indeterminate 모드로 전환하는 함수
def set_to_indeterminate():
    if is_task_running and current_task_index < task_count:
        determinate_bar.grid_remove()  # determinate 프로그레스 바 숨김
        indeterminate_bar.grid()  # indeterminate 프로그레스 바 표시
        indeterminate_bar.start()
        status_label.configure(text=f"작업 {current_task_index + 1}/{task_count} 진행 중 (대기 중...)")

# 작업 완료 후 determinate 모드로 복귀
def complete_task():
    global is_task_running, current_task_index
    if not is_task_running:
        return

    # indeterminate 모드를 멈추고 determinate로 전환
    indeterminate_bar.stop()
    indeterminate_bar.grid_remove()  # indeterminate 프로그레스 바 숨김
    determinate_bar.grid()  # determinate 프로그레스 바 다시 표시

    # 진행 상태 업데이트
    current_task_index += 1
    progress = current_task_index / task_count
    determinate_bar.set(progress)

    if current_task_index < task_count:
        # 다음 작업으로 넘어가기
        root.after(100, run_task)
    else:
        # 모든 작업이 완료됨
        finish_task()

# 모든 작업 완료 후 처리
def finish_task():
    global is_task_running
    is_task_running = False
    determinate_bar.set(1.0)
    status_label.configure(text="모든 작업이 완료되었습니다.")

# 작업 시작 버튼
start_button = ctk.CTkButton(master=main_frame, text="Start Process", command=run_task)
start_button.grid(row=2, column=0, sticky='nsew', pady=10)

root.mainloop()
