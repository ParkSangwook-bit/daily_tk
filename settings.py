# This file is used to store all the settings for the project

# tkinter
import customtkinter as ctk
import tkinter as tk
from tkinter import ttk

# data processing
import shelve
import threading
import queue
import time
import traceback
import cv2
import numpy as np
import subprocess
from typing import cast

# UI control
import uiautomation as auto
import pyautogui

# os
import os
from pathlib import Path
from datetime import datetime

# own made modules
# from kakao_control import *
# from shelve_manager import *

# global variables
ROI_OFFSET_BOTTOM = 100
ROI_THRESHOLD = 0.8
# TM = template matching
TM_MAX_ATTEMPTS = 3


def theWorld(second: int):
    time.sleep(second)
    print(f"히야~ 내가 시간을 {second}초나 멈출 수 있다~")
    exit()