from rest_framework import serializers

from .models import Recruitments, Applicant

class RecruitmentSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()    

    class Meta:
        model = Recruitments
        fields = "__all__"
        # fields = ("id", "user", "title", "content", "image", "created_at", "updated_at",) # 미구현 추가 내용 "category", "rate", "comment_count", "like_count",

    def get_user(self, obj):
        return {"id":obj.user.id, "nickname":obj.user.nickname}
        

class RecruitmentDetailSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()    
    participant = serializers.SerializerMethodField()    

    class Meta:
        model = Recruitments
        fields = "__all__"

    def get_user(self, obj):
        return {"id":obj.user.id, "nickname":obj.user.nickname}
        # return {"id":obj.user.id, "nickname":obj.user.email, "age":obj.user.age, "gender":obj.user.gender}
        # user모델에 age, gender가 없어서 잠시 주석처리 해놓았습니다.
        
    def get_participant(self, obj):
        participant_data = obj.participant.values("id", 'nickname')
        return participant_data

class RecruitmentEditSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()

    class Meta:
        model = Recruitments
        fields = ("id", "user", "title", "image", "place", "departure", "arrival", "content",) # 미구현 추가 내용 "category",
        
    def get_user(self, obj):
        return {"id":obj.user.id, "nickname":obj.user.nickname}
        # return {"id":obj.user.id, "nickname":obj.user.email, "age":obj.user.age, "gender":obj.user.gender}


class RecruitmentJoinSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()

    class Meta:
        model = Applicant
        fields = ("user", "appeal",)

    def get_user(self, obj):
        return {"id":obj.user.id, "nickname":obj.user.nickname}
