from django.shortcuts import render, redirect
from accounts.models import Account

def index(request):
    if request.user.is_authenticated:
        try:
            account = Account.objects.get(user=request.user.id)
        except:
            return redirect('accounts:register')
        return render(request, 'home.html', {
            'account': account
        })
    else:
        return render(request, 'index.html', {})