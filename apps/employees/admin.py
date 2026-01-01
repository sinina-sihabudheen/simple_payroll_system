from django.contrib import admin
from .models import (
    Department, Designation, Category, EmployeeType, EmployeeProfile, EmployeeAllowance, EmployeeDeduction
)

admin.site.register(Department)
admin.site.register(Designation)
admin.site.register(Category)
admin.site.register(EmployeeType)

@admin.register(EmployeeProfile)
class EmployeeProfileAdmin(admin.ModelAdmin):
    list_display = (
        "employee_code",
        "name",
        "department",
        "designation",
        "category",
        "status",
        "basic_salary",
        "net_salary",
        "is_active",
    )
    search_fields = ("employee_code", "name", "passport_number", "emirates_id_number")
    list_filter = ("department", "designation", "category", "status", "is_active")
    readonly_fields = ("created_at", "updated_at", "net_salary")

admin.site.register(EmployeeAllowance)
admin.site.register(EmployeeDeduction)


