from django.conf import settings
from django.db import models
from django.urls import reverse


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
    content = models.TextField("본문", blank=True, default="")
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="episodes",
    )
    branch_direction = models.CharField("분기 방향", max_length=100, blank=True, default="")
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


class EpisodePurchase(models.Model):
    """에피소드 구매 기록 (Polygon 스테이블코인 결제)."""

    episode = models.ForeignKey(Episode, on_delete=models.CASCADE, related_name="purchases")
    buyer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="purchases",
    )
    tx_hash = models.CharField("트랜잭션 해시", max_length=66, unique=True)
    token = models.CharField("토큰", max_length=10)  # "USDC" or "USDT"
    amount = models.DecimalField("결제 금액", max_digits=20, decimal_places=6)
    confirmed = models.BooleanField("확인 여부", default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "episode_purchases"
        unique_together = [("episode", "buyer")]

    def __str__(self):
        return f"{self.buyer} → {self.episode} ({self.amount} {self.token})"


class EpisodeLink(models.Model):
    """에피소드 간 연결 (그래프 관계)."""

    class LinkType(models.TextChoices):
        NEXT = "next", "다음 화"
        BRANCHES_FROM = "branches_from", "분기 원본"

    from_episode = models.ForeignKey(
        Episode,
        on_delete=models.CASCADE,
        related_name="outgoing_links",
    )
    to_episode = models.ForeignKey(
        Episode,
        on_delete=models.CASCADE,
        related_name="incoming_links",
    )
    link_type = models.CharField(
        "연결 유형",
        max_length=20,
        choices=LinkType.choices,
    )
    is_original = models.BooleanField("원작 여부", default=False)
    visit_count = models.PositiveIntegerField("방문 수", default=0)
    engagement_score = models.FloatField("참여 점수", default=0.0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "episode_links"
        unique_together = [("from_episode", "to_episode", "link_type")]
        indexes = [
            models.Index(fields=["from_episode", "link_type"]),
            models.Index(fields=["to_episode", "link_type"]),
        ]

    def __str__(self):
        return f"{self.from_episode} → {self.to_episode} ({self.link_type})"
