from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser


class UserManager(BaseUserManager):
    def create_user(self, email, nickname, password=None):
        if not email:
            raise ValueError("Users must have an email address")

        user = self.model(email=self.normalize_email(email), nickname=nickname)

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, nickname, password=None):
        user = self.create_user(
            email,
            nickname=nickname,
            password=password,
        )
        user.is_admin = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser):
    area = models.ForeignKey(
        "spots.Area",
        verbose_name="시도",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    email = models.EmailField(
        verbose_name="이메일",
        max_length=255,
        unique=True,
    )
    nickname = models.CharField(verbose_name="닉네임", max_length=50, blank=False)
    image = models.ImageField(upload_to="users", blank=True)
    bio = models.CharField(verbose_name="자기소개", max_length=100, blank=True)
    sigungu = models.IntegerField(verbose_name="시군구", null=True, blank=True)
    GENDER_CHOICES = (
        ("M", "남성"),
        ("F", "여성"),
    )
    gender = models.CharField(
        verbose_name="성별", max_length=1, choices=GENDER_CHOICES, blank=True
    )
    age = models.PositiveIntegerField(verbose_name="나이", null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(verbose_name="활성화 여부", default=True)
    is_admin = models.BooleanField(verbose_name="관리자 여부", default=False)
    followings = models.ManyToManyField(
        "self", symmetrical=False, related_name="followers", blank=True
    )

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["nickname"]

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return True

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True

    @property
    def is_staff(self):
        "Is the user a member of staff?"
        # Simplest possible answer: All admins are staff
        return self.is_admin
