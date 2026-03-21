from django.contrib.auth.decorators import login_required
from django.shortcuts import render


def work_list(request):
    """작품 목록 페이지."""
    return render(request, "stories/pages/work_list.html")


def work_detail(request, pk):
    """작품 상세 페이지."""
    return render(request, "stories/pages/work_detail.html", {"work_id": pk})


@login_required
def work_create(request):
    """작품 생성 페이지."""
    return render(request, "stories/pages/work_create.html")


@login_required
def episode_write(request, work_pk):
    """에피소드 작성 페이지."""
    return render(request, "stories/pages/episode_write.html", {"work_id": work_pk})


def episode_read(request, work_pk, episode_number):
    """에피소드 읽기 페이지."""
    return render(request, "stories/pages/episode_read.html", {
        "work_id": work_pk,
        "episode_number": episode_number,
    })
