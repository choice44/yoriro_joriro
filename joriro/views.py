from rest_framework.views import APIView
from rest_framework import status, permissions
from rest_framework.response import Response

from .serializers import JoriroSerializer
from .ai import predict, fit_background, blend
from .apps import JoriroConfig

from PIL import Image
import numpy as np
import cv2
import os


class JoriroView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        # 시리얼라이저 초기화 및 request.data 저장
        serializer = JoriroSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save(user=request.user)

        # 이미지, 배경, 모델 로드
        img = Image.open(instance.image)
        # 3 채널로 변환
        img = img.convert("RGB")
        background = np.array(Image.open(
            JoriroConfig.backgrounds[instance.place]))
        model = JoriroConfig.models[instance.model]
        weights = JoriroConfig.weights[instance.model]

        # 모델과 이미지로 마스크 예측
        mask = predict(model, weights, img)

        # 이미지 numpy array로 변환
        img = np.array(img)

        # 배경 크기 이미지와 맞춤
        background = fit_background(img, background)

        # 이미지, 마스크, 배경 합성
        result = blend(img, mask, background)

        # 저장 경로 초기화
        save_path = "media/joriro/result/"

        # 저장 경로에 폴더가 없으면 생성
        if not os.path.exists(save_path):
            os.makedirs(save_path)

        # 업로드한 파일에서 이름을 가져옴
        file_name = str(instance.image).split("/")[-1].split(".")[0]

        # 결과물 저장
        cv2.imwrite(save_path + file_name + ".jpg", result)

        # 모델에 결과물 경로 저장
        instance.result = "/" + save_path + file_name + ".jpg"
        instance.save()

        # 새 시리얼라이저 초기화
        new_serializer = JoriroSerializer(instance)

        return Response(new_serializer.data, status=status.HTTP_201_CREATED)
