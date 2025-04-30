# Description: Constants used in the project
from pathlib import Path
import os
import json
import sys
import cv2
import numpy as np

# 프로젝트 루트 경로 설정
BASE_DIR = Path(__file__).parent
TEMPLATES_DIR = BASE_DIR / "templates"  # 템플릿 이미지 폴더
DATA_DIR = BASE_DIR / "data"  # 데이터 저장 폴더
CONFIG_DIR = BASE_DIR / "config"  # 설정 파일 저장 폴더 추가
ROI_SCREENSHOT_DIR = BASE_DIR / "roi_screenshot"  # ROI 스크린샷 저장 폴더 추가
SHELVE_TEST_DIR = BASE_DIR.parent / "shelve_test"  # BASE_DIR의 상위 폴더에 있는 shelve_test 폴더

# 필요한 디렉토리 자동 생성
TEMPLATES_DIR.mkdir(exist_ok=True)
DATA_DIR.mkdir(exist_ok=True)
CONFIG_DIR.mkdir(exist_ok=True)
ROI_SCREENSHOT_DIR.mkdir(exist_ok=True)  # ROI 스크린샷 폴더 생성

# 이미지 템플릿 경로 (상대 경로로 변환)
PATH_MAIN_IMAGE = str(TEMPLATES_DIR / "sample_success_am_kor.png")
PATH_TEMPLATE_SUC = str(TEMPLATES_DIR / "sample_am_kor_200per.png")
PATH_TEMPLATE_FAIL = str(TEMPLATES_DIR / "sample_template_aggresive2.png")

# for laptop
PATH_TEMPLATE_SUC_LAPTOP = str(TEMPLATES_DIR / "sample_pm_kor_125per.png")

# 사용자 설정 파일 경로 (JSON 형식)
USER_CONFIG_PATH = CONFIG_DIR / "user_settings.json"

# 기본 사용자 설정
DEFAULT_USER_SETTINGS = {
    "kakao_install_path": r"C:\Program Files (x86)\Kakao\KakaoTalk\KakaoTalk.exe",
    "file_directory": str(BASE_DIR / "shelve_test"),
    "theme": "dark"
}

# 사용자 설정 로드 또는 생성
def load_user_settings():
    """
    개선: 사용자 설정 파일을 로드하거나, 없으면 기본값으로 생성
    """
    if USER_CONFIG_PATH.exists():
        try:
            with open(USER_CONFIG_PATH, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"설정 파일 로드 중 오류: {e}, 기본 설정을 사용합니다.")
            return DEFAULT_USER_SETTINGS
    else:
        # 설정 파일이 없으면 기본값으로 생성
        save_user_settings(DEFAULT_USER_SETTINGS)
        return DEFAULT_USER_SETTINGS

# 사용자 설정 저장
def save_user_settings(settings):
    """
    개선: 사용자 설정을 JSON 파일로 저장
    """
    try:
        with open(USER_CONFIG_PATH, 'w', encoding='utf-8') as f:
            json.dump(settings, f, ensure_ascii=False, indent=4)
    except Exception as e:
        print(f"설정 파일 저장 중 오류: {e}")

# 사용자 설정 로드
USER_SETTINGS = load_user_settings()

# Constants
TM_MAX_ATTEMPTS = 3  # Template Matching 최대 시도 횟수
ROI_THRESHOLD = 0.8  # Template Matching 유사도 임계값
ROI_OFFSET_BOTTOM = 100  # ROI 영역 하단에서의 Offset
MAIN_SHELVE = str(DATA_DIR / "daily_files_shelve")  # shelve 파일 경로 (상대 경로로 변환)

# path
# 사용자 설정에서 카카오톡 설치 경로 가져오기
KAKAOTALK_INSTALL_PATH = USER_SETTINGS.get("kakao_install_path", DEFAULT_USER_SETTINGS["kakao_install_path"])

# dict
TM_TEMPLATES = {
    "성공": PATH_TEMPLATE_SUC,
    "실패": PATH_TEMPLATE_FAIL,
    # "전송중": PATH_TEMPLATE_SENDING
}

# 시스템 메타데이터 감지 (해상도, 배율 등)
def detect_system_metadata():
    """
    개선: 시스템 해상도, 화면 배율 등 자동 감지
    """
    import pyautogui
    
    metadata = {}
    try:
        # 해상도
        screen_width, screen_height = pyautogui.size()
        metadata["screen_width"] = screen_width
        metadata["screen_height"] = screen_height
        
        # Windows 화면 배율(DPI) 감지
        if sys.platform == "win32":
            try:
                import ctypes
                user32 = ctypes.windll.user32
                # 현재 모니터의 DPI를 가져옴
                awareness = ctypes.c_int()
                ctypes.windll.shcore.GetProcessDpiAwareness(0, ctypes.byref(awareness))
                
                # DPI 인식 모드 설정
                ctypes.windll.shcore.SetProcessDpiAwareness(2)
                
                # DPI 가져오기
                dpi = user32.GetDpiForSystem()
                scale_factor = dpi / 96  # 기본 96 DPI 기준으로 스케일 계산
                metadata["scale_factor"] = scale_factor
                
                # 원래 DPI 인식 모드로 복구
                ctypes.windll.shcore.SetProcessDpiAwareness(awareness.value)
                
            except Exception as e:
                print(f"DPI 감지 오류: {e}")
                metadata["scale_factor"] = 1.0
    except Exception as e:
        print(f"시스템 메타데이터 감지 오류: {e}")
    
    return metadata

# 초기화 시 경로 유효성 검사
def validate_paths():
    """
    개선: 필요한 경로가 유효한지 검사하고 문제 발견 시 경고
    """
    paths_to_check = {
        "카카오톡 설치 경로": KAKAOTALK_INSTALL_PATH,
        "메인 이미지": PATH_MAIN_IMAGE,
        "성공 템플릿": PATH_TEMPLATE_SUC,
        "실패 템플릿": PATH_TEMPLATE_FAIL,
        "노트북용 템플릿": PATH_TEMPLATE_SUC_LAPTOP
    }
    
    issues = []
    
    for name, path in paths_to_check.items():
        if not os.path.exists(path):
            issues.append(f"{name}: {path} (경로를 찾을 수 없음)")
    
    return issues

# # 실행 시 필요한 템플릿 경로 반환
# def get_appropriate_template_path():
#     """
#     개선: 화면 해상도와 배율에 따라 적절한 템플릿 경로 반환
#     """
#     metadata = detect_system_metadata()
#     screen_width = metadata.get("screen_width", 1920)
    
#     # 작은 화면 또는 노트북 환경
#     if screen_width <= 1366:
#         return PATH_TEMPLATE_SUC_LAPTOP
#     # 일반 데스크탑 환경
#     else:
#         return PATH_TEMPLATE_SUC

if __name__ == "__main__":
    # # 경로 유효성 검사
    # path_issues = validate_paths()
    # if path_issues:
    #     print("경로 유효성 검사 결과:")
    #     for issue in path_issues:
    #         print(f"- {issue}")
    # else:
    #     print("모든 경로가 유효합니다.")
    
    # # 시스템 메타데이터 출력
    # metadata = detect_system_metadata()
    # print("\n시스템 메타데이터:")
    # for key, value in metadata.items():
    #     print(f"- {key}: {value}")
    pass

