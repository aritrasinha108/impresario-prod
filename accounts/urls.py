from django.conf.urls import include
from django.urls import path
from .views import logout_user,register_user,login_user


app_name = 'accounts'


urlpatterns = [
    path('logout/',logout_user,name='logout'),
    path('register/',register_user,name='register'),
    path('login/',login_user,name='login')
]
