"""
This module contains serializers for the credit service.
If REST Framework is not available, it provides dummy versions.
"""
from .models import User, Loan, Billing, Payment
from decimal import Decimal
from django.conf import settings

# Dummy serializers that will be used only for migrations
class UserSerializer:
    pass

class LoanApplicationSerializer:
    pass

class PaymentSerializer:
    pass

class LoanStatementSerializer:
    pass

class TransactionSerializer:
    pass

class UpcomingEMISerializer:
    pass

class StatementResponseSerializer:
    pass

# The actual implementation would be used when REST Framework is available
try:
    from rest_framework import serializers
    
    class UserSerializer(serializers.ModelSerializer):
        class Meta:
            model = User
            fields = ['unique_user_id', 'aadhar_id', 'name', 'email', 'annual_income', 'credit_score']
            read_only_fields = ['unique_user_id', 'credit_score']
            
    class LoanApplicationSerializer(serializers.ModelSerializer):
        unique_user_id = serializers.UUIDField()
        
        class Meta:
            model = Loan
            fields = [
                'unique_user_id', 'loan_type', 'loan_amount', 
                'interest_rate', 'term_period', 'disbursement_date'
            ]
            
        def validate(self, data):
            """
            Validate loan application based on criteria:
            - Credit score >= 450
            - Annual income >= 150,000
            - Loan amount <= 5,000
            - Interest rate >= 12%
            - Monthly EMI <= 20% of monthly income
            """
            # Validate user exists
            try:
                user = User.objects.get(unique_user_id=data['unique_user_id'])
            except User.DoesNotExist:
                raise serializers.ValidationError("User not found")
            
            # Validate credit score
            if not user.credit_score or user.credit_score < settings.MIN_CREDIT_SCORE_FOR_LOAN:
                raise serializers.ValidationError("Credit score is too low or not available")
            
            # Validate annual income
            if user.annual_income < settings.MIN_ANNUAL_INCOME:
                raise serializers.ValidationError("Annual income does not meet minimum requirements")
            
            # Validate loan amount
            if data['loan_amount'] > settings.MAX_LOAN_AMOUNT:
                raise serializers.ValidationError(f"Loan amount exceeds maximum allowed amount of {settings.MAX_LOAN_AMOUNT}")
            
            # Validate interest rate
            if data['interest_rate'] < settings.MIN_INTEREST_RATE:
                raise serializers.ValidationError(f"Interest rate must be at least {settings.MIN_INTEREST_RATE}%")
            
            # Validate loan type
            if data['loan_type'] != 'CC':
                raise serializers.ValidationError("Only Credit Card loans are supported at this time")
            
            # Validate EMI doesn't exceed 20% of monthly income
            monthly_income = user.annual_income / Decimal('12')
            max_allowed_emi = monthly_income * settings.MAX_EMI_PERCENTAGE_OF_INCOME / Decimal('100')
            
            # Calculate EMI (approximate using simple interest for validation)
            principal = data['loan_amount']
            rate = data['interest_rate'] / Decimal('100') / Decimal('12')  # Monthly rate
            term = data['term_period']
            
            # Principal portion (3% of principal)
            principal_portion = principal * Decimal('0.03')
            
            # Interest for first month
            monthly_interest = principal * rate
            
            # Estimated first EMI
            estimated_emi = principal_portion + monthly_interest
            
            if estimated_emi > max_allowed_emi:
                raise serializers.ValidationError(f"Monthly EMI exceeds {settings.MAX_EMI_PERCENTAGE_OF_INCOME}% of monthly income")
            
            # Ensure monthly interest exceeds minimum required
            if monthly_interest < settings.MIN_MONTHLY_INTEREST:
                raise serializers.ValidationError(f"Monthly interest must be at least {settings.MIN_MONTHLY_INTEREST}")
            
            return data

    class PaymentSerializer(serializers.Serializer):
        loan_id = serializers.UUIDField()
        amount = serializers.DecimalField(max_digits=10, decimal_places=2)
        
        def validate(self, data):
            # Validate loan exists and is active
            try:
                loan = Loan.objects.get(loan_id=data['loan_id'])
            except Loan.DoesNotExist:
                raise serializers.ValidationError("Loan not found")
            
            if loan.status != 'ACTIVE':
                raise serializers.ValidationError("Loan is already closed")
            
            return data

    REST_FRAMEWORK_AVAILABLE = True
except ImportError:
    # Provide dummy implementations when REST Framework is not available
    REST_FRAMEWORK_AVAILABLE = False
    
    class serializers:
        class Serializer:
            pass
            
        class ModelSerializer:
            pass
            
        class ValidationError(Exception):
            pass
            
        class UUIDField:
            def __init__(self, **kwargs):
                pass
                
        class DecimalField:
            def __init__(self, **kwargs):
                pass
                
        class DateField:
            def __init__(self, **kwargs):
                pass

