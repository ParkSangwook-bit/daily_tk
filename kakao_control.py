from settings import shelve, time, auto, subprocess
from shelve_manager import extract_student_name

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


def dummy_process_func():
    ensure_kakao_running()
    time.sleep(2)
    kakao_window = activate_kakao_window()

    if kakao_window and kakao_window.Exists(0, 0):
        main_view = find_element_with_partial_name(kakao_window, "OnlineMainView")
        if main_view:
            rect, width, height = get_kakao_bounding_rect(main_view)
            if rect is not None:
                print(f"Found element with Name: {main_view.Name}")
                move_cursor_to_top_left(main_view)
                click_by_offset(main_view, 60, 60)

                # -----------------------------------------------------
                # 아래부터 TODO 구현 예시
                # -----------------------------------------------------
                # (가) shelve에서 "검색해야 할 친구" 목록을 가정적으로 불러온다고 치겠습니다.
                #     실제 구현 시 "daily_files_shelve" 등에서 "미전송" 상태인 파일들의
                #     "학부모" 이름을 꺼내오는 식으로 확장 가능합니다.
                
                #! 여기 아직 더미임
                dummy_shelve_path = 'dummy_friends_shelve'
                print("쉘브 불러왔음")
                # shelve 예시 생성 (처음 한 번만)
                with shelve.open(dummy_shelve_path) as db:
                    if 'search_names' not in db:
                        db['search_names'] = ['장운형']
                print("쉘브 생성 완료")
                
                with shelve.open(dummy_shelve_path) as db:
                    search_names = db['search_names']
                    print(f"검색해야 할 친구 목록: {search_names}")
                    
                # 이름 검색 루프
                for friend_name in search_names:
                    print("for문 진입")
                    print(f"\n--- 시작: 친구 '{friend_name}' 검색 테스트 ---")
                    
                    # 1. CTRL + F로 친구 검색창 열기
                    auto.SendKeys('{Ctrl}f')  # Ctrl + F
                    time.sleep(0.2)
                    print("검색창 열기")

                    # 2. 검색창에 특정 친구 이름 입력 후 엔터
                    auto.SendKeys(friend_name, interval=0.01)  # 글자 하나씩 입력
                    time.sleep(0.2)
                    auto.SendKeys('{ENTER}')
                    time.sleep(0.2)

                    # 3. 검색 결과에서 친구 선택 (UI 구조에 따라 Tab/Down/Enter 등 필요)
                    #    카카오톡 버전에 따라 다를 수 있습니다. 아래는 예시 시나리오
                    # auto.SendKeys('{DOWN}')
                    # time.sleep(0.2)
                    # auto.SendKeys('{ENTER}')
                    # time.sleep(0.2)

                    # 4. 친구 채팅창으로 열기 (이미 Enter로 열렸다고 가정)
                    #    필요하다면 한번 더 Enter / Tab 등을 전송
                    #    여기서는 생략

                    # 5. 채팅창에 포커스 맞추기(한번 더 이름 체크)
                    #    실제로는 채팅창 WindowControl 탐색 등을 추가로 할 수 있으나,
                    #    여기서는 간단히 로그만
                    print(f"채팅창 '{friend_name}' 포커스 맞춘 것으로 가정")
                    break

                    # 6. CTRL + T로 첨부 파일 열기
                    auto.SendKeys('{Ctrl}t')
                    time.sleep(0.2)

                    # 7. 디렉토리 지정: CTRL + L, 파일 선택 후 열기 (ALT + N, ALT + O)
                    auto.SendKeys('{Ctrl}l')
                    time.sleep(0.2)
                    # 디렉토리 경로 예시 입력 (가상)
                    auto.SendKeys(r'C:\Users\qkrtk\Desktop\shelve_test', interval=0.01)
                    time.sleep(0.2)
                    auto.SendKeys('{ENTER}')
                    time.sleep(0.2)

                    # 파일 검색(ALT+N) / 열기(ALT+O)는
                    #   Windows 공용 대화상자에서 동작할 수도 있고 아닐 수도 있으니
                    #   실제 상황에 맞춰 조정 필요
                    auto.SendKeys('{Alt}n')  # ALT+N
                    time.sleep(0.2)
                    auto.SendKeys('icon_14.png', interval=0.05)                    
                    # auto.SendKeys('{Alt}o')  # ALT+O
                    auto.SendKeys('{esc}')  # ESC
                    time.sleep(0.2)

                    # 8. 파일 전송 확인창 감지 후 상호작용(엔터)
                    auto.SendKeys('{ENTER}')
                    time.sleep(0.2)

                    # 9. opencv 실행 후 결과 확인 (여기서는 실제로는 안 함, 모의)
                    print("(모의) OpenCV로 전송 성공/실패 확인...")
                    time.sleep(0.5)

                    # 10. 결과에 따른 shelve 파일 수정 (여기서는 dummy_shelve에 기록)
                    with shelve.open(dummy_shelve_path, writeback=True) as db:
                        # 임의로 "성공"이라고 저장
                        # 실제로는 OpenCV 결과에 따라 "성공" or "실패" 처리를 해야 함
                        print(f"파일 전송 결과 -> '성공' 기록 가정")
                        # dummy 로직이라 key도 'friend_name'으로 예시
                        db[friend_name] = "성공"

                    # 11. 채팅창 닫기(esc)
                    auto.SendKeys('{ESC}')
                    time.sleep(0.2)

                    # 12. 반복
                    #     -> for friend_name in search_names: 로 계속 진행
                    
                    print(f"--- 완료: 친구 '{friend_name}' 검색 + 모의 첨부 테스트 ---")

                print("모든 dummy 친구 검색 및 첨부 파일 모의 테스트 완료.")

        else:
            print("OnlineMainView not found.")
    else:
        print("KakaoTalk window not found or not activated.")

