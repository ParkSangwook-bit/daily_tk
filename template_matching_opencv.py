from settings import cv2, time, np, pyautogui, Any, Path, os
from datetime import datetime
import constants

def get_roi_bounds(rect) -> dict[str, Any]:
    """
    BoundingRectangle을 기반으로 ROI 영역을 계산하여 반환
    """
    return {
        "left": rect.left,
        "top": rect.bottom - constants.ROI_OFFSET_BOTTOM,
        "right": rect.right,
        "bottom": rect.bottom
    }

def capture_and_save_roi(
        rect: Any,
        bounds_func=get_roi_bounds,
        save_root: Path = constants.ROI_SCREENSHOT_DIR,
        file_prefix: str = "roi",
        fmt: str = "%Y%m%d_%H%M%S",
) -> Path:
    now = datetime.now()
    ts = now.strftime(fmt)
    bounds = bounds_func(rect)
    x, y = bounds["left"], bounds["top"]
    w = bounds["right"] - bounds["left"]
    h = bounds["bottom"] - bounds["top"]

    screenshot = pyautogui.screenshot(region=(x, y, w, h))
    save_dir = save_root / now.strftime("%Y%m%d")
    os.makedirs(save_dir, exist_ok=True)
    file_name = f"{file_prefix}_{ts}.png"
    save_path = save_dir / file_name

    screenshot.save(save_path)
    print(f"[ROI] {save_path} ({w}x{h}) 저장 완료")
    return save_path

def load_image(image_path):
    try:
        image = cv2.imread(image_path)
        if image is None:
            raise FileNotFoundError(f"이미지를 로드하지 못했습니다: {image_path}")
        return image
    except Exception as e:
        raise FileNotFoundError(f"이미지 로딩 중 오류 발생: {image_path}, 오류: {e}")

def load_main_image():
    try:
        if not os.path.exists(constants.PATH_MAIN_IMAGE):
            msg = (f"메인 이미지 파일을 찾을 수 없습니다: {constants.PATH_MAIN_IMAGE}\n"
                   "templates 폴더가 비어있는지 확인하세요.\n"
                   "필요한 이미지 파일을 templates 폴더에 추가해주세요.")
            raise FileNotFoundError(msg)
        img = cv2.imread(constants.PATH_MAIN_IMAGE)
        if img is None:
            raise FileNotFoundError(f"메인 이미지 로딩 실패: {constants.PATH_MAIN_IMAGE}")
        return img
    except Exception as e:
        raise FileNotFoundError(f"메인 이미지 로딩 중 오류 발생: {e}")

def load_templates() -> dict[str, Any]:
    try:
        path_suc = get_appropriate_template_path()
        suc = cv2.imread(path_suc)
        fail = cv2.imread(constants.PATH_TEMPLATE_FAIL)
        if suc is None:
            raise FileNotFoundError(f"성공 템플릿 로드 실패: {path_suc}")
        if fail is None:
            raise FileNotFoundError(f"실패 템플릿 로드 실패: {constants.PATH_TEMPLATE_FAIL}")
        return {"성공": suc, "실패": fail}
    except Exception as e:
        raise Exception(f"템플릿 로딩 중 오류 발생: {e}")

def get_appropriate_template_path():
    screen_width, _ = pyautogui.size()
    if screen_width <= 1366:
        print(f"작은 화면 감지(너비: {screen_width}), 노트북 템플릿 사용")
        return constants.PATH_TEMPLATE_SUC_LAPTOP
    else:
        print(f"일반 화면 감지(너비: {screen_width}), 기본 템플릿 사용")
        return constants.PATH_TEMPLATE_SUC

