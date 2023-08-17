from django.shortcuts import render

# Create your views here.


from django.shortcuts import render , redirect
from django.http import HttpResponse
from django.views.decorators.cache import never_cache
from django.contrib.auth import authenticate
from django.contrib import auth
# from user.models import User 
# from .models import Game


# Create your views here.

@never_cache
def signIn(request):
    if request.user.is_authenticated and request.session.get('admin'):
        return redirect('admin-home')
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        admin = authenticate(request , username = username, password = password)
    
        if admin is not None and admin.is_superuser:
            request.session['admin'] = username
            auth.login(request , admin)
            return redirect('admin-home')
        else:
            return render(request , 'adminpanel/login.html', {'error' : 'Invalid username or password'})   
    return render(request , 'adminpanel/login.html' )

@never_cache
def adminHome(request):
    if request.session.get('admin') is None:
        return redirect('admin-signin')
    
    return render(request , 'adminpanel/adminhome.html' )

@never_cache
def adminLogout(request):
    # request.session.flush()
    request.session.pop('user', None)
    auth.logout(request)
    return redirect('admin-signin')


def gameDetails(request):
    return render(request , 'adminpanel/gamesdetails.html')





