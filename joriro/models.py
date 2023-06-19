from django.db import models
from users.models import User


class Joriro(models.Model):
    MODEL_CHOICE = [
        (1, "품질"),
        (2, "보통"),
        (3, "성능"),
    ]

    PLACE_CHOICE = [
        (1, "6.25"),
        (2, "해운대"),
        (3, "한라산"),
        (4, "판문점"),
        (5, "석굴암"),
    ]

    user = models.ForeignKey(User, verbose_name="작성자",
                             on_delete=models.SET_NULL, related_name="joriros", null=True)
    image = models.ImageField("이미지", upload_to="joriro/%Y/%m/")
    model = models.PositiveIntegerField("모델", choices=MODEL_CHOICE, default=2)
    place = models.PositiveIntegerField("여행지", choices=PLACE_CHOICE)
    result = models.CharField("결과", max_length=250, null=True, blank=True)
    created_at = models.DateTimeField("작성일", auto_now_add=True)
    updated_at = models.DateTimeField("수정일", auto_now=True)
