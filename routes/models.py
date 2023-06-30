from django.db import models
from users.models import User
from spots.models import Area, Spot


class Route(models.Model):
    user = models.ForeignKey(User, verbose_name="작성자",
                             on_delete=models.CASCADE, related_name="routes")
    title = models.CharField("제목", max_length=50)
    content = models.TextField("내용")
    created_at = models.DateTimeField("작성시각", auto_now_add=True)
    updated_at = models.DateTimeField("수정시각", auto_now=True)
    image = models.ImageField("이미지", upload_to="Routes/%Y/%m/", blank=True)
    cost = models.PositiveIntegerField("경비")
    duration = models.PositiveIntegerField("기간")
    spots = models.ManyToManyField(
        Spot, verbose_name="루트스팟", blank=True, related_name='routes', through='RouteSpot')

    def __str__(self):
        return self.title


class RouteSpot(models.Model):
    route = models.ForeignKey(Route, on_delete=models.CASCADE, related_name="route_spots")
    spot = models.ForeignKey(Spot, on_delete=models.CASCADE)
    order = models.PositiveIntegerField("순서")
    day = models.PositiveIntegerField("일차")
    

class RouteArea(models.Model):
    route = models.ForeignKey(Route, verbose_name="경로",
                              on_delete=models.CASCADE, related_name="areas")
    area = models.ForeignKey(Area, verbose_name="시도", on_delete=models.CASCADE,
                             related_name="routes", blank=True, null=True)
    sigungu = models.PositiveIntegerField("시군구", blank=True, null=True)

    def __str__(self):
        return f"Route: {self.route.title}, Area: {self.area.name}, Sigungu: {self.sigungu}"


class RouteRate(models.Model):
    route = models.ForeignKey(Route, verbose_name="경로",
                              on_delete=models.CASCADE, related_name="rates")
    user = models.ForeignKey(User, verbose_name="작성자",
                             on_delete=models.CASCADE, related_name="rates")
    rate = models.PositiveIntegerField("평가", default=0)


class Comment(models.Model):
    user = models.ForeignKey(User, verbose_name="작성자",
                             on_delete=models.CASCADE, related_name="comments")
    route = models.ForeignKey(Route, verbose_name="경로",
                              on_delete=models.CASCADE, related_name="comments")
    content = models.TextField("내용")
    created_at = models.DateTimeField("작성시각", auto_now_add=True)
    updated_at = models.DateTimeField("수정시각", auto_now=True)

    def __str__(self):
        return self.content
