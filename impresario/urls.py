from django.contrib import admin
from django.urls import path, include
from . import views


urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('accounts/auth/', include('allauth.urls')),
    path('', views.index, name='home'),
    path('orgs/', include('organisations.urls')),
    path('userprofile/', include('userprofile.urls')),
]
