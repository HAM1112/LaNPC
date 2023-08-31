from django.urls import path
from . import views

urlpatterns = [
    path('home/', views.home , name='home' ),
    path('browse/', views.browse , name='browse' ),
    path('profile/', views.profile , name='profile' ),
    path('game/<int:gameId>/' , views.gameDetails , name='game'),
    path('allgames/' , views.allGames , name='all-games'),
    path('coins/', views.coins , name='coins'),
    path('category/<int:categoryId>/' , views.categoryGame , name='category-game'),
    path('logout/', views.userLogout, name='user-logout'),
    
    path('addWishList/<int:gameId>', views.addWishList, name='add-wishlist'),     
    path('delWishList/<int:gameId>', views.delWishList, name='del-wishlist'),     
    path('buyGame/<int:gameId>', views.buyGame, name='buy-game'),     
    

]
