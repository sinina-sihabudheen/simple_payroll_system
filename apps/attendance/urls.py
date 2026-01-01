from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    AttendanceViewSet,
    LeaveViewSet,
    LeaveTypeViewSet,
    EsslPunchViewSet,
    SyncEsslToAttendance,
    AttendanceByDate,
    MarkAttendanceManually
)


router = DefaultRouter()
router.register(r'attendance', AttendanceViewSet)
router.register(r'leaves', LeaveViewSet)
router.register(r'leave-types', LeaveTypeViewSet)
router.register(r'essl-punches', EsslPunchViewSet)

urlpatterns = [
    path('sync-essl/', SyncEsslToAttendance.as_view(), name='sync_essl'),
    path('attendance-by-date/', AttendanceByDate.as_view(), name='attendance_by_date'),
    path('mark-attendance/', MarkAttendanceManually.as_view(), name='mark_attendance'),


    path('', include(router.urls)),
]
