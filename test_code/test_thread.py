import threading
import time
import queue
import logging

logging.basicConfig(level=logging.ERROR, format="[%(threadName)s] %(message)s")

log_queue = queue.Queue()

def worker():
    logging.error("알림! 작업 시작")
    for i in range(5):
        time.sleep(1.5)
        log_queue.put(f"작업 {i+1}/5 완료")
        logging.error("스레드 작업 종료")
        
def monitor_queue():
    while True:
        try:
            msg = log_queue.get_nowait()
            logging.error(f"큐 메세지: {msg}")
        except queue.Empty: break
        
t = threading.Thread(target=worker, daemon=True)
t.start()

while t.is_alive():
    monitor_queue()
    time.sleep(0.5)
    
logging.error("알림! 메인 스레드 종료")
    