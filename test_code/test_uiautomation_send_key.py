import uiautomation as auto
import time

time.sleep(5)

# 1. CTRL + F로 친구 검색창 열기
auto.SendKeys('{Ctrl}f')  # Ctrl + F