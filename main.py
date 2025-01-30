from settings import *
from style import *

from sending_proccess import *
from shelve_manager import *

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

        self.current_frame_index = 0    # 현재 프레임 인덱스. 0부터 시작
        self.current_frame = None       # 현재 프레임을 저장할 변수
        
        self.show_current_frame()       # 첫 번째 프레임 표시

    # 현재 프레임 표시
    def show_current_frame(self):
        # 기존 프레임이 있으면 숨기고 제거
        if self.current_frame is not None:
            self.current_frame.pack_forget()
            self.current_frame.destroy()

        # 현재 프레임 인덱스에 따라 새로운 프레임을 생성합니다.
        if self.current_frame_index == 0:
            self.current_frame = DailyDetectionShow(self, self.next_frame)
        elif self.current_frame_index == 1:
            self.current_frame = SendingProcessShow(self)
        elif self.current_frame_index == 2:
            # self.current_frame = ResultFrame(self, self.restart)
            #! 여기에 결과 프레임 추가
            pass

        # 새로 생성한 프레임을 표시합니다.
        if self.current_frame is not None:
            self.current_frame.pack(padx=50, pady=50, fill="both", expand=True)

    # 다음 프레임으로 이동
    def next_frame(self):
        if self.current_frame_index < 2:
            self.current_frame_index += 1
            print(f'현재 페이지 인덱스: {self.current_frame_index}')
            self.show_current_frame()

    # 첫 프레임으로 이동
    def restart(self):
        self.current_frame_index = 0
        self.show_current_frame()

        

class DailyDetectionShow(ctk.CTkFrame):
    def __init__(self, parent, next_frame_callback):
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
        print(f'detection step - label size: {self.label.winfo_geometry()}')

        # step 정보 라벨 코드는 트리뷰 아래에 있음

        # Treeview style
        # TODO 홀수 짝수 라인 별로 색상 다르게 변경하면 좋을 듯
        self.style = ttk.Style()
        # self.style.configure("Treeview", font=('Arial', 12)) # 항목 폰트
        # self.style.configure("Treeview.Heading", font=('Arial', 14, 'bold')) # 헤더 폰트
        
        # treeview
        self.file_tree = ttk.Treeview(self, columns=('name', 'size', 'modified_date', 'status'), show='headings', height=30)
        # 헤더 설정
        self.file_tree.heading('name', text='name', anchor='w')
        self.file_tree.heading('size', text='size', anchor='w')
        self.file_tree.heading('modified_date', text='modified_date', anchor='w')
        self.file_tree.heading('status', text='status', anchor='w')
        # 컬럼 설정
        self.file_tree.column('name', anchor='w')
        self.file_tree.column('size', anchor='w')
        self.file_tree.column('modified_date', anchor='w')
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
            command=next_frame_callback
        )

        self.exit_btn.grid(row=3, column=0, sticky='ws', padx=20, pady=20)
        self.confirm_btn.grid(row=3, column=2, sticky='es', padx=0, pady=20)


        # TODO shelve 제어 항목 분리 필요
        #! 파일 읽기 및 Treeview 업데이트
        self.daily_info_label = ctk.CTkLabel(self, text=f'총 파일 개수: {self.file_list_len}', font=('Arial', 16, 'bold'))
        self.daily_info_label.grid(row=1, column=0, sticky='nw', padx=(20, 0))
        
        self.read_directory_and_update_treeview('..\\shelve_test', 'daily_files_shelve')

    def read_directory_and_update_treeview(self, directory: str, shelve_filename: str):
        """
        지정된 디렉토리에서 파일 정보를 읽어 shelve에 저장한 후,
        Treeview에 표시
        """
        # 1) 디렉토리 내 .png 파일을 shelve에 저장
        # from shelve_manager import store_png_files_in_shelve, load_all_files_from_shelve

        stored_count = store_png_files_in_shelve(directory, shelve_filename)
        print(f"{stored_count}개의 .png 파일을 shelve에 저장했습니다.")

        # 2) shelve로부터 모든 파일 정보를 불러와 Treeview에 삽입
        file_info_list = load_all_files_from_shelve(shelve_filename)
        for file_info in file_info_list:
            filename = file_info["파일명"]
            size_bytes = file_info["크기"]
            mod_date = file_info["수정 날짜"]
            status = file_info["전송 상태"]

            # Treeview 삽입
            self.file_tree.insert("", "end", values=(filename, f"{size_bytes} bytes", mod_date, status))
            self.file_list_len += 1
            print(file_info)

        # 혹은 self.daily_info_label 등의 UI 요소에도 추가 반영
        self.daily_info_label.configure(text=f"총 파일 개수: {self.file_list_len}")


