from django.urls import path
from . import views

urlpatterns = [
    path('' , views.signUp , name='acc-signup'),
    path('verify_otp/' , views.verifyOtp , name='verify-otp'),
    path('signin/' , views.signIn , name='acc-signin'),
    
    # payment urls
    
    path('payment/<int:packId>/' , views.payment , name='payment' ),
    path('payment-completed/' , views.payment_completed_view , name='payment-completed' ),
    path('payment-failed/' , views.payment_failed_view , name='payment-failed' ),
    # path('payment-canceled/' , views.payment_canceled_view , name='payment-canceled' ),
]