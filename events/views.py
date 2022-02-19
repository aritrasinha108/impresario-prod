import re
from django.shortcuts import render, redirect
from organisations.models import Organization, MembershipLevel
from django.contrib.auth.models import User
from .models import Event
from .utils import is_time_between
from .gsetup import *
import datetime
from impresario import settings


def add_event(request, org_id):
    if request.user.is_authenticated:
        user = request.user
        org  = Organization.objects.get(pk=org_id)
        if not org:
            return redirect('organisations:new_org')
        if request.method == 'POST':
            start_date = request.POST['start-date']
            start_time = request.POST['start-time']
            end_date = request.POST['end-date']
            end_time = request.POST['end-time']
            start = str(start_date) + " " + str(start_time) + '+0000'
            end = str(end_date) + " " + str(end_time) + '+0000'
            title = request.POST['title']
            start = datetime.datetime.strptime(start, "%Y-%m-%d %H:%M%z")
            end= datetime.datetime.strptime(end, "%Y-%m-%d %H:%M%z")
            if start >= end:
                return render(request, 'add_event.html', {
                    'warning': "Invalid time and/or inputs", 
                    'org': org,
                    'user': request.user
                })
            description = request.POST['description']
            location = request.POST['location']
            
            all_events = Event.objects.all()
            clash_events = []
            for e in all_events:
                if is_time_between(start, end, e.start_time) or is_time_between(start, end, e.end_time) or is_time_between(e.start_time, e.end_time, end) or is_time_between(e.start_time, e.end_time, start):
                    clash_events.append(e)

            members = MembershipLevel.objects.filter(organization=org).values('user')
            for c in clash_events:
                org2  = c.organization
                mem2 = MembershipLevel.objects.filter(organization=org2).values('user')
                for m in mem2:
                    if m in members:
                        return render(request, 'add_event.html', {
                            'warning': "Some events are clashing", 
                            'org': org
                        })
            
            attendees = []
            for m in members:
                user = User.objects.get(pk = m['user'])
                attendees.append({'email': user.email})
            
            event = google_create_event(location, title, description, start, end, 'Tentative', attendees)
            if event['id']:
                new_event = Event.objects.create(organization=org, title=title, description=description, location=location, start_time=start, end_time=end, status=0, event_id=event['id'])
                new_event.save()
                return render(request, 'add_event.html', {
                    'warning': "Success! Event created",
                    'org': org,
                    'user': request.user
                })
            else:
                return render(request, 'add_event.html', {
                    'warning': "Failure! Couldn't create event, please try again",
                    'org': org,
                    'user': request.user
                })
        else:
            return render(request, 'add_event.html', {
                'org': org,
                'user':request.user
            })
    else:
        return redirect('accounts:login')


def view_event(request, event_id):
    if not request.user.is_authenticated:
        return redirect('accounts:login')
    event = Event.objects.get(pk=event_id)
    if not event:   
        return redirect('organisations:org_tree')
    members = MembershipLevel.objects.filter(organization=event.organization.id).values('user')
    attendees = User.objects.filter(pk__in=members)
    return render(request, 'show_event.html', {
        'event': event , 
        'attendees': attendees,
        'user': request.user
})


def update_event(request, event_id):
    if not request.user.is_authenticated:
        return redirect('accounts:login')

    event = Event.objects.get(pk=event_id)
    if not event:
        return redirect('organisations:org_tree')
    if request.method == 'POST':
        title = request.POST['title']
        location = request.POST['location']
        description = request.POST['description']
        start_date = request.POST['start-date']
        start_time = request.POST['start-time']
        end_date = request.POST['end-date']
        end_time = request.POST['end-time']
        start = str(start_date) + " " + str(start_time)
        end = str(end_date) + " " + str(end_time)
        start = datetime.datetime.strptime(start, "%Y-%m-%d %H:%M")
        end = datetime.datetime.strptime(end, "%Y-%m-%d %H:%M")
        status = request.POST['status']
        if status==0:
            status = "Tentative"
        elif status==1:
            status = "Cancelled"
        else:
            status = "Confirmed"
        
        updated_event = google_update_event(
            event.event_id, 
            title, 
            description, 
            location, 
            start, 
            end, 
            status
        )

        if not updated_event.get('id'):
            return render(request, 'update_event.html', {
                'event': event,
                'user': request.user,
                'warning': "Couldn't update event"
            })

        event.event_id = updated_event['id']
        event.title = updated_event['summary']
        event.location = updated_event['location']
        event.description = updated_event['description']
        if status == "Tentative":
            event.status=0
        elif status == "Cancelled":
            event.status=1
        else:
            event.status=2
        event.start_time = start
        event.end_time =  end
        event.save()
        return redirect('organisations:events:view_event event.id')
    return render(request, 'update_event.html', {
        'event': event,
        'user': request.user,
        'warning': "Event updated successfully"
    })


from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from allauth.socialaccount.models import SocialToken, SocialApp
from django.http import JsonResponse

def my_events(request):
    # Creating a Google Calendar API client
    token = SocialToken.objects.get(account__user=request.user, account__provider='google')
    credentials = Credentials(
        token=token.token,
        refresh_token=token.token_secret,
        token_uri='https://oauth2.googleapis.com/token',
        client_id=settings.OAUTH_CLIET_ID,
        client_secret=settings.OAUTH_CLIENT_SECRET
    )
    service = build('calendar', 'v3', credentials=credentials)
    events = service.events().list(calendarId='primary').execute()['items']
    events = list(filter(lambda x : x['organizer']['email'] == 'c_pk8tirrl4j7c9r9ee1o32c7rho@group.calendar.google.com', events))
    return JsonResponse(events, safe=False)
    
def view_calendar(request):
    # Creating a Google Calendar API client
    try:
        token = SocialToken.objects.get(account__user=request.user, account__provider='google')
        credentials = Credentials(
            token=token.token,
            refresh_token=token.token_secret,
            token_uri='https://oauth2.googleapis.com/token',
            client_id=settings.OAUTH_CLIET_ID,
            client_secret=settings.OAUTH_CLIENT_SECRET
        )
        service = build('calendar', 'v3', credentials=credentials)
        events = service.events().list(calendarId='primary').execute()['items']
        events = list(filter(lambda x : x['organizer']['email'] == 'c_pk8tirrl4j7c9r9ee1o32c7rho@group.calendar.google.com', events))
        return render(request, 'my_cal.html', {
            'cal_url': request.user.email
        })
    except:
        return render(request, 'calendar.html', {'user': request.user})