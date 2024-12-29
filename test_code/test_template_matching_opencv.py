import cv2

# resource
main_image = cv2.imread(r'C:\\Users\\qkrtk\\Desktop\\screenshot\\opencv_test\\while_sending\\sample_complete_sending.png')
template_suc= cv2.imread(r'C:\\Users\\qkrtk\\Desktop\\screenshot\\opencv_test\\sample_am_kor_200per.png')
template_fail= cv2.imread(r'C:\\Users\\qkrtk\\Desktop\\screenshot\\opencv_test\\sample_am_kor_200per.png')
template_sending= cv2.imread(r'C:\\Users\\qkrtk\\Desktop\\screenshot\\opencv_test\\sample_am_kor_200per.png')
#! 해상도에 따라서 완전히 인식률이 달라짐 샘플은 모두 준비하는게 맞지만, 각 해상도에 맞는 샘플을 준비해야됨.
#! 같은 해상도에서 인식률이 매우 높아짐.




# 템플릿 이미지가 제대로 로드되지 않았다면 경고 출력
if main_image is None:
    print("메인 이미지를 로드하지 못했습니다. 경로를 확인하세요.")
if template_suc is None or template_fail is None or template_sending is None:
    print("템플릿 이미지를 로드하지 못했습니다. 경로를 확인하세요.")

# 디버깅을 위한 기본 정보 출력
print("메인 이미지 크기:", main_image.shape)
print("템플릿 이미지 크기:", template_suc.shape, template_fail.shape, template_sending.shape)

# 템플릿 매칭 (TM_CCOEFF_NORMED: 높은 상관관계를 찾는 방식)
result = cv2.matchTemplate(main_image, template, cv2.TM_CCOEFF_NORMED)

# 디버깅을 위한 결과 매트릭스 정보 출력
print("결과 행렬(result) 크기:", result.shape)

# 결과에서 가장 높은 유사도의 위치 찾기
min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
#? min_val: 최소값, max_val: 최대값, min_loc: 최소값 위치, max_loc: 최대값 위치
# min_val이 음수인 것은 

# 디버깅을 위한 유사도 정보 출력
print("최소값:", min_val, "최대값:", max_val)
print("최소값 위치:", min_loc, "최대값 위치:", max_loc)

# 유사도가 특정 임계값 이상인 경우 매칭으로 간주
threshold = 0.8  # 유사도 임계값 (필요시 조정)
if max_val >= threshold:
    print(f"템플릿 매칭 성공! 유사도: {max_val}")
    top_left = max_loc  # 매칭된 템플릿의 좌상단 좌표
    h, w = template.shape[:2]
    bottom_right = (top_left[0] + w, top_left[1] + h)

    # 매칭 영역 표시
    cv2.rectangle(main_image, top_left, bottom_right, (0, 255, 0), 2)
    cv2.imshow('Matched Result', main_image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
else:
    print("템플릿 매칭 실패. 유사도를 확인하세요.")
    print(f"최대 유사도: {max_val}")
