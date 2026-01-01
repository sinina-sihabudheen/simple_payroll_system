from rest_framework.views import APIView
from rest_framework.response import Response
from apps.attendance.models import Attendance, Leave
from apps.employees.models import EmployeeProfile
from .models import SalaryRecord, Allowance, Deduction
from .serializers import AllowanceSerializer, SalaryRecordSerializer, DeductionSerializer
from .utils import calculate_deductions, calculate_working_days
from datetime import date
from calendar import monthrange
from rest_framework import viewsets
from decimal import Decimal
from apps.employees.models import EmployeeAllowance, EmployeeDeduction
from django.db.models import Sum
from django.utils import timezone
from rest_framework import status



class AllowanceViewSet(viewsets.ModelViewSet):
    queryset = Allowance.objects.all()
    serializer_class = AllowanceSerializer

class DeductionViewSet(viewsets.ModelViewSet):
    queryset = Deduction.objects.all()
    serializer_class = DeductionSerializer


class GenerateSalaryAPIView(APIView):
    def post(self, request):
        year = int(request.data.get('year'))
        month = int(request.data.get('month'))
        today = date.today()

        # Determine last day to calculate
        if year == today.year and month == today.month:
            last_day = today.day  # Calculate up to today
        else:
            last_day = monthrange(year, month)[1]  # Full month

        results = []
        employees = EmployeeProfile.objects.all()

        for employee in employees:
            
            present_days, absent_days, sunday_count, approved_leave_count = calculate_working_days(employee, year, month, last_day)

            # ----- Salary Calculation -----
            basic = employee.basic_salary or Decimal(0)
            hra = employee.house_rent_allowance or Decimal(0)
            transport = employee.transportation_allowance or Decimal(0)
            col_allowance = employee.cost_of_living_allowance or Decimal(0)

            total_allowance = hra + transport + col_allowance
            gross_basic = basic + total_allowance

            total_days_in_month = monthrange(year, month)[1]
            daily_salary = gross_basic / total_days_in_month
            
            # Paid days include present days, Sundays (weekly off), and approved leaves
            paid_days = present_days + sunday_count + approved_leave_count
            salary_on_attendance = daily_salary * paid_days
            
            advance_deduction, other_deductions = calculate_deductions(employee, year, month)

            total_deductions = advance_deduction + other_deductions


            total_salary = salary_on_attendance - total_deductions
            previous_due = SalaryRecord.objects.filter(
                    employee=employee, status="pending"
                ).exclude(year=year, month=month).aggregate(
                    total_due=Sum('gross_salary')
                )['total_due'] or Decimal(0)

           
            salary_record, created = SalaryRecord.objects.get_or_create(
                employee=employee,
                year=year,
                month=month,
                defaults={
                    'present_days': present_days,
                    'absent_days': absent_days,
                    'lop_count': absent_days,
                    'total_allowances': total_allowance,
                    'total_deductions': total_deductions,
                    'gross_salary': total_salary,
                    'salary_due': previous_due,
                    'status': 'pending',
                }
            )

            # if not created, update fields except status
            if not created:
                salary_record.present_days = present_days
                salary_record.absent_days = absent_days
                salary_record.lop_count = absent_days
                salary_record.total_allowances = total_allowance
                salary_record.total_deductions = total_deductions
                salary_record.gross_salary = total_salary
                salary_record.salary_due = previous_due
                salary_record.save()


            results.append({
                'id': salary_record.id,
                'employee_id': employee.id,
                'employee_name': employee.name,
                'employee_number': employee.employee_code,
                'present_days': present_days,
                'absent_days': absent_days,
                'leave_count': sunday_count, # Keeping legacy name for Sundays
                'approved_leave_count': approved_leave_count,
                'basic_salary': basic,
                'gross_basic_salary': gross_basic,
                'house_rent_allowance': hra,
                'transportation_allowance': transport,
                'cost_of_living_allowance': col_allowance,
                'total_allowance': total_allowance,
                'salary_on_attendance': salary_on_attendance,
                'advance_deduction': advance_deduction,
                'other_deductions': other_deductions,
                'total_deduction': total_deductions,
                'total_salary': total_salary,
                'holiday_count': sunday_count, # Keeping legacy name for Sundays
                'status': salary_record.status,
                'paid_amount': salary_record.paid_amount or Decimal(0),
                'balance_amount': salary_record.balance_amount or (
                    (salary_record.gross_salary + salary_record.salary_due) - (salary_record.paid_amount or Decimal(0))
                ),
                'paid_date': salary_record.paid_date,
                
            })

        return Response(results)


class PaySalaryAPIView(APIView):
    def patch(self, request, pk):
        try:
            salary_record = SalaryRecord.objects.get(pk=pk)
        except SalaryRecord.DoesNotExist:
            return Response({"error": "Salary record not found"}, status=status.HTTP_404_NOT_FOUND)

        paid_amount = Decimal(request.data.get("paid_amount", 0))
        total_to_pay = salary_record.gross_salary + salary_record.salary_due

        salary_record.paid_amount += paid_amount

        # Deduction reimbursement
        remaining_amount_to_apply = paid_amount
        deductions = EmployeeDeduction.objects.filter(employee=salary_record.employee, is_closed=False)
        for deduction in deductions:
            applied = deduction.apply_reimbursement(remaining_amount_to_apply)
            remaining_amount_to_apply -= applied
            if remaining_amount_to_apply <= 0:
                break

        if salary_record.paid_amount >= total_to_pay:
            salary_record.balance_amount = Decimal(0)
            salary_record.status = "paid"
            salary_record.paid_date = timezone.now().date()
        else:
            salary_record.balance_amount = total_to_pay - salary_record.paid_amount
            salary_record.status = "partially_paid"
            salary_record.paid_date = timezone.now().date()

        salary_record.save()

        return Response({
            "employee": salary_record.employee.name,
            "month": salary_record.month,
            "year": salary_record.year,
            "gross_salary": salary_record.gross_salary,
            "salary_due": salary_record.salary_due,
            "paid_amount": salary_record.paid_amount,
            "balance_amount": salary_record.balance_amount,
            "status": salary_record.status,
            "paid_date": salary_record.paid_date,
        }, status=status.HTTP_200_OK)