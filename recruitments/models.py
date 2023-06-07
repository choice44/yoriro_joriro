from django.db import models
from users.models import User


class Recruitments(models.Model):
    user = models.ForeignKey(User, verbose_name="유저", on_delete=models.CASCADE)
    title = models.CharField("제목", max_length=128)
    place = models.CharField("여행지", max_length=128)
    cost = models.IntegerField("경비")
    content = models.TextField("내용")
    departure = models.DateTimeField("출발일")
    arrival = models.DateTimeField("도착일")
    participator_count = models.IntegerField("모집 인원", blank=False)
    created_at = models.DateTimeField("작성일", auto_now_add=True)
    updated_at = models.DateTimeField("수정일", auto_now=True)
    is_complete = models.BooleanField("모집 완료 여부", default=False)
    # image = models.ImageField("이미지", upload_to="recruitments/%Y/%m/%d", blank=True)

    def __str__(self):
        return self.title


class Applicant(models.Model):
    user = models.ManyToManyField(User, verbose_name="신청자", blank=True)
    recruitment = models.ForeignKey(Recruitments, "동료 모집", on_delete=models.CASCADE)
    appeal = models.CharField("포부", max_length=128)
    acceptence = models.BooleanField("합격 여부", default=False)

    def __str__(self):
        return self.recruitment
    

class Participant(models.Model):
    user = models.ManyToManyField(User, verbose_name="신청자", blank=True)
    recruitment = models.ForeignKey(Recruitments, "동료 모집", on_delete=models.CASCADE)
    
    def __str__(self):
        return self.recruitment