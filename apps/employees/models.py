from django.db import models
from django.contrib.auth.models import User
from apps.salary.models import Allowance, Deduction
from django.utils import timezone
from decimal import Decimal


class Department(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Designation(models.Model):
    title = models.CharField(max_length=100)

    def __str__(self):
        return self.title

class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class EmployeeType(models.Model):
    name = models.CharField(max_length=100) 

    def __str__(self):
        return self.name

STATUS_CHOICES = [
    ('working', 'Working'),
    ('resigned', 'Resigned'),
]

class EmployeeProfile(models.Model):
    # Basic Details
    name = models.CharField(max_length=200, null=True, blank=True)  # Instead of username/first_name/last_name
    employee_code = models.CharField(max_length=50, unique=True)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True)
    designation = models.ForeignKey(Designation, on_delete=models.SET_NULL, null=True, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)    

    CATEGORY_CHOICES = (
        ("staff", "Staff"),
        ("labour", "Labour"),
    )
    category = models.CharField(max_length=20, null=True, blank=True, choices=CATEGORY_CHOICES)

    # Employment Dates
    date_of_joining = models.DateField()
    date_of_resignation = models.DateField(null=True, blank=True)  # resignation/termination
    last_working_day = models.DateField(null=True, blank=True)

    # Documents
    passport_number = models.CharField(max_length=50, null=True, blank=True)
    passport_expiry_date = models.DateField(null=True, blank=True)
    emirates_id_number = models.CharField(max_length=50, null=True, blank=True)
    emirates_id_expiry_date = models.DateField(null=True, blank=True)

    STATUS_CHOICES = (
        ("working", "Working"),
        ("resigned", "Resigned"),
        ("terminated", "Terminated"),
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="working")

    # Salary (fixed fields)
    basic_salary = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    house_rent_allowance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    transportation_allowance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    cost_of_living_allowance = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    # Meta fields
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if self.pk:
            self.updated_at = timezone.now()
        super().save(*args, **kwargs)

    @property
    def net_salary(self):
        return (
            self.basic_salary +
            self.house_rent_allowance +
            self.transportation_allowance +
            self.cost_of_living_allowance
        )

    def __str__(self):
        return f"{self.name} ({self.employee_code})"


class EmployeeAllowance(models.Model):
    employee = models.ForeignKey(EmployeeProfile, on_delete=models.CASCADE)
    allowance = models.ForeignKey(Allowance, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if self.pk:
            self.updated_at = timezone.now()
        super().save(*args, **kwargs)

    class Meta:
        unique_together = ('employee', 'allowance')


class EmployeeDeduction(models.Model):
    DEDUCTION_METHOD_CHOICES = [
        ("next_month", "Next Month Salary"),
        ("installments", "Equal Deduction for X Months"),
        ("annual_leave", "Deduction from Annual Leave Salary"),
    ]

    employee = models.ForeignKey(EmployeeProfile, on_delete=models.CASCADE)
    deduction_type = models.ForeignKey(Deduction, on_delete=models.CASCADE,null=True, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    method = models.CharField(max_length=20, choices=DEDUCTION_METHOD_CHOICES, default="next_month")
    months = models.PositiveIntegerField(null=True, blank=True)
    date = models.DateField(default=timezone.now)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(null=True, blank=True)

    # New fields for tracking reimbursement
    reimbursed_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0, null=True, blank=True)
    remaining_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0, null=True, blank=True)
    remaining_installments = models.PositiveIntegerField(null=True, blank=True)
    is_closed = models.BooleanField(default=False)  # True if fully reimbursed

    def save(self, *args, **kwargs):
        if self.method == "installments":
            if not self.months or self.months <= 0:
                raise ValueError("Number of months must be greater than 0 for installment deduction.")
        
        if self.pk:
            self.updated_at = timezone.now()
        else:
            # Initialize remaining_amount and remaining_installments on first save
            self.remaining_amount = self.amount
            if self.method == "installments":
                self.remaining_installments = self.months
        super().save(*args, **kwargs)

    def apply_reimbursement(self, paid_amount):
        """
        Apply a salary payment to reduce the deduction.
        Returns the amount actually applied.
        """
        if self.is_closed:
            return Decimal("0.00")

        applied = Decimal("0.00")

        if self.method == "installments":
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

    def __str__(self):
        return f"{self.employee.name} - {self.deduction_type.name} ({self.amount})"