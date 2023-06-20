from rest_framework import serializers
from django.db.models import Avg
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
    rate = serializers.SerializerMethodField()
    
    def get_rate(self, obj):
        rate_avg = obj.spot_reviews.aggregate(Avg("rate"))["rate__avg"]
        if rate_avg:
            rate_avg = round(rate_avg, 1)
        return rate_avg
    
    class Meta:
        model = Spot
        fields = "__all__"
