import ctypes
from win32api import GetSystemMetrics

def get_system_dpi():
    """
    주요 모니터의 DPI를 가져옵니다.
    Windows 8 이상에서 호환됩니다.
    """
    try:
        # DPI 인식 활성화 (Windows 8.1 이상)
        ctypes.windll.shcore.SetProcessDpiAwareness(2)
    except AttributeError:
        # Windows 8 이하에서는 SetProcessDPIAware() 사용
        ctypes.windll.user32.SetProcessDPIAware()

    # 주요 모니터의 DPI 가져오기
    hdc = ctypes.windll.user32.GetDC(0)
    dpi = ctypes.windll.gdi32.GetDeviceCaps(hdc, 88)  # 88: LOGPIXELSX
    ctypes.windll.user32.ReleaseDC(0, hdc)

    return dpi

def get_actual_resolution():
    """
    실제 해상도를 계산합니다 (DPI 스케일링 무시).
    """
    # 스케일링된 해상도 가져오기
    scaled_width = GetSystemMetrics(0)
    scaled_height = GetSystemMetrics(1)

    # DPI 가져오기
    dpi = get_system_dpi()

    # 스케일링 기반 실제 해상도 계산
    scaling_factor = dpi / 96
    actual_width = int(scaled_width * scaling_factor)
    actual_height = int(scaled_height * scaling_factor)

    return actual_width, actual_height

def show_display_settings():
    """
    해상도, DPI, 배율 정보를 출력합니다.
    """
    scaled_width = GetSystemMetrics(0)
    scaled_height = GetSystemMetrics(1)
    actual_width, actual_height = get_actual_resolution()
    dpi = get_system_dpi()
    scaling_factor = dpi / 96 * 100

    result = (
        f"스케일링된 해상도: {scaled_width}x{scaled_height}\n"
        f"실제 해상도: {actual_width}x{actual_height}\n"
        f"현재 DPI: {dpi}\n"
        f"배율: {scaling_factor:.2f}%"
    )
    print(result)

if __name__ == "__main__":
    show_display_settings()
