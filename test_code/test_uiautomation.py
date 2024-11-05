import uiautomation as auto
import subprocess

# 카카오톡 프로그램 실행 파일 경로
kakao_path = r"C:\Program Files (x86)\Kakao\KakaoTalk\KakaoTalk.exe"

# Popen을 이용해 카카오톡 실행
subprocess.Popen([kakao_path], shell=False)

kakao_window = auto.WindowControl(searchDepth=1, Name="카카오톡")

friend_list = kakao_window.MenuItemControl(Name="친구")
if friend_list.Exists:
    print("친구 메뉴를 찾았습니다.")
    friend_list.Click()