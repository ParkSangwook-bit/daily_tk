import uiautomation as auto
import subprocess
import time

# 메모장 실행
subprocess.Popen('KakaoTalk.exe')
time.sleep(1)  # 메모장이 열릴 때까지 대기

# 메모장 창 찾기
kakao_window = auto.WindowControl(searchDepth=1, ClassName='KaKaoTalk')
if kakao_window.Exists():
    # 메모장의 에디트 컨트롤 찾기
    edit = kakao_window.EditControl()
    if edit.Exists():
        edit.SetFocus()
        edit.SendKeys('Hello, this is a test using WindowControl!\n')
else:
    print("메모장을 찾을 수 없습니다.")
