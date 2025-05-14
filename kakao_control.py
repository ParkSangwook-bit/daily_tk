from turtle import update
from constants import MAIN_SHELVE, SHELVE_TEST_DIR, ROI_OFFSET_BOTTOM
from settings  import shelve, theWorld, time, auto, subprocess
from utils     import extract_student_name
from shelve_manager import update_file_status
import template_matching_opencv as tm

# ────────────────────────────────────────────────────────────────
# 1. DPI 보정 함수 추가  ⭑
# ────────────────────────────────────────────────────────────────
def ui_to_logical(rect):
    """
    화면 DPI 배율(확대/축소)을 고려해
    UIAutomation BoundingRectangle(px) → 논리 좌표(px)로 환산한다.
    """
    import ctypes

    # ── Win32 DLL 핸들 ───────────────────────────
    user32 = ctypes.windll.user32
    gdi32  = ctypes.windll.gdi32

    # ── 현재 프로세스를 DPI Aware 로 설정 ────
    user32.SetProcessDPIAware()

    # ── 시스템 DPI 가져오기 ────────────────────
    hdc   = user32.GetDC(0)
    dpi_x = gdi32.GetDeviceCaps(hdc, 88)   # LOGPIXELSX
    dpi_y = gdi32.GetDeviceCaps(hdc, 90)   # LOGPIXELSY
    user32.ReleaseDC(0, hdc)    #! 해제 필수


    # X·Y 축 평균값(대부분 동일하지만, 듀얼 모니터 혼합 대비)
    scale = (dpi_x + dpi_y) / 192.0        # 96 dpi 기준 → 192 = 96*2

    # ── 좌표 보정 후 반환 ──────────────────────
    return (
        round(rect.left   / scale),
        round(rect.top    / scale),
        round(rect.right  / scale),
        round(rect.bottom / scale)
    )

# ────────────────────────────────────────────────────────────────
# 2. ‘대화 팝업창’ 활성화 함수 신규  ⭑
# ────────────────────────────────────────────────────────────────
def activate_chat_window(student_name: str):
    """
    ① 이미 열린 ‘장운형A’ 팝업이 있으면 활성화해 반환  
    ② 없으면 메인창에서 친구 더블클릭 → 새 팝업이 뜰 때까지 폴링
    """
    # ── ① 이미 열린 팝업 찾기 ───────────────────────────
    chat = auto.WindowControl(
        searchDepth = 1,                      # ⚑ 루트‑레벨
        Name        = student_name,           # 정확히 일치
        ClassName   = 'EVA_Window_Dblclk'     # 팝업/메인 둘 다 이 클래스
    )
    if chat.Exists(0, 0):
        chat.SetActive(); chat.SetFocus()
        return chat                           # ← 바로 반환

    # ── ② 메인창에서 친구 더블클릭 ─────────────────────
    main = auto.WindowControl(searchDepth=1, Name="카카오톡")
    if not main.Exists(0, 0):
        print("[ERR] KakaoTalk main window not found."); return None

    friend = main.Control(Name=student_name, searchDepth=5)
    if not friend.Exists(0, 0):
        print(f"[ERR] Friend '{student_name}' not in list."); return None

    friend.DoubleClick()
    # 팝업이 뜰 때까지 루트‑레벨에서 폴링
    for _ in range(20):                       # 최대 2 초 (100 ms × 20)
        chat = auto.WindowControl(
            searchDepth = 1,
            Name        = student_name
        )
        if chat.Exists(0, 0):
            chat.SetActive(); chat.SetFocus()
            return chat
        time.sleep(0.1)

    print("[ERR] Chat window did not appear.")
    return None

