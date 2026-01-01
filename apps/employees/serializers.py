from rest_framework import serializers
from .models import (Department, 
            Designation, 
            Category, 
            EmployeeType, 
            EmployeeProfile, 
            EmployeeAllowance, 
            EmployeeDeduction
            )
from apps.salary.models import Allowance, Deduction
from django.utils import timezone

class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        # fields = '__all__'
        fields = ['id', 'name']

class DesignationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Designation
        # fields = '__all__'
        fields = ['id', 'title']

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        # fields = '__all__'
        fields = ['id', 'name']

class EmployeeTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmployeeType
        # fields = '__all__'
        fields = ['id', 'name']

class EmployeeAllowanceSerializer(serializers.ModelSerializer):
    allowance_name = serializers.CharField(source="allowance.name", read_only=True)
    employee_name = serializers.CharField(source="employee.username", read_only=True)
    employee_id = serializers.IntegerField(source="employee.id", read_only=True)  
    employee_code = serializers.CharField(source="employee.employee_code", read_only=True)

    class Meta:
        model = EmployeeAllowance
        fields = ["id", "allowance", "employee_name", "employee_code", "employee_id", "allowance_name", "amount"]

class EmployeeProfileSerializer(serializers.ModelSerializer):
    department = DepartmentSerializer(read_only=True)
    designation = DesignationSerializer(read_only=True)

    department_id = serializers.PrimaryKeyRelatedField(
        source="department", queryset=Department.objects.all(), write_only=True
    )
    designation_id = serializers.PrimaryKeyRelatedField(
        source="designation", queryset=Designation.objects.all(), write_only=True
    )

    allowances = EmployeeAllowanceSerializer(many=True, source="employeeallowance_set", read_only=True)
    net_salary = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = EmployeeProfile
        fields = [
            "id",
            "name",
            "employee_code",
            "department", "designation", "category",
            "department_id", "designation_id","date_of_birth",
            "date_of_joining", "date_of_resignation", "last_working_day",
            "passport_number", "passport_expiry_date",
            "emirates_id_number", "emirates_id_expiry_date",
            "status",
            "basic_salary", "house_rent_allowance", "transportation_allowance",
            "cost_of_living_allowance", "net_salary",
            "allowances"
        ]

    def validate(self, attrs):
        status = attrs.get("status", getattr(self.instance, "status", "working"))
        resignation_date = attrs.get(
            "date_of_resignation", getattr(self.instance, "date_of_resignation", None)
        )

        if status in ["resigned", "terminated"] and not resignation_date:
            raise serializers.ValidationError({
                "date_of_resignation": "Resignation date must be provided if status is resigned or terminated."
            })

        return attrs

    def update(self, instance, validated_data):
        # Update status first
        status = validated_data.get("status", instance.status)
        instance.status = status

        # Set is_active based on status
        if status in ["resigned", "terminated"]:
            instance.is_active = False
            # Ensure resignation date is set (already validated)
            instance.date_of_resignation = validated_data.get(
                "date_of_resignation", instance.date_of_resignation
            )
        else:
            instance.is_active = True

        # Call super to update other fields
        return super().update(instance, validated_data)


# class EmployeeDeductionSerializer(serializers.ModelSerializer):
#     employee_name = serializers.CharField(source="employee.name", read_only=True)
#     employee_code = serializers.CharField(source="employee.employee_code", read_only=True)
#     employee = serializers.PrimaryKeyRelatedField(queryset=EmployeeProfile.objects.all(), write_only=True)
#     deduction_type = serializers.PrimaryKeyRelatedField(queryset=Deduction.objects.all(), required=False)
#     deduction_type_name = serializers.CharField(source="deduction_type.name", read_only=True)
#     method = serializers.CharField()
#     months = serializers.IntegerField(required=False, allow_null=True)

#     class Meta:
#         model = EmployeeDeduction
#         fields = [
#             "id",
#             "employee",
#             "employee_name",
#             "employee_code",
#             "deduction_type",
#             "deduction_type_name",
#             "amount",
#             "method",
#             "months",
#             "date",
#             "updated_at",
#             "created_at",
#         ]
class EmployeeDeductionSerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(source="employee.name", read_only=True)
    employee_code = serializers.CharField(source="employee.employee_code", read_only=True)
    employee = serializers.PrimaryKeyRelatedField(queryset=EmployeeProfile.objects.all(), write_only=True)
    deduction_type = serializers.PrimaryKeyRelatedField(queryset=Deduction.objects.all(), required=False)
    deduction_type_name = serializers.CharField(source="deduction_type.name", read_only=True)
    method = serializers.CharField()
    months = serializers.IntegerField(required=False, allow_null=True)

    class Meta:
        model = EmployeeDeduction
        fields = [
            "id",
            "employee",
            "employee_name",
            "employee_code",
            "deduction_type",
            "deduction_type_name",
            "amount",
            "reimbursed_amount",
            "remaining_amount",
            "remaining_installments",
            "is_closed",
            "method",
            "months",
            "date",
            "updated_at",
            "created_at",
        ]

    def validate(self, attrs):
        method = attrs.get("method")
        months = attrs.get("months")

        if method == "installments":
            if not months or months <= 0:
                raise serializers.ValidationError({"months": "Number of months must be greater than 0 for installment deduction."})
        
        return attrs
