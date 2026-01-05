from rest_framework import serializers
from .models import Attendance, Leave, LeaveType, EsslPunch

class AttendanceSerializer(serializers.ModelSerializer):
    employee_name = serializers.SerializerMethodField()
    employee_code = serializers.SerializerMethodField()

    class Meta:
        model = Attendance
        fields = '__all__'

    def get_employee_name(self, obj):
        return f"{obj.employee.name}"
    def get_employee_code(self, obj):
        return f"{obj.employee.employee_code}"


class LeaveSerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(source="employee.name", read_only=True)
    employee_code = serializers.CharField(source="employee.employee_code", read_only=True)
    leave_type_name = serializers.CharField(source="leave_type.name", read_only=True)
  
    class Meta:
        model = Leave
        fields = ["id", "employee", "employee_name", "employee_code", "approved", "date", "leave_type", "leave_type_name"]

class LeaveTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeaveType
        fields = '__all__'

class EsslPunchSerializer(serializers.ModelSerializer):
    class Meta:
        model = EsslPunch
        fields = '__all__'