# class SendingProcessShow(ctk.CTkFrame):
#     def __init__(self, parent):
#         super().__init__(master=parent)

#         # frame setting
#         self.grid(column=0, row=0, sticky='nsew', padx=50, pady=50)

#         # layout
#         # 4x3 그리드
#         self.rowconfigure(0, weight=1, uniform='b')
#         self.rowconfigure(1, weight=2, uniform='b')
#         self.rowconfigure(2, weight=8, uniform='b')
#         self.rowconfigure(3, weight=2, uniform='b')
#         self.columnconfigure(0, weight=1, uniform='b')
#         self.columnconfigure(1, weight=1, uniform='b')
#         self.columnconfigure(2, weight=1, uniform='b')

#         # step 설명 라벨
#         font = ctk.CTkFont(family=FONT, size=MAIN_LABEL_FONT_SIZE)
#         self.label = ctk.CTkLabel(self, text='Sending Process', text_color=WHITE, font=font)
#         self.label.grid(row=0, column=0)
#         # print(f'sending process - label size: {self.label.winfo_geometry()}')

#         # 프로그레스 바
#         #! 스레드 사용하여 프로그레스 바 업데이트

#         # 프로그레스 바 생성
#         self.sending_progress_bar = ctk.CTkProgressBar(
#             master=self,
#             height=45,
#             corner_radius=20,
#             border_width=2,
#             mode='determinate',
#             )
#         self.sending_progress_bar.grid(row=1, column=0, columnspan=3, sticky='ew', padx=50, pady=20)

#         # 프로그레스 바 테스트용 시작
#         self.sending_progress_bar.start()
        

#         # 전송 상태 표시
#         self.status_log_txtbox = ctk.CTkTextbox(
#             master=self,
#             width=500,
#             height=300,
#             # State=,
#             )
#         self.status_log_txtbox.grid(row=2, column=0, columnspan=3, sticky='nsew', padx=50, pady=20)
        
#         self.status_log_txtbox.insert("0.0", "파일 전송 상태 창!...\n")  #! 테스트용 텍스트

#         # 사용자 입력 방지
#         def disable_user_input(event):
#             return "break"
        
#         self.status_log_txtbox.bind("<Key>", disable_user_input)  #! 사용자 키보드 입력 방지
#         self.status_log_txtbox.bind("<Button-1>", disable_user_input)  #! 마우스 클릭 방지

#         # 제어 버튼
#         #? 사용할지 안할지 미정
#         #! 사용자가 이상을 감지하고 중지 시킨 경우에 만약 새로 처음부터 보내야한다면, shelve에 있는 파일 제어를 어떻게 할 것인가?
#         #! 우선은 예외처리 없이 구현하고, 나중에 예외처리를 추가할 예정



