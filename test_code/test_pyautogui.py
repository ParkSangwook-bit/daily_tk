from settings import time, pyautogui, subprocess, Any
import constants
import uiautomation as uia

from test_template_matching_opencv import *

def is_kakao_running():
    result = subprocess.run(['tasklist', '/fi', 'IMAGENAME eq KakaoTalk.exe'],
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if 'KakaoTalk.exe' in result.stdout:
        print("'KakaoTalk.exe' 프로세스를 감지했습니다.")
        return True
    print("Failed detecting 'KakaoTalk.exe' process")
    return False

def launch_kakao():
    kakao_path = constants.KAKAOTALK_INSTALL_PATH
    try:
        subprocess.Popen([kakao_path], shell=False)
        print("카카오톡 프로세스 실행 완료")
        # 카카오톡 실행 후 UI가 준비될 때까지 잠시 대기
        time.sleep(3)
    except FileNotFoundError as e:
        print(f"{kakao_path}에서 카카오톡을 찾을 수 없습니다. 경로를 확인해주세요.")
        print(f"error code: {e}")

def ensure_kakao_running():
    if is_kakao_running():
        print("카카오톡이 이미 실행 중입니다.")
    else:
        print("카카오톡이 실행되고 있지 않습니다. 카카오톡 실행 시도 . . .")
        launch_kakao()

# 채팅창 윈도우는 PaneControl 속성
def activate_kakao_window():
    kakao_window = uia.PaneControl(searchDepth=1, Name="장운형")
    if kakao_window.Exists(0, 0):
        kakao_window.SetActive()
        kakao_window.SetFocus()
        print("KakaoTalk window activated.")
        return kakao_window
    else:
        print("KakaoTalk window not found.")
        return None

# 부분 이름으로 요소 찾기
def find_element_with_partial_name(parent_element, partial_name):
    children = parent_element.GetChildren()
    print(f"Found {len(children)} children under '{parent_element.Name}'")
    for child in children:
        print(f"Checking element: {child.Name}")
        if partial_name in child.Name:
            return child
    return None

# AutomationId로 요소 찾기
def find_element_by_automation_id(parent_element, automation_id):
    """
    특정 parent_element의 자식들 중 AutomationId로 요소를 찾는 함수
    """
    children = parent_element.GetChildren()
    print(f"Searching for AutomationId '{automation_id}' among {len(children)} children.")
    
    for child in children:
        print(f"Checking child: Name='{child.Name}', AutomationId='{child.AutomationId}'")
        if child.AutomationId == automation_id:
            print(f"Found element with AutomationId '{automation_id}': Name='{child.Name}', ClassName='{child.ClassName}'")
            return child
    
    print(f"No element found with AutomationId '{automation_id}'.")
    return None

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

def capture_screen_region(bounds):
    """
    특정 BoundingRectangle 범위의 화면을 캡처하고 이미지 객체 반환
    """
    screenshot = pyautogui.screenshot(region=(
        bounds["left"],
        bounds["top"],
        bounds["right"] - bounds["left"],
        bounds["bottom"] - bounds["top"]
    ))
    return convert_pillow_to_opencv(screenshot)

def save_image(image, output_file):
    """
    캡처된 이미지를 로컬 파일로 저장
    """
    image.save(output_file)
    print(f"Screenshot saved to {output_file}")

if __name__ == "__main__":
    #! 시작 시간 측정
    start = time.time()

    template_suc_path = r'C:\\Users\\qkrtk\\Desktop\\screenshot\\opencv_test\\sample_am_kor_200per.png'
    template_fail_path = r'C:\\Users\\qkrtk\\Desktop\\screenshot\\opencv_test\\sample_template_aggresive2.png'
    # template_sending_path = r'C:\\Users\\qkrtk\\Desktop\\screenshot\\opencv_test\\sample_am_kor_200per.png'

    template_suc = load_image(template_suc_path)
    template_fail = load_image(template_fail_path)

    # 탐지 진행
    templates = {
        "성공": template_suc,   # 약 0.003초(대기시간 미포함)
        "실패": template_fail,  # 약 4초(대기시간 포함)
        # "전송 중": template_sending   # 약 8.02초(대기시간 포함)
    }

    ensure_kakao_running()
    time.sleep(1)
    kakao_window = activate_kakao_window()

    try:
        if kakao_window and kakao_window.Exists(0, 0):
            main_view = find_element_by_automation_id(kakao_window, "100")
            if main_view:
                rect, width, height = get_kakao_bounding_rect(main_view)
                if rect is not None:

                    target_bounds = {
                        "left": rect.left,
                        "top": rect.bottom - 100,
                        "right": rect.right,
                        "bottom": rect.bottom
                    }
                    
                    roi_result = capture_screen_region(target_bounds)
                    # save_image(roi_result, "kakao_main_view.png")
                    detected_status = detect_status(roi_result, templates)
                    print(f"탐지된 상태: {detected_status}")
                    #! 종료 시간 측정
                    end = time.time()
                    print(f"소요 시간: {end - start:.5}초")
    except Exception as e:
        print(f"An error occurred: {e}")