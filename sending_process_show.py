from settings import *
from style import *

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
        # self.sending_progress_bar.start()  # 무한 모드 대신, 필요 시 set(value) 사용

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
            # (1) 미전송 파일 목록 불러오기 (예: shelve_manager에서)
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
