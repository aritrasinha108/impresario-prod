from django.contrib import admin
from .models import MembershipLevel, Organization


admin.site.register(Organization)
admin.site.register(MembershipLevel)
