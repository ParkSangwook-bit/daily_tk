import customtkinter as ctk

# 메인 윈도우 설정
root = ctk.CTk()
root.geometry("600x500")
root.title("File Transfer Status Log Example")

# 메인 프레임 생성
main_frame = ctk.CTkFrame(master=root)
main_frame.pack(pady=20, padx=20, fill="both", expand=True)

# 상태 표시용 텍스트 박스 생성 (읽기 전용 로그 창)
status_textbox = ctk.CTkTextbox(master=main_frame, width=500, height=300)
status_textbox.grid(row=0, column=0, pady=10, padx=10)
status_textbox.insert("0.0", "파일 전송 상태 창...\n")
status_textbox.configure(state="disabled", text_color="black")  # 사용자가 수정할 수 없도록 비활성화

# 상태 업데이트 함수
def update_status(text):
    # 텍스트 박스를 일시적으로 활성화하여 업데이트 후 다시 비활성화
    status_textbox.configure(state="normal")
    status_textbox.insert("end", text + "\n")
    status_textbox.configure(state="disabled")
    status_textbox.yview("end")  # 항상 최신 로그가 보이도록 스크롤

# 전송 테스트 시뮬레이션 함수
def simulate_transfer():
    # 첫 번째 파일 전송 중...
    update_status("1번 파일 전송중...")
    root.after(2000, lambda: update_status("1번 파일 성공"))  # 2초 후 첫 번째 파일 성공

    # 두 번째 파일 전송 중...
    root.after(3000, lambda: update_status("2번 파일 전송중..."))
    root.after(5000, lambda: update_status("2번 파일 실패"))  # 5초 후 두 번째 파일 실패

    # 세 번째 파일 전송 중...
    root.after(6000, lambda: update_status("3번 파일 전송중..."))
    root.after(8000, lambda: update_status("3번 파일 성공"))  # 8초 후 세 번째 파일 성공

    # 네 번째 파일 전송 중...
    root.after(9000, lambda: update_status("4번 파일 전송중..."))
    root.after(11000, lambda: update_status("4번 파일 성공"))  # 11초 후 네 번째 파일 성공

    # 다섯 번째 파일 전송 중...
    root.after(12000, lambda: update_status("5번 파일 전송중..."))
    root.after(14000, lambda: update_status("5번 파일 실패"))  # 14초 후 다섯 번째 파일 실패

    # 여섯 번째 파일 전송 중...
    root.after(15000, lambda: update_status("6번 파일 전송중..."))
    root.after(17000, lambda: update_status("6번 파일 성공"))  # 17초 후 여섯 번째 파일 성공

    # 일곱 번째 파일 전송 중...
    root.after(18000, lambda: update_status("7번 파일 전송중..."))
    root.after(20000, lambda: update_status("7번 파일 실패"))  # 20초 후 일곱 번째 파일 실패

    # 여덟 번째 파일 전송 중...
    root.after(21000, lambda: update_status("8번 파일 전송중..."))
    root.after(23000, lambda: update_status("8번 파일 성공"))  # 23초 후 여덟 번째 파일 성공

    # 아홉 번째 파일 전송 중...
    root.after(24000, lambda: update_status("9번 파일 전송중..."))
    root.after(26000, lambda: update_status("9번 파일 실패"))  # 26초 후 아홉 번째 파일 실패

    # 열 번째 파일 전송 중...
    root.after(27000, lambda: update_status("10번 파일 전송중..."))
    root.after(29000, lambda: update_status("10번 파일 성공"))  # 29초 후 열 번째 파일 성공

# 파일 전송 시작 버튼 생성
start_button = ctk.CTkButton(master=main_frame, text="파일 전송 시작", command=simulate_transfer)
start_button.grid(row=1, column=0, pady=10)

root.mainloop()
