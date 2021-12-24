from django.contrib import admin
from .models import MembershipLevel, Organization, TeamRequest


admin.site.register(Organization)
admin.site.register(MembershipLevel)
admin.site.register(TeamRequest)
