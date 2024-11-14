import psutil
import subprocess
import time
import uiautomation as auto

'''
uiautomation을 사용하여 메모장 제어를 테스트해보자.
이 코드에서는 추상화와 모듈화, 단일 책임원칙을 준수하며 코드를 작성할 것 이다.
gpt는 이 프로그램에서 탑-다운으로 추상화 과정을 가져서 구조를 구성하는게 올바르다고 했지만, 구현은
낮은 단계의 추상화 정도를 가지는 함수부터 하라고 하였다.

목적: 이 프로그램은 메모장 프로세스를 감지하여 자동으로 메모장을 실행하여 특정 위치에 있는 txt파일을 여는 것이다.
'''

# high level

# 메모장을 자동으로 감지하고 지정된 파일을 자동으로 여는 함수(전체 플로우)
def file_as_notepad():
    ensure_notepad_running()
    open_file_in_notepad()

# medium level

# 자동으로 메모장을 감지하고 경우에 따라 실행하는 함수
def ensure_notepad_running():
    if is_notepad_running():
        pass
    else:
        open_notepad()

# 메모장에서 파일을 여는 함수
def open_file_in_notepad():
    open_file_using_uiauto()

# low level

# 메모장이 실행중인지 아닌지 검사하는 함수
def is_notepad_running():
    for proc in psutil.process_iter(attrs=['pid', 'name']):
        if proc.info['name'].lower() == 'notepad.exe':
            return True
        else:
            return False

# 메모장을 실행하는 함수
def open_notepad():
    subprocess.Popen('notepad.exe', shell=True)

# uiautomation을 이용하여 메모장에서 파일을 불러오는 동작을 하는 함수
def open_file_using_uiauto():
    pass
   

if __name__ == "__main__":
    file_as_notepad()