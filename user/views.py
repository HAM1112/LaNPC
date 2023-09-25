from django.shortcuts import render
from django.contrib.auth import logout
from django.shortcuts import render , redirect
from django.http import HttpResponse
from adminpanel.models import Game , Category , CoinsPack
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist

from .models import Wishlist , PurchasedGame , Review , Message
from account.models import Transaction , User

from datetime import datetime

import os
import io
import zipfile
from django.core.files.storage import default_storage
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings


# --------------------------------------------------#
# ------------------Home Page-----------------------#
# --------------------------------------------------#

# @login_required()
def home(request):
    user = request.user
    if user.id:
        mygames = PurchasedGame.objects.filter(user=request.user)
        print(request.user)
    else:
        mygames = False
    latest_games = Game.objects.order_by('-time_of_creation')[:8]
    context = {
        'latests' : latest_games,
        'mygames' : mygames,
    }
    print(request.user.is_authenticated) 
    print(latest_games[0])
    return render(request , 'user/home.html' , context)

# --------------------------------------------------#
# ------------------Game details--------------------#
# --------------------------------------------------#
def gameDetails(request , gameId):
    game = Game.objects.get(id=gameId)
    print(gameId)
    if request.method == "POST":
        rating  = request.POST.get('rate')
        description = request.POST.get('description')

        review = Review.objects.create(
            user = request.user,
            game = game,
            rating = rating,
            description = description
        )
        review.save()
        return redirect('game' , gameId = gameId )
    
    count = 0
    total = 0
    reviews = Review.objects.filter(game=game)
    for review in reviews:
        count += 1
        total += review.rating
    
    if count > 0:
        rating = total / count
    else:
        rating = 4.5
        
    reviews_with_description = Review.objects.filter(game=game).exclude(description__isnull=True).exclude(description__exact='')
    
    related_games = Game.objects.filter(category=game.category).exclude(id=game.id)
    wishlist = Wishlist.objects.filter(user = request.user , game = game).exists()
    
    no_of_downloads_left = 3
    try:
        purchased_game = PurchasedGame.objects.get(game=game, user=request.user)
        purchased = True
        
        no_of_downloads_left = 3 - purchased_game.download_count
    except PurchasedGame.DoesNotExist:
        purchased = False

    print(no_of_downloads_left)
    
    context = {
        'game' : game,
        'related' : related_games,
        'wishlist' : wishlist,
        'purchased' : purchased,
        'reviews' : reviews,
        'reviews_discription' : reviews_with_description,
        'rating' : rating,
        'no_of_downloads_left':no_of_downloads_left
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
    
    top_coins = Game.objects.order_by('-coins')[:3]
    other_games = Game.objects.all()[:6]
  
    if request.user :
        try:
            user_games = PurchasedGame.objects.filter(user=request.user)
            for purchased_game in user_games:
                date_added = purchased_game.time_added.date()
                print(date_added)
            print(user_games)
        except Exception as e:
            print("user is not signed in !!!!!!Please in sign in")
            user_games = None  # Assign a default value or handle the error as needed

    else :
        user_games = None
          
    context = {
        'games' : games,
        'categories' : categories,
        'top_coins' : top_coins,
        'other_games' : other_games,   
        'user_games' : user_games,
    }   
    return render(request , 'user/browse.html' , context )

@login_required
def buyGame(request , gameId):
    
    game = Game.objects.get(id=gameId)
    user = request.user
    
    
    if PurchasedGame.objects.filter(user=user, game=game).exists():
        return redirect('game' , gameId)
    
    if user.coins >= game.coins:
        purchase = PurchasedGame.objects.create(user=user , game=game)
        purchase.save()
        user.coins -= game.coins
        user.save()   
        game.purchases += 1
        game.save()
        
        try:
            # Try to get the Wishlist object if it exists
            wishlist_entry = Wishlist.objects.get(user=user, game=game)
            
            # If it exists, delete it
            wishlist_entry.delete()
        except ObjectDoesNotExist:
            # Handle the case where the Wishlist entry doesn't exist
            pass
        
        return redirect('profile')
    else:
        return redirect('coins')

# Adding game to wishlist
def addWishList(request , gameId):
    print(request.user)
    user = request.user
    wishlist = Wishlist.objects.create(user = user , game_id = gameId)
    wishlist.save()
    return redirect('game' , gameId=gameId)
# deleting game from wishlist
def delWishList(request, gameId):
    try:
        print("i am tryingg ")
        user = request.user
        wishlist = Wishlist.objects.get(user=user, game_id=gameId)
        wishlist.delete()
        return redirect('profile')
    except ObjectDoesNotExist:
        print(ObjectDoesNotExist)
        return redirect('profile')

# display coins packages
def coins(request):
    if 'pack_id' in request.session:
        del request.session['pack_id']
    if 'in_id' in request.session:
        del request.session['in_id']
    if 'details' in request.session:
        del request.session['details']
    if 'amount' in request.session:
        del request.session['amount']
    if 'coupon_id' in request.session:
        del request.session['coupon_id']
    coinsPack = CoinsPack.objects.order_by('coins')
    context = {
        'coins' : coinsPack,
    }
    return render(request, 'user/coins.html' , context)

# display profile page
def profile(request):
    if request.method == "POST":
        username = request.POST.get('username')
        first_name = request.POST.get('firstname')
        second_name = request.POST.get('secondname')
        dob_str = request.POST.get('dob')
        dob_date = datetime.strptime(dob_str, '%Y-%m-%d').date()
   
        user = request.user
        user.username = username
        user.first_name = first_name
        user.last_name = second_name
        user.date_of_birth = dob_date
        user.save()
        
        return redirect('profile')
    
    user = request.user
    wishlists = Wishlist.objects.filter(user = user)
    purchased_games = PurchasedGame.objects.filter(user = user)
    
    transactions = Transaction.objects.filter(user=request.user)
    
    gamechat = purchased_games[0].game
    
    context = {
        'wishlists' : wishlists,
        'purchased_games' : purchased_games,
        'wishlist_count' : wishlists.count(),
        'purchase_count' : purchased_games.count(),
        'transactions' : transactions,
        "gamechat" : gamechat,
    } 
    return render(request , 'user/profile.html' , context)

@csrf_exempt  
def download_game_images(request, game_id):
    game = Game.objects.get(pk=game_id)
    
    purchase = PurchasedGame.objects.get(game_id = game_id , user = request.user)
    
    if purchase.download_count < 3 :
        temp_dir = os.path.join(settings.MEDIA_ROOT, 'temp')
        os.makedirs(temp_dir, exist_ok=True)

        
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w') as zipf:

            for image in [game.banner_image, game.cover_image]:
                if image:
                    image_path = default_storage.path(image.name)
                    zipf.write(image_path, os.path.basename(image_path))

        os.rmdir(temp_dir)

       
        response = HttpResponse(zip_buffer.getvalue(), content_type='application/zip')
        response['Content-Disposition'] = f'attachment; filename="{game.name}_images.zip"'
        
        response.write('<script>window.onload = function() { location.reload(); }</script>')
        
        purchase.download_count += 1
        purchase.save()
        if purchase.download_count == 3:
            purchase.delete()
        return response
    else:
        purchase.delete()  
        return redirect('game' , game_id)
        
    

def chatRooms(request , game_id):
    # if request.method == "POST":
    #     print(request.POST.get('message'))
    
    purchased_games = PurchasedGame.objects.filter(user = request.user)
    game = Game.objects.get(id=game_id)
    messages = Message.objects.filter(game = game)
    context = {
        'games' : purchased_games,
        'game' : game,
        'messages' : messages,
    }
    return render(request , 'user/chatrooms.html', context)



# user logout 
def userLogout(request):
    logout(request)
    return redirect('home')



