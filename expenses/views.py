# expenses/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import SignUpForm, LoginForm, ExpenseForm
from .models import Expense

def signup_view(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = SignUpForm()
    return render(request, 'expenses/signup.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('home')
    else:
        form = LoginForm()
    return render(request, 'expenses/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def home_view(request):
    expenses = Expense.objects.filter(user=request.user).order_by('-date')
    return render(request, 'expenses/home.html', {'expenses': expenses})

@login_required
def add_expense_view(request):
    if request.method == 'POST':
        form = ExpenseForm(request.POST)
        if form.is_valid():
            expense = form.save(commit=False)
            expense.user = request.user  # VERY IMPORTANT
            expense.save()
            return redirect('home')  # redirect after saving
    else:
        form = ExpenseForm()
    return render(request, 'expenses/add_expense.html', {'form': form})

@login_required
def delete_expense_view(request, expense_id):
    expense = get_object_or_404(Expense, id=expense_id, user=request.user)
    expense.delete()
    messages.success(request, 'Expense deleted successfully.')
    return redirect('home')

@login_required
def monthly_reports_view(request):
    from django.db.models import Sum
    from django.db.models.functions import TruncMonth
    import json

    # Get expenses for the current user
    expenses = Expense.objects.filter(user=request.user)

    # Monthly totals
    monthly_totals = expenses.annotate(month=TruncMonth('date')).values('month').annotate(total=Sum('amount')).order_by('month')

    # Category totals
    category_totals = expenses.values('category').annotate(total=Sum('amount')).order_by('-total')

    # Prepare data for charts
    monthly_labels = [item['month'].strftime('%B %Y') for item in monthly_totals]
    monthly_data = [float(item['total']) for item in monthly_totals]

    category_labels = [item['category'] for item in category_totals]
    category_data = [float(item['total']) for item in category_totals]

    context = {
        'monthly_labels': json.dumps(monthly_labels),
        'monthly_data': json.dumps(monthly_data),
        'category_labels': json.dumps(category_labels),
        'category_data': json.dumps(category_data),
        'monthly_totals': monthly_totals,
        'category_totals': category_totals,
    }
    return render(request, 'expenses/monthly_reports.html', context)

