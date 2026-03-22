from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models


class UserManager(BaseUserManager):
    """이메일을 로그인 ID로 사용하는 커스텀 매니저."""

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("이메일은 필수입니다.")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    """커스텀 User 모델. 이메일을 로그인 ID로 사용."""

    username = None
    email = models.EmailField("이메일", unique=True)
    nickname = models.CharField("닉네임", max_length=50)
    wallet_address = models.CharField("지갑 주소", max_length=200, blank=True, default="")
    point_balance = models.IntegerField("포인트 잔액", default=0)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["nickname"]

    objects = UserManager()

    class Meta:
        db_table = "users"

    def __str__(self):
        return self.nickname


class FingerprintLog(models.Model):
    """브라우저 핑거프린트 로그."""

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="fingerprint_logs")
    fingerprint = models.CharField("핑거프린트", max_length=64, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "fingerprint_logs"

    def __str__(self):
        return f"{self.fingerprint[:16]}... ({self.user or 'anon'})"


class FingerprintBlacklist(models.Model):
    """차단된 핑거프린트."""

    fingerprint = models.CharField("핑거프린트", max_length=64, unique=True)
    reason = models.TextField("차단 사유")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "fingerprint_blacklist"

    def __str__(self):
        return f"{self.fingerprint[:16]}... (차단)"
