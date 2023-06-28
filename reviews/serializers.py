from rest_framework import serializers
from reviews.models import Review


# 리뷰 목록 조회
class ReviewListSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()
    spot = serializers.SerializerMethodField()
    created_at = serializers.SerializerMethodField()
    updated_at = serializers.SerializerMethodField()
    like_count = serializers.SerializerMethodField()
    
    
    def get_user(self, obj):
        return {"id": obj.user.id, "nickname": obj.user.nickname}
    
    
    def get_spot(self, obj):
        return {
            "id": obj.spot.id,
            "type": obj.spot.type,
            "area": obj.spot.area.id,
            "sigungu": obj.spot.sigungu,
            "title": obj.spot.title, 
            "addr": obj.spot.addr1
            }
    
    
    def get_created_at(self, obj):
        return obj.created_at.strftime("%Y-%m-%d %H:%M")
    
    
    def get_updated_at(self, obj):
        return obj.updated_at.strftime("%Y-%m-%d %H:%M")
     
    
    def get_like_count(self, obj):
        return obj.likes.count()
    
    
    class Meta:
        model = Review
        fields = "__all__"
        

# 리뷰 상세 조회        
class ReviewDetailSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()
    user_image = serializers.SerializerMethodField()
    spot = serializers.SerializerMethodField()
    created_at = serializers.SerializerMethodField()
    updated_at = serializers.SerializerMethodField()
    like_count = serializers.SerializerMethodField()
    
    
    def get_user(self, obj):
        if obj.user.image:
            return {"id": obj.user.id, "nickname": obj.user.nickname, "image": obj.user.image.url}
        else:
            return {"id": obj.user.id, "nickname": obj.user.nickname}
    
    
    def get_user_image(self, obj):
        if obj.user.image:
            return obj.user.image.url
        else:
            return None
    
    
    def get_spot(self, obj):
        return {
            "id": obj.spot.id,
            "type": obj.spot.type,
            "area": obj.spot.area.id,
            "sigungu": obj.spot.sigungu,
            "title": obj.spot.title, 
            "addr": obj.spot.addr1,
            "tel": obj.spot.tel,
            "image": obj.spot.firstimage
            }
    
    
    def get_created_at(self, obj):
        return obj.created_at.strftime("%Y-%m-%d %H:%M")
    
    
    def get_updated_at(self, obj):
        return obj.updated_at.strftime("%Y-%m-%d %H:%M")
     
    
    def get_like_count(self, obj):
        return obj.likes.count()
    
    
    class Meta:
        model = Review
        fields = "__all__"
        

# 리뷰 수정
class ReviewUpdateSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Review
        fields = ("title", "content", "rate", "visited_date", "image")
        
        
# 리뷰 작성
class ReviewCreateSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Review
        fields = ("spot", "title", "content", "rate", "visited_date", "image")      
