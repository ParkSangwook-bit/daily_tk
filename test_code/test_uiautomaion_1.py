import psutil
import subprocess
import time
import uiautomation as auto

# 메모장 프로세스를 감지하는 함수
def is_notepad_running():
    for proc in psutil.process_iter(attrs=['pid', 'name']):
        if proc.info['name'].lower() == 'notepad.exe':
            return True
    return False

# 메모장을 실행하는 함수
def run_notepad():
    subprocess.Popen('notepad.exe', shell=True)

# 메모장 창을 찾고 포커스를 맞추는 함수
def focus_notepad_window():
    notepad_window = auto.WindowControl(searchDepth=1, ClassName='Notepad')
    if notepad_window.Exists():
        notepad_window.SetFocus()
        return notepad_window
    else:
        return None

# 메모장 자동 실행 및 포커스 맞추기
def ensure_notepad_running():
    if not is_notepad_running():
        print("메모장이 실행 중이지 않습니다. 메모장을 실행합니다.")
        run_notepad()
        # 메모장이 실행되는 동안 잠시 대기
        time.sleep(2)
    else:
        print("메모장이 이미 실행 중입니다.")
    
    # 메모장 창을 찾고 포커스를 맞추기
    notepad_window = focus_notepad_window()
    if notepad_window:
        print("메모장에 포커스를 맞췄습니다.")
    else:
        print("메모장 창을 찾을 수 없습니다.")

# 메모장에 텍스트를 입력하는 함수
def write_text_to_notepad(text):
    notepad_window = focus_notepad_window()
    if notepad_window:
        edit_control = notepad_window.EditControl()
        if edit_control.Exists():
            edit_control.SendKeys(text)
            print("텍스트 입력 완료.")
        else:
            print("메모장 텍스트 입력란을 찾을 수 없습니다.")

if __name__ == "__main__":
    # 메모장 실행 및 포커스 맞추기
    ensure_notepad_running()

    # 메모장에 텍스트 입력
    write_text_to_notepad("uiautomation 라이브러리를 사용하여 메모장 자동화를 연습하고 있습니다.\n")
