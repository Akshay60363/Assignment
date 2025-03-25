# Bright Credit Service

A Django-based credit service application that facilitates efficient lending by a loan provider to users.

## Features

- User registration with credit score calculation
- Credit card loan application and processing
- Loan payment handling
- Statement generation and retrieval
- Daily interest accrual
- Monthly billing cycles

## API Endpoints

### 1. User Registration
- **Endpoint**: `/api/register-user/`
- **Method**: POST
- **Request Body**:
  ```json
  {
    "aadhar_id": "123456789012",
    "name": "John Doe",
    "email": "john@example.com",
    "annual_income": 500000
  }
  ```
- **Response**:
  ```json
  {
    "error": null,
    "unique_user_id": "uuid-string"
  }
  ```

### 2. Loan Application
- **Endpoint**: `/api/apply-loan/`
- **Method**: POST
- **Request Body**:
  ```json
  {
    "unique_user_id": "uuid-string",
    "loan_type": "CC",
    "loan_amount": 5000,
    "interest_rate": 15,
    "term_period": 12,
    "disbursement_date": "2023-08-01"
  }
  ```
- **Response**:
  ```json
  {
    "error": null,
    "loan_id": "uuid-string",
    "due_dates": [
      {
        "date": "2023-09-15",
        "amount_due": 300
      },
      ...
    ]
  }
  ```

### 3. Make Payment
- **Endpoint**: `/api/make-payment/`
- **Method**: POST
- **Request Body**:
  ```json
  {
    "loan_id": "uuid-string",
    "amount": 300
  }
  ```
- **Response**:
  ```json
  {
    "error": null
  }
  ```

### 4. Get Statement
- **Endpoint**: `/api/get-statement/?loan_id=uuid-string`
- **Method**: GET
- **Response**:
  ```json
  {
    "error": null,
    "past_transactions": [
      {
        "date": "2023-09-15",
        "principal": 150,
        "interest": 150,
        "amount_paid": 300
      },
      ...
    ],
    "upcoming_transactions": [
      {
        "date": "2023-10-15",
        "amount_due": 300
      },
      ...
    ]
  }
  ```

## Setup and Installation

1. Clone the repository
2. Install dependencies:
   ```
   pip install django djangorestframework celery django-celery-results pandas
   ```
3. Run migrations:
   ```
   python manage.py makemigrations
   python manage.py migrate
   ```
4. Start the development server:
   ```
   python manage.py runserver
   ```
5. Start Celery worker for background tasks:
   ```
   celery -A bright_credit worker -l info
   ```
6. Run scheduled tasks:
   ```
   celery -A bright_credit beat -l info
   ```

## Business Rules

- Interest accrues daily
- Billing cycle is 30 days
- Due date is 15 days after billing date
- Minimum due = (Principal Balance * 3%) + (Interest accrued in the billing cycle)
- Past due amounts are paid first
- Loan is closed when principal balance is $0

## Technologies Used

- Django
- Django REST Framework
- Celery for asynchronous tasks
- SQLite (can be replaced with PostgreSQL for production)
- Pandas for transaction processing 