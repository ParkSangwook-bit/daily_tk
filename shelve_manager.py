from settings import shelve, os, datetime
# 순환 의존성 해결: kakao_control 임포트 제거, utils 모듈 사용
from utils import extract_student_name

# TODO CRUD 구현

#! CREATE: 디렉토리 기반으로 shelve 생성

#! READ: key 또는 value 값을 기반으로 shelve 읽기

#! UPDATE: value값 수정

#! DELETE: shelve 파일 제거 또는 특정 파일 리스트에서 제거

# def read_directory_and_update_treeview(self, directory: str, shelve_filename: str):
#     """
#     지정된 디렉토리에서 파일 정보를 읽고 Shelve에 저장한 후 Treeview에 표시
#     """
#     # Shelve에 파일 정보 저장
#     with shelve.open(shelve_filename) as db:
#         for filename in os.listdir(directory):
#             filepath = os.path.join(directory, filename)
#             if os.path.isfile(filepath) and filename.endswith(".png"):
#                 file_info = {
#                     "파일명": filename,
#                     "크기": os.path.getsize(filepath),
#                     "수정 날짜": datetime.fromtimestamp(os.path.getmtime(filepath)).strftime('%Y-%m-%d %H:%M'),
#                     "전송 상태": "미전송"
#                 }
#                 db[filename] = file_info
#             self.file_list_len += 1

#     # Treeview 업데이트
#     with shelve.open(shelve_filename) as db:
#         for key in db:
#             file_info = db[key]
#             self.file_tree.insert("", "end", values=(file_info["파일명"], f"{file_info['크기']} bytes", file_info["수정 날짜"], file_info["전송 상태"]))
            
            
            
# def send_files_worker(self, log_queue):
#     """
#     백그라운드 스레드에서 실행될 전송 로직:
#     1. shelve에서 '미전송' 파일 목록 가져오기
#     2. uiautomation으로 카카오톡 열기 & 파일 전송
#     3. ROI 캡처 + opencv 매칭
#     4. shelve 업데이트
#     5. 진행 상황을 log_queue에 put()하여 UI 표시
#     """
#     try:
#         # (1) 미전송 파일 목록 불러오기
#         with shelve.open("daily_files_shelve") as db:
#             keys = [k for k in db.keys() if db[k].get("전송 상태") == "미전송"]
        
#         total_files = len(keys)
#         log_queue.put(("log", f"[Worker] 미전송 파일 {total_files}개 발견."))

#         # uia: 카카오 실행 + 활성화
#         ensure_kakao_running()
#         time.sleep(1)
#         kakao_window = activate_kakao_window()
#         time.sleep(1)

#         processed_count = 0

#         for filename in keys:
#             # 파일 정보 가져오기
#             with shelve.open("daily_files_shelve", writeback=True) as db:
#                 file_info = db[filename]

#             log_queue.put(("log", f"[Worker] '{filename}' 전송 시도중..."))

#             # (2) uia 부분 (간단 예시 - 실제 로직 대체)
#             time.sleep(2)  # 더미 대기
#             result = "성공"  # 일단 더미
#             time.sleep(1)

#             # (4) shelve 업데이트
#             with shelve.open("daily_files_shelve", writeback=True) as db:
#                 file_info = db[filename]
#                 file_info["전송 상태"] = result
#                 db[filename] = file_info

#             log_queue.put(("log", f"[Worker] '{filename}' => {result}"))

#             # Progress 갱신
#             processed_count += 1
#             progress_ratio = processed_count / total_files
#             log_queue.put(("progress", progress_ratio))

#         log_queue.put(("done", "모든 파일 전송 작업이 완료되었습니다."))

#     except Exception as e:
#         log_queue.put(("log", f"[에러] {str(e)}"))
#         log_queue.put(("done", "작업 중단 (에러 발생)"))
        

#-----------------------------------------------------------------------------------

def extract_student_name(filename: str) -> str:
    """
    파일명에서 학생이름 추출
    예) '20250124_홍길동2_영어.png' -> '홍길동2'
    규칙: '{YYYYMMDD}_{이름}_{과목}.png'
    """
    name_no_ext = os.path.splitext(filename)[0]  # 예: '20250124_홍길동2_영어'
    parts = name_no_ext.split('_')               # ['20250124', '홍길동2', '영어']
    if len(parts) >= 2: # 과목이 없을 수도 있음
        return parts[1]  # 두 번째 요소(홍길동2)가 "학생이름"으로 가정
    else:
        #! 규칙에 맞지 않으면 파일 이름이 잘못된 것을 의심
        # TODO 규칙에 맞지 않으면 빈 문자열 등 처리 | 아직 명확한 처리법 없음
        return ""

