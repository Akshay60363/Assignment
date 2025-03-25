from django.db import models
import uuid
from decimal import Decimal
from django.utils import timezone
import datetime


class User(models.Model):
    """
    Model representing a user registered in the system.
    """
    unique_user_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    aadhar_id = models.CharField(max_length=12, unique=True)
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    annual_income = models.DecimalField(max_digits=12, decimal_places=2)
    credit_score = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.name} ({self.aadhar_id})"


class Loan(models.Model):
    """
    Model representing a loan issued to a user.
    """
    LOAN_TYPE_CHOICES = [
        ('CC', 'Credit Card'),
    ]
    
    LOAN_STATUS_CHOICES = [
        ('ACTIVE', 'Active'),
        ('CLOSED', 'Closed'),
    ]
    
    loan_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='loans')
    loan_type = models.CharField(max_length=2, choices=LOAN_TYPE_CHOICES)
    loan_amount = models.DecimalField(max_digits=10, decimal_places=2)
    interest_rate = models.DecimalField(max_digits=5, decimal_places=2)  # Annual interest rate in percentage
    term_period = models.PositiveIntegerField()  # In months
    disbursement_date = models.DateField()
    principal_balance = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=10, choices=LOAN_STATUS_CHOICES, default='ACTIVE')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Loan {self.loan_id} - {self.user.name}"
    
    def daily_interest_rate(self):
        """Calculate daily interest rate"""
        return round(self.interest_rate / Decimal('365'), 3)
    
    def calculate_min_due(self, interest_accrued):
        """Calculate minimum due amount for a billing cycle"""
        principal_portion = self.principal_balance * Decimal('0.03')  # 3% of principal balance
        return principal_portion + interest_accrued
    
    def get_next_billing_date(self):
        """Get the next billing date, which is 30 days after account creation or last billing date"""
        last_billing = self.billings.order_by('-billing_date').first()
        
        if last_billing:
            return last_billing.billing_date + datetime.timedelta(days=30)
        else:
            # If no previous billing exists, use 30 days from disbursement date
            return self.disbursement_date + datetime.timedelta(days=30)
    
    def get_due_date(self, billing_date):
        """Get the due date, which is 15 days from the billing date"""
        return billing_date + datetime.timedelta(days=15)


class Billing(models.Model):
    """
    Model representing a billing cycle for a loan.
    """
    billing_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    loan = models.ForeignKey(Loan, on_delete=models.CASCADE, related_name='billings')
    billing_date = models.DateField()
    due_date = models.DateField()
    principal_amount = models.DecimalField(max_digits=10, decimal_places=2)
    interest_amount = models.DecimalField(max_digits=10, decimal_places=2)
    minimum_due = models.DecimalField(max_digits=10, decimal_places=2)
    total_due = models.DecimalField(max_digits=10, decimal_places=2)
    is_paid = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Billing {self.billing_id} for Loan {self.loan.loan_id}"


class Payment(models.Model):
    """
    Model representing a payment made by a user towards a loan.
    """
    payment_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    loan = models.ForeignKey(Loan, on_delete=models.CASCADE, related_name='payments')
    billing = models.ForeignKey(Billing, on_delete=models.CASCADE, related_name='payments', null=True, blank=True)
    payment_date = models.DateField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    principal_payment = models.DecimalField(max_digits=10, decimal_places=2)
    interest_payment = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Payment {self.payment_id} for Loan {self.loan.loan_id}"


class InterestAccrual(models.Model):
    """
    Model to track daily interest accruals.
    """
    loan = models.ForeignKey(Loan, on_delete=models.CASCADE, related_name='interest_accruals')
    accrual_date = models.DateField()
    principal_balance = models.DecimalField(max_digits=10, decimal_places=2)
    daily_interest_rate = models.DecimalField(max_digits=10, decimal_places=5)
    interest_amount = models.DecimalField(max_digits=10, decimal_places=2)
    billing = models.ForeignKey(Billing, on_delete=models.CASCADE, related_name='interest_accruals', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('loan', 'accrual_date')
    
    def __str__(self):
        return f"Interest accrual for Loan {self.loan.loan_id} on {self.accrual_date}"
