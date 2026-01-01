
from django.db import models
from apps.employees.models import EmployeeProfile
class Attendance(models.Model):
    employee = models.ForeignKey(EmployeeProfile, on_delete=models.CASCADE)
    date = models.DateField()
    in_time = models.TimeField(null=True, blank=True)
    out_time = models.TimeField(null=True, blank=True)
    marked_manually = models.BooleanField(default=False)
    is_present = models.BooleanField(default=False)

    class Meta:
        unique_together = ('employee', 'date')

class LeaveType(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name

class Leave(models.Model):
    employee = models.ForeignKey(EmployeeProfile, on_delete=models.CASCADE)
    date = models.DateField()
    leave_type = models.ForeignKey(LeaveType, on_delete=models.CASCADE)
    approved = models.BooleanField(default=False)

    class Meta:
        unique_together = ('employee', 'date')

class EsslPunch(models.Model):
    employee_code = models.CharField(max_length=20)
    punch_time = models.DateTimeField()
