from django.db import models
from users.models import User

class Routes(models.Model):
    
    user = models.ForeignKey(User, verbose_name="작성자", on_delete=models.CASCADE, related_name="user")
    title = models.CharField("제목", max_length=50)
    content = models.TextField("내용")
    created_at = models.DateTimeField("작성시각", auto_now_add=True)
    updated_at = models.DateTimeField("수정시각", auto_now=True)
    image = models.ImageField("이미지", upload_to="article/%Y/%m/", blank=True)
    cost = models.IntegerField("경비")
    duration = models.CharField("기간")
    
    
    def __str__(self):
        return self.title


class Destinations(models.Model):
    route = models.ForeignKey(Routes, verbose_name="경로", on_delete=models.CASCADE, related_name="route")
    area_code = models.IntegerField("지역코드")
    sigungu_code = models.IntegerField("시군구코드")
    

class Places(models.Model):
    route = models.ForeignKey(Routes, verbose_name="경로", on_delete=models.CASCADE, related_name="route")
    content_id = models.IntegerField("컨텐트아이디")
    content_type_id = models.IntegerField("컨텐트타입아이디")