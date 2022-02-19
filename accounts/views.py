from django.shortcuts import render, redirect
from django.contrib.auth import logout, authenticate, login, update_session_auth_hash
from django.contrib.auth.models import User, auth
from .models import Profile, Account
from django.contrib import messages


def settings_menu(request):
    if request.user.is_authenticated:
        return render(request, 'settings_menu.html', {
            'user': request.user
        })
    else:
        return redirect('accounts:login')


def logout_user(request):
    if request.user.is_authenticated:
        logout(request)
    return redirect('home')


def register_oauth_user(request):
    if request.method == 'POST':
        email = request.user.email
        user = User.objects.get(email=email)
        try:
            user.username = request.POST['username']
            user.save()

            profile = Profile(
                first_name=request.user.first_name,
                last_name=request.user.last_name,
                phone_number=request.POST['phone'],
                gender=request.POST['gender'],
                user=user
            )
            profile.save()

            account = Account(
                profile=profile,
                user=user
            )
            account.save()
                
            return redirect('home')
        except:
            return render(request, 'register.html', {
                'warning': "This username has already been taken"
            })
    return render(request,'register.html',{})


def register_user(request):
    if request.user.is_authenticated:
        try:
            profile = Profile.objects.get(user=request.user.id)
            return redirect('home')
        except:
            return register_oauth_user(request)
    elif request.method == 'POST':
        try:
            User.objects.get(username=request.POST['username'])
            return render(request,'register.html', {
                'warning': "This username has already been taken"
            })
        except User.DoesNotExist:
            if request.POST['password'] == request.POST['password2']:
                user=User.objects.create_user(
                    request.POST['username'],
                    request.POST['email'].lower(),
                    request.POST['password']
                )
                user.save()
                
                profile = Profile(
                    first_name=request.POST['fname'],
                    last_name=request.POST['lname'],
                    phone_number=request.POST['phone'],
                    gender=request.POST['gender'],
                    user=user
                )
                profile.save()

                account = Account(
                    profile=profile,
                    user=user
                )                 
                account.save()
                
                return redirect('accounts:login')
            else:
                return render(request, 'register.html', {
                    'warning': "The passwords do not match"
                })
    return render(request,'register.html', {})


def login_user(request):
    if request.method == 'POST':
        user = authenticate(
            request, 
            username=request.POST['username'], 
            password=request.POST['password']
        )
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            return render(request, 'login.html', {
                'warning': "Incorrect username or password"
            })
    return render(request, 'login.html', {})


def change_password(request):
    if not request.user.is_authenticated:
         return redirect('accounts:login')
    if request.method == 'POST':
        cur_pwd = request.POST['cur_password']
        pwd = request.POST['password']
        pwd2 = request.POST['password2']
        username = request.user.get_username()
        user = User.objects.get(username__exact=username)
        check = auth.authenticate(request, username=username, password=cur_pwd)
        if check is None:
            messages.info(request, 'Current Password is not correct')
            return redirect('accounts:change_password')
        if pwd == pwd2:
            user.set_password(pwd)
            user.save()
            update_session_auth_hash(request, user)
            messages.info(request, 'Password changed successfully')
            return redirect('accounts:change_password')
        else:
            messages.info(request, 'The Passwords do not match')
            return redirect('accounts:change_password')
    else:
        return render(request,'change_pass.html')