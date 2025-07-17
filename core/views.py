from django.shortcuts import render, redirect
from django.db.models import Q
from django.contrib.auth import authenticate, login, logout
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import get_user_model



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
            print("User logged in successfully.")
            messages.success(request, "Login successful.")
            return redirect('sales/sales_dashboard/')
    
    return render(request, 'core/login.html')

