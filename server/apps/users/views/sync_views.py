from django.shortcuts import render

# Create your views here.
def signup_page(request):
    """Signup page view."""
    return render(request, 'pages/signup.html')


def login_page(request):
    """Login page view."""
    return render(request, 'pages/login.html')
