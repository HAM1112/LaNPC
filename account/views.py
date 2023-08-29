from django.shortcuts import render , redirect
from .utils import generate_otp
from django.core.mail import EmailMessage ,send_mail
from .models import User
from django.http import HttpResponse
from django.contrib.auth import authenticate, login
from django.utils.crypto import get_random_string
from django.contrib.sessions.models import Session
import random

from decouple import config
# Create your views here.

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
            
            
        