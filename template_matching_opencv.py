from settings import cv2, time, np, pyautogui, Any
import constants
import os

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
    """
    개선: 이미지 로드 시 상세한 오류 메시지를 제공하며 예외 처리
    """
    try:
        image = cv2.imread(image_path)
        if image is None:
            raise FileNotFoundError(f"이미지를 로드하지 못했습니다: {image_path}")
        return image
    except Exception as e:
        # 파일 경로와 함께 오류 상세 정보 제공
        raise FileNotFoundError(f"이미지 로딩 중 오류 발생: {image_path}, 오류: {str(e)}")

def load_main_image():
    """
    constants.PATH_MAIN_IMAGE를 읽고 cv2.imread() → ndarray 반환
    개선: 더 명확한 오류 메시지 제공 및 복구 방법 제안
    """
    try:
        # 경로가 유효한지 먼저 확인
        if not os.path.exists(constants.PATH_MAIN_IMAGE):
            error_msg = f"메인 이미지 파일을 찾을 수 없습니다: {constants.PATH_MAIN_IMAGE}\n"
            error_msg += f"templates 폴더가 비어있는지 확인하세요.\n"
            error_msg += f"필요한 이미지 파일을 templates 폴더에 추가해주세요."
            raise FileNotFoundError(error_msg)
            
        img = cv2.imread(constants.PATH_MAIN_IMAGE)
        if img is None:
            raise FileNotFoundError(f"메인 이미지 로딩 실패: {constants.PATH_MAIN_IMAGE}")
        return img
    except Exception as e:
        # 오류 발생 시 자세한 정보 제공
        detailed_error = f"메인 이미지 로딩 중 오류 발생: {constants.PATH_MAIN_IMAGE}\n"
        detailed_error += f"오류 내용: {str(e)}"
        raise FileNotFoundError(detailed_error)

def load_templates() -> dict[str, Any]:
    """
    성능/확장성을 위해, 각 템플릿 이미지 경로를 constants.py에 저장해두고
    여기서 로드하여 딕셔너리로 반환
    개선: 템플릿 자동 선택 로직 추가
    """
    try:
        # 자동 템플릿 선택 로직
        appropriate_template_path = get_appropriate_template_path()
        
        suc = cv2.imread(appropriate_template_path)
        fail = cv2.imread(constants.PATH_TEMPLATE_FAIL)
        
        # 각 이미지가 None이면 예외처리
        if suc is None:
            raise FileNotFoundError(f"성공 템플릿 로드 실패: {appropriate_template_path}")
        if fail is None:
            raise FileNotFoundError(f"실패 템플릿 로드 실패: {constants.PATH_TEMPLATE_FAIL}")

        return {
            "성공": suc,
            "실패": fail,
        }
    except Exception as e:
        raise Exception(f"템플릿 로딩 중 오류 발생: {str(e)}")

def get_appropriate_template_path():
    """
    개선: 화면 해상도와 배율에 따라 적절한 템플릿 경로 반환
    """
    screen_width, screen_height = pyautogui.size()
    
    # 윈도우 배율 감지 (예: 125%, 150%, 200%)
    # 간단한 예시 - 실제로는 OS별 특화된 방법 사용 필요
    if screen_width <= 1366:  # 노트북 등 작은 화면
        print(f"작은 화면 감지(너비: {screen_width}), 노트북 템플릿 사용")
        return constants.PATH_TEMPLATE_SUC_LAPTOP
    else:  # 일반적인 데스크탑 화면
        print(f"일반 화면 감지(너비: {screen_width}), 기본 템플릿 사용")
        return constants.PATH_TEMPLATE_SUC

