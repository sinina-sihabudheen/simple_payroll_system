# apps/employees/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    AdminLoginView,
    DepartmentViewSet,
    DesignationViewSet,
    CategoryViewSet,
    EmployeeTypeViewSet,
    EmployeeAllowanceViewSet,
    EmployeeProfileViewSet,
    EmployeeDeductionViewSet,
    EmployeesReportAPIView,
    EmployeesReportPDFAPIView,
    EmployeesReportExcelAPIView,
    EmployeeDeductionsReportAPIView,
    EmployeeDeductionsReportPDFAPIView,
    EmployeeDeductionsReportExcelAPIView,
)

router = DefaultRouter()
router.register(r'departments', DepartmentViewSet)
router.register(r'designations', DesignationViewSet)
router.register(r'categories', CategoryViewSet)
router.register(r'employee-types', EmployeeTypeViewSet)
router.register(r'employee-allowances', EmployeeAllowanceViewSet)
router.register(r'profiles', EmployeeProfileViewSet)
router.register(r'employee-deductions', EmployeeDeductionViewSet)

urlpatterns = [
    path('admin-login/', AdminLoginView.as_view(), name='admin_login'),
    path('', include(router.urls)),
    path('reports/employees/', EmployeesReportAPIView.as_view(), name='employees_report'),
    path('reports/employees.pdf', EmployeesReportPDFAPIView.as_view(), name='employees_report_pdf'),
    path('reports/employees.xlsx', EmployeesReportExcelAPIView.as_view(), name='employees_report_excel'),
    path('reports/deductions/', EmployeeDeductionsReportAPIView.as_view(), name='employee_deductions_report'),
    path('reports/deductions.pdf', EmployeeDeductionsReportPDFAPIView.as_view(), name='employee_deductions_report_pdf'),
    path('reports/deductions.xlsx', EmployeeDeductionsReportExcelAPIView.as_view(), name='employee_deductions_report_excel'),
]
