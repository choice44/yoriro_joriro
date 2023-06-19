from rest_framework import serializers
from spots.models import Area, Sigungu, Spot


# 시도
class AreaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Area
        fields = "__all__"


# 시군구
class SigunguSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sigungu
        fields = "__all__"


# 관광지, 맛집
class SpotSerializer(serializers.ModelSerializer):
    class Meta:
        model = Spot
        fields = "__all__"
