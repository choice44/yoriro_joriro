from rest_framework import serializers

from .models import Recruitments, Applicant

class RecruitmentSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()    

    class Meta:
        model = Recruitments
        fields = ("id", "user", "title", "content", "image", "created_at", "updated_at",) # 미구현 추가 내용 "category", "rate", "comment_count", "like_count",

    def get_user(self, obj):
        return {"id":obj.user.id, "nickname":obj.user.email}
        

class RecruitmentDetailSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()    

    class Meta:
        model = Recruitments
        fields = "__all__"

    def get_user(self, obj):
        return {"id":obj.user.id, "nickname":obj.user.email}
        # return {"id":obj.user.id, "nickname":obj.user.email, "age":obj.user.age, "gender":obj.user.gender}
        