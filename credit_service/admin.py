from django.contrib import admin
from .models import User, Loan, Billing, Payment, InterestAccrual

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('name', 'aadhar_id', 'email', 'annual_income', 'credit_score', 'created_at')
    search_fields = ('name', 'aadhar_id', 'email')

@admin.register(Loan)
class LoanAdmin(admin.ModelAdmin):
    list_display = ('loan_id', 'user', 'loan_type', 'loan_amount', 'interest_rate', 'term_period', 
                    'disbursement_date', 'principal_balance', 'status', 'created_at')
    list_filter = ('status', 'loan_type')
    search_fields = ('loan_id', 'user__name', 'user__aadhar_id')

@admin.register(Billing)
class BillingAdmin(admin.ModelAdmin):
    list_display = ('billing_id', 'loan', 'billing_date', 'due_date', 'principal_amount', 
                   'interest_amount', 'minimum_due', 'total_due', 'is_paid')
    list_filter = ('is_paid', 'billing_date', 'due_date')
    search_fields = ('billing_id', 'loan__loan_id')

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('payment_id', 'loan', 'payment_date', 'amount', 'principal_payment', 'interest_payment')
    list_filter = ('payment_date',)
    search_fields = ('payment_id', 'loan__loan_id')

@admin.register(InterestAccrual)
class InterestAccrualAdmin(admin.ModelAdmin):
    list_display = ('loan', 'accrual_date', 'principal_balance', 'daily_interest_rate', 'interest_amount')
    list_filter = ('accrual_date',)
    search_fields = ('loan__loan_id',)
