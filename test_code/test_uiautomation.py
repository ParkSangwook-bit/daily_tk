import uiautomation as auto
import subprocess
import time

def is_kakao_running():
    # KakaoTalk.exe만 필터링하여 검색
    result = subprocess.run(['tasklist', '/fi', 'IMAGENAME eq KakaoTalk.exe'],
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if 'KakaoTalk.exe' in result.stdout:
        print("'KakaoTalk.exe' 프로세스를 감지했습니다.")
        return True
    print("Failed detecting 'KakaoTalk.exe' process")
    return False

def ensure_kakao_running():
    if is_kakao_running():
        print("카카오톡이 이미 실행 중입니다.")
    else:
        print("카카오톡이 실행되고 있지 않습니다. 카카오톡 실행 시도 . . .")
        launch_kakao()

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

def move_cursor_to_top_left(element):
    """
    UI 요소의 좌측 상단 (0,0) 위치로 커서를 이동하는 함수.
    Args:
    - element: uiautomation으로 탐지된 UI 요소
    """
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

def find_element_with_partial_name(parent_element, partial_name):
    """
    특정 이름(또는 텍스트)을 포함하는 UI 요소를 탐지.
    Args:
    - parent_element: 검색을 시작할 부모 UI 요소
    - partial_name: 이름에 포함될 문자열 (예: "OnlineMainView")
    Returns:
    - 탐지된 UI 요소 객체 또는 None
    """
    children = parent_element.GetChildren()
    print(f"Found {len(children)} children under '{parent_element.Name}'")
    for child in children:
        print(f"Checking element: {child.Name}")
        if partial_name in child.Name:
            return child
    return None

def get_kakao_bounding_rect(element):
    '''
    카카오톡 메인 뷰의 BoundingRectangle 정보를 출력하는 함수
    '''
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

def click_by_offset(element, offset_x, offset_y):
    """
    요소의 (0,0) 기준으로 offset_x, offset_y 픽셀 떨어진 지점을 비율로 환산 후 클릭하는 함수.
    """
    if element is None or not element.Exists(0, 0):
        print("Element not found or invalid.")
        return
    rect = element.BoundingRectangle
    width = rect.right - rect.left
    height = rect.bottom - rect.top

    # 비율 계산
    x_ratio = offset_x / width
    y_ratio = offset_y / height

    # 실제 좌표 계산
    click_x = rect.left + (width * x_ratio)
    click_y = rect.top + (height * y_ratio)

    # 커서 이동 및 클릭
    auto.MoveTo(int(click_x), int(click_y))
    auto.Click(int(click_x), int(click_y))
    print(f"Clicked at offset ({offset_x}, {offset_y}) which is ratio ({x_ratio:.3f}, {y_ratio:.3f})")


if __name__ == "__main__":
    ensure_kakao_running()

    # 카카오톡을 실행하거나 이미 실행 중인 경우라면, 잠시 대기 후 활성화
    time.sleep(2)
    kakao_window = activate_kakao_window()

    if kakao_window and kakao_window.Exists(0, 0):
        main_view = find_element_with_partial_name(kakao_window, "OnlineMainView")
        if main_view:
            rect, width, height = get_kakao_bounding_rect(main_view)
            if rect is not None:
                print(f"Found element with Name: {main_view.Name}")
                # 먼저 top-left로 커서 이동 (디버깅용)
                move_cursor_to_top_left(main_view)

                # 예: bounding rect 기반으로 (0,0)에서 60px, 60px 떨어진 지점 클릭
                click_by_offset(main_view, 60, 60)

                """
                TODO
                1. CTRL + F로 친구 검색창 열기{키보드 입력}
                2. 검색창에 특정 친구 이름 입력 후 엔터{키보드 입력}
                3. 검색 결과에서 친구 선택{키보드 입력}
                4. 친구 채팅창으로 열기{키보드 입력}
                5. 채팅창에 포커스 맞추기{한번 더 이름 체크}
                6. CTRL + T로 첨부 파일 열기{키보드 입력}
                7. 디렉토리 지정{CTRL + L}, 파일 선택 후 열기{ALT + N, ALT + O}
                8. 파일 전송 확인창 감지 후 상호작용(엔터){키보드 입력}
                9. opencv실행 후 결과 확인
                10. 결과에 따른 shelve 파일 수정
                11. 채팅창 닫기{esc}
                12. 반복{포커스 다시 카카오톡 메인 클라이언트로}

                """ 
        else:
            print("OnlineMainView not found.")
    else:
        print("KakaoTalk window not found or not activated.")