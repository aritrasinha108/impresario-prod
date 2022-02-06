from django.urls import path
from . import views


app_name = 'accounts'


urlpatterns = [
    path('auth/', views.auth, name='auth'),
    path('logout/', views.logout_user, name='logout'),
    path('settings/', views.settings_menu, name='menu'),
    path('change-password/', views.change_password, name='change_password')
]
