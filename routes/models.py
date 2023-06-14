from django.db import models
from users.models import User


class Area(models.Model):
    name = models.CharField("이름", max_length=50)
    
    def __str__(self):
        return self.name
    

class Sigungu(models.Model):
    area = models.ForeignKey(Area, verbose_name="시도", on_delete=models.CASCADE, related_name="sigungus")
    code = models.IntegerField("코드", default=0)
    name = models.CharField("이름", max_length=50)

    def __str__(self):
        return self.name

class Spot(models.Model):
    area = models.ForeignKey(Area, verbose_name="시도", on_delete=models.CASCADE, related_name="spots", blank=True, null=True)  
    type = models.IntegerField("타입")
    title = models.CharField("제목", max_length=50)
    sigungu = models.IntegerField("시군구", blank=True, null=True)
    addr1 = models.CharField("주소", max_length=200, blank=True, null=True)
    addr2 = models.CharField("상세주소", max_length=200, blank=True, null=True)
    mapx = models.FloatField("x좌표")
    mapy = models.FloatField("y좌표")
    firstimage = models.TextField("이미지", blank=True, null=True)
    tel = models.CharField("전화번호", max_length=20, blank=True, null=True)
    
    def __str__(self):
        return self.title

class Route(models.Model):
    user = models.ForeignKey(User, verbose_name="작성자", on_delete=models.CASCADE, related_name="routes")
    title = models.CharField("제목", max_length=50)
    content = models.TextField("내용")
    created_at = models.DateTimeField("작성시각", auto_now_add=True)
    updated_at = models.DateTimeField("수정시각", auto_now=True)
    image = models.ImageField("이미지", upload_to="Routes/%Y/%m/", blank=True)
    cost = models.IntegerField("경비")
    duration = models.CharField("기간", max_length=50)
    spots = models.ManyToManyField(Spot, verbose_name="루트스팟", blank=True, related_name='routes')
    
    def __str__(self):
        return self.title


class RouteArea(models.Model):
    route = models.ForeignKey(Route, verbose_name="경로", on_delete=models.CASCADE, related_name="areas")
    area = models.ForeignKey(Area, verbose_name="시도", on_delete=models.CASCADE, related_name="routes", blank=True, null=True)  
    sigungu = models.IntegerField("시군구", blank=True, null=True)
    
    def __str__(self):
        return f"Route: {self.route.title}, Area: {self.area.name}, Sigungu: {self.sigungu}"


class RouteRate(models.Model):
    route = models.ForeignKey(Route, verbose_name="경로", on_delete=models.CASCADE, related_name="rates")
    user = models.ForeignKey(User, verbose_name="작성자", on_delete=models.CASCADE, related_name="rates")
    rate = models.IntegerField("평가", default=0)
    
    
class Comment(models.Model):
    user = models.ForeignKey(User, verbose_name="작성자", on_delete=models.CASCADE, related_name="comments")
    route = models.ForeignKey(Route, verbose_name="경로", on_delete=models.CASCADE, related_name="comments")
    content = models.TextField("내용")
    created_at = models.DateTimeField("작성시각", auto_now_add=True)
    updated_at = models.DateTimeField("수정시각", auto_now=True)
    
    def __str__(self):
        return self.content
