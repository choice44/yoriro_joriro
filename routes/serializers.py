from rest_framework import serializers
from django.db.models import Avg

from .models import Routes, Comment, Destinations, Places, RouteRate

# 여행지
class DestinationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Destinations
        fields = ('area_code', 'sigungu_code')

# 장소
class PlaceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Places
        fields = ('content_id', 'content_type_id')
        

# 여행경로 전체 조회
class RouteSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()
    comment_count = serializers.SerializerMethodField()
    rate = serializers.SerializerMethodField()
    destinations = DestinationSerializer(many=True)
    places = PlaceSerializer(many=True)

    def get_user(self, obj):
        return {'id': obj.user.pk, 'nickname': obj.user.nickname}

    def get_comment_count(self, obj):
        return obj.comments.count()

    def get_rate(self, obj):
        rate_avg = obj.rate.aggregate(average=Avg('rate'))['average']
        return rate_avg

    class Meta:
        model = Routes
        fields = "__all__"

# 댓글 조회
class CommentSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()

    def get_user(self, obj):
        return {'id': obj.user.pk, 'nickname': obj.user.nickname}

    class Meta:
        model = Comment
        exclude = ('route',)

# 여행경로 작성, 수정
class RouteCreateSerializer(serializers.ModelSerializer):
    destinations = DestinationSerializer(many=True)
    places = PlaceSerializer(many=True)

    class Meta:
        model = Routes
        fields = ("title", "content", "image", "duration")

# 여행경로 상세보기
class RouteDetailSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()
    comments = CommentSerializer(many=True)
    comment_count = serializers.SerializerMethodField()
    rate = serializers.SerializerMethodField()
    destinations = DestinationSerializer(many=True)
    places = PlaceSerializer(many=True)

    def get_user(self, obj):
        return {'id': obj.user.pk, 'nickname': obj.user.nickname}

    def get_comment_count(self, obj):
        return obj.comments.count()

    def get_rate(self, obj):
        rate_avg = obj.rate.aggregate(average=Avg('rate'))['average']
        return rate_avg

    class Meta:
        model = Routes
        fields = "__all__"
        
        
# 댓글 작성, 수정
class CommentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ("content",)
