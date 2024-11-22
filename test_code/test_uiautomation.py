import uiautomation as auto
import subprocess
import time

def ensure_kakao_running():
    if is_kakao_running():
        print("카카오톡이 이미 실행 중입니다.")
    else:
        print("카카오톡이 실행되고 있지 않습니다. 카카오톡 실행 시도 . . .")
        launch_kakao()

def is_kakao_running():
    try:
        start_time = time.time()
        result = subprocess.run(['tasklist'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        end_time = time.time()
        print(f"tasklist 실행 시간: {end_time - start_time:.6f}초")

        if 'KakaoTalk.exe' in result.stdout:
            print("'KakaoTalk.exe' 프로세스를 감지했습니다.")
            return True
    except subprocess.SubprocessError as e:
        print(f"subprocess 실행 오류: {e}")
    print("Failed detecting 'KakaoTalk.exe' process")
    return False

def launch_kakao():
    kakao_path = r"C:\Program Files (x86)\Kakao\KakaoTalk\KakaoTalk.exe"
    try:
        subprocess.Popen([kakao_path], shell=False)
        print("카카오톡 프로세스 실행 완료")
    except FileNotFoundError as e:
        print(f"{kakao_path}에서 카카오톡을 찾을 수 없습니다. 경로를 확인해주세요.")
        print(f"error code: {e}")

def move_cursor_to_top_left(element):
    """
    UI 요소의 좌측 상단 (0,0) 위치로 커서를 이동하는 함수.
    Args:
    - element: uiautomation으로 탐지된 UI 요소
    """
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
    for child in parent_element.GetChildren():
        if partial_name in child.Name:
            return child
    return None

if __name__ == "__main__":
    ensure_kakao_running()
    kakao_window = auto.WindowControl(searchDepth=1, Name="카카오톡")

    if kakao_window.Exists(0, 0):
        main_view = find_element_with_partial_name(kakao_window, "OnlineMainView")
        if main_view:
            print(f"Found element with Name: {main_view.Name}")
            move_cursor_to_top_left(main_view)
        else:
            print("OnlineMainView not found.")
    else:
        print("KakaoTalk window not found.")
