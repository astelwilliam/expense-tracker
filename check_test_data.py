#!/usr/bin/env python
import os
import sys
import django

# Add the project directory to the Python path
sys.path.append(os.path.dirname(__file__))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'expense_tracker.settings')

django.setup()

from django.contrib.auth.models import User
from expenses.models import Expense

try:
    user = User.objects.get(username='testuser')
    expenses = Expense.objects.filter(user=user).order_by('-date')
    print(f"Number of expenses for testuser: {expenses.count()}")
    total = 0
    for e in expenses:
        print(f"{e.date} - {e.title} - ${e.amount}")
        total += e.amount
    print(f"Total amount: ${total}")
except User.DoesNotExist:
    print("testuser does not exist")
except Exception as e:
    print(f"Error: {e}")
