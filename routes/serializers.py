from rest_framework import serializers
from django.db.models import Avg

from .models import Route, Comment, RouteArea, RouteSpot

from spots.models import Area, Spot
from spots.serializers import SpotSerializer

# 여행경로 지역
class RouteAreaSerializer(serializers.ModelSerializer):
    class Meta:
        model = RouteArea
        fields = ('area', 'sigungu')
        
class RouteSpotSerializer(serializers.ModelSerializer):
    spot = SpotSerializer()
    
    class Meta:
        model = RouteSpot
        fields = ['spot', 'order', 'day']


# 여행경로 전체 조회
class RouteSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()
    comment_count = serializers.SerializerMethodField()
    rate = serializers.SerializerMethodField()
    areas = RouteAreaSerializer(many=True)

    # 유저 정보 가져오기
    def get_user(self, obj):
        return {'id': obj.user.pk, 'nickname': obj.user.nickname}

    # 댓글 갯수 카운트
    def get_comment_count(self, obj):
        return obj.comments.count()

    # 해당 게시글의 평점을 모두 가져온 후 평균값 내기
    def get_rate(self, obj):
        rate_avg = obj.rates.aggregate(average=Avg('rate'))['average']
        return rate_avg

    class Meta:
        model = Route
        fields = "__all__"


# 댓글 조회
class CommentSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()

    # 유저 정보 가져오기
    def get_user(self, obj):
        return {'id': obj.user.pk, 'nickname': obj.user.nickname}

    class Meta:
        model = Comment
        exclude = ('route',)


# 여행경로 작성, 수정
class RouteCreateSerializer(serializers.ModelSerializer):
    areas = serializers.JSONField()
    spots = serializers.JSONField()

    class Meta:
        model = Route
        fields = ('title', 'title', 'content', 'image',
                  'cost', 'duration', 'spots', 'areas')
        
    # 파이썬 객체를 클라이언트에 보낼 수 있는 형식(json)으로 바꿔주는 메서드
    # instance = Route입니다.
    def to_representation(self, instance):
        # instance의 모든 필드를 기본형식으로 변환 -> 결과를 data라는 딕셔너리로 저장
        data = super().to_representation(instance)
        # Route에 연결된 모든 RouteSpot 객체를 찾음
        route_spots = RouteSpot.objects.filter(route=instance)
        
        # data에 areas의 값을 바꿔줍니다.
        # RouteAreaSerializer의 instance는 RouteArea인데 areas로 엮인 모든 객체를 직렬화
        # data['areas']의 값은 RouteAreaSerializer로 직렬화된 RouteArea 객체의 데이터
        data['areas'] = RouteAreaSerializer(instance.areas.all(), many=True).data
        # spot 정보를 data의 spots키에 할당
        data['spots'] = RouteSpotSerializer(route_spots, many=True).data
        # data는 딕셔너리, data는 areas와 spots에 해당 정보들을 포함하고 있음
        return data

    def create(self, validated_data):
        # 루트지역과 루트스팟 데이터 가져오기
        # 얘네 둘은 다대다 관계로 되어 있어서 특별 취급이 필요함
        route_area_data = validated_data.pop('areas')
        route_spots_data = validated_data.pop('spots')

        # areas데이터의 area id를 이용해 Area객체를 데이터베이스에서 가져옴
        area = Area.objects.get(pk=route_area_data['area'])
        route_area_data['area'] = area
        
        # 모델 생성
        # RouteArea모델은 route가 인자로 필요함
        route = Route.objects.create(**validated_data)
        routearea = RouteArea.objects.create(route=route, **route_area_data)

        # route_spots_data를 돌면서 각 spot마다의 정보를 가져옴
        for spot_data in route_spots_data:
            spot = Spot.objects.get(pk=spot_data['spot'])  # spots의 spot id를 이용해 Spot객체를 데이터베이스에서 가져옴
            spot_data['spot'] = spot
            RouteSpot.objects.create(route=route, **spot_data)
        
        return route

    def update(self, instance, validated_data):
        # 루트지역과 루트스팟 데이터 가져오기
        route_area_data = validated_data.pop('areas', None)
        route_spots_data = validated_data.pop('spots', None)

        # 새로운 정보를 기존 정보에 덮어 씌우기
        instance.title = validated_data.get('title', instance.title)
        instance.content = validated_data.get('content', instance.content)
        instance.image = validated_data.get('image', instance.image)
        instance.duration = validated_data.get('duration', instance.duration)
        instance.cost = validated_data.get('cost', instance.cost)

        # 기존 정보 삭제
        RouteArea.objects.filter(route=instance).delete()
        RouteSpot.objects.filter(route=instance).delete()

        # 새로운 areas 데이터 추가
        if route_area_data is not None:
            area = Area.objects.get(pk=route_area_data['area'])
            route_area_data['area'] = area
            RouteArea.objects.create(route=instance, **route_area_data)

        # 새로운 spots 데이터 추가
        if route_spots_data is not None:
            for spot_data in route_spots_data:
                spot = Spot.objects.get(pk=spot_data['spot'])
                spot_data['spot'] = spot
                RouteSpot.objects.create(route=instance, **spot_data)

        instance.save()
        return instance
    

# 여행경로 상세보기
class RouteDetailSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()
    comments = CommentSerializer(many=True)
    comment_count = serializers.SerializerMethodField()
    rate = serializers.SerializerMethodField()
    spots = RouteSpotSerializer(source='route_spots', many=True)    # source를 붙히지 않으면 Spot의 객체를 찾으러 가버림
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
