import psutil
import subprocess
import time
import uiautomation as auto

'''
uiautomation을 사용하여 메모장 제어를 테스트해보자.
이 코드에서는 추상화와 모듈화, 단일 책임원칙을 준수하며 코드를 작성할 것 이다.
'''

#! high level abstraction for controlling notepad
def ensure_notepad_running():
    if not is_notepad_running():
        print("메모장이 실행 중이지 않습니다. 메모장을 실행합니다.")
        run_notepad()
        time.sleep(2)
    else:
        print("메모장이 이미 실행 중입니다.")

    notepad_window = focus_notepad_window()
    if notepad_window:
        print("메모장에 포커스를 맞췄습니다.")
    else:
        print("메모장 창을 찾을 수 없습니다.")

def write_text_to_notepad(text):
    notepad_window = focus_notepad_window()
    if notepad_window:
        edit_control = notepad_window.EditControl()
        if edit_control.Exists():
            edit_control.SendKeys(text)
            print("텍스트 입력 완료.")
        else:
            print("메모장 텍스트 입력란을 찾을 수 없습니다.")

'''
-------------------------------------------------------------------------------------------
'''

#! medium level abstraction for controlling notepad
def is_notepad_running():
    for proc in psutil.process_iter(attrs=['pid', 'name']): # 프로세스 목록 조회
        if proc.info['name'].lower() == 'notepad.exe':  # 메모장 프로세스가 실행 중인지 확인
            return True
        else:
            return "메모장이 실행 중이지 않습니다."

def run_notepad():
    subprocess.Popen('notepad.exe', shell=True)  # 메모장 실행

def focus_notepad_window():
    notepad_window = auto.WindowControl(searchDepth=1, ClassName='Notepad')  # 메모장 창 찾기
    if notepad_window.Exists():
        notepad_window.SetFocus()
        return notepad_window
    else:
        return None

if __name__ == "__main__:":
    ensure_notepad_running()
    write_text_to_notepad("uiautomation 라이브러리를 사용하여 메모장 자동화를 연습하고 있습니다.\n")