from django.contrib import admin
from .models import Attendance, Leave, LeaveType

admin.site.register(Attendance)
admin.site.register(Leave)
admin.site.register(LeaveType)