from .models import User, Loan, Billing, Payment
from decimal import Decimal
from django.conf import settings


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['unique_user_id', 'aadhar_id', 'name', 'email', 'annual_income', 'credit_score']
        read_only_fields = ['unique_user_id', 'credit_score']
        

class LoanApplicationSerializer(serializers.ModelSerializer):
    unique_user_id = serializers.UUIDField()
    
    class Meta:
        model = Loan
        fields = [
            'unique_user_id', 'loan_type', 'loan_amount', 
            'interest_rate', 'term_period', 'disbursement_date'
        ]
        
    def validate(self, data):
        """
        Validate loan application based on criteria:
        - Credit score >= 450
        - Annual income >= 150,000
        - Loan amount <= 5,000
        - Interest rate >= 12%
        - Monthly EMI <= 20% of monthly income
        """
        # Validate user exists
        try:
            user = User.objects.get(unique_user_id=data['unique_user_id'])
        except User.DoesNotExist:
            raise serializers.ValidationError("User not found")
        
        # Validate credit score
        if not user.credit_score or user.credit_score < settings.MIN_CREDIT_SCORE_FOR_LOAN:
            raise serializers.ValidationError("Credit score is too low or not available")
        
        # Validate annual income
        if user.annual_income < settings.MIN_ANNUAL_INCOME:
            raise serializers.ValidationError("Annual income does not meet minimum requirements")
        
        # Validate loan amount
        if data['loan_amount'] > settings.MAX_LOAN_AMOUNT:
            raise serializers.ValidationError(f"Loan amount exceeds maximum allowed amount of {settings.MAX_LOAN_AMOUNT}")
        
        # Validate interest rate
        if data['interest_rate'] < settings.MIN_INTEREST_RATE:
            raise serializers.ValidationError(f"Interest rate must be at least {settings.MIN_INTEREST_RATE}%")
        
        # Validate loan type
        if data['loan_type'] != 'CC':
            raise serializers.ValidationError("Only Credit Card loans are supported at this time")
        
        # Validate EMI doesn't exceed 20% of monthly income
        monthly_income = user.annual_income / Decimal('12')
        max_allowed_emi = monthly_income * settings.MAX_EMI_PERCENTAGE_OF_INCOME / Decimal('100')
        
        # Calculate EMI (approximate using simple interest for validation)
        principal = data['loan_amount']
        rate = data['interest_rate'] / Decimal('100') / Decimal('12')  # Monthly rate
        term = data['term_period']
        
        # Principal portion (3% of principal)
        principal_portion = principal * Decimal('0.03')
        
        # Interest for first month
        monthly_interest = principal * rate
        
        # Estimated first EMI
        estimated_emi = principal_portion + monthly_interest
        
        if estimated_emi > max_allowed_emi:
            raise serializers.ValidationError(f"Monthly EMI exceeds {settings.MAX_EMI_PERCENTAGE_OF_INCOME}% of monthly income")
        
        # Ensure monthly interest exceeds minimum required
        if monthly_interest < settings.MIN_MONTHLY_INTEREST:
            raise serializers.ValidationError(f"Monthly interest must be at least {settings.MIN_MONTHLY_INTEREST}")
            
        return data


class PaymentSerializer(serializers.Serializer):
    loan_id = serializers.UUIDField()
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    
    def validate(self, data):
        # Validate loan exists and is active
        try:
            loan = Loan.objects.get(loan_id=data['loan_id'])
        except Loan.DoesNotExist:
            raise serializers.ValidationError("Loan not found")
            
        if loan.status != 'ACTIVE':
            raise serializers.ValidationError("Loan is already closed")
            
        return data


class LoanStatementSerializer(serializers.Serializer):
    loan_id = serializers.UUIDField()
    
    def validate(self, data):
        # Validate loan exists
        try:
            loan = Loan.objects.get(loan_id=data['loan_id'])
        except Loan.DoesNotExist:
            raise serializers.ValidationError("Loan not found")
            
        return data


class TransactionSerializer(serializers.Serializer):
    date = serializers.DateField()
    principal = serializers.DecimalField(max_digits=10, decimal_places=2)
    interest = serializers.DecimalField(max_digits=10, decimal_places=2)
    amount_paid = serializers.DecimalField(max_digits=10, decimal_places=2)


class UpcomingEMISerializer(serializers.Serializer):
    date = serializers.DateField()
    amount_due = serializers.DecimalField(max_digits=10, decimal_places=2)


class StatementResponseSerializer(serializers.Serializer):
    past_transactions = TransactionSerializer(many=True)
    upcoming_transactions = UpcomingEMISerializer(many=True)
    
    def to_representation(self, instance):
        data = super().to_representation(instance)
        if instance.get('error'):
            data['error'] = instance['error']
            data.pop('past_transactions', None)
            data.pop('upcoming_transactions', None)
        else:
            data['error'] = None
        return data 