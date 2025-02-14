import customtkinter as ctk

#! 동적 프레임 생성 방식
#! 아마 이걸 메인 코드에 적용할 계획
#? 참고: https://stackoverflow.com/questions/7546050/switch-between-two-frames-in-tkinter
#? 이 코드는 callback 함수를 사용하여 프레임을 전환하는 방법을 보여줌.

# CustomTkinter 설정
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("green")

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        # 윈도우 설정
        self.title("Dynamic Frame Example")
        self.geometry("500x400")

        # 현재 프레임 인덱스
        self.current_frame_index = 0
        self.current_frame = None  # 현재 프레임을 저장할 변수

        # 첫 번째 프레임을 표시합니다.
        self.show_current_frame()

    def show_current_frame(self):
    # 기존 프레임이 있으면 숨기고 제거
        if self.current_frame is not None:
            self.current_frame.pack_forget()
            self.current_frame.destroy()

        # 현재 프레임 인덱스에 따라 새로운 프레임을 생성합니다.
        if self.current_frame_index == 0:
            self.current_frame = Frame1(self, self.next_frame)
        elif self.current_frame_index == 1:
            self.current_frame = Frame2(self, self.next_frame)
        elif self.current_frame_index == 2:
            self.current_frame = Frame3(self, self.next_frame)
        elif self.current_frame_index == 3:
            self.current_frame = ResultFrame(self, self.restart)

        # 새로 생성한 프레임을 표시합니다.
        if self.current_frame is not None:
            self.current_frame.pack(padx=50, pady=50, fill="both", expand=True)


    def next_frame(self):
        # 다음 프레임으로 이동
        if self.current_frame_index < 3:  # 프레임 개수에 맞춰 수정
            self.current_frame_index += 1
            self.show_current_frame()

    def restart(self):
        # 첫 번째 프레임으로 돌아가기
        self.current_frame_index = 0
        self.show_current_frame()

class Frame1(ctk.CTkFrame):
    def __init__(self, parent, next_frame_callback):
        super().__init__(parent)
        
        label = ctk.CTkLabel(self, text="Step 1: Load Data", font=("Arial", 20))
        label.pack(pady=20)

        button = ctk.CTkButton(self, text="Next", command=next_frame_callback)
        button.pack(pady=10)
        
        # 해당 단계의 기능: 데이터 로드
        self.load_data()
    
    def load_data(self):
        # 데이터 로드 작업
        print("Data loaded.")

class Frame2(ctk.CTkFrame):
    def __init__(self, parent, next_frame_callback):
        super().__init__(parent)

        label = ctk.CTkLabel(self, text="Step 2: Process Data", font=("Arial", 20))
        label.pack(pady=20)

        button = ctk.CTkButton(self, text="Next", command=next_frame_callback)
        button.pack(pady=10)

        # 해당 단계의 기능: 데이터 처리
        self.process_data()
    
    def process_data(self):
        # 데이터 처리 작업
        print("Data processed.")

class Frame3(ctk.CTkFrame):
    def __init__(self, parent, next_frame_callback):
        super().__init__(parent)

        label = ctk.CTkLabel(self, text="Step 3: Analyze Data", font=("Arial", 20))
        label.pack(pady=20)

        button = ctk.CTkButton(self, text="Next", command=next_frame_callback)
        button.pack(pady=10)

        # 해당 단계의 기능: 데이터 분석
        self.analyze_data()
    
    def analyze_data(self):
        # 데이터 분석 작업
        print("Data analyzed.")

class ResultFrame(ctk.CTkFrame):
    def __init__(self, parent, restart_callback):
        super().__init__(parent)

        label = ctk.CTkLabel(self, text="Final Step: Show Results", font=("Arial", 20))
        label.pack(pady=20)

        button = ctk.CTkButton(self, text="Restart", command=restart_callback)
        button.pack(pady=10)

        # 해당 단계의 기능: 결과 표시
        self.show_results()

    def show_results(self):
        # 결과 표시 작업
        print("Results are displayed.")

if __name__ == "__main__":
    app = App()
    app.mainloop()
