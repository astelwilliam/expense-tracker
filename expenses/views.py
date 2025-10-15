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
    from django.db.models import Sum
    from django.db.models.functions import TruncMonth
    from datetime import datetime

    expenses = Expense.objects.filter(user=request.user).order_by('-date')

    # Calculate monthly total for current month
    current_month = datetime.now().month
    current_year = datetime.now().year
    monthly_total = Expense.objects.filter(
        user=request.user,
        date__year=current_year,
        date__month=current_month
    ).aggregate(total=Sum('amount'))['total'] or 0

    return render(request, 'expenses/home.html', {
        'expenses': expenses,
        'monthly_total': monthly_total,
        'current_month': datetime.now().strftime('%B %Y')
    })

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
def expenses_day_view(request):
    from datetime import date
    today = date.today()
    expenses = Expense.objects.filter(user=request.user, date=today).order_by('-date')
    return render(request, 'expenses/expenses_day.html', {'expenses': expenses, 'filter_date': today})

@login_required
def expenses_week_view(request):
    from datetime import date, timedelta
    today = date.today()
    week_start = today - timedelta(days=today.weekday())
    week_end = week_start + timedelta(days=6)
    expenses = Expense.objects.filter(user=request.user, date__range=[week_start, week_end]).order_by('-date')
    return render(request, 'expenses/expenses_week.html', {'expenses': expenses, 'week_start': week_start, 'week_end': week_end})

@login_required
def expenses_month_view(request):
    from datetime import date
    today = date.today()
    expenses = Expense.objects.filter(user=request.user, date__year=today.year, date__month=today.month).order_by('-date')
    return render(request, 'expenses/expenses_month.html', {'expenses': expenses, 'current_month': today.strftime('%B %Y')})

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

