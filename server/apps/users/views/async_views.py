from django.contrib.auth import alogin, alogout, authenticate, get_user_model
from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.http import require_http_methods
from asgiref.sync import sync_to_async

from ..forms import SignupForm, LoginForm

User = get_user_model()


@require_http_methods(["POST"])
async def htmx_signup(request):
    """HTMX 회원가입 처리."""
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

    response = HttpResponse()
    response["HX-Redirect"] = "/users/login/"
    return response


@require_http_methods(["POST"])
async def htmx_login(request):
    """HTMX 로그인 처리."""
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
