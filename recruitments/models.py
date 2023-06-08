from django.db import models
from users.models import User
from django.core.validators import MinValueValidator, MaxValueValidator


class Recruitments(models.Model):
    user = models.ForeignKey(User, verbose_name="유저", on_delete=models.CASCADE)
    title = models.CharField("제목", max_length=50)
    place = models.CharField("여행지", max_length=128)
    cost = models.PositiveIntegerField("경비")
    content = models.TextField("내용")
    departure = models.DateTimeField("출발일")
    arrival = models.DateTimeField("도착일")
    participator_count = models.PositiveIntegerField("모집 인원", blank=False, validators=[MinValueValidator(1), MaxValueValidator(10)])
    created_at = models.DateTimeField("작성일", auto_now_add=True)
    updated_at = models.DateTimeField("수정일", auto_now=True)

    IS_COMPLETE_CHOICE = [
        (0, "모집중"),
        (1, "모집완료"),
        (2, "여행중"),
        (3, "여행완료"),
    ]
    is_complete = models.CharField("모집 완료 여부", max_length=20, choices=IS_COMPLETE_CHOICE, default=0)
    image = models.ImageField("이미지", upload_to="recruitments/%Y/%m/", blank=True)
    
    participant = models.ManyToManyField(User, verbose_name="참가자", blank=True, related_name="participant")
    
    def __str__(self):
        return self.title


class Applicant(models.Model):
    user = models.ForeignKey(User, verbose_name="신청자", blank=True, on_delete=models.CASCADE)
    recruitment = models.ForeignKey(Recruitments, verbose_name="동료 모집", on_delete=models.CASCADE)
    appeal = models.CharField("포부", max_length=128)
    acceptence = models.BooleanField("합격 여부", default=False)

    def __str__(self):
        return self.appeal
    

# class Participant(models.Model):
#     user = models.ManyToManyField(User, verbose_name="참가자", blank=True)
#     recruitment = models.ForeignKey(Recruitments, verbose_name="동료 모집", on_delete=models.CASCADE)
    
#     def __str__(self):
#         return self.user
