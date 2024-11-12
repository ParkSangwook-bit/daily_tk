import customtkinter as ctk

# 메인 윈도우 설정
root = ctk.CTk()
root.geometry("600x500")
root.title("Prevent User Input for CTkTextbox Example")

# 메인 프레임 생성
main_frame = ctk.CTkFrame(master=root)
main_frame.pack(pady=20, padx=20, fill="both", expand=True)

# 텍스트 박스 생성 (로그용)
textbox = ctk.CTkTextbox(master=main_frame, width=500, height=200)
textbox.grid(row=0, column=0, pady=10, padx=10)
textbox.insert("0.0", "작업 상태 창...\n")
textbox.configure(text_color="white")

# 사용자 입력 차단을 위한 이벤트 가로채기
def disable_user_input(event):
    return "break"  # 사용자가 키 입력을 시도할 때 이벤트를 취소하여 입력을 막음

# 키보드와 마우스 입력을 모두 차단
textbox.bind("<Key>", disable_user_input)     # 키보드 입력 차단
textbox.bind("<Button-1>", disable_user_input) # 마우스 클릭 입력 차단

# 로그 추가 버튼을 사용하여 로그 추가 테스트
def add_log():
    textbox.insert("end", "새로운 작업 로그 추가\n")
    textbox.yview("end")  # 항상 최신 로그가 보이도록 스크롤

# 로그 추가 버튼 생성
add_button = ctk.CTkButton(master=main_frame, text="로그 추가", command=add_log)
add_button.grid(row=1, column=0, pady=10)

root.mainloop()
