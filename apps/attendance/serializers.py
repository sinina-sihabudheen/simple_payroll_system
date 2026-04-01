from rest_framework import serializers
from .models import Attendance, Leave, LeaveType, EsslPunch, EsslConfig

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
    employee_name = serializers.ReadOnlyField(source='employee.name')
    employee_code = serializers.ReadOnlyField(source='employee.employee_code')
    leave_type_name = serializers.ReadOnlyField(source='leave_type.name')

    class Meta:
        model = Leave
        fields = ['id', 'employee', 'employee_name', 'employee_code', 'date', 'leave_type', 'leave_type_name', 'status', 'created_at']

class LeaveTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeaveType
        fields = '__all__'

class EsslPunchSerializer(serializers.ModelSerializer):
    class Meta:
        model = EsslPunch
        fields = '__all__'

class EsslConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = EsslConfig
        fields = ['id', 'device_ip', 'device_port', 'updated_at']
