from rest_framework import serializers

from .models import Recruitments, Applicant

class RecruitmentSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()    

    class Meta:
        model = Recruitments
        fields = ("id", "user", "title", "content", "image", "created_at", "updated_at",) # 미구현 추가 내용 "category", "rate", "comment_count", "like_count",

    def get_user(self, obj):
        return {"id":obj.user.id, "nickname":obj.user.email} # nickname이 email인 부분 추후 수정 예정 / 지금은 제가 임시로 쓰는 user가 그렇게 되어있다보니....
        

class RecruitmentDetailSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()    

    class Meta:
        model = Recruitments
        fields = "__all__"

    def get_user(self, obj):
        return {"id":obj.user.id, "nickname":obj.user.email}
        # return {"id":obj.user.id, "nickname":obj.user.email, "age":obj.user.age, "gender":obj.user.gender}
        # 임시로 사용중인 user모델에 age, gender가 없어서 잠시 주석처리 해놓았습니다.
        
class RecruitmentEditSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()

    class Meta:
        model = Recruitments
        fields = ("id", "user", "title", "image", "place", "departure", "arrival", "content",) # 미구현 추가 내용 "category",

        
    def get_user(self, obj):
        return {"id":obj.user.id, "nickname":obj.user.email}
        # return {"id":obj.user.id, "nickname":obj.user.email, "age":obj.user.age, "gender":obj.user.gender}