from django.shortcuts import render

from django.shortcuts import render , redirect
from django.http import HttpResponse
from django.views.decorators.cache import never_cache
from django.contrib.auth import authenticate
from django.contrib import auth
 
from account.models import User , Transaction
from user.models import Wishlist , PurchasedGame
from .models import Game , Category , CoinsPack

from .forms import GameForm

import hashlib
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
    purchase_history = PurchasedGame.objects.order_by('-time_added').all()
    
    transactions = Transaction.objects.all()
    total_income = 0
    for transaction in transactions:
        if transaction.status:
            total_income += transaction.coins_pack.price_after_offer
    
    context = {
        'usersCount' : users.count(),
        'gamesCount' : games.count(),
        'income' : total_income,
        'purchaseCount' : purchase_history.count(),
        'purchase_history' : purchase_history,
         
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
        name = request.POST.get('name')
        description = request.POST.get('description')
        coins = request.POST.get('coins')
        category = request.POST.get('category')
        # featured = request.POST.get('featured')
        banner_image = request.FILES.get('bannerImage')  # Retrieve uploaded file
        cover_image = request.FILES.get('coverImage') 
        
        featured = True if request.POST.get('featured') else False

        print('-----------------------')
        print(featured)
        print(category)
        print(banner_image)
        print(cover_image)
        
        print('-----------------------')
        
        game = Game(
            name=name,
            description = description,
            coins = coins,
            banner_image = banner_image,
            cover_image = cover_image,
            featured = featured,
            category_id = category
        )
        game.save()
        
    games = Game.objects.all()
    categories = Category.objects.all()
    context = {
        'games': games,
        'categories': categories,
    }
    print()
    return render(request, 'adminpanel/gamesdetails.html', context)


# display single game in detail
def singleGame(request , gameId):
    
    game = Game.objects.get(pk=gameId)
    purchases = PurchasedGame.objects.filter(game_id=gameId)
    for purchase in purchases:
        purchase.id = hashlib.sha256(str(purchase.id).encode()).hexdigest()
    context = {
        'game' : game,
        'purchases' : purchases
    }
    
    return render(request , 'adminpanel/singlegame.html' , context)

def editGame(request , gameId):
    if request.method == "POST":
        name = request.POST.get('name')
        description = request.POST.get('description')
        coins = request.POST.get('coins')
        category = request.POST.get('category')
        featured = True if request.POST.get('featured') else False
        
        game = Game.objects.get(id=gameId)
        
        # updating values
        game.name = name
        game.description = description
        game.coins = coins 
        game.category_id = category
        game.featured = featured 
        game.save()
        return redirect('game-details', gameId = gameId)
    
    game = Game.objects.get(id=gameId)
    categories = Category.objects.exclude(id=game.category_id).all()
    context = {
        'game' : game,
        'categories' : categories,
    }
    return render(request , 'adminpanel/editgame.html' , context)

def deleteGame(request , gameId):
    game = Game.objects.get(pk=gameId)
    game.delete()
    return redirect('gameslist')
    

#-----------------------------------------------#
# ------------- CATEGORY RELATED -------------- #
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

#-----------------------------------------------#
# ------------- Coins RELATED ----------------- #
#-----------------------------------------------#
def coinsList(request):
    if request.method == "POST":
        coins = request.POST.get('coins')
        offer = request.POST.get('offer')
        print(coins)
        print(offer)
        
        coinPack = CoinsPack.objects.create(coins = coins , offer = offer)
        coinPack.save()
        return redirect('coinslist')
        
    coinsPack = CoinsPack.objects.all()
    transaction_history = Transaction.objects.order_by('-id')
    
    context = {
        'coins' : coinsPack,
        'transactions' : transaction_history,
    }
    
    return render(request , 'adminpanel/coinsdetails.html' , context)

def deleteCoins(request , coinsId):
    coinPack = CoinsPack.objects.get(id = coinsId)
    coinPack.delete()
    return redirect('coinslist')