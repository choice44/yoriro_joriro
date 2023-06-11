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
        fields = ("title", "content", "image", "duration", "cost", "destinations", "places")
    
    # drf에서는 중첩된 필드에 대해 조회만 가능하게 지원한다.
    # 그래서 입력값을 저장하기 위해 create, update메서드를 오버라이드 해줘야한다.    
    def create(self, validated_data):
        destinations_data = validated_data.pop('destinations', [])
        places_data = validated_data.pop('places', [])
        
        route = Routes.objects.create(**validated_data)
        
        for destination_data in destinations_data:
            Destinations.objects.create(route=route, **destination_data)
        
        for place_data in places_data:
            Places.objects.create(route=route, **place_data)
        
        return route    
    
    def update(self, instance, validated_data):
        # 기존 데이터를 새로운 데이터로 교체
        # 역참조 관계에서는 직접 값을 할당하는 것이 허용되지 않아서 destinations, places는 별도로 작성
        instance.title = validated_data.get('title', instance.title)
        instance.content = validated_data.get('content', instance.content)
        instance.image = validated_data.get('image', instance.image)
        instance.duration = validated_data.get('duration', instance.duration)
        instance.cost = validated_data.get('cost', instance.cost)

        # 업데이트 할 데이터를 할당
        destinations_data = validated_data.pop('destinations', [])
        places_data = validated_data.pop('places', [])

        # 목적지 업데이트
        # 목록 전체를 비우고 시작하기에 빈 값을 넣게되면 그대로 비워버린다.
        # 수정할때 프론트에서 반드시 이전 정보를 불러와 입력란에 정보를 넣어줘야한다.
        instance.destinations.all().delete()
        for destination_data in destinations_data:
            Destinations.objects.create(route=instance, **destination_data)

        # 장소 업데이트
        instance.places.all().delete()
        for place_data in places_data:
            Places.objects.create(route=instance, **place_data)

        instance.save()
        return instance

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
