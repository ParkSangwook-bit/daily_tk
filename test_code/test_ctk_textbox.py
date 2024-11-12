import customtkinter as ctk

# 메인 윈도우 설정
root = ctk.CTk()
root.geometry("600x500")
root.title("Progress Bar with Task Status Example")

# 메인 프레임 생성 (모든 UI 요소를 포함)
main_frame = ctk.CTkFrame(master=root)
main_frame.pack(pady=20, padx=20, fill="both", expand=True)

# determinate 모드의 프로그레스 바
determinate_bar = ctk.CTkProgressBar(master=main_frame, width=500, height=30)
determinate_bar.grid(row=0, column=0, pady=(0, 10))
determinate_bar.set(0.0)

# indeterminate 모드의 프로그레스 바 (기본적으로 숨김)
indeterminate_bar = ctk.CTkProgressBar(master=main_frame, width=500, height=30, mode="indeterminate")
indeterminate_bar.grid(row=0, column=0, pady=(0, 10))
indeterminate_bar.grid_remove()  # 기본적으로 숨김

# 상태 메시지 텍스트 박스 생성 (작업 상태 로그용)
textbox = ctk.CTkTextbox(master=main_frame, width=500, height=200)
textbox.grid(row=1, column=0, pady=10, padx=10)
textbox.insert("0.0", "작업 상태 창...\n")
textbox.configure(state="disabled", text_color="white")  # 사용자 입력을 막기 위해 비활성화

# 작업 상태 관리 변수
is_task_running = False
current_task_index = 0
task_count = 10
current_dots = 0  # 진행 중일 때 점(dot)의 개수를 관리하기 위한 변수

# 작업 단계 진행 함수
def run_task():
    global is_task_running, current_task_index, current_dots
    is_task_running = True
    current_dots = 0  # 점 개수 초기화

    # 텍스트 박스를 일시적으로 활성화하여 업데이트 후 다시 비활성화
    textbox.configure(state="normal")
    task_number = current_task_index + 1
    textbox.insert("end", f"{task_number}번째 작업 시작\n")
    textbox.configure(state="disabled")
    textbox.yview("end")

    progress = current_task_index / task_count
    determinate_bar.set(progress)

    # 3초 후 indeterminate 모드로 전환 (아직 작업이 끝나지 않은 경우)
    root.after(3000, set_to_indeterminate)

    # 작업 중 상태 표시 (1초마다 점을 추가)
    update_progress_text(task_number)

# 점을 추가하며 진행 상태를 표시하는 함수
def update_progress_text(task_number):
    global current_dots
    if not is_task_running or current_task_index >= task_count:
        return

    # 텍스트 박스를 일시적으로 활성화하여 업데이트 후 다시 비활성화
    textbox.configure(state="normal")
    dots = '.' * current_dots
    textbox.insert("end", f"{task_number}번째 작업 진행중 {dots}\n")
    textbox.configure(state="disabled")
    textbox.yview("end")  # 항상 최신 로그가 보이도록 스크롤

    # 점이 최대 3개가 될 때까지 반복적으로 호출 (1초마다)
    current_dots = (current_dots + 1) % 4
    root.after(1000, update_progress_text, task_number)

# indeterminate 모드로 전환하는 함수
def set_to_indeterminate():
    if is_task_running and current_task_index < task_count:
        determinate_bar.grid_remove()  # determinate 프로그레스 바 숨김
        indeterminate_bar.grid()  # indeterminate 프로그레스 바 표시
        indeterminate_bar.start()

# 작업 완료 후 determinate 모드로 복귀
def complete_task():
    global is_task_running, current_task_index
    if not is_task_running:
        return

    # indeterminate 모드에서 determinate로 돌아옴
    indeterminate_bar.stop()
    indeterminate_bar.grid_remove()
    determinate_bar.grid()

    # 텍스트 박스를 일시적으로 활성화하여 작업 완료 상태 표시 후 다시 비활성화
    textbox.configure(state="normal")
    task_number = current_task_index + 1
    textbox.insert("end", f"{task_number}번째 작업 완료\n")
    textbox.configure(state="disabled")
    textbox.yview("end")  # 항상 최신 로그가 보이도록 스크롤

    # 다음 작업 진행을 위한 상태 업데이트
    current_task_index += 1
    progress = current_task_index / task_count
    determinate_bar.set(progress)

    # 모든 작업 완료 또는 다음 작업으로 넘어가기
    if current_task_index < task_count:
        root.after(100, run_task)
    else:
        finish_task()

# 모든 작업 완료 후 처리
def finish_task():
    global is_task_running
    is_task_running = False
    determinate_bar.set(1.0)
    
    # 텍스트 박스를 일시적으로 활성화하여 모든 작업 완료 표시 후 다시 비활성화
    textbox.configure(state="normal")
    textbox.insert("end", "모든 작업이 완료되었습니다.\n")
    textbox.configure(state="disabled")
    textbox.yview("end")

# 작업 시작 버튼
start_button = ctk.CTkButton(master=main_frame, text="Start Process", command=run_task)
start_button.grid(row=2, column=0, pady=10)

root.mainloop()