def match_template(main_image, template,
                   max_attempts: int = constants.TM_MAX_ATTEMPTS,
                   threshold: float = constants.ROI_THRESHOLD,
                   log_queue=None):
    attempt = 0
    while attempt < max_attempts:
        res = cv2.matchTemplate(main_image, template, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, max_loc = cv2.minMaxLoc(res)
        msg = f"시도 {attempt+1}: 최대 유사도: {max_val:.4f}"
        if log_queue:
            log_queue.put(("log", msg))
        else:
            print(msg)
        if max_val >= threshold:
            success_msg = f"템플릿 매칭 성공! 유사도: {max_val:.4f}"
            if log_queue:
                log_queue.put(("log", success_msg))
            else:
                print(success_msg)
            return True, max_loc, template.shape[:2], max_val
        else:
            fail_msg = f"템플릿 매칭 실패. 최대 유사도: {max_val:.4f}"
            if log_queue:
                log_queue.put(("log", fail_msg))
            else:
                print(fail_msg)
            attempt += 1
            if attempt < max_attempts:
                time.sleep(2)
    end_msg = f"템플릿 매칭 {max_attempts}회 시도 후 실패."
    if log_queue:
        log_queue.put(("log", end_msg))
    else:
        print(end_msg)
    return False, None, None, max_val

def capture_screen_region(bounds):
    screenshot = pyautogui.screenshot(region=(
        bounds["left"],
        bounds["top"],
        bounds["right"] - bounds["left"],
        bounds["bottom"] - bounds["top"]
    ))
    return convert_pillow_to_opencv(screenshot)

def convert_pillow_to_opencv(image):
    np_image = np.array(image)
    return cv2.cvtColor(np_image, cv2.COLOR_RGB2BGR)

def detect_status(main_image, templates,
                  threshold: float = constants.ROI_THRESHOLD,
                  log_queue=None) -> str:
    """
    성공/실패 템플릿 모두를 먼저 시각화한 뒤, 매칭 결과에 따라 상태 반환
    """
    print("\n===== 템플릿 시각화 (디버그용) =====")
    for name, tmpl in templates.items():
        vis = visualize_template_matches(main_image, tmpl, threshold)
        cv2.imshow(f"{name} 매칭 시각화 (유사도≥{threshold})", vis)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    #! 이미지와 메세지는 두번 나오는게 맞음. 성공 탬플릿과 실패 탬플릿에 대한 각각의 결과
    print("\n===== 템플릿 매칭 디버그 정보 =====")
    print(f"- 템플릿 수: {len(templates)}개")
    for name, img in templates.items():
        print(f"  * '{name}': 크기={img.shape}, dtype={img.dtype}")
    print(f"- 대상 이미지: 크기={main_image.shape}, dtype={main_image.dtype}")
    print(f"- 임계값: {threshold}")
    print("====================================")

    for status_name, tmpl in templates.items():
        print(f"\n[템플릿 매칭 시도] '{status_name}'")
        matched, loc, size, sim = match_template(
            main_image, tmpl, threshold=threshold, log_queue=log_queue)
        print(f"- 결과: {'성공' if matched else '실패'}, 유사도: {sim:.4f}")
        if matched and loc is not None and size is not None:
            x, y = loc
            h, w = size
            print(f"- 위치: ({x}, {y}), 크기: ({w}×{h})")
            return status_name

    print("\n모든 매칭 실패 → '전송 중' 상태로 간주")
    return "전송 중"

def validate_paths() -> list[str]:
    issues = []
    paths = {
        "메인 이미지": constants.PATH_MAIN_IMAGE,
        "성공 템플릿": constants.PATH_TEMPLATE_SUC,
        "실패 템플릿": constants.PATH_TEMPLATE_FAIL
    }
    for name, path in paths.items():
        if not os.path.exists(path):
            issues.append(f"{name}: {path} (존재하지 않음)")
    return issues

def visualize_template_matches(main_image: np.ndarray,
                               template: np.ndarray,
                               threshold: float = constants.ROI_THRESHOLD) -> np.ndarray:
    """
    디버그용: 유사도가 threshold 이상인 위치를 그룹핑하고,
    그룹이 비어 있으면 최고 유사도 위치를 표시

    Parameters:
    -----------
    main_image : numpy.ndarray
        대상 BGR 이미지
    template : numpy.ndarray
        찾을 템플릿 이미지
    threshold : float
        최소 유사도 임계값

    Returns:
    --------
    numpy.ndarray
        박스가 그려진 이미지 복사본
    """
    # 1) 템플릿 매칭
    res = cv2.matchTemplate(main_image, template, cv2.TM_CCOEFF_NORMED)

    # 2) threshold 이상인 좌표 수집
    ys, xs = np.where(res >= threshold)
    h, w = template.shape[:2]

    # 3) [x, y, width, height] 포맷으로 사각형 리스트 생성
    rects = [[int(x), int(y), w, h] for x, y in zip(xs, ys)]

    # 4) 그룹핑 (단일 매칭도 허용하도록 groupThreshold=0)
    grouped, weights = cv2.groupRectangles(rects, groupThreshold=0, eps=0.5)
    print(f"[시각화] 유사도≥{threshold} 매칭 클러스터: {len(grouped)}개, weights={list(weights)}")

    # 5) 시각화: 복사본에 박스 그리기
    vis = main_image.copy()
    if len(grouped) > 0:
        for x, y, rw, rh in grouped:
            cv2.rectangle(vis, (x, y), (x + rw, y + rh), (0, 0, 255), 2)
    else:
        # fallback: 한 번이라도 매칭된 최고 유사도 위치만 표시
        _, max_val, _, max_loc = cv2.minMaxLoc(res)
        if max_val >= threshold:
            x, y = max_loc
            cv2.rectangle(vis, (x, y), (x + w, y + h), (0, 0, 255), 2)

    return vis


if __name__ == "__main__":
    try:
        issues = validate_paths()
        if issues:
            print("경로 문제:")
            for i in issues:
                print(" -", i)
            print("계속 시 오류 발생할 수 있습니다.")

        main_image = load_image(constants.PATH_MAIN_IMAGE)
        tpl_suc = load_image(get_appropriate_template_path())
        tpl_fail = load_image(constants.PATH_TEMPLATE_FAIL)

        print("\n[미리보기] 계속하려면 아무 키나 누르세요...")
        cv2.imshow("메인 이미지", main_image)
        cv2.imshow("성공 템플릿", tpl_suc)
        cv2.imshow("실패 템플릿", tpl_fail)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

        start = time.time()
        templates = {"성공": tpl_suc, "실패": tpl_fail}
        status = detect_status(main_image, templates)
        print(f"탐지된 상태: {status}")
        print(f"소요 시간: {time.time() - start:.4f}초")

    except Exception as e:
        print(f"실행 중 오류 발생: {e}")
    finally:
        cv2.destroyAllWindows()
