from django.db import models
from organisations.models import Organization


class Event(models.Model):
    event_id = models.TextField(blank=False)
    title = models.CharField(blank=False, max_length=100)
    description = models.CharField(blank=False, max_length=500)
    location = models.CharField(max_length=100)
    
    Tentative=0
    Cancelled=1
    Confirmed=2
    STATUS=(
        (Tentative, "Tentative"),
        (Cancelled, "Cancelled"),
        (Confirmed, "Confirmed")
    )

    status = models.IntegerField(choices=STATUS, blank=False)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='event')
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()

    def __str__(self):
        return self.title
