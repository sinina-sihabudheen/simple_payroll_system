from rest_framework import viewsets
from rest_framework.views import APIView
from .models import Attendance, Leave, LeaveType, EsslPunch
from apps.employees.models import EmployeeProfile  
from rest_framework.response import Response
from datetime import date, datetime
from rest_framework import status
from .serializers import *
from collections import defaultdict

class AttendanceViewSet(viewsets.ModelViewSet):
    queryset = Attendance.objects.all()
    serializer_class = AttendanceSerializer

class LeaveViewSet(viewsets.ModelViewSet):
    queryset = Leave.objects.all()
    serializer_class = LeaveSerializer
    
    def perform_update(self, serializer):
        leave = serializer.save()
        if leave.approved:
            Attendance.objects.update_or_create(
                employee=leave.employee,
                date=leave.date,
                defaults={
                    "is_present": True,
                    "marked_manually": False,
                    "in_time": None,
                    "out_time": None,
                }
            )

class LeaveTypeViewSet(viewsets.ModelViewSet):
    queryset = LeaveType.objects.all()
    serializer_class = LeaveTypeSerializer

class EsslPunchViewSet(viewsets.ModelViewSet):
    queryset = EsslPunch.objects.all()
    serializer_class = EsslPunchSerializer

from .utils.essl_reader import fetch_essl_data

class SyncEsslToAttendance(APIView):
    def post(self, request):
        # First, try to fetch new data from the device
        success, message = fetch_essl_data()
        
        # Even if fetching fails (e.g., device offline), we process existing logs
        # but we should warn the user.
        
        punch_map = defaultdict(list)
        for punch in EsslPunch.objects.all():
            punch_date = punch.punch_time.date()
            punch_map[(punch.employee_code, punch_date)].append(punch.punch_time.time())

        updated_count = 0
        for (emp_code, punch_date), times in punch_map.items():
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
                updated_count += 1
            except EmployeeProfile.DoesNotExist:
                continue

        response_data = {
            'detail': 'ESSL synced to attendance.',
            'device_status': message,
            'records_processed': updated_count
        }
        
        status_code = status.HTTP_200_OK if success else status.HTTP_207_MULTI_STATUS
        return Response(response_data, status=status_code)


class AttendanceByDate(APIView):
    def get(self, request):
        date_str = request.query_params.get("date")
        if not date_str:
            return Response({"error": "Date parameter is required."}, status=400)

        try:
            date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            return Response({"error": "Invalid date format. Use YYYY-MM-DD."}, status=400)

        employees = EmployeeProfile.objects.filter(date_of_joining__lte=date_obj)

        response_data = []
        for emp in employees:
            attendance = Attendance.objects.filter(employee=emp, date=date_obj).first()
            response_data.append({
                "employee_id": emp.id,
                "employee_name": f"{emp.first_name} {emp.last_name}",
                "employee_code": emp.employee_code,
                "attendance": AttendanceSerializer(attendance).data if attendance else None
            })

        return Response(response_data)

class MarkAttendanceManually(APIView):
    def post(self, request):
        data = request.data

        employee_id = data.get("employee")
        attendance_date = data.get("date")
        is_present = data.get("is_present", False)
        in_time = data.get("in_time")
        out_time = data.get("out_time")
        marked_manually = data.get("marked_manually", True)

        if not employee_id or not attendance_date:
            return Response({"error": "Employee and date are required."}, status=400)

        try:
            employee = EmployeeProfile.objects.get(id=employee_id)
        except EmployeeProfile.DoesNotExist:
            return Response({"error": "Employee not found."}, status=404)

        try:
            attendance_date_obj = datetime.strptime(attendance_date, "%Y-%m-%d").date()
        except ValueError:
            return Response({"error": "Invalid date format. Use YYYY-MM-DD."}, status=400)

        if attendance_date_obj > date.today():
            return Response({"error": "Cannot mark attendance for a future date."}, status=400)

        if attendance_date_obj < employee.date_of_joining:
            return Response({"error": "Cannot mark attendance before employee's date of joining."}, status=400)

        is_today = attendance_date_obj == date.today()

        if is_present:
            if is_today and not in_time:
                return Response({"error": "In time is required for today's attendance."}, status=400)
            if not is_today and (not in_time or not out_time):
                return Response({"error": "Both in and out time are required for past attendance."}, status=400)

        attendance, created = Attendance.objects.update_or_create(
            employee=employee,
            date=attendance_date,
            defaults={
                "in_time": in_time,
                "out_time": out_time,
                "is_present": is_present,
                "marked_manually": marked_manually,
            },
        )

        serializer = AttendanceSerializer(attendance)
        return Response(serializer.data, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)