# subprocess를 이용해 KakaoTalk.exe 프로세스가 실행 중인지 확인
def is_kakao_running():
    result = subprocess.run(['tasklist', '/fi', 'IMAGENAME eq KakaoTalk.exe'],
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if 'KakaoTalk.exe' in result.stdout:
        print("'KakaoTalk.exe' 프로세스를 감지했습니다.")
        return True
    print("Failed detecting 'KakaoTalk.exe' process")
    return False

# 카카오톡 실행 여부 확인 후 실행
def ensure_kakao_running():
    if is_kakao_running():
        print("카카오톡이 이미 실행 중입니다.")
    else:
        print("카카오톡이 실행되고 있지 않습니다. 카카오톡 실행 시도 . . .")
        launch_kakao()

# 카카오톡 exe 실행
def launch_kakao():
    kakao_path = r"C:\Program Files (x86)\Kakao\KakaoTalk\KakaoTalk.exe"
    try:
        subprocess.Popen([kakao_path], shell=False)
        print("카카오톡 프로세스 실행 완료")
        # 카카오톡 실행 후 UI가 준비될 때까지 잠시 대기
        time.sleep(3)
    except FileNotFoundError as e:
        print(f"{kakao_path}에서 카카오톡을 찾을 수 없습니다. 경로를 확인해주세요.")
        print(f"error code: {e}")

# 카카오톡 창 활성화(SetActive, SetFocus)
#! 시스템 트레이에 숨겨진 카카오톡은 찾지 못함
#! -> 이 경우를 대비해서 그냥 곧바로 launch_kakao()를 할지 고민
#! -> 어짜피 세마포어 때문에 카카오톡 창은 하나일 것
#? kakao_window.ShowWindow()          # 내부적으로 SW_RESTORE
#? 이거 검토해보기. SW_플래그는 0,1,2,6,9인가가 있음. 9가 SW_RESTORE
def activate_kakao_window():
    kakao_window = auto.WindowControl(searchDepth=1, Name="카카오톡")
    if kakao_window.Exists(0, 0):
        kakao_window.SetActive()
        kakao_window.SetFocus()
        print("KakaoTalk window activated.")
        return kakao_window
    else:
        print("KakaoTalk window not found.")
        return None

# 특정 element의 최-좌상단으로 커서 이동
def move_cursor_to_top_left(element):
    if element is None or not element.Exists(0, 0):
        print("Invalid element or element does not exist.")
        return
    rect = element.BoundingRectangle
    if rect is None:
        print("Element does not have a BoundingRectangle.")
        return
    target_x = rect.left
    target_y = rect.top
    auto.MoveTo(target_x, target_y)
    print(f"Cursor moved to top-left at ({target_x}, {target_y})")

# 부모 element에서 특정 이름을 포함하는 자식 element 찾기
def find_element_with_partial_name(parent_element, partial_name):
    children = parent_element.GetChildren()
    print(f"Found {len(children)} children under '{parent_element.Name}'")
    for child in children:
        print(f"Checking element: {child.Name}")
        if partial_name in child.Name:
            return child
    return None

# element의 BoundingRectangle 정보 출력
def get_kakao_bounding_rect(element):
    if element is not None and element.Exists(0, 0):
        rect = element.BoundingRectangle
        width = rect.right - rect.left
        height = rect.bottom - rect.top
        print(f"BoundingRectangle: left={rect.left}, top={rect.top}, right={rect.right}, bottom={rect.bottom}")
        print(f"Width: {width}, Height: {height}")
        return rect, width, height
    else:
        print("main_view not found.")
        return None, None, None

# element 내에서 offset을 이용한 클릭
def click_by_offset(element, offset_x, offset_y):
    if element is None or not element.Exists(0, 0):
        print("Element not found or invalid.")
        return
    rect = element.BoundingRectangle
    width = rect.right - rect.left
    height = rect.bottom - rect.top

    x_ratio = offset_x / width
    y_ratio = offset_y / height

    click_x = rect.left + (width * x_ratio)
    click_y = rect.top + (height * y_ratio)

    auto.MoveTo(int(click_x), int(click_y))
    auto.Click(int(click_x), int(click_y))
    print(f"Clicked at offset ({offset_x}, {offset_y}) which is ratio ({x_ratio:.3f}, {y_ratio:.3f})")


def dummy_process_func(filename: dict, kakao_window: auto.WindowControl):# -> Any | None | Literal['전송 중'] | Literal['unknown']:
    # 카카오톡 실행 여부 확인 후 실행
    ensure_kakao_running()
    time.sleep(2)
    #? 카카오톡 창 활성화(SetActive, SetFocus) | 근데 어짜피 걍 launch_kakao()로 해도 될 듯
    # kakao_window = activate_kakao_window()
    file_name_temp = filename["파일명"]
    
    student_name = extract_student_name(file_name_temp)

    #! 채팅창 포커스 풀리는거 방지를 위한 focus 유지 함수 호출 타이밍 봐야함
    # 카카오톡 창이 활성화되었을 때
    if kakao_window and kakao_window.Exists(0, 0):
        # OnlineMainView element 찾기
        main_view = find_element_with_partial_name(kakao_window, "OnlineMainView")
        # OnlineMainView가 존재할 때
        if main_view:
            # OnlineMainView의 BoundingRectangle 정보 출력
            rect, width, height = get_kakao_bounding_rect(main_view)
            # BoundingRectangle 정보가 존재할 때
            if rect is not None:
                print(f"Found element with Name: {main_view.Name}")
                # OnlineMainView의 최-좌상단으로 커서 이동
                move_cursor_to_top_left(main_view)
                # OnlineMainView의 offset(60, 60)으로 클릭
                click_by_offset(main_view, 60, 60)

                # -----------------------------------------------------
                print(f"\n--- 시작: 친구 '{student_name}' 검색 테스트 ---")
                
                # 1. CTRL + F로 친구 검색창 열기
                auto.SendKeys('{Ctrl}f')  # Ctrl + F
                time.sleep(0.2)
                print("[LOG]\'검색창 열기\' 완료")

                # 2. 검색창에 특정 친구 이름 입력 후 엔터
                auto.SendKeys(student_name, interval=0.01)  # 글자 하나씩 입력
                print("[LOG]\'특정 친구 이름 입력 후 엔터\' 완료")
                time.sleep(0.2)
                auto.SendKeys('{ENTER}')
                print("[LOG]\'엔터\' 완료")
                time.sleep(0.2)

                # 4. 친구 채팅창으로 열기 (이미 Enter로 열렸다고 가정)

                # 5. 채팅창에 포커스 맞추기(한번 더 이름 체크)
                #! 실제로는 채팅창 WindowControl 탐색 등을 추가
                print(f"채팅창 '{student_name}' 포커스 맞춘 것으로 가정")

                # 6. CTRL + T로 첨부 파일 열기
                auto.SendKeys('{Ctrl}t')
                print("[LOG]\'첨부 파일창 열기\' 완료")
                time.sleep(0.2)

                # 7. 디렉토리 지정: CTRL + L, 파일 선택 후 열기 (ALT + N, ALT + O)
                auto.SendKeys('{Ctrl}l')
                print("[LOG]\'디렉토리 창 포커스\' 완료")
                time.sleep(0.2)
                # 디렉토리 경로 예시 입력 (가상)
                #! 디렉토리 못찾는 경우 대비해서 예외처리 필요
                #? 파일첨부 창에서의 디렉터리에서도 상대 경로 사용 가능
                #? ..\sehlve_test 이런식으로 가능(범용성 증가)
                # auto.SendKeys(SHELVE_TEST_DIR, interval=0.01)
                auto.SendKeys(str(SHELVE_TEST_DIR), interval=0.01)
                print("[LOG]\'디렉토리 경로 입력\' 완료")
                time.sleep(0.2)
                auto.SendKeys('{ENTER}')
                print("[LOG]\'디렉토리 열기\' 완료")
                time.sleep(0.2)

                # 파일 검색(ALT+N) / 열기(ALT+O)
                auto.SendKeys('{Alt}n')  # ALT+N
                print("[LOG]\'파일명 입력창 포커스\' 완료")
                time.sleep(0.2)
                auto.SendKeys(filename["파일명"], interval=0.05)
                print("[LOG]\'파일명 입력\' 완료")
                auto.SendKeys('{Alt}o')  # ALT+O
                print("[LOG]\'파일 열기\' 완료")
                time.sleep(0.2)

                #! 8. 모의) 파일 전송 확인창에서 취소(esc)
                auto.SendKeys('{esc}')
                print("[LOG]\'파일 전송 확인창에서 취소\' 완료")
                time.sleep(0.2)

                # 9. template matching(OpenCV) 실행 후 결과 확인
                # 이전 코드: 저장된 이미지 파일을 로드
                # main_img = tm.load_main_image()
                
                # 새로운 코드: 실시간 화면 캡처 사용
                # 9-1. 채팅창 ROI 영역 계산
                roi_bounds = tm.get_roi_bounds(rect)
                
                # 9-2. 해당 영역 실시간 캡처
                main_img = tm.capture_screen_region(roi_bounds)
                print(f"[LOG] 실시간 ROI 영역 캡처 완료: {roi_bounds}")
                
                # 9-3. 템플릿 로드 및 매칭 수행
                templates = tm.load_templates()
                
                print(f"[LOG] 템플릿 매칭 시작 - 템플릿 파일: ")
                for name, template in templates.items():
                    print(f"- {name}: {template.shape}")
                
                # 수정: 불필요한 매개변수 제거
                template_matching_result = tm.detect_status(main_img, templates)
                
                time.sleep(0.5)
                #! 시간정지
                theWorld(100)

                # todo 10. 결과에 따른 shelve 파일 수정
                update_file_status(MAIN_SHELVE, file_name_temp, template_matching_result)

                # 11. 채팅창 닫기(esc)
                auto.SendKeys('{ESC}')
                time.sleep(0.2)
                
                # 결과 반환(string)
                return template_matching_result

        else:
            print("OnlineMainView not found.")
    else:
        print("KakaoTalk window not found or not activated.")


#? 파일이름이랑 카카오 윈도우 전달 받아서
#? app() -> send_files_worker() -> sending_process(filename, kakao_window) -> 다시 send_files_worker()로 복귀 
# def sending_process(filename: dict, kakao_window: auto.WindowControl):# -> Any | None | Literal['전송 중'] | Literal['unknown']:
#     # 카카오톡 실행 여부 확인 후 실행
#     ensure_kakao_running()
#     time.sleep(2)
#     #? 카카오톡 창 활성화(SetActive, SetFocus) | 근데 어짜피 걍 launch_kakao()로 해도 될 듯
#     # kakao_window = activate_kakao_window()
#     file_name_temp = filename["파일명"]
    
#     student_name = extract_student_name(file_name_temp)

#     #! 채팅창 포커스 풀리는거 방지를 위한 focus 유지 함수 호출 타이밍 봐야함
#     # 카카오톡 창이 활성화되었을 때
#     if kakao_window and kakao_window.Exists(0, 0):
#         # OnlineMainView element 찾기
#         main_view = find_element_with_partial_name(kakao_window, "OnlineMainView")
#         # OnlineMainView가 존재할 때
#         if main_view:
#             # OnlineMainView의 BoundingRectangle 정보 출력
#             rect, width, height = get_kakao_bounding_rect(main_view)
#             # BoundingRectangle 정보가 존재할 때
#             if rect is not None:
#                 print(f"Found element with Name: {main_view.Name}")
#                 # OnlineMainView의 최-좌상단으로 커서 이동
#                 move_cursor_to_top_left(main_view)
#                 # OnlineMainView의 offset(60, 60)으로 클릭
#                 click_by_offset(main_view, 60, 60)

#                 # -----------------------------------------------------
#                 # 메인 클라이언트 윈도우 부분
#                 print(f"\n--- 시작: 친구 '{student_name}' 검색 테스트 ---")
                
#                 # 1. CTRL + F로 친구 검색창 열기
#                 auto.SendKeys('{Ctrl}f')  # Ctrl + F
#                 time.sleep(0.2)
#                 print("검색창 열기")

#                 # 2. 검색창에 특정 친구 이름 입력 후 엔터
#                 auto.SendKeys(student_name, interval=0.01)  # 글자 하나씩 입력
#                 time.sleep(0.2)
#                 auto.SendKeys('{ENTER}')
#                 time.sleep(0.2)

#                 # 3. 검색 결과에서 친구 선택 (UI 구조에 따라 Tab/Down/Enter 등 필요)
#                 # auto.SendKeys('{DOWN}')
#                 time.sleep(0.2)
#                 auto.SendKeys('{ENTER}')
#                 time.sleep(0.2)

#                 # 4. 친구 채팅창으로 열기 (이미 Enter로 열렸다고 가정)
#                 #! 여기서 부터 채팅창(서브 윈도우) 부분

#                 # 5. 채팅창에 포커스 맞추기(한번 더 이름 체크)
#                 # activate_chat_window(student_name)  #! 문제있을 수도 있음
#                 # print(f"채팅창 '{student_name}' 포커스")

#                 # 6. CTRL + T로 첨부 파일 열기
#                 auto.SendKeys('{Ctrl}t')
#                 time.sleep(0.2)

#                 # 7. 디렉토리 지정: CTRL + L, 파일 선택 후 열기 (ALT + N, ALT + O)
#                 auto.SendKeys('{Ctrl}l')
#                 time.sleep(0.2)
#                 # 디렉토리 경로 예시 입력 (가상)
#                 #! 디렉토리 못찾는 경우 대비해서 예외처리 필요
#                 auto.SendKeys(str(SHELVE_TEST_DIR), interval=0.01)
#                 time.sleep(0.2)
#                 auto.SendKeys('{ENTER}')
#                 time.sleep(0.2)

#                 # 파일 검색(ALT+N) / 열기(ALT+O)는
#                 #   Windows 공용 대화상자에서 동작할 수도 있고 아닐 수도 있으니
#                 #   실제 상황에 맞춰 조정 필요
#                 auto.SendKeys('{Alt}n')  # ALT+N
#                 time.sleep(0.2)
#                 #! filename을 문자열로서 입력하도록 수정 필요
#                 # file_name = filename["파일명"]
#                 auto.SendKeys(filename["파일명"], interval=0.05)
#                 #! 파일 열기 확정
#                 auto.SendKeys('{Alt}o')  # ALT+O
#                 time.sleep(0.2)

#                 # 8. 파일 전송 확인창 감지 후 상호작용(엔터)
#                 auto.SendKeys('{ENTER}')
#                 time.sleep(0.2)

#                 # 9. template matching(OpenCV) 실행 후 결과 확인
#                 # 이전 코드: 저장된 기본 이미지 파일을 로드
#                 # main_img = tm.load_main_image()
                
#                 # 새로운 코드: 실시간 화면 캡처 사용
#                 # 9-1. 채팅창 ROI 영역 계산
#                 roi_bounds = tm.get_roi_bounds(rect)
                
#                 # 9-2. 해당 영역 실시간 캡처
#                 main_img = tm.capture_screen_region(roi_bounds)
#                 print(f"[LOG] 실시간 ROI 영역 캡처 완료: {roi_bounds}")
                
#                 # 9-3. 템플릿 로드 및 매칭 수행
#                 templates = tm.load_templates()
                
#                 print(f"[LOG] 템플릿 매칭 시작 - 템플릿 파일: ")
#                 for name, template in templates.items():
#                     print(f"- {name}: {template.shape}")
                
#                 # 이 부분에서 템플릿 매칭 수행
#                 template_matching_result = tm.detect_status(main_img, templates)
                
#                 time.sleep(0.5)
#                 #! 시간정지
#                 theWorld(100)

#                 # todo 10. 결과에 따른 shelve 파일 수정 (여기서는 dummy_shelve에 기록)
#                 update_file_status(MAIN_SHELVE, file_name_temp, template_matching_result)

#                 # 11. 채팅창 닫기(esc)
#                 auto.SendKeys('{ESC}')
#                 time.sleep(0.2)
                
#                 # 결과 반환(string)
#                 return template_matching_result

#         else:
#             print("OnlineMainView not found.")
#     else:
#         print("KakaoTalk window not found or not activated.")

def sending_process_without_opencv(
        filename: dict,
        # kakao_window: auto.WindowControl,
        work_flag_bool: bool = False    # False: 전송 안함 / True: 전송함
) -> str:
    """
    1) 메인 창에서 학생 이름을 검색해 Enter 1회로 채팅 팝업을 연다.
    2) 단순 매크로 작업 후 템플릿 매칭 결과를 shelve DB 에 기록
    """
    # 0. 카카오톡 실행 보장
    ensure_kakao_running()
    time.sleep(1.5) #! 카카오톡 실행 대기. 그러나 나중에 프로세스 탐지로 비동기 처리

    file_name_temp = filename["파일명"]
    student_name   = extract_student_name(file_name_temp)

    # # 1. 메인 창에서 친구 검색 → 채팅 팝업 열기
    # main_view = find_element_with_partial_name(kakao_window, "OnlineMainView")
    # if not main_view:
    #     print("[ERR] OnlineMainView not found")
    #     return "unknown"

    # move_cursor_to_top_left(main_view)
    # click_by_offset(main_view, 60, 60)    auto.SendKeys('{Ctrl}f');              time.sleep(0.2)

    auto.SendKeys('{Ctrl}f')
    auto.SendKeys('{Ctrl}{HOME}')  # 문서의 맨 앞으로
    time.sleep(0.1)
    print("여기서 부터 shift + end 누르기 시도")
    auto.SendKeys('{Shift}{END}')  # 전체 선택
    time.sleep(0.1)
    print("여기서 부터 backspace 누르기 시도")
    auto.SendKeys('{DELETE}')
    time.sleep(0.2)
    # 검색창에 특정 친구 이름 입력 후 엔터
    auto.SendKeys(student_name, interval=0.01)  # 이름 검색
    auto.SendKeys('{ENTER}');              time.sleep(0.3)   # 팝업 생성

    #  3. 첨부 파일 전송 시퀀스
    auto.SendKeys('{Ctrl}t');   time.sleep(0.2) # 첨부파일 창 열기
    auto.SendKeys('{Ctrl}l');   time.sleep(0.2) # 디렉토리 열기
    auto.SendKeys(str(SHELVE_TEST_DIR), interval=0.01)  # 디렉토리 경로 입력
    auto.SendKeys('{ENTER}');   time.sleep(0.2) # 디렉토리 열기
    auto.SendKeys('{Alt}n');    time.sleep(0.2) # 파일명 입력창 포커스
    auto.SendKeys(filename["파일명"], interval=0.01)    # 파일명 입력
    auto.SendKeys('{Alt}o');    time.sleep(0.2) # 파일 열기
    if work_flag_bool:
        auto.SendKeys('{ENTER}');   time.sleep(0.2) # 파일 전송 확인창에서 엔터 (전송)
    else:
        auto.SendKeys('{esc}');   time.sleep(0.2) # 파일 전송 확인창에서 ESC (취소)

    # 4. shelve 갱신 및 채팅창 닫기
    # update_file_status(MAIN_SHELVE, file_name_temp, result)
    status = "성공" if work_flag_bool else "미전송"
    update_file_status(MAIN_SHELVE, file_name_temp, status)
    auto.SendKeys('{ESC}')
    time.sleep(0.2)

    return status

def sending_process(
        filename: dict,
        kakao_window: auto.WindowControl
) -> str:
    """
    1) 메인 창에서 학생 이름을 검색해 Enter 1회로 채팅 팝업을 연다.
    2) 막 뜬 채팅‑창의 **채팅 로그 Pane**(EVA_VH_ListControl_Dblclk) 기준
       하단 12%(또는80px 이상) 영역을 ROI 로 잡아 캡처한다.
    3) 템플릿 매칭 결과를 shelve DB 에 기록하고
       'success' / 'fail' / '전송 중' / 'unknown' 중 하나를 반환한다.
    """
    # ── 0. 카카오톡 실행 보장 ─────────────────────────────
    ensure_kakao_running()
    time.sleep(1.5)

    file_name_temp = filename["파일명"]
    student_name   = extract_student_name(file_name_temp)

    # ── 1. 메인 창에서 친구 검색 → 채팅 팝업 열기 ────────
    main_view = find_element_with_partial_name(kakao_window, "OnlineMainView")
    if not main_view:
        print("[ERR] OnlineMainView not found")
        return "unknown"

    move_cursor_to_top_left(main_view)
    click_by_offset(main_view, 60, 60)

    auto.SendKeys('{Ctrl}f');              time.sleep(0.2)
    auto.SendKeys(student_name, interval=0.01)
    auto.SendKeys('{ENTER}');              time.sleep(0.3)   # 팝업 생성

    #! 우선은 opencv 기능 없음
    # # ── 2. 팝업 창 및 채팅 로그 Pane 확보 ─────────────────
    # hwnd_fg  = auto.GetForegroundWindow()
    # chat_win = auto.WindowControl(handle=hwnd_fg)

    # chat_log = chat_win.Control(
    #     ClassName='EVA_VH_ListControl_Dblclk',
    #     AutomationId='100',
    #     searchDepth=3                      # 손자까지 탐색
    # )
    # if not chat_log.Exists(1000, 200):     # 1 s 폴링
    #     print("[ERR] chat list Pane not found")
    #     return "unknown"

    # # ── 2‑A. ROI 좌표 계산 (동적 margin) ────────────────
    # phys_rect = chat_log.BoundingRectangle          # 물리 px
    # l, t, r, b = ui_to_logical(phys_rect)           # DPI 보정

    # H = b - t                                       # Pane 높이
    # ROI_MARGIN = max(80, int(H * 0.12))             # 12 % 또는 80 px
    # roi_bounds = {
    #     "left":   l,
    #     "top":    b - ROI_MARGIN,
    #     "right":  r,
    #     "bottom": b
    # }
    # print("[DEBUG] ROI:", roi_bounds)

    # ── 3. 첨부 파일 전송 시퀀스 ────────────────────────
    auto.SendKeys('{Ctrl}t');   time.sleep(0.2)
    auto.SendKeys('{Ctrl}l');   time.sleep(0.2)
    auto.SendKeys(str(SHELVE_TEST_DIR), interval=0.01)
    auto.SendKeys('{ENTER}');   time.sleep(0.2)
    auto.SendKeys('{Alt}n');    time.sleep(0.2)
    auto.SendKeys(filename["파일명"], interval=0.01)
    auto.SendKeys('{Alt}o');    time.sleep(0.2)
    auto.SendKeys('{ENTER}');   time.sleep(0.2)

    #! opencv 기능 없음
    # # ── 4. ROI 캡처 & 템플릿 매칭 ───────────────────────
    # main_img  = tm.capture_screen_region(roi_bounds)
    # templates = tm.load_templates()
    # result    = tm.detect_status(main_img, templates)

    # ── 5. shelve 갱신 및 채팅창 닫기 ──────────────────
    update_file_status(MAIN_SHELVE, file_name_temp, result)
    auto.SendKeys('{ESC}');     time.sleep(0.2)

    return result



if __name__ == "__main__":
    ensure_kakao_running()
    print("카카오톡 실행 완료")
    chat_win = activate_chat_window("장운형A")
    print("chat_win:", chat_win)
    if chat_win is None:
        print("대화창을 찾지 못했습니다."); exit()

    # 2. chat_log 확보
    chat_log = chat_win.Control(
        ClassName='EVA_VH_ListControl_Dblclk',
        AutomationId='100',
        searchDepth=3
    )
    print("chat_log:", chat_log)
    if not chat_log.Exists(1000, 200):
        print("[ERR] chat list Pane not found"); exit()

    # 3. ROI 계산
    print("ROI 계산")
    phys_rect = chat_log.BoundingRectangle
    print("phys_rect:", phys_rect)
    l, t, r, b = ui_to_logical(phys_rect)
    H = b - t
    ROI_MARGIN = max(80, int(H * 0.12))
    roi_bounds = {"left": l, "top": b - ROI_MARGIN,
                  "right": r, "bottom": b}
    print("[DEBUG] ROI:", roi_bounds)

    # 4. 캡처 & 매칭
    main_img  = tm.capture_screen_region(roi_bounds)
    templates = tm.load_templates()
    result    = tm.detect_status(main_img, templates)
    print("[RESULT]", result)
