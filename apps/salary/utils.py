from decimal import Decimal
from apps.employees.models import EmployeeDeduction
from apps.attendance.models import Attendance, Leave
from datetime import date
from calendar import monthrange

# def calculate_deductions(employee, year, month):
#     """
#     Calculate total deductions for an employee for a given month.
#     Returns a tuple: (advance_amount, other_deductions_amount)
#     """
#     deductions = EmployeeDeduction.objects.filter(employee=employee)
#     advance_amount = Decimal("0.00")
#     other_deductions = Decimal("0.00")

#     for deduction in deductions:
#         # Skip if deduction_type is null
#         if not deduction.deduction_type:
#             continue

#         is_advance = deduction.deduction_type.name.lower() == "advance"

#         amount_to_add = Decimal("0.00")
#         if deduction.method == "next_month":
#             if deduction.date.month == month - 1 and deduction.date.year == year:
#                 amount_to_add = deduction.amount
#         elif deduction.method == "installments" and deduction.months:
#             installment_amount = deduction.amount / deduction.months
#             diff_months = (year - deduction.date.year) * 12 + (month - deduction.date.month)
#             if 0 <= diff_months < deduction.months:
#                 amount_to_add = installment_amount
#         elif deduction.method == "annual_leave" and month == 12:
#             amount_to_add = deduction.amount

#         if is_advance:
#             advance_amount += amount_to_add
#         else:
#             other_deductions += amount_to_add

#     return advance_amount, other_deductions
def calculate_deductions(employee, year, month):
    """
    Calculate total deductions for an employee for a given month.
    Returns a tuple: (advance_amount, other_deductions_amount)
    """
    deductions = EmployeeDeduction.objects.filter(employee=employee)
    advance_amount = Decimal("0.00")
    other_deductions = Decimal("0.00")

    for deduction in deductions:
        # Skip if deduction_type is null or already paid off
        if not deduction.deduction_type or deduction.is_closed or deduction.remaining_amount <= 0:
            continue

        is_advance = deduction.deduction_type.name.lower() == "advance"

        amount_to_add = Decimal("0.00")
        if deduction.method == "next_month":
            if deduction.date.month == month - 1 and deduction.date.year == year:
                amount_to_add = deduction.amount
        elif deduction.method == "installments" and deduction.months:
            installment_amount = deduction.amount / deduction.months
            diff_months = (year - deduction.date.year) * 12 + (month - deduction.date.month)
            if 0 <= diff_months < deduction.months:
                amount_to_add = installment_amount
        elif deduction.method == "annual_leave" and month == 12:
            amount_to_add = deduction.amount

        if is_advance:
            advance_amount += amount_to_add
        else:
            other_deductions += amount_to_add

    return advance_amount, other_deductions


def apply_reimbursement(self, paid_amount):
    """
    Apply salary payment to reduce this deduction.
    Returns the amount applied.
    """
    if self.is_closed:
        return Decimal("0.00")

    applied = Decimal("0.00")

    if self.method == "installments" and self.remaining_installments:
        installment_amount = self.amount / self.months
        applied = min(installment_amount, self.remaining_amount, paid_amount)
        self.reimbursed_amount += applied
        self.remaining_amount -= applied
        self.remaining_installments = max(0, self.remaining_installments - 1)
    else:
        applied = min(self.remaining_amount, paid_amount)
        self.reimbursed_amount += applied
        self.remaining_amount -= applied

    if self.remaining_amount <= 0:
        self.is_closed = True
        self.remaining_amount = Decimal("0.00")
        self.remaining_installments = 0

    self.save()
    return applied


def calculate_working_days(employee, year, month, last_day):
    present_days = 0
    absent_days = 0
    sunday_count = 0
    approved_leave_count = 0

    for day in range(1, last_day + 1):
        current_date = date(year, month, day)

        # Skip Sundays
        if current_date.weekday() == 6:  # Sunday is 6
            sunday_count += 1
            continue

        attendance = Attendance.objects.filter(
            employee=employee, date=current_date, is_present=True
        ).first()

        if attendance and attendance.is_present:
            present_days += 1
        else:
            # Check for approved leave
            leave = Leave.objects.filter(
                employee=employee, date=current_date, approved=True
            ).exists()
            
            if leave:
                approved_leave_count += 1
            else:
                absent_days += 1

    return present_days, absent_days, sunday_count, approved_leave_count

