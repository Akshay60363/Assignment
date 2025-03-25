from django.shortcuts import render
from django.http import JsonResponse
from django.views import View
from django.db import transaction
from django.utils import timezone
import datetime
from decimal import Decimal

from .models import User, Loan, Billing, Payment, InterestAccrual
from .tasks import calculate_credit_score

# Simple views for demonstration when DRF is not available
class RegisterUserView(View):
    pass

class ApplyLoanView(View):
    pass

class MakePaymentView(View):
    pass

class GetStatementView(View):
    pass
