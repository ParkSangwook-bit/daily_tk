from settings import shelve, time, os, datetime
from kakao_control import *

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
# initialize
def store_png_files_in_shelve(directory: str, shelve_filename: str) -> int:
    """
    지정된 디렉토리에서 .png 파일 정보를 읽고,
    shelve 파일에 {"파일명": file_info} 형태로 저장.

    file_info 예시 구조:
    {
      "파일명": filename,
      "크기": ...,
      "수정 날짜": ...,
      "전송 상태": "미전송"
    }

    Returns:
        파일로 등록된 개수(int)
    """
    stored_count = 0
    with shelve.open(shelve_filename) as db:
        for filename in os.listdir(directory):
            filepath = os.path.join(directory, filename)
            if os.path.isfile(filepath) and filename.lower().endswith(".png"):
                file_info = {
                    "파일명": filename,
                    "크기": os.path.getsize(filepath),
                    "수정 날짜": datetime.fromtimestamp(os.path.getmtime(filepath)).strftime('%Y-%m-%d %H:%M'),
                    "전송 상태": "미전송"
                }
                db[filename] = file_info
                stored_count += 1
    return stored_count

def load_all_files_from_shelve(shelve_filename: str) -> list:
    """
    shelve에서 모든 파일 정보를 불러옴.

    Returns:
        [file_info, file_info, ...] 형태의 리스트
        각 file_info는 딕셔너리 구조.
    """
    file_info_list = []
    with shelve.open(shelve_filename) as db:
        for key in db:
            file_info_list.append(db[key])
    return file_info_list

def load_file_info(shelve_filename: str, filename: str) -> dict:
    """
    특정 파일(filename)에 대한 file_info를 반환.
    없으면 None.
    """
    with shelve.open(shelve_filename) as db:
        if filename in db:
            return db[filename]
        else:
            return {}   # 빈 형식

def update_file_status(shelve_filename: str, filename: str, new_status: str) -> None:
    """
    shelve에서 해당 filename의 '전송 상태'를 new_status로 업데이트.
    """
    with shelve.open(shelve_filename, writeback=True) as db:
        if filename in db:
            db[filename]["전송 상태"] = new_status

def get_pending_files(shelve_filename: str) -> list:
    """
    '미전송' 상태인 파일 목록(파일명)을 반환.
    Returns:
        ['file1.png', 'file2.png', ...]
    """
    pending_list = []
    with shelve.open(shelve_filename) as db:
        for key, info in db.items():
            if info.get("전송 상태") == "미전송":
                pending_list.append(key)
    return pending_list
