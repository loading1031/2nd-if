"""
Asynchronous views for core app.

Django 6.0+ Native Async ORM 사용:
- aget, alist, acreate, adelete, asave 등
"""
from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.http import require_http_methods


@require_http_methods(["POST"])
async def htmx_signup(request):
    """HTMX 회원가입 처리 (TODO: 서버 로직 구현 필요)"""
    # TODO: 디자인 확정 후 서버 로직 구현
    return HttpResponse("<p class='text-green-600'>회원가입 처리 (구현 예정)</p>")


@require_http_methods(["POST"])
async def htmx_login(request):
    """HTMX 로그인 처리 (TODO: 서버 로직 구현 필요)"""
    # TODO: 디자인 확정 후 서버 로직 구현
    return HttpResponse("<p class='text-green-600'>로그인 처리 (구현 예정)</p>")


@require_http_methods(["POST"])
async def htmx_logout(request):
    """HTMX 로그아웃 처리 (TODO: 서버 로직 구현 필요)"""
    # TODO: 서버 로직 구현
    response = HttpResponse()
    response['HX-Redirect'] = '/'
    return response
