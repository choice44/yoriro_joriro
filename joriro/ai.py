import numpy as np
import cv2


def predict(model, weights, img):
    # 전처리
    preprocess = weights.transforms(antialias=True)

    # 전처리 적용
    batch = preprocess(img).unsqueeze(0)

    # 모델을 사용하여 예측 및 사람 마스크만 추출
    prediction = model(batch)["out"]
    normalized_masks = prediction.softmax(dim=1)
    class_to_idx = {cls: idx for (idx, cls) in enumerate(
        weights.meta["categories"])}
    mask = normalized_masks[0, class_to_idx["person"]]

    # numpy array로 변환
    mask = mask.detach().cpu().numpy()

    return mask


def fit_background(img, background):
    # 이미지 사이즈 추출
    fg_h, fg_w, _ = img.shape

    # 배경 사이즈 추출
    bg_h, bg_w, _ = background.shape

    # 높이 맞추기
    background = cv2.resize(background, dsize=(int(fg_h * bg_w / bg_h), fg_h))

    # 배경 사이즈 초기화
    bg_h, bg_w, _ = background.shape

    # 남는 너비 채우기
    margin = (bg_w - fg_w) // 2

    if margin > 0:
        background = background[:, margin:-margin, :]
    else:
        background = cv2.copyMakeBorder(background, top=0, bottom=0,
                                        left=abs(margin), right=abs(margin), borderType=cv2.BORDER_REPLICATE)

    # 최종 리사이즈
    background = cv2.resize(background, dsize=(fg_w, fg_h))

    return background


def blend(img, mask, background):
    # 전경 사이즈 초기화
    fg_h, fg_w, _ = img.shape

    # 마스크를 전경 크기에 맞춤
    mask = cv2.resize(mask, (fg_w, fg_h))

    # 마스크 타입 변환 및 차원 추가
    alpha = mask.astype(float)
    alpha = np.repeat(np.expand_dims(alpha, axis=2),
                      3, axis=2)  # (height, width, 3)

    # 이미지와 마스크 합성, 배경과 마스크 합성
    foreground = cv2.multiply(alpha, img.astype(float))
    background = cv2.multiply(1. - alpha, background.astype(float))

    # 전경과 배경 합성
    result = cv2.add(foreground, background).astype(np.uint8)

    # 색상 변환
    result = cv2.cvtColor(result, cv2.COLOR_RGB2BGR)

    return result
