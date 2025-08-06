from django.shortcuts import render, redirect, HttpResponseRedirect
from django.db.models import Q
from django.contrib.auth import authenticate, login, logout
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import get_user_model





def index(request):
    return render(request, 'index.html')

def login_page(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        User = get_user_model()
        user_object = User.objects.filter(
            Q(username=username) | Q(email=username)
        ).first()

        if not user_object:
            messages.error(request, "User does not exist.")
            return render(request, 'core/login.html')
        

        user_object = authenticate(username=username, password=password)
        if user_object:
            login(request, user_object)
            next_url = request.GET.get('next')
            if next_url:
                return HttpResponseRedirect(next_url)
            else:
                return redirect('SalesDashboard')
            
    
    return render(request, 'core/login.html')

