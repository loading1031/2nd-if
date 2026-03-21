from django.contrib.auth import alogin, alogout, authenticate, get_user_model
from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.http import require_http_methods
from asgiref.sync import sync_to_async

from ..forms import SignupForm, LoginForm
from ..models import FingerprintLog, FingerprintBlacklist

User = get_user_model()


async def _check_fingerprint_blacklist(request) -> str | None:
    """핑거프린트 블랙리스트 확인. 차단이면 에러 메시지, 아니면 None."""
    fp = request.headers.get("X-Fingerprint") or request.COOKIES.get("_2ndif_fp")
    if not fp:
        return None
    if await FingerprintBlacklist.objects.filter(fingerprint=fp).aexists():
        return "이 기기에서는 서비스를 이용할 수 없습니다."
    return None


async def _log_fingerprint(request, user=None):
    """핑거프린트 로그 기록."""
    fp = request.headers.get("X-Fingerprint") or request.COOKIES.get("_2ndif_fp")
    if fp:
        await FingerprintLog.objects.acreate(user=user, fingerprint=fp)


@require_http_methods(["POST"])
async def htmx_signup(request):
    """HTMX 회원가입 처리."""
    # 핑거프린트 블랙리스트 확인
    block_msg = await _check_fingerprint_blacklist(request)
    if block_msg:
        return render(request, "pages/signup.html", {
            "error_message": block_msg,
            "errors": {},
        })

    form = SignupForm(request.POST)
    is_valid = await sync_to_async(form.is_valid)()

    if not is_valid:
        errors = {field: errs[0] for field, errs in form.errors.items()}
        return render(request, "pages/signup.html", {
            "error_message": "입력 정보를 확인해주세요.",
            "errors": errors,
        })

    data = form.cleaned_data
    user = User(email=data["email"], nickname=data["nickname"])
    user.set_password(data["password"])
    await user.asave()

    await _log_fingerprint(request, user)

    response = HttpResponse()
    response["HX-Redirect"] = "/users/login/"
    return response


@require_http_methods(["POST"])
async def htmx_login(request):
    """HTMX 로그인 처리."""
    # 핑거프린트 블랙리스트 확인
    block_msg = await _check_fingerprint_blacklist(request)
    if block_msg:
        return render(request, "pages/login.html", {
            "error_message": block_msg,
            "errors": {},
        })

    form = LoginForm(request.POST)
    is_valid = await sync_to_async(form.is_valid)()

    if not is_valid:
        return render(request, "pages/login.html", {
            "error_message": "이메일과 비밀번호를 입력해주세요.",
            "errors": {},
        })

    data = form.cleaned_data
    user = await sync_to_async(authenticate)(
        request,
        email=data["email"],
        password=data["password"],
    )

    if user is None:
        return render(request, "pages/login.html", {
            "error_message": "이메일 또는 비밀번호가 올바르지 않습니다.",
            "errors": {},
        })

    # remember-me 처리
    if not request.POST.get("remember-me"):
        request.session.set_expiry(0)

    await alogin(request, user)
    await _log_fingerprint(request, user)

    response = HttpResponse()
    response["HX-Redirect"] = "/"
    return response


@require_http_methods(["POST"])
async def htmx_logout(request):
    """HTMX 로그아웃 처리."""
    await alogout(request)
    response = HttpResponse()
    response["HX-Redirect"] = "/"
    return response
