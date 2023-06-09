from rest_framework import serializers
from reviews.models import Review


# 리뷰 전체 목록 조회, 리뷰 상세 조회, 리뷰 작성
class ReviewSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()
    created_at = serializers.SerializerMethodField()
    updated_at = serializers.SerializerMethodField()
    like_count = serializers.SerializerMethodField()
    
    
    def get_user(self, obj):
        return {'nickname': obj.user.nickname, 'pk': obj.user.pk}
    
    
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