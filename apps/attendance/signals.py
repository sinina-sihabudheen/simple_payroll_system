from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import EsslPunch, Attendance
from apps.employees.models import EmployeeProfile
from collections import defaultdict

@receiver(post_save, sender=EsslPunch)
def sync_essl_to_attendance(sender, instance, created, **kwargs):
    print(" Signal triggered for ESSL punch!")

    if not created:
        return  # Only handle new punches

    emp_code = instance.employee_code
    punch_date = instance.punch_time.date()
    all_punches = EsslPunch.objects.filter(employee_code=emp_code, punch_time__date=punch_date)

    times = [p.punch_time.time() for p in all_punches]
    try:
        employee = EmployeeProfile.objects.get(employee_code=emp_code)
        Attendance.objects.update_or_create(
            employee=employee,
            date=punch_date,
            defaults={
                'in_time': min(times),
                'out_time': max(times),
                'is_present': True,
                'marked_manually': False
            }
        )
    except EmployeeProfile.DoesNotExist:
        # Could log a warning if employee doesn't exist
        pass
