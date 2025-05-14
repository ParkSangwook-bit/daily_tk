from ast import main
from settings import ttk, ctk, queue, cast, threading, traceback
from style import *
import constants
import random

from kakao_control import *
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
        
        # 데이터 홀더(프레임간 데이터 공유 용)
        self.pending_files_list = []  # 전송 대기 중인 파일 리스트
        self.student_names = []  # 학생 이름 리스트

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
            self.current_frame = SendingProcessShow(self, self.next_frame)
        elif self.current_frame_index == 2:
            self.current_frame = ResultFrame(self, self.restart)

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

# 데일리 감지 및 Treeview 표시 프레임
class DailyDetectionShow(ctk.CTkFrame):
    def __init__(self, parent: "App", next_frame_callback):
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

        #! 파일 읽기 및 Treeview 업데이트
        self.daily_info_label = ctk.CTkLabel(self, text=f'총 파일 개수: {self.file_list_len}', font=('Arial', 16, 'bold'))
        self.daily_info_label.grid(row=1, column=0, sticky='nw', padx=(20, 0))
        
        self.read_directory_and_update_treeview(str(constants.SHELVE_TEST_DIR), 'daily_files_shelve')

    def read_directory_and_update_treeview(self, directory: str, shelve_filename: str):
        """
        지정된 디렉토리에서 파일 정보를 읽어 shelve에 저장한 후,
        Treeview에 표시
        """
        # lint 오탐지로, self.master를 App으로 캐스팅(다른 클래스도 필요하면 추가 또는 다른 방법 적용 필요)
        app = cast(App, self.master)
        
        # 1) 디렉토리 내 .png 파일을 shelve에 저장

        stored_count = store_png_files_in_shelve(directory, shelve_filename)
        print(f"{stored_count}개의 .png 파일을 shelve에 저장했습니다.")

        # 2) shelve로부터 미전송 파일 리스트를 Treeview에 삽입
        app.pending_files_list = get_pending_file_infos(shelve_filename)
        for file_info in app.pending_files_list:
            filename = file_info["파일명"]
            size_bytes = file_info["크기"]
            mod_date = file_info["수정 날짜"]
            status = file_info["전송 상태"]

            # Treeview 삽입
            self.file_tree.insert("", "end", values=(filename, f"{size_bytes} bytes", mod_date, status))
            self.file_list_len += 1

        # 혹은 self.daily_info_label 등의 UI 요소에도 추가 반영
        self.daily_info_label.configure(text=f"총 파일 개수: {self.file_list_len}")

# 전송 및 전송 과정 표시 프레임
class SendingProcessShow(ctk.CTkFrame):
    def __init__(self, parent: "App", next_frame_callback):
        self.next_frame_callback = next_frame_callback
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
        self.sending_progress_bar.set(0)  # 0으로 초기화

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
        # worker_thread = threading.Thread(target=self.dummy_send_files_worker, args=(self.log_queue,))
        worker_thread.daemon = True
        worker_thread.start()

    #! 리팩토링 필요
    def send_files_worker(self, log_queue):
        """
        백그라운드 스레드에서 실행될 전송 로직:
        1. App 클래스에 있는 데이터 홀더로부터 파일 정보 리스트를 가져옴
        2. uiautomation으로 카카오톡 열기 & 파일 전송
        #? 3. ROI 캡처 + opencv 매칭
        4. shelve 업데이트
        5. 진행 상황을 log_queue에 put()하여 UI 표시
        """
        try:
            # (1) 미전송 파일 목록 불러오기
            app = cast(App, self.master)
            
            total_files = len(app.pending_files_list)
            log_queue.put(("log", f"[Worker] 미전송 파일 {total_files}개 발견."))
            
            # 서브 스레드에서 uiautomation을 사용하기 위해 COM(Windows Component Object Model) 초기화
            with auto.UIAutomationInitializerInThread():
                # auto: 카카오 실행 + 활성화
                ensure_kakao_running()
                time.sleep(1)
                self.kakao_window = activate_kakao_window()
                log_queue.put(("log", "[Worker] 카카오톡 창 활성화"))
                # print("[FLAG] 카카오톡 창 활성화")
                time.sleep(1)

                processed_count = 0 # 전송된 파일 수 카운트


                # 최초에 카카오톡창을 포커스 -> 친구창 클릭
                main_view = find_element_with_partial_name(self.kakao_window, "OnlineMainView")
                if not main_view:
                    print("[ERR] OnlineMainView not found")
                    return "unknown"
                move_cursor_to_top_left(main_view)
                click_by_offset(main_view, 60, 60)

                # filename = type(dict)
                for filename in app.pending_files_list: #! 현재 미전송 파일만 자동으로 특정함.
                    # 파일 정보 가져오기

                    log_queue.put(("log", f"[Worker] '{filename["파일명"]}' 전송 시도중..."))

                    # (2) auto 부분 (간단 예시 - 실제 로직 대체)
                    # ex) search_friend, attach_file, etc.
                    if self.kakao_window is not None:

                        # 파일 전송 시도
                        #! 현재 opencv 기능 없이 진행
                        #! 현재 False = 실제 전송 없이 진행하는 더미
                        result = sending_process_without_opencv(filename, False)
                    else:
                        log_queue.put(("log", "[에러] 카카오톡 창을 찾을 수 없습니다."))
                        break
                    
                    time.sleep(2)  

                    log_queue.put(("log", f"[Worker] '{filename}' => {result}"))

                    # Progress 갱신
                    processed_count += 1
                    progress_ratio = processed_count / total_files
                    log_queue.put(("progress", progress_ratio))

                log_queue.put(("done", "모든 파일 전송 작업이 완료되었습니다."))

        except Exception as e:
            trace_str = traceback.format_exc()
            log_queue.put(("log", f"[에러] {str(e)}\n{trace_str}"))
            log_queue.put(("done", "작업 중단 (에러 발생)"))

    def dummy_send_files_worker(self, log_queue):
        """
        파일 전송 프로세스를 시뮬레이션하는 더미 작업자 함수.
        각 파일에 대해 2초의 소요시간을 두고 진행률을 업데이트하고 상태를 로그에 기록합니다.
        """
        import random
        import time
        import traceback

        try:
            app = cast(App, self.master)
            total_files = len(app.pending_files_list)
            log_queue.put(("log", f"[DummyWorker] {total_files}개의 대기 파일을 발견했습니다."))

            processed_count = 0

            for file_info in app.pending_files_list:
                file_name = file_info.get("파일명", "알 수 없음")
                log_queue.put(("log", f"[DummyWorker] '{file_name}' 처리 중..."))

                # 2초 동안 부드러운 진행률 업데이트
                for step in range(20):
                    progress_ratio = (processed_count + (step + 1) / 20) / total_files
                    log_queue.put(("progress", progress_ratio))
                    time.sleep(0.1)  # 0.1초 * 20 = 2초

                result = random.choice(["성공", "실패", "전송 중", "미전송"])
                update_file_status("daily_files_shelve", file_name, result)
                log_queue.put(("log", f"[DummyWorker] '{file_name}' => {result}"))

                processed_count += 1

            log_queue.put(("progress", 1.0))
            log_queue.put(("done", "모든 파일이 성공적으로 처리되었습니다 (더미 모드)."))

        except Exception as e:
            error_message = f"[Error] dummy_send_files_worker에서 예외가 발생했습니다: {str(e)}"
            log_queue.put(("log", error_message))
            log_queue.put(("done", "에러로 인해 처리가 중단되었습니다."))
            traceback.print_exc()

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

                # print(f"진행률: {msg_content:.2%}")  #! 디버그용
            elif msg_type == "done":
                self.status_log_txtbox.insert("end", msg_content + "\n")
                # 이건 전송 완료 후 버튼 활성화
                # self.start_button.configure(state="normal")

                self.start_button.configure(state="normal", text="결과 보기", command=self.next_frame_callback)

                
        # 0.2초마다 Queue 확인
        self.after(200, self.poll_queue)

