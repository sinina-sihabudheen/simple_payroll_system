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
]
