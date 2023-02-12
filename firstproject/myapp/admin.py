from django.contrib import admin
from .models import Member, LeaveForm

# from .models import Employee

admin.site.register(Member)
# admin.site.register(Employee)
admin.site.register(LeaveForm)


# from django.contrib.sessions.models import Session

# admin.site.register(Session)
