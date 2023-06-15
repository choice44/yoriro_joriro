from django.db import models
from users.models import User
from routes.models import Spot

class Review(models.Model):
    RATE_CHOICES = (
        (1, "⭐"),
        (2, "⭐⭐"),
        (3, "⭐⭐⭐"),
        (4, "⭐⭐⭐⭐"),
        (5, "⭐⭐⭐⭐⭐"),
    )
    
    user = models.ForeignKey(User, verbose_name="작성자", on_delete=models.CASCADE, related_name="reviews")
    spot = models.ForeignKey(Spot, verbose_name="장소", on_delete=models.CASCADE, related_name="spot_reviews")
    rate = models.PositiveSmallIntegerField("평점", choices=RATE_CHOICES, default=1)
    title = models.CharField("제목", max_length=150)
    content = models.TextField("리뷰")
    visited_date = models.DateField("방문일")
    created_at = models.DateTimeField("작성시각", auto_now_add=True)
    updated_at = models.DateTimeField("수정시각", auto_now=True)
    image = models.ImageField("대표 이미지", upload_to="review/images/%Y/%m/", blank=True)
    likes = models.ManyToManyField(User, verbose_name="좋아요", blank=True, related_name="like_reviews")
    
    
    def __str__(self):
        return self.title
    