#? 파일이름이랑 카카오 윈도우 전달 받아서
#? app() -> send_files_worker() -> sending_process(filename, kakao_window) -> 다시 send_files_worker()로 복귀 
def sending_process(filename: dict, kakao_window: auto.WindowControl):
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

                '''
                여기 필요한 것
                - shelve에서 미전송 파일들의 file_info 가져오기
                - 거기서 학생 이름만 추출하기
                - 학생 이름으로 구성된 전송 리스트 구성
                '''
                
                print(f"\n--- 시작: 친구 '{student_name}' 검색 테스트 ---")
                
                # 1. CTRL + F로 친구 검색창 열기
                auto.SendKeys('{Ctrl}f')  # Ctrl + F
                time.sleep(0.2)
                print("검색창 열기")

                # 2. 검색창에 특정 친구 이름 입력 후 엔터
                auto.SendKeys(student_name, interval=0.01)  # 글자 하나씩 입력
                time.sleep(0.2)
                auto.SendKeys('{ENTER}')
                time.sleep(0.2)

                # 3. 검색 결과에서 친구 선택 (UI 구조에 따라 Tab/Down/Enter 등 필요)
                # auto.SendKeys('{DOWN}')
                time.sleep(0.2)
                auto.SendKeys('{ENTER}')
                time.sleep(0.2)

                # 4. 친구 채팅창으로 열기 (이미 Enter로 열렸다고 가정)
                #    필요하다면 한번 더 Enter / Tab 등을 전송
                #    여기서는 생략

                # 5. 채팅창에 포커스 맞추기(한번 더 이름 체크)
                #    실제로는 채팅창 WindowControl 탐색 등을 추가로 할 수 있으나,
                #    여기서는 간단히 로그만
                print(f"채팅창 '{student_name}' 포커스 맞춘 것으로 가정")

                # 6. CTRL + T로 첨부 파일 열기
                auto.SendKeys('{Ctrl}t')
                time.sleep(0.2)

                # 7. 디렉토리 지정: CTRL + L, 파일 선택 후 열기 (ALT + N, ALT + O)
                auto.SendKeys('{Ctrl}l')
                time.sleep(0.2)
                # 디렉토리 경로 예시 입력 (가상)
                #! 디렉토리 못찾는 경우 대비해서 예외처리 필요
                #? 파일첨부 창에서의 디렉터리에서도 상대 경로 사용 가능
                #? ..\sehlve_test 이런식으로 가능(범용성 증가)
                auto.SendKeys(r'..\shelve_test', interval=0.01)
                time.sleep(0.2)
                auto.SendKeys('{ENTER}')
                time.sleep(0.2)

                # 파일 검색(ALT+N) / 열기(ALT+O)는
                #   Windows 공용 대화상자에서 동작할 수도 있고 아닐 수도 있으니
                #   실제 상황에 맞춰 조정 필요
                auto.SendKeys('{Alt}n')  # ALT+N
                time.sleep(0.2)
                #! filename을 문자열로서 입력하도록 수정 필요
                file_name = filename["파일명"]
                auto.SendKeys(filename["파일명"], interval=0.05)
                #! 파일 열기 확정
                auto.SendKeys('{Alt}o')  # ALT+O
                time.sleep(0.2)

                # 8. 파일 전송 확인창 감지 후 상호작용(엔터)
                auto.SendKeys('{ENTER}')
                time.sleep(0.2)

                # 9. opencv 실행 후 결과 확인 (여기서는 실제로는 안 함, 모의)
                print("(모의) OpenCV로 전송 성공/실패 확인...")
                time.sleep(0.5)

                # todo 10. 결과에 따른 shelve 파일 수정 (여기서는 dummy_shelve에 기록)

                # 11. 채팅창 닫기(esc)
                auto.SendKeys('{ESC}')
                time.sleep(0.2)

                print(f"--- 완료: 친구 '{student_name}' 검색 + 모의 첨부 테스트 ---")

                print("모든 dummy 친구 검색 및 첨부 파일 모의 테스트 완료.")

        else:
            print("OnlineMainView not found.")
    else:
        print("KakaoTalk window not found or not activated.")


if __name__ == "__main__":
    dummy_process_func()
