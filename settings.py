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
from typing import cast, Any

# UI control
import uiautomation as auto
import pyautogui

# os
import os
from pathlib import Path
from datetime import datetime

def theWorld(second: int):
    print(f"히야~ 내가 시간을 {second}초나 멈출 수 있다~")
    time.sleep(second)
    exit()