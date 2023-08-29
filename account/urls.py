from django.urls import path
from . import views

urlpatterns = [
    path('' , views.signUp , name='acc-signup'),
    path('verify_otp/' , views.verifyOtp , name='verify-otp'),
    path('signin/' , views.signIn , name='acc-signin'),
    
]