from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.signIn , name='admin-signin'),
    path('home/' , views.adminHome, name='admin-home')
    
]
