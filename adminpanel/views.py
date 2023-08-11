from django.shortcuts import render , redirect
from django.http import HttpResponse
from django.views.decorators.cache import never_cache
from django.contrib.auth import authenticate
from django.contrib import auth

# Create your views here.

@never_cache
def signIn(request):
    # if request.user.is_authenticated and request.session.get('admin'):
    #     return redirect('admin-home')
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        admin = authenticate(request , username = username, password = password)
    
        if admin is not None and admin.is_superuser:
            request.session['admin'] = username
            auth.login(request , admin)
            return redirect('admin-home')
        else:
            return render(request , 'login.html', {'error' : 'Invalid username or password'})   
    return render(request , 'login.html' )

def adminHome(request):
    return HttpResponse('this is admin home page')