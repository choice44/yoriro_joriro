from rest_framework.views import APIView
from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.generics import get_object_or_404

from .serializers import JoriroSerializer, Joriro
from .ai import predict, fit_background, blend
from .apps import JoriroConfig

from PIL import Image
import numpy as np
import cv2
import os


class JoriroView(APIView):
    def post(self, request):
        serializer = JoriroSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        img = Image.open(serializer.data["image"][1:])
        background = np.array(Image.open(
            JoriroConfig.backgrounds[serializer.data["place"]]))
        model = JoriroConfig.models[serializer.data["model"]]
        weights = JoriroConfig.weights[serializer.data["model"]]

        mask = predict(model, weights, img)

        img = np.array(img)

        background = fit_background(img, background)

        result = blend(img, mask, background)

        save_path = "media/joriro/result/"

        if not os.path.exists(save_path):
            os.makedirs(save_path)

        cv2.imwrite(save_path + str(serializer.data["id"]) + ".jpg", result)

        return Response({"image": f"/media/joriro/result/{serializer.data['id']}.jpg"})
