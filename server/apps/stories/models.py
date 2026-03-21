from django.conf import settings
from django.db import models
from django.urls import reverse
from django_editorjs_fields import EditorJsJSONField


class Work(models.Model):
    """작품 모델."""

    class Status(models.TextChoices):
        ONGOING = "ongoing", "연재중"
        COMPLETED = "completed", "완결"
        SUSPENDED = "suspended", "중단"

    class Font(models.TextChoices):
        DEFAULT = "default", "기본 (Pretendard)"
        SERIF = "serif", "명조 (Noto Serif KR)"
        CLASSIC = "classic", "궁서 (Gowun Batang)"
        MODERN = "modern", "고딕 (Noto Sans KR)"

    class License(models.TextChoices):
        FREE = "free", "자유 분기 허용"
        NON_COMMERCIAL = "non_commercial", "비상업적 분기만 허용"
        SHARE_ALIKE = "share_alike", "동일 조건 변경 허락"
        NO_BRANCH = "no_branch", "분기 금지"

    title = models.CharField("제목", max_length=200)
    description = models.TextField("소개", blank=True, default="")
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="works",
    )
    license = models.CharField(
        "라이선스",
        max_length=20,
        choices=License.choices,
        default=License.FREE,
    )
    status = models.CharField(
        "상태",
        max_length=20,
        choices=Status.choices,
        default=Status.ONGOING,
    )
    font = models.CharField(
        "글씨체",
        max_length=20,
        choices=Font.choices,
        default=Font.DEFAULT,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "works"
        ordering = ["-created_at"]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("stories:work_detail", kwargs={"pk": self.pk})


class Episode(models.Model):
    """에피소드 모델."""

    work = models.ForeignKey(Work, on_delete=models.CASCADE, related_name="episodes")
    episode_number = models.PositiveIntegerField("화 번호")
    title = models.CharField("제목", max_length=200)
    content = EditorJsJSONField(
        plugins=[
            "@editorjs/paragraph",
            "@editorjs/header",
            "@editorjs/list",
            "@editorjs/image",
            "@editorjs/code",
            "@editorjs/quote",
        ],
        null=True,
        blank=True,
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="episodes",
    )
    is_paid = models.BooleanField("유료 여부", default=False)
    price = models.DecimalField("코인 가격", max_digits=10, decimal_places=2, null=True, blank=True)
    view_count = models.PositiveIntegerField("조회수", default=0)
    avg_rating = models.FloatField("별점 평균", null=True, blank=True)
    rating_count = models.PositiveIntegerField("별점 수", default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "episodes"
        ordering = ["episode_number"]
        unique_together = [("work", "episode_number")]

    def __str__(self):
        return f"{self.work.title} - {self.episode_number}화: {self.title}"


class Rating(models.Model):
    """에피소드 별점."""

    episode = models.ForeignKey(Episode, on_delete=models.CASCADE, related_name="ratings")
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="ratings",
    )
    score = models.PositiveSmallIntegerField("별점")  # 1~5
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "ratings"
        unique_together = [("episode", "user")]

    def __str__(self):
        return f"{self.user.nickname} → {self.episode}: {self.score}점"