def store_png_files_in_shelve(directory: str, shelve_filename: str) -> int:
    """
    지정된 디렉토리에서 .png 파일 정보를 읽고,
    shelve 파일에 {"파일명": file_info} 형태로 저장.
    (이미 존재하는 파일이면 상태를 포함한 정보 변경 없이 패스)

    추가로, 'student_names'라는 set/list 키를 두어,
    'extract_student_name(filename)' 결과도 중복 없이 관리.

    file_info 예시:
    {
      "파일명": filename,
      "크기": ...,
      "수정 날짜": ...,
      "전송 상태": "미전송"
    }

    Returns:
        새로 등록된 파일 개수(int)
    """
    stored_count = 0
    with shelve.open(shelve_filename, writeback=True) as db:
        # 만약 student_names가 없으면 초기화
        
        if "student_names" not in db:
            db["student_names"] = set()
            
        students = db["student_names"]
        
        for name in students:
            print(f"name = {name}")

        student_names_set = db["student_names"]

        for filename in os.listdir(directory):
            filepath = os.path.join(directory, filename)
            # 1) .png 파일인지?
            if os.path.isfile(filepath) and filename.lower().endswith(".png"):
                # 2) shelve에 이미 존재하는 파일명인가?
                if filename not in db:
                    # 새로운 파일 정보 생성 및 저장
                    file_info = {
                        "파일명": filename,
                        "크기": os.path.getsize(filepath),
                        "수정 날짜": datetime.fromtimestamp(os.path.getmtime(filepath)).strftime('%Y-%m-%d %H:%M'),
                        "전송 상태": "미전송"
                    }
                    db[filename] = file_info
                    stored_count += 1

                # 학생 이름 추출 후 student_names에 추가
                name = extract_student_name(filename)
                if name:  # 이름이 있을 경우에만 추가
                    student_names_set.add(name)


        # writeback=True 이므로, 수정한 student_names_set도 자동 반영 
        db["student_names"] = student_names_set

    return stored_count

def load_all_files_from_shelve(shelve_filename: str) -> list:
    """
    shelve에서 모든 파일 정보를 불러옴.
    Returns:
        [file_info, file_info, ...]
        각 file_info는 딕셔너리 구조.
    """
    file_info_list = []
    with shelve.open(shelve_filename) as db:
        for key in db:
            # student_names 등 다른 키 제외, 파일명만 file_info라 가정
            if isinstance(db[key], dict) and "파일명" in db[key]:
                file_info_list.append(db[key])
    return file_info_list

def load_file_info(shelve_filename: str, filename: str) -> dict:
    """
    특정 파일(filename)에 대한 file_info를 반환.
    없으면 빈 dict
    """
    with shelve.open(shelve_filename) as db:
        if filename in db:
            return db[filename]
        else:
            return {}

def get_student_names(shelve_filename: str) -> list:
    """
    shelve에서 'student_names'를 불러와 list로 반환
    """
    with shelve.open(shelve_filename) as db:
        names_struct = db.get("student_names", set())
        # 만약 set 대신 list를 쓴다면, 여기서 sorted(...) 가능
        return sorted(names_struct)

def update_file_status(shelve_filename: str, filename: str, new_status: str) -> None:
    """
    shelve에서 해당 filename의 '전송 상태'를 new_status로 업데이트.
    """
    with shelve.open(shelve_filename, writeback=True) as db:
        if filename in db:
            db[filename]["전송 상태"] = new_status

def get_pending_file_names(shelve_filename: str) -> list:
    """
    '미전송' 상태인 파일 목록(파일명)을 반환.
    Returns: ['file1.png', 'file2.png', ...]
    """
    pending_list = []
    with shelve.open(shelve_filename) as db:
        for key, info in db.items():
            if (isinstance(info, dict) and 
                info.get("전송 상태") == "미전송"):
                pending_list.append(key)
    return pending_list

def get_pending_file_infos(shelve_filename: str) -> list:
    """
    '미전송' 상태인 file_info(딕셔너리)를 리스트 형태로 반환.

    Returns:
        [
          {
            "파일명": filename,
            "크기": ...,
            "수정 날짜": ...,
            "전송 상태": "미전송"
          },
          ...
        ]
    """
    pending_list = []
    with shelve.open(shelve_filename) as db:
        for key, info in db.items():
            if (isinstance(info, dict) and 
                info.get("전송 상태") == "미전송"):
                pending_list.append(info)
    return pending_list

def get_specific_status_files_infos(status_list: list, shelve_filename: str) -> list:
    """
    shelve에서 특정 상태들에 해당하는 file_info들을 리스트로 반환.

    Args:
        status_list: list[str]
            원하는 상태들의 리스트 예시: ["성공", "실패", "전송중", "미전송"]
        shelve_filename: str
            shelve 파일 경로 또는 이름
    Returns:
        list: 해당 상태들의 파일 정보 리스트
    """
    result = []
    with shelve.open(shelve_filename) as db:
        for key, info in db.items():
            if (isinstance(info, dict) and 
                info.get("전송 상태") in status_list):
                result.append(info)  # status_list가 아닌 result에 추가
    return result


if __name__ == "__main__":
    pass