import customtkinter as ctk

#! 이 코드는 쓸모없음.
#! 이 방식으로는 모든 프레임을 한번에 생성하여서 프레임에 할당된 작업이 실행하자마자 모든 작업이 시작됨.

# CustomTkinter 설정
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        # 윈도우 설정
        self.title("Step-by-Step Wizard Example")
        self.geometry("500x400")

        # 프레임들을 리스트로 저장하고, 현재 프레임 인덱스를 설정합니다.
        self.frames = [Frame1(self, self.next_frame), 
                       Frame2(self, self.next_frame),
                       Frame3(self, self.next_frame),
                       FinalFrame(self, self.restart)]
        
        self.current_frame_index = 0
        
        # 첫 번째 프레임을 표시합니다.
        self.show_current_frame()

    def show_current_frame(self):
        # 모든 프레임을 숨기고, 현재 프레임만 표시합니다.
        for frame in self.frames:
            frame.pack_forget()
        self.frames[self.current_frame_index].pack(fill="both", expand=True)

    def next_frame(self):
        # 다음 프레임으로 이동합니다.
        if self.current_frame_index < len(self.frames) - 1:
            self.current_frame_index += 1
            self.show_current_frame()

    def restart(self):
        # 첫 번째 프레임으로 돌아갑니다.
        self.current_frame_index = 0
        self.show_current_frame()

class Frame1(ctk.CTkFrame):
    def __init__(self, parent, next_frame_callback):
        super().__init__(parent)

        label = ctk.CTkLabel(self, text="Step 1: Welcome!", font=("Arial", 20))
        label.pack(pady=20)

        button = ctk.CTkButton(self, text="Next", command=next_frame_callback)
        button.pack(pady=10)

class Frame2(ctk.CTkFrame):
    def __init__(self, parent, next_frame_callback):
        super().__init__(parent)

        label = ctk.CTkLabel(self, text="Step 2: Information", font=("Arial", 20))
        label.pack(pady=20)

        button = ctk.CTkButton(self, text="Next", command=next_frame_callback)
        button.pack(pady=10)

class Frame3(ctk.CTkFrame):
    def __init__(self, parent, next_frame_callback):
        super().__init__(parent)

        label = ctk.CTkLabel(self, text="Step 3: Confirmation", font=("Arial", 20))
        label.pack(pady=20)

        button = ctk.CTkButton(self, text="Next", command=next_frame_callback)
        button.pack(pady=10)

class FinalFrame(ctk.CTkFrame):
    def __init__(self, parent, restart_callback):
        super().__init__(parent)

        label = ctk.CTkLabel(self, text="Final Step: Complete!", font=("Arial", 20))
        label.pack(pady=20)

        button = ctk.CTkButton(self, text="Restart", command=restart_callback)
        button.pack(pady=10)

if __name__ == "__main__":
    app = App()
    app.mainloop()
