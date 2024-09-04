from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from .models import User, Message


@csrf_exempt
def index(request):
    if request.method == "POST":
        login = request.POST.get('login')
        password = request.POST.get('password')
        if User.objects.filter(email=login).first() is None:
            User.objects.create(email=login, password=password)

    return render(request, 'index.html')


def main(request):
    return render(request, 'login.html')
