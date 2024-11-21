import uiautomation as auto
import subprocess
import psutil

# 카카오 실행 여부 검사 및 실행
def ensure_kakao_running():
    if is_kakao_running():
        pass
    else:
        print("카카오톡이 실행되고 있지 않습니다. 카카오톡 실행 시도 . . .")
        launch_kakao()

#? is_kakao_installed() 필요할까?

# 카카오톡 프로세스 감지
def is_kakao_running():
    for proc in psutil.process_iter():
        try:
            if proc.name().lower() == 'KakaoTalk.exe'.lower():
                print("'KakaoTalk.exe' 프로세스를 감지했습니다.")
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess) as e:
            print(f"다음의 사유로 프로세스를 건너뜀: {e}")
        
        #! 이 부분 수정해야함. 루프를 돌며 첫번째로 감지된 프로세스가 카카오톡이 아니면 곧바로 false 리턴함
        #? psutil과 subprocess를 모두 결합한 방식 채용 또는, 루프 조건 변경.try-catch-except 사용
        # 로직 수정하기. 기존 로직은 반드시 launch_kakao()호출 
        # 해결했음

    print("Failed detecting 'KakaoTalk.exe' process")
    return False

# 카카오톡 프로세스 실행
def launch_kakao():
    # 카카오톡 프로그램 실행 파일 경로
    kakao_path = r"C:\Program Files (x86)\Kakao\KakaoTalk\KakaoTalk.exe"

    try:
        # Popen을 이용해 카카오톡 실행
        subprocess.Popen([kakao_path], shell=False)
        print("카카오톡 프로세스 실행 완료")
    except FileNotFoundError as e:
        print(f"{kakao_path}에서 카카오톡을 찾을 수 없습니다. 경로를 확인해주세요.")
        print(f"error code: {e}")

'''
==========================================================================================
==========================================================================================
==========================================================================================
'''
# 카카오톡 윈도우 활성화 및 포커스
def activate_kakao_window():
    try:
        # 카카오톡 메인 창 찾기
        kakao_main = auto.WindowControl(searchDepth=1, Name="카카오톡")
        if not kakao_main.Exists():
            print("카카오톡 메인 창을 찾을 수 없습니다.")
            return False
            
        # 윈도우 활성화 및 포커스
        kakao_main.SetActive()
        kakao_main.SetFocus()
        print("카카오톡 창을 활성화했습니다.")
        return True
        
    except Exception as e:
        print(f"카카오톡 창 활성화 중 오류 발생: {e}")
        return False


# 카카오톡 친구창 접근
def access_friends_window():
    if not activate_kakao_window():
        print("카카오톡 창을 활성화할 수 없습니다.")
        return False

    try:
        # 카카오톡 메인 창 찾기
        kakao_main = auto.WindowControl(searchDepth=1, Name="카카오톡")
        if not kakao_main.Exists():
            print("카카오톡 메인 창을 찾을 수 없습니다.")
            return False
        
        # 탭 버튼을 6번 눌러 친구 탭으로 이동
        for _ in range(6):
            auto.SendKeys("{TAB}")
        
        # 엔터 키를 눌러 친구 탭 활성화
        auto.SendKeys("{ENTER}")
        print("친구 탭으로 전환했습니다.")

        # 연락처 목록 컨트롤 찾기
        contact_list_ctrl = kakao_main.Control(Name="ContactListView_0x0002049c")
        if not contact_list_ctrl.Exists():
            print("연락처 목록 컨트롤을 찾을 수 없습니다.")
            return False
            
        if contact_list_ctrl.SetFocus():
            print("연락처 목록에 포커스를 설정했습니다.")
            return True
        else:
            print("친구 목록 창에 포커스를 설정할 수 없습니다.")
            return False
        
    except Exception as e:
        print(f"친구창 접근 중 오류 발생: {e}")
        return False



# 메인 함수
if __name__ == "__main__":
    ensure_kakao_running()
    # subprocess.run("tasklist",shell=True)
    access_friends_window()