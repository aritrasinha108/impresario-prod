from django.shortcuts import render,redirect
from django.contrib.auth import logout, authenticate, login
from django.contrib.auth.models import User
from userauth.models import Profile


# Google OAuth 2.0
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from rest_auth.registration.views import SocialLoginView

class GoogleLogin(SocialLoginView):
    class GoogleAdapter(GoogleOAuth2Adapter):
        access_token_url = "https://oauth2.googleapis.com/token"
        authorize_url = "https://accounts.google.com/o/oauth2/v2/auth"
        profile_url = "https://www.googleapis.com/oauth2/v2/userinfo"
    adapter_class = GoogleAdapter
    callback_url = "http://localhost:8000/accounts/register"
    client_class = OAuth2Client


def logout_user(request):
    if request.user.is_authenticated:
        logout(request)
    return redirect('home')


def register_user(request):
    if request.method == 'POST':
        try:
            User.objects.get(username=request.POST['username'])
            return render(request,'register.html',{'warning':"User already exists!!"})
        except User.DoesNotExist:
            if request.POST['password']==request.POST['password2']:
                user=User.objects.create_user(
                    request.POST['username'],
                    request.POST['email'].lower(),
                    request.POST['password']
                )
                # user.last_name=request.POST['lname']
                # user.first_name=request.POST['fname']
                user.save()
                
                profile = Profile(
                    first_name=request.POST['fname'],
                    last_name=request.POST['lname'],
                    phone_number=request.POST['phone'],
                    gender=request.POST['gender']
                )
                profile.save()
                
                # account = Account(profile=profile,user=user)                 
                # account.save()
                
                return redirect('accounts:login')
            else:
                return render(request,'register.html',{'warning':"Passwords do not match!!"})
    return render(request,'register.html',{})

def login_user(request):
    if request.method=='POST':
        user = authenticate(request,username=request.POST['username'],password=request.POST['password'])
        if user is not None:
            login(request,user)
            return redirect('/userauth')
        else:
            return render(request,'login.html',{'warning':"Incorrect username or password"})
    return render(request,'login.html',{})