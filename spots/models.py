from django.db import models
from django.urls import reverse


class Area(models.Model):
    name = models.CharField("이름", max_length=50)

    def get_absolute_url(self):
        return reverse('sigungu_view', kwargs={"area_id": self.id})

    def __str__(self):
        return self.name


class Sigungu(models.Model):
    area = models.ForeignKey(Area, verbose_name="시도",
                             on_delete=models.CASCADE, related_name="sigungus")
    code = models.IntegerField("코드", default=0)
    name = models.CharField("이름", max_length=50)

    def __str__(self):
        return self.name


class Spot(models.Model):
    area = models.ForeignKey(Area, verbose_name="시도", on_delete=models.CASCADE,
                             related_name="spots", blank=True, null=True)
    type = models.IntegerField("타입")
    title = models.CharField("제목", max_length=200)
    sigungu = models.IntegerField("시군구", blank=True, null=True)
    addr1 = models.CharField("주소", max_length=200, blank=True, null=True)
    addr2 = models.CharField("상세주소", max_length=200, blank=True, null=True)
    mapx = models.FloatField("x좌표")
    mapy = models.FloatField("y좌표")
    firstimage = models.TextField("이미지", blank=True, null=True)
    tel = models.CharField("전화번호", max_length=200, blank=True, null=True)

    def get_absolute_url(self):
        return reverse('spot_detail_view', kwargs={"spot_id": self.id})

    def __str__(self):
        return self.title
