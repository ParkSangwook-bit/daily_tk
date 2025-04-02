from settings import cv2, time, np, pyautogui, Any
import constants

def get_roi_bounds(rect):# -> dict[str, Any]:
    """
    BoundingRectangle을 기반으로 ROI 영역을 계산하여 반환
    """
    return {
        "left": rect.left,
        "top": rect.bottom - constants.ROI_OFFSET_BOTTOM,
        "right": rect.right,
        "bottom": rect.bottom
    }

def load_image(image_path):
    """이미지 로드 및 에러 핸들링"""

    image = cv2.imread(image_path)
    if image is None:
        raise FileNotFoundError(f"이미지를 로드하지 못했습니다: {image_path}")
    return image

def load_main_image():
    """
    constants.PATH_MAIN_IMAGE를 읽고 cv2.imread() → ndarray 반환
    """
    img = cv2.imread(constants.PATH_MAIN_IMAGE)
    if img is None:
        # raise FileNotFoundError("메인 이미지 로딩 실패: {constants.PATH_MAIN_IMAGE}")
        raise FileNotFoundError("메인 이미지 로딩 실패: PATH_MAIN_IMAGE")
    return img

def load_templates() -> dict[str, Any]:
    """
    성능/확장성을 위해, 각 템플릿 이미지 경로를 constants.py에 저장해두고
    여기서 로드하여 딕셔너리로 반환
    """
    suc = cv2.imread(constants.PATH_TEMPLATE_SUC)
    fail = cv2.imread(constants.PATH_TEMPLATE_FAIL)
    # sending = cv2.imread(constants.PATH_TEMPLATE_SENDING)

    # 각 이미지가 None이면 예외처리
    if suc is None:
        raise FileNotFoundError(f"성공 템플릿 로드 실패: {constants.PATH_TEMPLATE_SUC}")
    if fail is None:
        raise FileNotFoundError(f"실패 템플릿 로드 실패: {constants.PATH_TEMPLATE_FAIL}")

    return {
        "성공": suc,
        "실패": fail,
        # "전송중": sending
    }

def match_template(main_image, template, max_attempts=constants.TM_MAX_ATTEMPTS, threshold=constants.ROI_THRESHOLD):
    """템플릿 매칭 함수"""
    """
    params:
        main_image: 메인 이미지,
        template: 템플릿 이미지,
        threshold: 유사도 임계값,
        max_attempts: 최대 시도 횟수
    """

    attempt = 0
    while attempt < max_attempts:   # 3회 시도
        # print(f"템플릿 매칭 시도 {attempt + 1}회째...")
        result = cv2.matchTemplate(main_image, template, cv2.TM_CCOEFF_NORMED)

        # 유사도 및 위치 찾기
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

        # 디버깅 정보 출력
        #! log queue에 출력할 수 있도록 수정 필요(당연히 디버그 정보는 제거)
        print(f"시도 {attempt + 1}: 최소값:", min_val, "최대값:", max_val)
        print("최소값 위치:", min_loc, "최대값 위치:", max_loc)

        # 임계값에 따라 결과 반환
        if max_val >= threshold:
            print(f"템플릿 매칭 성공! 유사도: {max_val}")
            return True, max_loc, template.shape[:2]  # 성공 시 위치와 템플릿 크기 반환
        else:
            print(f"템플릿 매칭 실패. 유사도를 확인하세요. 최대 유사도: {max_val}")
            attempt += 1
            if attempt < max_attempts:
                time.sleep(2)  # 2초 대기

    print("템플릿 매칭 3회 시도 후 실패.")
    return False, None, None

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

def convert_pillow_to_opencv(image):
    """
    Pillow 이미지를 OpenCV에서 사용할 수 있는 NumPy 배열로 변환.
    """
    # Pillow 이미지를 NumPy 배열로 변환
    np_image = np.array(image)
    # OpenCV는 BGR 순서를 사용하므로 RGB -> BGR로 변환
    opencv_image = cv2.cvtColor(np_image, cv2.COLOR_RGB2BGR)
    return opencv_image

'''
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
'''

def draw_rectangle(image, top_left, bottom_right):
    """매칭된 영역 표시"""
    #! 디버그 용 추후에 제거
    # TODO 나중에 오류를 일으키는 케이스를 위해서 사용될 수 있도록 
    cv2.rectangle(image, top_left, bottom_right, (0, 255, 0), 2)
    cv2.imshow('Matched Result', image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

def detect_status(main_image, templates, threshold=constants.ROI_THRESHOLD):
    """성공, 실패, 전송 중 상태를 탐지"""
    status = "unknown"
    try:
        detected = False  # 성공 또는 실패 탐지 여부
        for status_name, template in templates.items():
            matched, top_left, size = match_template(main_image, template)
            if matched:
                detected = True
                if size is not None:
                    h, w = size
                    if top_left is not None:
                        bottom_right = (top_left[0] + w, top_left[1] + h)
                        print(f"{status_name} 상태 탐지됨.")    #! log queue에 출력할 수 있도록 수정 필요
                        # draw_rectangle(main_image, top_left, bottom_right)
                        return status_name  # 상태 반환
        
        if not detected:
            print("성공 또는 실패 상태를 감지하지 못했습니다. '전송 중' 상태로 간주합니다.")
            return "전송 중"
        
        return status
    except Exception as e:
        print(f"오류 발생: {e}")
        return status

if __name__ == "__main__":
    try:
        # 메인 이미지 및 템플릿 로드
        main_image = load_image(constants.PATH_MAIN_IMAGE)
        template_suc = load_image(constants.PATH_TEMPLATE_SUC)
        template_fail = load_image(constants.PATH_TEMPLATE_FAIL)
        # template_sending = load_image(constants.PATH_TEMPLATE_SENDING)

        # 탐지 진행
        start = time.time()
        detected_status = detect_status(main_image, constants.TM_TEMPLATES)
        print(f"탐지된 상태: {detected_status}")
        end = time.time()
        print(f"소요 시간: {end - start:.5}초")

    finally:
        print("프로그램 종료.")
