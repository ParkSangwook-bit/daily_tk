"""
유틸리티 함수 모듈
순환 의존성 해결을 위해 공통 기능을 분리
"""
import os
from typing import Any

def extract_student_name(filename: str) -> str:
    """
    파일명에서 학생이름 추출
    예) '20250124_홍길동2_영어.png' -> '홍길동2'
    규칙: '{YYYYMMDD}_{이름}_{과목}.png'
    """
    name_no_ext = os.path.splitext(filename)[0]  # 예: '20250124_홍길동2_영어'
    parts = name_no_ext.split('_')               # ['20250124', '홍길동2', '영어']
    if len(parts) >= 2:  # 과목이 없을 수도 있음
        return parts[1]  # 두 번째 요소(홍길동2)가 "학생이름"으로 가정
    else:
        return ""