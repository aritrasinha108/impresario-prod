from django.shortcuts import render
from impresario import settings
from userauth.models import Account
import json


def index(request):
    if request.user.is_authenticated:
        account = Account.objects.get(user=request.user.id)
        return render(request,'home.html',{'account':account})
    else:
        # with open('credentials.json') as f:
        #     print(f)
        #     creds = json.loads(f)
        # print(creds)
        # print(settings.OAUTH_CLIET_ID)
        oauth_url = f'https://accounts.google.com/o/oauth2/v2/auth?client_id={settings.OAUTH_CLIET_ID}&response_type=code&scope=https://www.googleapis.com/auth/userinfo.profile&access_type=offline&redirect_uri=http://localhost:8000/accounts/register'
        return render(request,'index.html',{'oauth_url':oauth_url})