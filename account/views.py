from django.shortcuts import render , redirect
from django.urls import reverse
from django.http import HttpResponse
from django.contrib.auth import authenticate, login

from django.core.mail import EmailMessage ,send_mail
from django.utils.crypto import get_random_string
from django.contrib.sessions.models import Session

from paypal.standard.models import ST_PP_COMPLETED
from paypal.standard.forms import PayPalPaymentsForm

import random
import uuid  # For generating unique identifiers

from django.conf import settings
from decouple import config
from django.contrib.auth.decorators import login_required

from .models import User , Transaction
from adminpanel.models import CoinsPack


def signUp(request):
    
    if request.method == "POST":
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        otp = str(random.randint(100000, 999999))
        
        # storing details in session 
        request.session['otp'] = otp        
        request.session['username'] = username
        request.session['email'] = email
        request.session['password'] = password
        
        message = f"OTP verification Process. Your otp is : {otp}"
        subject = 'Otp verification'
        from_email = config('EMAIL_ADD')
        to_email = [email]
        send_mail(subject,message,from_email , to_email)
        
        return redirect('verify-otp')
    return render(request , 'account/accountsignup.html')

def verifyOtp(request):
    if request.method =="POST":
        user_otp = request.POST['otp']
        stored_otp = request.session.get('otp')
        stored_username = request.session.get('username')
        stored_email = request.session.get('email')
        stored_password = request.session.get('password')
        
        if user_otp == stored_otp:
            user = User.objects.create_user(username=stored_username,email=stored_email,password=stored_password)
            del request.session['otp']
            del request.session['email']
            del request.session['password']
            return redirect('acc-signin')
        else:
            return render(request, 'account/verify_otp.html', {'error': 'Invalid OTP'})     
    return render(request , 'account/verify_otp.html')


def signIn(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']  
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            return render(request, 'account/accountsignin.html', {'error_message': 'Invalid credentials'})
    return render(request , 'account/accountsignin.html')
            
            
@login_required(login_url='/account/signin/')
def payment(request , packId):
    pack = CoinsPack.objects.get(id = packId)
    item_name = f"Pack of {pack.coins} coins"
    unique_invoice_id = uuid.uuid4().hex
    
    request.session['in_id'] = unique_invoice_id
    request.session['pack_id'] = packId
    
    paypal_dict = {
        "business": settings.PAYPAL_RECEIVER_EMAIL ,
        "amount": pack.price_after_offer,
        "item_name": item_name ,
        "invoice": unique_invoice_id,
        "notify_url": request.build_absolute_uri(reverse('paypal-ipn')),
        "return": request.build_absolute_uri(reverse('payment-completed')),
        "cancel_return": request.build_absolute_uri(reverse('payment-failed')),
        # "custom": "premium_plan",  # Custom command to correlate to some function later (optional)
    }
    
    form = PayPalPaymentsForm(initial=paypal_dict)
    context = {
        "form": form,
        'coinpack' : pack,
        }
    return render(request , 'account/payment.html' , context)


def payment_completed_view(request): 
    if request.session.get('pack_id') and request.session.get('in_id'):
        packId = request.session.get('pack_id')
        transaction_id = request.session.get('in_id')
        userId = request.user.id
        
        pack = CoinsPack.objects.get(id=packId)
        
        transaction = Transaction.objects.create(
            coins_pack_id =  packId,
            user = request.user,
            transaction_id = transaction_id,
            status = True
        )
        transaction.save()
        
        user = User.objects.get(id = userId)
        user.coins += pack.coins
        user.save()          
        
        context = {
            'transactionId' : transaction_id,
            'pack' : pack,
            'user' : request.user,
        }
        del request.session['pack_id']
        del request.session['in_id']
        return render(request , 'account/payment-completed.html' , context)
    else:
        return redirect('coins')
    

def payment_failed_view(request):
    if request.session.get('pack_id') and request.session.get('in_id'):
        packId = request.session.get('pack_id')
        transaction_id = request.session.get('in_id')
        
        userId = request.user.id
        pack = CoinsPack.objects.get(id=packId)
        
        transaction = Transaction.objects.create(
            coins_pack_id =  packId,
            user_id = userId,
            transaction_id = transaction_id,
            status = False
        )
        transaction.save()

        context = {
            'pack' : pack
        }
        
        del request.session['pack_id']
        del request.session['in_id']
        
        return render(request , 'account/payment-failed.html' , context)

    else:
        return redirect('coins')
    
    
# def payment_canceled_view(request):
#     return render(request , 'account/payment-canceled.html')