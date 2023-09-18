from django.shortcuts import render , redirect
from django.urls import reverse
from django.http import HttpResponse
from django.contrib.auth import authenticate, login

from django.core.mail import EmailMessage ,send_mail
from django.utils.crypto import get_random_string
from django.contrib.sessions.models import Session

from paypal.standard.models import ST_PP_COMPLETED
from paypal.standard.forms import PayPalPaymentsForm

from decimal import Decimal
import random
import uuid  # For generating unique identifiers
from datetime import date , datetime

from django.conf import settings
from decouple import config
from django.contrib.auth.decorators import login_required

from .models import User , Transaction , CouponUsage
from adminpanel.models import CoinsPack, Coupon


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
    error = None
    coupon_offer = 0
    pack = CoinsPack.objects.get(id = packId)
    details = {}
    if request.method == "POST":
        coupon = request.POST.get('coupon')
        try:
            coupon = Coupon.objects.get(code=coupon)
            if CouponUsage.objects.filter(user=request.user, coupon=coupon).exists():
                print('coupon already used')
                error = 'Coupon already used'
            elif coupon.expiration_date < date.today():
                print('Coupon Expired')
                error = 'Coupon Expired'
            elif coupon.active == False :
                print('coupon is inactive')
                error = 'Coupon is Inactive'
            else:
                request.session['coupon_id'] = coupon.id
                coupon_offer = coupon.discount
                you_save = float(((Decimal(coupon_offer) / Decimal(100)) * Decimal(pack.price_after_offer)))
                details['you_save'] = you_save
                details['coupon_offer'] = coupon_offer
                
      
        except Coupon.DoesNotExist:
            error = 'Check you code again'
            print("Coupon does not exist")
        
        
    item_name = f"Pack of {pack.coins} coins"
    unique_invoice_id = uuid.uuid4().hex   
    request.session['in_id'] = unique_invoice_id
    request.session['pack_id'] = packId
    # amount = 0
    
    amount = float(Decimal(pack.price_after_offer) - ((Decimal(coupon_offer) / Decimal(100)) * Decimal(pack.price_after_offer)))
    print(amount)
    request.session['amount'] = amount
    paypal_dict = {
        "business": settings.PAYPAL_RECEIVER_EMAIL ,
        "amount": amount,
        "item_name": item_name ,
        "invoice": unique_invoice_id,
        "notify_url": request.build_absolute_uri(reverse('paypal-ipn')),
        "return": request.build_absolute_uri(reverse('payment-completed')),
        "cancel_return": request.build_absolute_uri(reverse('payment-failed')),
    }
    
    form = PayPalPaymentsForm(initial=paypal_dict)
    context = {
        "form": form,
        'coinpack' : pack,
        'amount' : amount,
        'error' : error,
        'details' : details
        }
    return render(request , 'account/payment.html' , context)


def payment_completed_view(request): 
    if request.session.get('pack_id') and request.session.get('in_id'):
        packId = request.session.get('pack_id')
        transaction_id = request.session.get('in_id')
        amount = request.session.get('amount')
        you_save = 0
        coupon = None
        
        userId = request.user.id
        
        pack = CoinsPack.objects.get(id=packId)
        
        transaction = Transaction.objects.create(
            coins_pack_id =  packId,
            user = request.user,
            transaction_id = transaction_id,
            amount = amount,
            status = True
        )
        transaction.save()
        details = {}
        if 'coupon_id' in request.session:
            coupon_Id = request.session.get('coupon_id')
            couponUse = CouponUsage(
                user = request.user,
                coupon_id =  coupon_Id,
                transaction_id = transaction_id
            )
            couponUse.save()
            
            coupon = Coupon.objects.get(id = coupon_Id)
            
            you_save = float(((Decimal(coupon.discount) / Decimal(100)) * Decimal(pack.price_after_offer)))
            del request.session['coupon_id']
        
        user = User.objects.get(id = userId)
        user.coins += pack.coins
        user.save()          
        
        context = {
            'transaction' : transaction,
            'pack' : pack,
            'user' : request.user,
            'coupon' : coupon,
            'amount' : amount,
            'you_save' : you_save
        }
        del request.session['pack_id']
        del request.session['in_id']
        del request.session['amount']
        if 'coupon_id' in request.session:
            del request.session['coupon_id']
            
        return render(request , 'account/payment-completed.html' , context)
    else:
        return redirect('coins')
    

def payment_failed_view(request):
    if request.session.get('pack_id') and request.session.get('in_id'):
        packId = request.session.get('pack_id')
        transaction_id = request.session.get('in_id')
        
        userId = request.user.id
        pack = CoinsPack.objects.get(id=packId)
        amount = request.session.get('amount')
        
        transaction = Transaction.objects.create(
            coins_pack_id =  packId,
            user_id = userId,
            transaction_id = transaction_id,
            status = False,
            amount = amount,
        )
        transaction.save()

        context = {
            'pack' : pack
        }
        
        del request.session['pack_id']
        del request.session['in_id']
        del request.session['amount']
        if 'coupon_id' in request.session:
            del request.session['coupon_id']
        
        return render(request , 'account/payment-failed.html' , context)

    else:
        return redirect('coins')
    
    
# def payment_canceled_view(request):
#     return render(request , 'account/payment-canceled.html')