from rest_framework import serializers

from .models import Recruitments, Applicant


class RecruitmentSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()

    class Meta:
        model = Recruitments
        fields = "__all__"

    def get_user(self, obj):
        return {"id":obj.user.id, "nickname":obj.user.nickname, "age":obj.user.age, "gender":obj.user.gender}
        

class RecruitmentDetailSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()
    participant = serializers.SerializerMethodField()
    participant_now = serializers.SerializerMethodField()

    class Meta:
        model = Recruitments
        fields = "__all__"

    def get_user(self, obj):
        if obj.user.image:
            return {"id": obj.user.id, "nickname": obj.user.nickname, "age":obj.user.age, "gender":obj.user.gender, "image": obj.user.image.url}
        else:
            return {"id": obj.user.id, "nickname": obj.user.nickname, "age":obj.user.age, "gender":obj.user.gender}
        
    def get_participant(self, obj):
        participant_data = obj.participant.values(
            "id", 'nickname', "age", "gender", "image")
        return participant_data

    def get_participant_now(self, obj):
        participant_now_data = obj.participant.count()
        return participant_now_data


class RecruitmentEditSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()

    class Meta:
        model = Recruitments
        fields = ("id", "user", "title", "image", "place", "departure", "arrival", "content", "participant_max") # 미구현 추가  내용 "category",
        
    def get_user(self, obj):
        return {"id":obj.user.id, "nickname":obj.user.nickname, "age":obj.user.age, "gender":obj.user.gender}


class RecruitmentJoinSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()

    class Meta:
        model = Applicant
        fields = ("id", "user", "appeal", "acceptence",)

    def get_user(self, obj):
        if obj.user.image:
            return {"id": obj.user.id, "nickname": obj.user.nickname, "age":obj.user.age, "gender":obj.user.gender, "image": obj.user.image.url}
        else:
            return {"id": obj.user.id, "nickname": obj.user.nickname, "age":obj.user.age, "gender":obj.user.gender}