def match_template(main_image, template, max_attempts=constants.TM_MAX_ATTEMPTS, threshold=constants.ROI_THRESHOLD, log_queue=None):
    """
    템플릿 매칭 함수
    개선: log_queue 파라미터 추가하여 로깅 체계 개선
    """
    attempt = 0
    while attempt < max_attempts:   # 3회 시도
        # 템플릿 매칭 수행
        result = cv2.matchTemplate(main_image, template, cv2.TM_CCOEFF_NORMED)

        # 유사도 및 위치 찾기
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

        # 로그 출력 방식 개선
        log_message = f"시도 {attempt + 1}: 최대 유사도: {max_val:.4f}"
        if log_queue:
            log_queue.put(("log", log_message))
        else:
            print(log_message)
            
        # 임계값에 따라 결과 반환
        if max_val >= threshold:
            success_msg = f"템플릿 매칭 성공! 유사도: {max_val:.4f}"
            if log_queue:
                log_queue.put(("log", success_msg))
            else:
                print(success_msg)
            return True, max_loc, template.shape[:2]  # 성공 시 위치와 템플릿 크기 반환
        else:
            fail_msg = f"템플릿 매칭 실패. 유사도를 확인하세요. 최대 유사도: {max_val:.4f}"
            if log_queue:
                log_queue.put(("log", fail_msg))
            else:
                print(fail_msg)
            attempt += 1
            if attempt < max_attempts:
                time.sleep(2)  # 2초 대기

    failure_msg = f"템플릿 매칭 {max_attempts}회 시도 후 실패."
    if log_queue:
        log_queue.put(("log", failure_msg))
    else:
        print(failure_msg)
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

def draw_rectangle(image, top_left, bottom_right):
    """매칭된 영역 표시"""
    #! 디버그 용 추후에 제거
    # TODO 나중에 오류를 일으키는 케이스를 위해서 사용될 수 있도록 
    cv2.rectangle(image, top_left, bottom_right, (0, 255, 0), 2)
    cv2.imshow('Matched Result', image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

def detect_status(main_image, templates, threshold=constants.ROI_THRESHOLD, log_queue=None):
    """
    성공, 실패, 전송 중 상태를 탐지
    개선: log_queue 파라미터 추가하여 로깅 체계 개선
    """
    status = "unknown"
    try:
        detected = False  # 성공 또는 실패 탐지 여부
        for status_name, template in templates.items():
            matched, top_left, size = match_template(main_image, template, log_queue=log_queue)
            if matched:
                detected = True
                if size is not None:
                    h, w = size
                    if top_left is not None:
                        bottom_right = (top_left[0] + w, top_left[1] + h)
                        
                        # 로그 메시지 개선
                        detect_msg = f"{status_name} 상태 탐지됨."
                        if log_queue:
                            log_queue.put(("log", detect_msg))
                        else:
                            print(detect_msg)
                        return status_name  # 상태 반환
        
        if not detected:
            # 로그 메시지 개선
            no_detect_msg = "성공 또는 실패 상태를 감지하지 못했습니다. '전송 중' 상태로 간주합니다."
            if log_queue:
                log_queue.put(("log", no_detect_msg))
            else:
                print(no_detect_msg)
            return "전송 중"
        
        return status
    except Exception as e:
        # 예외처리 개선
        error_msg = f"상태 탐지 중 오류 발생: {e}"
        if log_queue:
            log_queue.put(("log", error_msg))
        else:
            print(error_msg)
        return status

# 초기화 시 경로 유효성 검사 함수
def validate_paths():
    """
    개선: 필요한 경로가 유효한지 검사하고 문제 발견 시 경고
    """
    paths_to_check = {
        "메인 이미지": constants.PATH_MAIN_IMAGE,
        "성공 템플릿": constants.PATH_TEMPLATE_SUC,
        "실패 템플릿": constants.PATH_TEMPLATE_FAIL
    }
    
    issues = []
    
    for name, path in paths_to_check.items():
        if not os.path.exists(path):
            issues.append(f"{name}: {path} (경로를 찾을 수 없음)")
    
    return issues

if __name__ == "__main__":
    try:
        # 경로 유효성 검사
        path_issues = validate_paths()
        if path_issues:
            print("주의: 다음 경로에 문제가 있습니다:")
            for issue in path_issues:
                print(f"- {issue}")
            print("계속 진행하면 오류가 발생할 수 있습니다.")
        
        # 메인 이미지 및 템플릿 로드
        main_image = load_image(constants.PATH_MAIN_IMAGE)
        template_suc = load_image(get_appropriate_template_path())
        template_fail = load_image(constants.PATH_TEMPLATE_FAIL)

        # 탐지 진행
        start = time.time()
        templates = {
            "성공": template_suc,
            "실패": template_fail
        }
        detected_status = detect_status(main_image, templates)
        print(f"탐지된 상태: {detected_status}")
        end = time.time()
        print(f"소요 시간: {end - start:.5}초")

    except Exception as e:
        print(f"프로그램 실행 중 오류 발생: {e}")
    finally:
        print("프로그램 종료.")
