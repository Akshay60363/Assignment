import pandas as pd
from decimal import Decimal
try:
    from celery import shared_task
except ImportError:
    # Provide a dummy decorator when Celery is not available
    def shared_task(func):
        return func

from django.conf import settings
from django.db import transaction
from django.utils import timezone
import datetime

from .models import User, Loan, Billing, InterestAccrual


@shared_task
def calculate_credit_score(user_id):
    """
    Calculate credit score based on transactions in CSV file.
    
    Credit score calculation rules:
    - If account balance >= 1,000,000, credit score = 900
    - If account balance <= 10,000, credit score = 300
    - For intermediate values, adjust by 10 points for every Rs. 15,000
    """
    try:
        user = User.objects.get(unique_user_id=user_id)
    except User.DoesNotExist:
        return {"error": "User not found"}
    
    try:
        # Read CSV file
        transactions_df = pd.read_csv(settings.TRANSACTION_CSV_PATH)
        
        # Filter transactions for this user
        user_transactions = transactions_df[transactions_df['AADHAR_ID'] == user.aadhar_id]
        
        if user_transactions.empty:
            # No transactions found, assign minimum score
            user.credit_score = 300
            user.save()
            return {"error": None, "credit_score": user.credit_score}
        
        # Calculate total balance (CREDIT - DEBIT)
        credits = user_transactions[user_transactions['Transaction_type'] == 'CREDIT']['Amount'].sum()
        debits = user_transactions[user_transactions['Transaction_type'] == 'DEBIT']['Amount'].sum()
        total_balance = credits - debits
        
        # Calculate credit score based on rules
        if total_balance >= 1000000:
            credit_score = 900
        elif total_balance <= 10000:
            credit_score = 300
        else:
            # Adjust score by 10 points for every Rs. 15,000
            balance_above_min = total_balance - 10000
            points_to_add = int(balance_above_min / 15000) * 10
            credit_score = 300 + points_to_add
            
            # Ensure it doesn't exceed maximum
            credit_score = min(credit_score, 900)
        
        # Update user's credit score
        user.credit_score = credit_score
        user.save()
        
        return {"error": None, "credit_score": credit_score}
    
    except Exception as e:
        return {"error": str(e)}


@shared_task
def run_daily_billing():
    """
    Run daily task to generate billings for eligible loans.
    This should be scheduled to run once per day.
    """
    today = timezone.now().date()
    results = []
    
    # Find all active loans
    active_loans = Loan.objects.filter(status='ACTIVE')
    
    for loan in active_loans:
        next_billing_date = loan.get_next_billing_date()
        
        # Check if today is a billing date for this loan
        if next_billing_date == today:
            result = generate_billing_for_loan(loan.loan_id)
            results.append(result)
    
    return results


@shared_task
def generate_billing_for_loan(loan_id):
    """
    Generate billing for a specific loan.
    """
    try:
        with transaction.atomic():
            loan = Loan.objects.select_for_update().get(loan_id=loan_id)
            
            if loan.status != 'ACTIVE':
                return {"error": "Loan is not active", "loan_id": str(loan_id)}
            
            billing_date = loan.get_next_billing_date()
            due_date = loan.get_due_date(billing_date)
            
            # Calculate interest accrued since last billing date or loan disbursement
            last_billing = loan.billings.order_by('-billing_date').first()
            start_date = last_billing.billing_date + datetime.timedelta(days=1) if last_billing else loan.disbursement_date + datetime.timedelta(days=1)
            end_date = billing_date
            
            # Get all interest accruals for this period
            interest_accruals = loan.interest_accruals.filter(
                accrual_date__gte=start_date,
                accrual_date__lte=end_date
            )
            
            # Sum up all interest for this period
            total_interest = sum(accrual.interest_amount for accrual in interest_accruals)
            
            # Calculate minimum due
            min_due = loan.calculate_min_due(total_interest)
            
            # Create billing record
            billing = Billing.objects.create(
                loan=loan,
                billing_date=billing_date,
                due_date=due_date,
                principal_amount=loan.principal_balance,
                interest_amount=total_interest,
                minimum_due=min_due,
                total_due=loan.principal_balance + total_interest
            )
            
            # Link interest accruals to this billing
            interest_accruals.update(billing=billing)
            
            return {
                "error": None,
                "loan_id": str(loan_id),
                "billing_id": str(billing.billing_id),
                "billing_date": billing_date.isoformat(),
                "due_date": due_date.isoformat(),
                "minimum_due": float(min_due)
            }
            
    except Loan.DoesNotExist:
        return {"error": "Loan not found", "loan_id": str(loan_id)}
    except Exception as e:
        return {"error": str(e), "loan_id": str(loan_id)}


@shared_task
def accrue_daily_interest():
    """
    Daily task to accrue interest for all active loans.
    """
    today = timezone.now().date()
    results = []
    
    # Find all active loans
    active_loans = Loan.objects.filter(status='ACTIVE')
    
    for loan in active_loans:
        # Skip if interest already accrued for today
        if InterestAccrual.objects.filter(loan=loan, accrual_date=today).exists():
            continue
        
        try:
            with transaction.atomic():
                # Recalculate with lock to prevent race conditions
                loan = Loan.objects.select_for_update().get(loan_id=loan.loan_id)
                
                # Calculate daily interest
                daily_rate = loan.daily_interest_rate()
                interest_amount = (loan.principal_balance * daily_rate) / Decimal('100')
                
                # Record interest accrual
                InterestAccrual.objects.create(
                    loan=loan,
                    accrual_date=today,
                    principal_balance=loan.principal_balance,
                    daily_interest_rate=daily_rate,
                    interest_amount=interest_amount
                )
                
                results.append({
                    "error": None,
                    "loan_id": str(loan.loan_id),
                    "interest_amount": float(interest_amount)
                })
                
        except Exception as e:
            results.append({
                "error": str(e),
                "loan_id": str(loan.loan_id)
            })
    
    return results 