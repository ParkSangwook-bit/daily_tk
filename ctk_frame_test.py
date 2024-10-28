import customtkinter as ctk

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        # 메인 윈도우 설정
        self.title("CustomTkinter Example")
        self.geometry("400x400")

        # 프레임 생성 및 배치
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.pack(padx=20, pady=20, fill="both", expand=True)

        # 첫 번째 라벨 생성 및 배치
        self.label1 = ctk.CTkLabel(self.main_frame, text="This is Label 1")
        self.label1.grid(row=0, column=0, pady=10, padx=10, sticky="n")

        # 두 번째 라벨 생성 및 배치
        self.label2 = ctk.CTkLabel(self.main_frame, text="This is Label 2")
        self.label2.grid(row=1, column=0, pady=10, padx=10, sticky="n")

        # 첫 번째 버튼 생성 및 배치
        self.button1 = ctk.CTkButton(self.main_frame, text="Button 1")
        self.button1.grid(row=2, column=0, pady=10, padx=10, sticky="n")

        # 두 번째 버튼 생성 및 배치
        self.button2 = ctk.CTkButton(self.main_frame, text="Button 2")
        self.button2.grid(row=3, column=0, pady=10, padx=10, sticky="n")

# 애플리케이션 실행
if __name__ == "__main__":
    app = App()
    app.mainloop()
