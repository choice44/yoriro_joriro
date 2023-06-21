from django.apps import AppConfig
from torchvision.models.segmentation import (fcn_resnet50, FCN_ResNet50_Weights,
                                             lraspp_mobilenet_v3_large, LRASPP_MobileNet_V3_Large_Weights,
                                             deeplabv3_mobilenet_v3_large, DeepLabV3_MobileNet_V3_Large_Weights)
import ssl

ssl._create_default_https_context = ssl._create_unverified_context
from torchvision.models.segmentation import (fcn_resnet50, FCN_ResNet50_Weights,
                                             lraspp_mobilenet_v3_large, LRASPP_MobileNet_V3_Large_Weights,
                                             deeplabv3_mobilenet_v3_large, DeepLabV3_MobileNet_V3_Large_Weights)
import ssl

ssl._create_default_https_context = ssl._create_unverified_context


class JoriroConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "joriro"
