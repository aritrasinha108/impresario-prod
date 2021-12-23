from django.urls import path
from .views import logout_user,register_user,login_user


urlpatterns = [
    path('logout/',logout_user,name='logout'),
    path('register/',register_user,name='regsiter'),
    path('login/',login_user,name='login'),
    # path('auth/google/', GoogleLogin.as_view(), name='google_login')
]