class ResultFrame(ctk.CTkFrame):
    def __init__(self, parent: "App", restart_callback):
        super().__init__(master=parent)
        self.grid(column=0, row=0, sticky='nsew', padx=50, pady=50)

        self.file_list_len = 0  # 파일 리스트 길이

        # 레이아웃 설정
        self.rowconfigure(0, weight=1, uniform='a')
        self.rowconfigure(1, weight=2, uniform='a')
        self.rowconfigure(2, weight=8, uniform='a')
        self.rowconfigure(3, weight=2, uniform='a')
        self.columnconfigure(0, weight=1, uniform='a')
        self.columnconfigure(1, weight=1, uniform='a')
        self.columnconfigure(2, weight=1, uniform='a')

        font = ctk.CTkFont(family=FONT, size=MAIN_LABEL_FONT_SIZE)
        self.label = ctk.CTkLabel(self, text='Result', text_color=WHITE, font=font)
        self.label.grid(row=0, column=0)

        # 결과 표시 (예시로 텍스트 박스 사용)
        self.result_textbox = ctk.CTkTextbox(self)
        self.result_textbox.grid(row=2, column=0, columnspan=3, sticky='nsew', padx=(30, 0))

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

        # 버튼 설정
        self.restart_btn = ctk.CTkButton(
            self,
            text='다시 시작',
            font=('Arial', 20),
            command=restart_callback
        )
        self.restart_btn.grid(row=3, column=2, sticky='es', padx=(0, 20), pady=(0, 20))

        #! 파일 읽기 및 Treeview 업데이트
        self.daily_info_label = ctk.CTkLabel(self, text=f'총 파일 개수: {self.file_list_len}', font=('Arial', 16, 'bold'))
        self.daily_info_label.grid(row=1, column=0, sticky='nw', padx=(20, 0))
        
        self.result_treeview_show('daily_files_shelve')
    
    def result_treeview_show(self, shelve_filename: str):
        """
        shelve에서 결과를 읽어 Treeview에 표시
        """

        # 1) shelve의 내용 읽어오기
        print(get_specific_status_files_infos(["미전송", "실패", "전송중"], shelve_filename))
        self.result_files_list = get_specific_status_files_infos(["미전송", "실패", "전송중"], shelve_filename)
        for file_info in self.result_files_list:
            filename = file_info["파일명"]
            size_bytes = file_info["크기"]
            mod_date = file_info["수정 날짜"]
            status = file_info["전송 상태"]

            # Treeview 삽입
            self.file_tree.insert("", "end", values=(filename, f"{size_bytes} bytes", mod_date, status))
            self.file_list_len += 1

        self.daily_info_label.configure(text=f"총 파일 개수: {self.file_list_len}")



# 메인 함수
if __name__ == '__main__':
    app = App()
    app.mainloop()  # 메인 루프 실행