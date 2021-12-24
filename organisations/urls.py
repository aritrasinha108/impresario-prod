from django.urls import path
from . import views


app_name = 'organisations'


urlpatterns = [
    path('new/', views.create_org, name='new_org'),
    path('tree/', views.org_tree, name='org_tree'),
    path('<int:org_id>/', views.org_detail, name='org_detail')
]
