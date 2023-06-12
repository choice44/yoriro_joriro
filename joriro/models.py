from django.db import models
from users.models import User


class Joriro(models.Model):
    user = models.ForeignKey(User, verbose_name="작성자",
                             on_delete=models.SET_NULL, related_name="joriros", null=True)
    image = models.ImageField("이미지", upload_to="joriro/%Y/%m/")
    model = models.PositiveIntegerField("모델")
    place = models.PositiveIntegerField("여행지")
    created_at = models.DateTimeField("작성일", auto_now_add=True)
    updated_at = models.DateTimeField("수정일", auto_now=True)
