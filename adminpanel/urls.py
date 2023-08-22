from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.signIn , name='admin-signin'),
    path('home/' , views.adminHome, name='admin-home'),
    path('logout/', views.adminLogout, name="admin-logout"),
    path('games/' , views.gamesList , name='gameslist'),
    path('users/' , views.usersList , name='userslist'),
    path('categories/' , views.categoriesList , name='categorieslist'),
    path('user/<int:userId>' , views.singleUser , name='user-details'),
    path('game/<int:gameId>' , views.singleGame , name='game-details'),
    path('edituser/<int:userId>', views.editUser , name='edit-user'),
    path('deleteCategory/<int:categoryId>' , views.deleteCategory , name='deleteCategory'),
    
]
