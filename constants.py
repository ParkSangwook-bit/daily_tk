# Description: Constants used in the project

# Constants
TM_MAX_ATTEMPTS = 3 # Template Matching 최대 시도 횟수
ROI_THRESHOLD = 0.8 # Template Matching 유사도 임계값
ROI_OFFSET_BOTTOM = 100 # ROI 영역 하단에서의 Offset
MAIN_SHELVE = "daily_files_shelve" # shelve 파일 이름 | #! 이름으로 해도 되나...?

#! os라이브러리와 __file__ 이용해서 상대 경로 지정해야함
# path
KAKAOTALK_INSTALL_PATH= r"C:\Program Files (x86)\Kakao\KakaoTalk\KakaoTalk.exe"

PATH_MAIN_IMAGE = r'C:\\Users\\qkrtk\\Desktop\\screenshot\\opencv_test\\sample_sending_complete_crop.png'
PATH_TEMPLATE_SUC = r'C:\\Users\\qkrtk\\Desktop\\screenshot\\opencv_test\\sample_am_kor_200per.png'
PATH_TEMPLATE_FAIL = r'C:\\Users\\qkrtk\\Desktop\\screenshot\\opencv_test\\sample_template_aggresive2.png'
# PATH_TEMPLATE_SENDING = r'C:\\Users\\qkrtk\\Desktop\\screenshot\\opencv_test\\sample_am_kor_200per.png'

# for laptop
PATH_TEMPLATE_SUC_LAPTOP = r'C:\\Users\\PSW\\Desktop\\screenshot\\sample_pm_kor_125per.png'


# dict
TM_TEMPLATES = {
    "성공" : PATH_TEMPLATE_SUC,
    "실패" : PATH_TEMPLATE_FAIL,
    # "전송중" : PATH_TEMPLATE_SENDING
    }

