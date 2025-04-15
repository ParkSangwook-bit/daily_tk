from constants import MAIN_SHELVE
from settings import shelve, theWorld, time, auto, subprocess
# 순환 의존성 해결: extract_student_name 함수를 utils 모듈에서 가져옴
from utils import extract_student_name
from shelve_manager import update_file_status
import template_matching_opencv as tm

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
                # auto.SendKeys(r'..\shelve_test', interval=0.01)
                auto.SendKeys(r'C:\Git_clone\shelve_test', interval=0.01)
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
                # main_img = tm.load_main_image()
                # templates = tm.load_templates()
                # template_matching_result = tm.detect_status(main_img, templates)
                #! 여기서는 성공으로 가정
                template_matching_result = "성공"

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
def sending_process(filename: dict, kakao_window: auto.WindowControl):# -> Any | None | Literal['전송 중'] | Literal['unknown']:
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

                # 5. 채팅창에 포커스 맞추기(한번 더 이름 체크)
                #! 실제로는 채팅창 WindowControl 탐색 등을 추가
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
                # auto.SendKeys(r'..\shelve_test', interval=0.01)
                auto.SendKeys(r'C:\Git_clone\shelve_test', interval=0.01)
                time.sleep(0.2)
                auto.SendKeys('{ENTER}')
                time.sleep(0.2)

                # 파일 검색(ALT+N) / 열기(ALT+O)는
                #   Windows 공용 대화상자에서 동작할 수도 있고 아닐 수도 있으니
                #   실제 상황에 맞춰 조정 필요
                auto.SendKeys('{Alt}n')  # ALT+N
                time.sleep(0.2)
                #! filename을 문자열로서 입력하도록 수정 필요
                # file_name = filename["파일명"]
                auto.SendKeys(filename["파일명"], interval=0.05)
                #! 파일 열기 확정
                auto.SendKeys('{Alt}o')  # ALT+O
                time.sleep(0.2)

                # 8. 파일 전송 확인창 감지 후 상호작용(엔터)
                auto.SendKeys('{ENTER}')
                time.sleep(0.2)

                # 9. template matching(OpenCV) 실행 후 결과 확인
                main_img = tm.load_main_image()
                templates = tm.load_templates()
                template_matching_result = tm.detect_status(main_img, templates)
                
                time.sleep(0.5)
                #! 시간정지
                theWorld(100)

                # todo 10. 결과에 따른 shelve 파일 수정 (여기서는 dummy_shelve에 기록)
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


if __name__ == "__main__":
    pass