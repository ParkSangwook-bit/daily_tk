from settings import *
from style import *

# ctypes 라이브러리를 사용하여 화면 스케일링을 위한 DPI 정보를 가져옴
def CenterWindowToDisplay(Screen: ctk.CTk, width: int, height: int, scale_factor: float = 1.0):
    """Centers the window to the main display/monitor considering the scale factor"""
    screen_width = Screen.winfo_screenwidth()
    screen_height = Screen.winfo_screenheight()

    # 창을 화면 가운데에 배치하기 위한 x, y 위치 계산 (스케일 요소 고려)
    x = int(((screen_width / 2) - (width / 2)) * scale_factor)
    y = int(((screen_height / 2) - (height / 1.5)) * scale_factor)

    return f"{width}x{height}+{x}+{y}"

# 메인 클래스
class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title('TEST')
        self.resizable(False, False)

        # 창 중앙 배치 설정 (디스플레이 스케일링 고려)
        self.geometry(CenterWindowToDisplay(self, 1000, 600, self._get_window_scaling()))

        # # 단계별 프레임 생성
        # self.frames = [
        #     self.create_frame1(),
        #     self.create_frame2(),
        #     self.create_frame3(),
        #     self.create_frame4(),
        #     self.create_frame5()
        # ]

        # Daily Detection Show
        #! pack 부분을 update_step() 메서드로 대체
        self.daily_frame = Daily_Detection_Show(self)
        self.daily_frame.pack(padx=50, pady=50, fill='both', expand=True)

        self.mainloop()  # 메인 루프 실행

class Daily_Detection_Show(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(master=parent)
        # self['relief'] = 'groove'
        self.file_list_len = 0  # 파일 리스트 길이
        self.grid(column=0, row=0, sticky='nsew', padx=50, pady=50, )

        # layout
        # 4x3 그리드
        self.rowconfigure(0, weight=1, uniform='a')
        self.rowconfigure(1, weight=2, uniform='a')
        self.rowconfigure(2, weight=8, uniform='a')
        self.rowconfigure(3, weight=2, uniform='a')
        self.columnconfigure(0, weight=1, uniform='a')
        self.columnconfigure(1, weight=1, uniform='a')
        self.columnconfigure(2, weight=1, uniform='a')

        # step 설명 라벨
        font = ctk.CTkFont(family=FONT, size=MAIN_LABEL_FONT_SIZE)
        self.label = ctk.CTkLabel(self, text='Detection Step', text_color=WHITE, font=font)
        self.label.grid(row=0, column=0)
        print(f'self.label size: {self.label.winfo_geometry()}')

        # step 정보 라벨 코드는 트리뷰 아래에 있음

        # Treeview style
        self.style = ttk.Style()
        self.style.configure("Treeview", font=('Arial', 16)) # 항목 폰트
        self.style.configure("Treeview.Heading", font=('Arial', 18, 'bold')) # 헤더 폰트
        # treeview
        self.file_tree = ttk.Treeview(self, columns=('name', 'status'), show='headings', height=30)
        # 헤더 설정
        self.file_tree.heading('name', text='name', anchor='w')
        self.file_tree.heading('status', text='status', anchor='w')
        # 컬럼 설정
        self.file_tree.column('name', anchor='w')
        self.file_tree.column('status', anchor='e')
       
        # grid 배치
        self.file_tree.grid(row=2, column=0, columnspan = 3, sticky='nsew', padx=(30, 0))
        

        # 전체 Treeview 너비 비율 조정 (열 너비 비중 설정)
        total_columns_weight = 10  # 전체 비율 합계
        self.file_tree.column('name', width=int(0.7 * total_columns_weight), stretch=True)  # 70% 비율
        self.file_tree.column('status', width=int(0.3 * total_columns_weight), stretch=True)  # 30% 비율

        # Treeview 스크롤바 설정
        self.scrollbar = ctk.CTkScrollbar(self, orientation='vertical', command=self.file_tree.yview)
        self.file_tree.configure(yscrollcommand=self.scrollbar.set)
        self.scrollbar.grid(row=2, column=3, sticky='nsw', padx=(5, 25))

        # buttons
        self.exit_btn = ctk.CTkButton(  # 종료 버튼
            self,
            text='Exit',
            font = ('Arial', 20, 'bold'),
            fg_color='red',
            hover_color='brown',
            command= lambda: self.quit()
            )
        self.confirm_btn = ctk.CTkButton(
            self,
            text='Confirm',
            font=('Arial', 20, 'bold'),
            fg_color='green',
            hover_color='darkgreen',
            command=lambda: print('confirm button clicked')
        )
        self.exit_btn.grid(row=3, column=0, sticky='ws', padx=20, pady=20)
        self.confirm_btn.grid(row=3, column=2, sticky='es', padx=0, pady=20)




        #! 파일 읽기 및 Treeview 업데이트
        self.read_directory_and_update_treeview('C:\\Users\\qkrtk\\Desktop\\shelve_test', 'daily_files_shelve')

        self.testlabel = ctk.CTkLabel(self, text=f'총 파일 개수: {self.file_list_len}', font=('Arial', 16, 'bold'))
        self.testlabel.grid(row=1, column=0, sticky='nw', padx=(20, 0))


    def read_directory_and_update_treeview(self, directory: str, shelve_filename: str):
        """
        지정된 디렉토리에서 파일 정보를 읽고 Shelve에 저장한 후 Treeview에 표시
        """
        # Shelve에 파일 정보 저장
        with shelve.open(shelve_filename) as db:
            for filename in os.listdir(directory):
                filepath = os.path.join(directory, filename)
                if os.path.isfile(filepath) and filename.endswith(".png"):
                    file_info = {
                        "파일명": filename,
                        "크기": os.path.getsize(filepath),
                        "수정 날짜": datetime.fromtimestamp(os.path.getmtime(filepath)).strftime('%Y-%m-%d %H:%M:%S'),
                        "전송 상태": "미전송"
                    }
                    db[filename] = file_info
                #! print(f"{file_info['파일명']} : {file_info['전송 상태']} / {file_info['수정 날짜']}")
                self.file_list_len += 1
        #! print(f"Total {file_list_len} files are saved in shelve file")

        # Treeview 업데이트
        with shelve.open(shelve_filename) as db:
            for key in db:
                file_info = db[key]
                self.file_tree.insert("", "end", values=(file_info["파일명"], f"{file_info['크기']} bytes", file_info["수정 날짜"], file_info["전송 상태"]))


# 메인 함수
if __name__ == '__main__':
    App()