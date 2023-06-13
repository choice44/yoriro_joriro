from rest_framework import serializers
from django.db.models import Avg

from .models import Route, Comment, Area, Sigungu, Spot, RouteArea

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

# 스팟
class SpotSerializer(serializers.ModelSerializer):
    class Meta:
        model = Spot
        fields = "__all__"      

# 루트 지역        
class RouteAreaSerializer(serializers.ModelSerializer):
    class Meta:
        model = RouteArea
        fields = ('area', 'sigungu')

# 여행경로 전체 조회
class RouteSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()
    comment_count = serializers.SerializerMethodField()
    rate = serializers.SerializerMethodField()
    areas = RouteAreaSerializer(many=True)

    def get_user(self, obj):
        return {'id': obj.user.pk, 'nickname': obj.user.nickname}

    def get_comment_count(self, obj):
        return obj.comments.count()

    def get_rate(self, obj):
        rate_avg = obj.rates.aggregate(average=Avg('rate'))['average']
        return rate_avg

    class Meta:
        model = Route
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
    areas = RouteAreaSerializer()

    class Meta:
        model = Route
        fields = ('title', 'title', 'content', 'image', 'cost', 'duration', 'routespot', 'areas')
    
    def create(self, validated_data):
        route_area_data = validated_data.pop('areas')
        routespot_data = validated_data.pop('routespot')

        route = Route.objects.create(**validated_data)
        
        routearea = RouteArea.objects.create(route=route, **route_area_data)
        
        # 리스트 형태로 전달하면 리스트 자체를 하나의 인자로 처리
        # 리스트의 요소들을 개별 인자로 전달하기 위해 *을 사용
        route.routespot.add(*routespot_data)
        return route
     
    def update(self, instance, validated_data):
        route_area_data = validated_data.pop('areas')
        routespot_data = validated_data.pop('routespot')
        
        instance.title = validated_data.get('title', instance.title)
        instance.content = validated_data.get('content', instance.content)
        instance.image = validated_data.get('image', instance.image)
        instance.duration = validated_data.get('duration', instance.duration)
        instance.cost = validated_data.get('cost', instance.cost)
        
        instance.routespot.set(routespot_data)
        
        instance.areas.all().delete()
        
        routearea = RouteArea.objects.create(route=instance, **route_area_data)
        
        instance.save()
        return instance
    

# 여행경로 상세보기
class RouteDetailSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()
    comments = CommentSerializer(many=True)
    comment_count = serializers.SerializerMethodField()
    rate = serializers.SerializerMethodField()
    routespot = SpotSerializer(many=True)
    areas = RouteAreaSerializer(many=True)

    def get_user(self, obj):
        return {'id': obj.user.pk, 'nickname': obj.user.nickname}

    def get_comment_count(self, obj):
        return obj.comments.count()

    def get_rate(self, obj):
        rate_avg = obj.rates.aggregate(average=Avg('rate'))['average']
        return rate_avg

    class Meta:
        model = Route
        fields = "__all__"
        
        
# 댓글 작성, 수정
class CommentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ("content",)
