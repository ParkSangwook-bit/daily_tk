import settings
'''
걍 다 갈아엎어야겠다.
내 수준에서는 추상화 단계를 더 세분화 하는 것보다는 단계를 더 줄이거나 조금 더 뭉텅이로 묶어야겠다.
아무튼 추상화 단계를 계속 고려 하면서 루틴을 작성해야한다.
단일 원칙을 지켜야 하는 것을 명심
'''

#! High level abstraction for sending files using KakaoTalk
def send_files_using_kakao(file_shelve):
    ensure_kakao_running()
    for file in file_shelve:
        send_file_using_kakao(file)
    finalize_process()

#! Medium level abstraction for sending files using KakaoTalk

# KakaoTalk이 실행 중인지 확인하는 함수
def ensure_kakao_running():
    pass

# 친구 리스트 접근 및 친구 찾기
def access_and_search_friends():
    pass

# 대화창을 열고 파일 전송
def open_chat_and_send_file(friend, file):
    pass

def send_file_using_kakao(file):
    friend_name = extract_name_from_file(file)
    open_chat_and_send_file(friend_name, file)
    attach_and_send_file(file)
    verify_and_log_result(file)

#! Low level abstraction for sending files using KakaoTalk
def is_kakao_running():
    pass

def extract_name_from_file(file):
    pass

def attach_and_send_file(file):
    pass

def verify_and_log_result(file):
    pass

def finalize_process():
    pass