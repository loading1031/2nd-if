from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.http import require_http_methods
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import send_mail
from django.conf import settings
from asgiref.sync import sync_to_async

User = get_user_model()


def password_reset_page(request):
    """비밀번호 찾기 페이지"""
    return render(request, 'pages/password_reset.html')


def password_reset_confirm_page(request, uidb64, token):
    """새 비밀번호 입력 페이지"""
    return render(request, 'pages/password_reset_confirm.html', {
        'uidb64': uidb64,
        'token': token,
    })


@require_http_methods(["POST"])
async def htmx_password_reset(request):
    """비밀번호 재설정 이메일 발송"""
    email = request.POST.get('email', '').strip()

    if not email:
        return render(request, 'pages/password_reset.html', {
            'error_message': '이메일 주소를 입력해주세요.'
        })

    try:
        user = await User.objects.aget(email=email)
        # Generate token
        token = await sync_to_async(default_token_generator.make_token)(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))

        # Build reset URL
        reset_url = f"{request.scheme}://{request.get_host()}/users/password-reset/{uid}/{token}/"

        # Send email
        from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@2nd-if.com')
        await sync_to_async(send_mail)(
            subject='[2nd-if] 비밀번호 재설정',
            message=f'아래 링크를 클릭하여 비밀번호를 재설정하세요:\n\n{reset_url}\n\n이 링크는 1회만 사용 가능합니다.',
            from_email=from_email,
            recipient_list=[email],
            fail_silently=False,
        )
    except User.DoesNotExist:
        pass  # Don't reveal whether email exists
    except Exception:
        pass  # Email send failure — still show success to prevent enumeration

    # Always show success (prevents email enumeration)
    return render(request, 'pages/password_reset_done.html')


@require_http_methods(["POST"])
async def htmx_password_reset_confirm(request, uidb64, token):
    """비밀번호 재설정 확인"""
    new_password = request.POST.get('new_password', '')
    new_password_confirm = request.POST.get('new_password_confirm', '')

    if new_password != new_password_confirm:
        return render(request, 'pages/password_reset_confirm.html', {
            'error_message': '비밀번호가 일치하지 않습니다.',
            'uidb64': uidb64,
            'token': token,
        })

    if len(new_password) < 8:
        return render(request, 'pages/password_reset_confirm.html', {
            'error_message': '비밀번호는 8자 이상이어야 합니다.',
            'uidb64': uidb64,
            'token': token,
        })

    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = await User.objects.aget(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        return render(request, 'pages/password_reset_confirm.html', {
            'error_message': '유효하지 않은 링크입니다.',
            'uidb64': uidb64,
            'token': token,
        })

    # Verify token
    is_valid = await sync_to_async(default_token_generator.check_token)(user, token)
    if not is_valid:
        return render(request, 'pages/password_reset_confirm.html', {
            'error_message': '만료되었거나 이미 사용된 링크입니다.',
            'uidb64': uidb64,
            'token': token,
        })

    # Set new password
    await sync_to_async(user.set_password)(new_password)
    await user.asave()

    return render(request, 'pages/password_reset_complete.html')
