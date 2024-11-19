import uiautomation as auto
import subprocess
import psutil

# 카카오 실행 여부 검사 및 실행
def ensure_kakao_running():
    if is_kakao_running():
        pass
    else:
        launch_kakao()

# 카카오톡 프로세스 감지
def is_kakao_running():
    for proc in psutil.process_iter(attrs=['pid', 'name']):
        if proc.info['name'].lower() == 'kakaotalk.exe':
            print("\'KakaoTalk.exe\' ")
            return True
        else:
            print("Failed detecting \'KakaoTalk.exe\' process")
            return False

# 카카오톡 프로세스 실행
def launch_kakao():
    # 카카오톡 프로그램 실행 파일 경로
    kakao_path = r"C:\Program Files (x86)\Kakao\KakaoTalk\KakaoTalk.exe"

    # Popen을 이용해 카카오톡 실행
    subprocess.Popen([kakao_path], shell=False)


if __name__ == "__main__":
    ensure_kakao_running()