from django.urls import path
from . import views


app_name = 'accounts'


urlpatterns = [
    path('logout/', views.logout_user, name='logout'),
    path('register/', views.register_user, name='register'),
    path('login/', views.login_user, name='login'),
    path('settings/', views.settings_menu, name='menu'),
    path('change-password/', views.change_password, name='change_password')
]
