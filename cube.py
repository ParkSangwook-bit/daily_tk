import os
import time

# 1. **아스키 아트용字符들**
characters = [
    "▓",
    "□",
    "□",
    "▒",
    "█",
    "▒",
    "□",
    "□",
]

# 2. **3D cube Rotation Logic**
def rotate_cube():
    for _ in range(4):
        os.system("cls" if os.name == "nt" else "clear")
        print("[" + "".join(characters) + "]")
        time.sleep(1)

# 3. **타이머**
def print_and_rotate():
    while True:
        os.system("cls")
        print("[", end="")
        for char in characters:
            print(char, end="")
        print("]", end="")
        time.sleep(1)

# 4. **아스키 아트를 실행하기**
if __name__ == "__main__":
    print_and_rotate()
