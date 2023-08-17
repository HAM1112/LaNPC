from django.shortcuts import render

# Create your views here.
from django.shortcuts import render , redirect
from django.http import HttpResponse
from adminpanel.models import Game , Category


# Create your views here.

def home(request):
    
    latest_games = Game.objects.order_by('-time_of_creation')[:8]

    context = {
        'latests' : latest_games,
    }

    print(latest_games[0])

    return render(request , 'user/home.html' , context)

def gameDetails(request , gameId):
    
    game = Game.objects.get(id=gameId)
    related_games = Game.objects.filter(category=game.category).exclude(id=game.id)
    
    context = {
        'game' : game,
        'related' : related_games,
    }
    
    print(related_games)
    return render(request , 'user/gamedetails.html' , context )









def browse(request):
    
    return render(request , 'user/browse.html'  )

def profile(request):
    
    return render(request , 'user/profile.html')
