from django.shortcuts import render
from django.contrib.auth import logout
from django.shortcuts import render , redirect
from django.http import HttpResponse
from adminpanel.models import Game , Category , CoinsPack
from django.contrib.auth.decorators import login_required

from .models import Wishlist


# --------------------------------------------------#
# ------------------Home Page-----------------------#
# --------------------------------------------------#

# @login_required()
def home(request):
    latest_games = Game.objects.order_by('-time_of_creation')[:8]
    context = {
        'latests' : latest_games,
    }
    print(request.user.is_authenticated) 
    print(latest_games[0])
    return render(request , 'user/home.html' , context)

# --------------------------------------------------#
# ------------------Game details--------------------#
# --------------------------------------------------#
def gameDetails(request , gameId):    
    game = Game.objects.get(id=gameId)
    related_games = Game.objects.filter(category=game.category).exclude(id=game.id)
    wishlist = Wishlist.objects.filter(user = request.user , game = game).exists()
    print(wishlist)
    print("testing the world haters")
    context = {
        'game' : game,
        'related' : related_games,
        'wishlist' : wishlist,
    }
    return render(request , 'user/gamedetails.html' , context )

def allGames(request):
    if request.method == "POST":
        selected = request.POST['selected']
        search = request.POST['search']
        category = request.POST['category']
        print(selected)
        print(search)
        print(category)
        if category == "All":
            if search == '':
                games = Game.objects.all()
            else :
                games = Game.objects.filter(name__istartswith=search)
        else:
            if search == '':
                games = Game.objects.filter(category=category)
            else :
                games = Game.objects.filter(name__istartswith=search , category=category)
                
        if selected == 'latest':
            games = games.order_by('-time_of_creation')
        elif selected == 'oldest':
            games = games.order_by('time_of_creation')
        elif selected == 'highcoin':
            games = games.order_by('-coins')
        elif selected == 'lowcoin' :
            games = games.order_by('coins')
        
        categories = Category.objects.order_by('name')
        context = {
            'games' : games,
            'selected' : selected,
            'search' : search,
            'categories' : categories,
            'c_selected' : category,
            'search' : search,
        }
        return render(request , 'user/exploregames.html' , context )
        
    games = Game.objects.all()
    categories = Category.objects.all()
    context = {
        'games' : games,
        'categories' : categories,
    }
    return render(request, 'user/exploregames.html' , context)

def categoryGame(request , categoryId):
    games = Game.objects.filter(category = categoryId)
    categories = Category.objects.all()
    context = {
        'games' : games,
        'categories' : categories,
    }
    return render(request, 'user/exploregames.html' , context)

def browse(request):
    games = Game.objects.all()
    categories = Category.objects.all()
    
    top_coins = Game.objects.order_by('coins')[:3]
    other_games = Game.objects.all()[:6]
    context = {
        'games' : games,
        'categories' : categories,
        'top_coins' : top_coins,
        'other_games' : other_games,   
    }   
    return render(request , 'user/browse.html' , context )

# Adding game to wishlist
def addWishList(request , gameId):
    print(request.user)
    user = request.user
    wishlist = Wishlist.objects.create(user = user , game_id = gameId)
    wishlist.save()
    return redirect('game' , gameId=gameId)
# deleting game from wishlist
def delWishList(request, gameId):
    user = request.user
    wishlist = Wishlist.objects.get(user = user, game_id = gameId)
    wishlist.delete()
    return redirect('game' , gameId=gameId)

# display coins packages
def coins(request):
    coinsPack = CoinsPack.objects.order_by('coins')
    context = {
        'coins' : coinsPack,
    }
    return render(request, 'user/coins.html' , context)

# display profile page
def profile(request):
    
    user = request.user
    wishlists = Wishlist.objects.filter(user = user)
    print(wishlists)
    context = {
        'wishlists' : wishlists,
    }
    
    
    return render(request , 'user/profile.html' , context)

#user logout 
def userLogout(request):
    logout(request)
    return redirect('home')