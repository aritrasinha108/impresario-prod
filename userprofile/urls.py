from django.urls import path
from django.conf.urls import url
from . import views


app_name = 'userprofile'


urlpatterns = [
    
    path('<int:org_id>/add_event', views.add_event ,name = 'add_event'),
    path('edit_event/<int:event_id>', views.update_event ,name = 'edit_event'),
    path('view_event/<int:event_id>',views.view_event ,name = 'view_event'),
    path('calendar', views.view_calendar, name = "view_calendar")
]
