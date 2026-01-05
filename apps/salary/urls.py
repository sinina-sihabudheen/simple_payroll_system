from django.urls import path, include
from .views import GenerateSalaryAPIView, AllowanceViewSet, DeductionViewSet, PaySalaryAPIView, SalaryReportPDFAPIView, SalaryReportExcelAPIView

from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'allowances', AllowanceViewSet)
router.register(r'deductions', DeductionViewSet)


urlpatterns = [
    path('', include(router.urls)),
    path('generate/', GenerateSalaryAPIView.as_view(), name='generate-salary'),
    path("pay/<int:pk>/", PaySalaryAPIView.as_view(), name="pay-salary"),
    path('reports/salaries.pdf', SalaryReportPDFAPIView.as_view(), name='salary_report_pdf'),
    path('reports/salaries.xlsx', SalaryReportExcelAPIView.as_view(), name='salary_report_excel'),
]