class SendingProcessShow(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(master=parent)
        self.grid(column=0, row=0, sticky='nsew', padx=50, pady=50)

        # --- 기존 레이아웃 설정 (ProgressBar, Textbox 등) ---
        self.rowconfigure(0, weight=1, uniform='b')
        self.rowconfigure(1, weight=2, uniform='b')
        self.rowconfigure(2, weight=8, uniform='b')
        self.rowconfigure(3, weight=2, uniform='b')
        self.columnconfigure(0, weight=1, uniform='b')
        self.columnconfigure(1, weight=1, uniform='b')
        self.columnconfigure(2, weight=1, uniform='b')

        font = ctk.CTkFont(family=FONT, size=MAIN_LABEL_FONT_SIZE)
        self.label = ctk.CTkLabel(self, text='Sending Process', text_color=WHITE, font=font)
        self.label.grid(row=0, column=0)

        # 프로그레스 바
        self.sending_progress_bar = ctk.CTkProgressBar(
            master=self,
            height=45,
            corner_radius=20,
            border_width=2,
            mode='determinate',
        )
        self.sending_progress_bar.grid(row=1, column=0, columnspan=3, sticky='ew', padx=50, pady=20)
        self.sending_progress_bar.start()

        # 전송 상태 표시 (로그 박스)
        self.status_log_txtbox = ctk.CTkTextbox(
            master=self,
            width=500,
            height=300,
        )
        self.status_log_txtbox.grid(row=2, column=0, columnspan=3, sticky='nsew', padx=50, pady=20)
        self.status_log_txtbox.insert("0.0", "파일 전송 상태 창!...\n")

        # 사용자 입력 방지
        def disable_user_input(event):
            return "break"
        self.status_log_txtbox.bind("<Key>", disable_user_input)  
        self.status_log_txtbox.bind("<Button-1>", disable_user_input)

        # "전송 시작" 버튼 추가
        self.start_button = ctk.CTkButton(
            self,
            text='전송 시작',
            font=('Arial', 20, 'bold'),
            fg_color='green',
            hover_color='darkgreen',
            command=self.start_sending_process
        )
        self.start_button.grid(row=3, column=2, sticky='es', padx=20, pady=20)

        # Queue & 주기적 폴링
        self.log_queue = queue.Queue()
        self.after(200, self.poll_queue)

    def start_sending_process(self):
        """
        사용자가 '전송 시작' 버튼을 클릭하면 호출됨.
        별도 스레드에서 shelve -> uia -> opencv 로직을 실행.
        """
        self.log_queue.put(("log", "[Main] 전송 시작 버튼 클릭"))
        self.start_button.configure(state="disabled")  # 중복 클릭 방지
        self.current_progress = 0
        self.sending_progress_bar.set(0)  # 0% 초기화

        # 작업 스레드 생성
        worker_thread = threading.Thread(target=self.send_files_worker, args=(self.log_queue,))
        worker_thread.daemon = True
        worker_thread.start()

    def send_files_worker(self, log_queue):
        """
        백그라운드 스레드에서 실행될 전송 로직:
        1. shelve에서 '미전송' 파일 목록 가져오기
        2. uiautomation으로 카카오톡 열기 & 파일 전송
        3. ROI 캡처 + opencv 매칭
        4. shelve 업데이트
        5. 진행 상황을 log_queue에 put()하여 UI 표시
        """
        try:
            # (1) 미전송 파일 목록 불러오기
            with shelve.open("daily_files_shelve") as db:
                keys = [k for k in db.keys() if db[k].get("전송 상태") == "미전송"]
            
            total_files = len(keys)
            log_queue.put(("log", f"[Worker] 미전송 파일 {total_files}개 발견."))

            # uia: 카카오 실행 + 활성화
            ensure_kakao_running()
            time.sleep(1)
            kakao_window = activate_kakao_window()
            time.sleep(1)

            processed_count = 0

            for filename in keys:
                # 파일 정보 가져오기
                with shelve.open("daily_files_shelve", writeback=True) as db:
                    file_info = db[filename]

                log_queue.put(("log", f"[Worker] '{filename}' 전송 시도중..."))

                # (2) uia 부분 (간단 예시 - 실제 로직 대체)
                # ex) search_friend, attach_file, etc.
                time.sleep(2)  # 더미 대기
                # ROI 캡처 + opencv (또는 그냥 더미 결과)
                # (ROI 예시)
                # roi_image = capture_roi(kakao_window) # 별도 함수 구현
                # result = detect_status(roi_image, templates_dict)
                result = "성공"  # 일단 더미
                time.sleep(1)

                # (4) shelve 업데이트
                with shelve.open("daily_files_shelve", writeback=True) as db:
                    file_info = db[filename]
                    file_info["전송 상태"] = result
                    db[filename] = file_info

                log_queue.put(("log", f"[Worker] '{filename}' => {result}"))

                # Progress 갱신
                processed_count += 1
                progress_ratio = processed_count / total_files
                log_queue.put(("progress", progress_ratio))

            log_queue.put(("done", "모든 파일 전송 작업이 완료되었습니다."))

        except Exception as e:
            log_queue.put(("log", f"[에러] {str(e)}"))
            log_queue.put(("done", "작업 중단 (에러 발생)"))

    def poll_queue(self):
        """
        주기적으로 Queue를 확인하여 로그창과 ProgressBar를 업데이트.
        """
        while not self.log_queue.empty():
            msg_type, msg_content = self.log_queue.get()
            if msg_type == "log":
                self.status_log_txtbox.insert("end", msg_content + "\n")
            elif msg_type == "progress":
                # msg_content를 0~1 사이 값으로 가정
                self.sending_progress_bar.set(msg_content)
            elif msg_type == "done":
                self.status_log_txtbox.insert("end", msg_content + "\n")
                self.start_button.configure(state="normal")

        self.after(200, self.poll_queue)



# 메인 함수
if __name__ == '__main__':
    app = App()
    app.mainloop()  # 메인 루프 실행