from django.urls import path
from django.conf.urls import url
from . import views


app_name = 'organisations'


urlpatterns = [
    path('new-org/', views.create_org, name='new_org'),
    path('tree/', views.org_tree, name='org_tree'),
    path('<int:org_id>/', views.org_detail, name='org_detail'),
    path('<int:par_id>/new-team/', views.create_team, name='new_team'),
    path('<int:org_id>/edit/', views.edit_team, name='edit_team'),
    path('<int:par_id>/team_reqs', views.team_reqs, name='team_requests'),
    url(r'^ajax/approve_or_reject/$', views.ajax_change_status, name='ajax_change_status'),
    path('<int:org_id>/change_role/', views.change_role, name='change_role'),
    path('<int:org_id>/dismiss_admin/', views.dismiss_admin, name='dismiss_admin'),
    path('<int:org_id>/leave/', views.leave_team, name='leave_team'),
]
