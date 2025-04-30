# ───────────────────────────────── settings.py
"""
프로젝트 전역에서 공통으로 쓰는 외부 라이브러리를 re‑export 한다.

* ❶  이 파일 하나만 import 경로로 사용한다:
      from settings import cv2, np, auto, time …

* ❷  settings.py 자체에는 ‘설정’·‘상수’는 두지 않는다
      (상수는 constants.py 로 분리).  →  의존 사이클 방지

* ❸  __all__ 로 노출 목록을 고정해 IDE 타입 추적이 끊기지 않게 한다.
"""
from __future__ import annotations

# ── 실질 import ────────────────────────────────────────────
import cv2                                   # OpenCV
import numpy as np
import uiautomation as auto                  # UI Automation
import pyautogui

import time
import subprocess
import shelve
import threading, queue, traceback
import math
from typing import Any, cast


# (GUI)  ───── 필요‑시에만 주석 해제
import customtkinter as ctk
import tkinter as tk
from tkinter import ttk

# (OS / 경로)
import os
from pathlib import Path
from datetime import datetime

# ── 선택: 프로젝트 전용 유틸 함수 ─────────────────────────
def theWorld(seconds: int) -> None:
    """디버깅용: n 초 슬립 후 강제 종료(주의!)."""
    print(f"[DEV] time.sleep({seconds}) 후 프로그램 종료")
    time.sleep(seconds)
    raise SystemExit(0)

# ── IDE & 정적 분석을 위한 노출 목록 ───────────────────────
__all__: list[str] = [
    # 영상/수치
    "cv2", "np",
    # UI 자동화
    "auto", "pyautogui",
    # 시스템
    "time", "subprocess", "shelve",
    "threading", "queue", "traceback",
    "os", "Path", "datetime", "Any", "cast",
    # GUI (선택)
    "ctk", "tk", "ttk",
    # 유틸
    "theWorld",
]
# ──────────────────────────────────────────────────────────
# ── IDE & 정적 분석을 위한 노출 목록 ───────────────────────