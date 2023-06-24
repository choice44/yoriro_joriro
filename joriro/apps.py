from django.apps import AppConfig
from torchvision.models.segmentation import (fcn_resnet50, FCN_ResNet50_Weights,
                                             lraspp_mobilenet_v3_large, LRASPP_MobileNet_V3_Large_Weights,
                                             deeplabv3_mobilenet_v3_large, DeepLabV3_MobileNet_V3_Large_Weights)
import ssl

ssl._create_default_https_context = ssl._create_unverified_context


class JoriroConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "joriro"
    weights = {
        1: FCN_ResNet50_Weights.DEFAULT,
        2: DeepLabV3_MobileNet_V3_Large_Weights.DEFAULT,
        3: LRASPP_MobileNet_V3_Large_Weights.DEFAULT
    }
    models = {
        1: fcn_resnet50(weights=weights[1]).eval(),
        2: deeplabv3_mobilenet_v3_large(weights=weights[2]).eval(),
        3: lraspp_mobilenet_v3_large(weights=weights[3]).eval()
    }
    backgrounds = {
        1: "background_image/625.jpg",
        2: "background_image/haeundae.jpg",
        3: "background_image/hanra.png",
        4: "background_image/panmunjeom.JPG",
        5: "background_image/seokguram.jpeg"
    }
