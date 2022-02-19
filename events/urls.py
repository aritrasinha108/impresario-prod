from django.urls import path
from . import views


app_name = 'events'


urlpatterns = [
    path('<int:org_id>/add-event', views.add_event, name='add_event'),
    path('event/<int:event_id>', views.view_event, name='view_event'),
    path('event/<int:event_id>/edit', views.update_event, name='edit_event'),
    path('my-cal/', views.view_calendar, name='calendar'),
    path('my-events/', views.my_events, name='my_events')
]
