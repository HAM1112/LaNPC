from django.urls import path
from . import views

urlpatterns = [
    path('home/', views.home , name='home' ),
    path('browse/', views.browse , name='browse' ),
    path('profile/', views.profile , name='profile' ),
    path('game/<int:gameId>/' , views.gameDetails , name='game'),
]
