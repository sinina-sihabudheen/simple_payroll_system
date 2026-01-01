from django.db import models
# from apps.employees.models import EmployeeProfile

class Allowance(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    def __str__(self):
        return self.name

class Deduction(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    def __str__(self):
        return self.name


class SalaryRecord(models.Model):
    STATUS_CHOICES = (
        ("pending", "Pending"),
        ("partially_paid", "Partially Paid"),
        ("paid", "Paid"),
    )

    employee = models.ForeignKey('employees.EmployeeProfile', on_delete=models.CASCADE)
    year = models.IntegerField()
    month = models.IntegerField()

    present_days = models.IntegerField(default=0)
    absent_days = models.IntegerField(default=0)
    lop_count = models.IntegerField(default=0)  # Loss of Pay

    gross_salary = models.DecimalField(max_digits=12, decimal_places=2)   # Current month net
    total_allowances = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_deductions = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    salary_due = models.DecimalField(
        max_digits=12, decimal_places=2, default=0,
        help_text="Unpaid salary from previous months"
    )

    # Payment tracking
    paid_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    balance_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    paid_date = models.DateField(null=True, blank=True)


    generated_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.employee.name} - {self.month}/{self.year}"
