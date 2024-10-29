from PIL import Image
import os

# 더미 파일을 저장할 디렉토리 설정
output_dir = "..\\shelve_test"
os.makedirs(output_dir, exist_ok=True)

# 40개의 더미 PNG 파일 생성
for i in range(1, 41):
    # 빈 이미지 생성 (100x100 크기, 흰색 배경)
    img = Image.new("RGB", (100, 100), color=(255, 255, 255))
    
    # 파일 이름 지정 및 저장
    file_name = f"dummy_{i}.png"
    file_path = os.path.join(output_dir, file_name)
    img.save(file_path)

print(f"{len(os.listdir(output_dir))}개의 더미 PNG 파일이 '{output_dir}' 폴더에 생성되었습니다.")
