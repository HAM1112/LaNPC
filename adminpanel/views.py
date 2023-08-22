from django.shortcuts import render

from django.shortcuts import render , redirect
from django.http import HttpResponse
from django.views.decorators.cache import never_cache
from django.contrib.auth import authenticate
from django.contrib import auth
 
from account.models import User
from .models import Game , Category

from .forms import GameForm

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
    
    users = User.objects.all()
    games = Game.objects.all()
    
    context = {
        'usersCount' : users.count(),
        'gamesCount' : games.count(),
    }
    print(users.count())
    return render(request , 'adminpanel/adminhome.html' , context )

@never_cache
def adminLogout(request):
    # request.session.flush()
    request.session.pop('user', None)
    auth.logout(request)
    return redirect('admin-signin')

#-----------------------------------------------#
# ------------- USER RELATED ------------------ #
#-----------------------------------------------#

# Display all users in a table
def usersList(request):
    
    # users = User.objects.filter(is_superuser=False)
    users = User.objects.all()
    
    context = {
        'users' : users,
    }
    
    return render(request , 'adminpanel/usersdetails.html' , context)

# diplay details of single users
def singleUser(request , userId):
    
    user = User.objects.get(id=userId)
    
    context = {
        'user' : user,
    }
    
    return render(request , 'adminpanel/singleuser.html' , context)

def editUser(request , userId):
    
    user = User.objects.get(id=userId)
    context = {
        'user' : user,
    }
    
    return render(request , 'adminpanel/edituser.html' , context)
    
    

#-----------------------------------------------#
# ------------- GAMES RELATED ------------------ #
#-----------------------------------------------#


# Displaying all game inn a table
def gamesList(request):     
    if request.method == 'POST':
        form = GameForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()  # Save the form data as a new Game instance
            print("form is valid")
            return redirect('gameslist')  # Redirect to the games list page or any other appropriate view
        else:
            print("form not valid")
    
    
    form = GameForm()
    
    games = Game.objects.all()
    categories = Category.objects.all()
    context = {
        'games': games,
        'categories': categories,
        'form': form
    }
    return render(request, 'adminpanel/gamesdetails.html', context)


# display single game in detail
def singleGame(request , gameId):
    
    game = Game.objects.get(pk=gameId)
    context = {
        'game' : game,
    }
    
    return render(request , 'adminpanel/singlegame.html' , context)


#-----------------------------------------------#
# ------------- CATEGORY RELATED ------------------ #
#-----------------------------------------------#


# Listing all categories
def categoriesList(request):
    
    if request.method == 'POST' and request.POST['category'] != '':
        category = request.POST['category']
        Category.objects.create(name=category)
        return redirect('categorieslist')
        
    categories = Category.objects.order_by('name')
    context = {
        'categories' : categories,   
    }  
    return render(request , 'adminpanel/categorydetails.html' , context )

def deleteCategory(request , categoryId):
    category = Category.objects.get(pk = categoryId)
    category.delete()
    return redirect('categorieslist')
    