# expenses/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum, Q
from datetime import datetime, date
from .forms import SignUpForm, LoginForm, ExpenseForm, BudgetForm, RecurringExpenseForm
from .models import Expense, Budget, RecurringExpense
import csv
import pandas as pd
from django.http import HttpResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from io import BytesIO

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

    # Get budget information for current month
    current_month_date = date(current_year, current_month, 1)
    overall_budget = Budget.objects.filter(
        user=request.user,
        category='Overall',
        month=current_month_date
    ).first()

    budget_remaining = None
    budget_alert = None
    if overall_budget:
        budget_remaining = overall_budget.amount - monthly_total
        if monthly_total >= overall_budget.amount:
            budget_alert = "exceeded"
        elif monthly_total >= overall_budget.amount * 0.9:
            budget_alert = "warning"

    return render(request, 'expenses/home.html', {
        'expenses': expenses,
        'monthly_total': monthly_total,
        'current_month': datetime.now().strftime('%B %Y'),
        'overall_budget': overall_budget,
        'budget_remaining': budget_remaining,
        'budget_alert': budget_alert,
    })

@login_required
def add_expense_view(request):
    if request.method == 'POST':
        form = ExpenseForm(request.POST)
        if form.is_valid():
            expense = form.save(commit=False)
            expense.user = request.user  # VERY IMPORTANT

            # Check for budget alerts before saving
            alerts = check_budget_alerts(request.user, expense.category, expense.amount, expense.date)
            expense.save()

            # Show alerts if any
            for alert in alerts:
                messages.warning(request, alert)

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

    # Get budgets for comparison
    budgets = Budget.objects.filter(user=request.user, category='Overall').order_by('-month')

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
        'budgets': budgets,
    }
    return render(request, 'expenses/monthly_reports.html', context)


@login_required
def budgets_view(request):
    budgets = Budget.objects.filter(user=request.user).order_by('-month', 'category')
    return render(request, 'expenses/budgets.html', {'budgets': budgets})


@login_required
def add_budget_view(request):
    if request.method == 'POST':
        form = BudgetForm(request.POST)
        if form.is_valid():
            budget = form.save(commit=False)
            budget.user = request.user
            # Set is_overall based on category
            budget.is_overall = (budget.category == 'Overall')
            budget.save()
            messages.success(request, 'Budget added successfully!')
            return redirect('budgets')
    else:
        form = BudgetForm()
    return render(request, 'expenses/add_budget.html', {'form': form})


@login_required
def edit_budget_view(request, budget_id):
    budget = get_object_or_404(Budget, id=budget_id, user=request.user)
    if request.method == 'POST':
        form = BudgetForm(request.POST, instance=budget)
        if form.is_valid():
            budget = form.save(commit=False)
            budget.is_overall = (budget.category == 'Overall')
            budget.save()
            messages.success(request, 'Budget updated successfully!')
            return redirect('budgets')
    else:
        form = BudgetForm(instance=budget)
    return render(request, 'expenses/edit_budget.html', {'form': form, 'budget': budget})


@login_required
def delete_budget_view(request, budget_id):
    budget = get_object_or_404(Budget, id=budget_id, user=request.user)
    budget.delete()
    messages.success(request, 'Budget deleted successfully!')
    return redirect('budgets')


@login_required
def recurring_expenses_view(request):
    recurring_expenses = RecurringExpense.objects.filter(user=request.user).order_by('category', 'title')
    return render(request, 'expenses/recurring_expenses.html', {'recurring_expenses': recurring_expenses})


@login_required
def add_recurring_expense_view(request):
    if request.method == 'POST':
        form = RecurringExpenseForm(request.POST)
        if form.is_valid():
            recurring_expense = form.save(commit=False)
            recurring_expense.user = request.user
            recurring_expense.save()
            messages.success(request, 'Recurring expense added successfully!')
            return redirect('recurring_expenses')
    else:
        form = RecurringExpenseForm()
    return render(request, 'expenses/add_recurring_expense.html', {'form': form})


@login_required
def edit_recurring_expense_view(request, recurring_id):
    recurring_expense = get_object_or_404(RecurringExpense, id=recurring_id, user=request.user)
    if request.method == 'POST':
        form = RecurringExpenseForm(request.POST, instance=recurring_expense)
        if form.is_valid():
            form.save()
            messages.success(request, 'Recurring expense updated successfully!')
            return redirect('recurring_expenses')
    else:
        form = RecurringExpenseForm(instance=recurring_expense)
    return render(request, 'expenses/edit_recurring_expense.html', {'form': form, 'recurring_expense': recurring_expense})


@login_required
def delete_recurring_expense_view(request, recurring_id):
    recurring_expense = get_object_or_404(RecurringExpense, id=recurring_id, user=request.user)
    recurring_expense.delete()
    messages.success(request, 'Recurring expense deleted successfully!')
    return redirect('recurring_expenses')


@login_required
def generate_recurring_expenses_view(request):
    """Manually trigger generation of recurring expenses for today"""
    from datetime import date
    today = date.today()
    generated_count = generate_recurring_expenses_for_date(request.user, today)
    messages.success(request, f'Generated {generated_count} recurring expenses for today.')
    return redirect('home')


def generate_recurring_expenses_for_date(user, target_date):
    """Generate expenses from active recurring templates for a specific date"""
    recurring_expenses = RecurringExpense.objects.filter(user=user, is_active=True)
    generated_count = 0

    for recurring in recurring_expenses:
        if recurring.should_generate_expense(target_date):
            # Check if expense already exists for this recurring expense on this date
            existing_expense = Expense.objects.filter(
                user=user,
                title=f"[Recurring] {recurring.title}",
                date=target_date,
                category=recurring.category,
                amount=recurring.amount
            ).exists()

            if not existing_expense:
                # Create the expense
                Expense.objects.create(
                    user=user,
                    title=f"[Recurring] {recurring.title}",
                    amount=recurring.amount,
                    date=target_date,
                    category=recurring.category,
                    notes=f"Auto-generated from recurring expense. {recurring.notes or ''}"
                )
                generated_count += 1

                # Update last_generated
                recurring.last_generated = target_date
                recurring.save()

    return generated_count


@login_required
def export_expenses_view(request):
    """Export expenses to CSV, Excel, or PDF"""
    export_format = request.GET.get('format', 'csv')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    expenses = Expense.objects.filter(user=request.user).order_by('-date')

    if start_date:
        expenses = expenses.filter(date__gte=start_date)
    if end_date:
        expenses = expenses.filter(date__lte=end_date)

    if export_format == 'csv':
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="expenses.csv"'

        writer = csv.writer(response)
        writer.writerow(['Date', 'Title', 'Amount', 'Category', 'Notes'])

        for expense in expenses:
            writer.writerow([
                expense.date.strftime('%Y-%m-%d'),
                expense.title,
                float(expense.amount),
                expense.category,
                expense.notes or ''
            ])

        return response

    elif export_format == 'excel':
        df = pd.DataFrame(list(expenses.values('date', 'title', 'amount', 'category', 'notes')))
        df['date'] = df['date'].dt.strftime('%Y-%m-%d')
        df['amount'] = df['amount'].astype(float)

        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename="expenses.xlsx"'

        with pd.ExcelWriter(response, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Expenses', index=False)

        return response

    elif export_format == 'pdf':
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="expenses.pdf"'

        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        styles = getSampleStyleSheet()

        # Title
        title = Paragraph("Expense Report", styles['Title'])
        elements = [title]

        # Table data
        data = [['Date', 'Title', 'Amount', 'Category', 'Notes']]
        for expense in expenses:
            data.append([
                expense.date.strftime('%Y-%m-%d'),
                expense.title,
                f"${float(expense.amount):.2f}",
                expense.category,
                expense.notes or ''
            ])

        # Create table
        table = Table(data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), '#f0f0f0'),
            ('TEXTCOLOR', (0, 0), (-1, 0), '#000000'),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), '#ffffff'),
            ('GRID', (0, 0), (-1, -1), 1, '#000000'),
        ]))

        elements.append(table)
        doc.build(elements)

        pdf = buffer.getvalue()
        buffer.close()
        response.write(pdf)
        return response

    return redirect('home')


@login_required
def import_expenses_view(request):
    """Import expenses from CSV or Excel file"""
    if request.method == 'POST' and request.FILES.get('file'):
        uploaded_file = request.FILES['file']
        file_extension = uploaded_file.name.split('.')[-1].lower()

        try:
            if file_extension == 'csv':
                df = pd.read_csv(uploaded_file)
            elif file_extension in ['xlsx', 'xls']:
                df = pd.read_excel(uploaded_file)
            else:
                messages.error(request, 'Unsupported file format. Please upload CSV or Excel file.')
                return redirect('import_export')

            # Process the dataframe
            imported_count = 0
            errors = []

            for index, row in df.iterrows():
                try:
                    # Map columns (case insensitive)
                    date_str = str(row.get('date', row.get('Date', ''))).strip()
                    title = str(row.get('title', row.get('Title', ''))).strip()
                    amount_str = str(row.get('amount', row.get('Amount', ''))).strip()
                    category = str(row.get('category', row.get('Category', ''))).strip()
                    notes = str(row.get('notes', row.get('Notes', ''))).strip()

                    # Validate required fields
                    if not date_str or not title or not amount_str:
                        errors.append(f"Row {index + 2}: Missing required fields (date, title, amount)")
                        continue

                    # Parse date
                    try:
                        expense_date = pd.to_datetime(date_str).date()
                    except:
                        errors.append(f"Row {index + 2}: Invalid date format")
                        continue

                    # Parse amount
                    try:
                        amount = float(amount_str.replace('$', '').replace(',', ''))
                    except:
                        errors.append(f"Row {index + 2}: Invalid amount format")
                        continue

                    # Validate category
                    valid_categories = [choice[0] for choice in Expense.CATEGORY_CHOICES]
                    if category not in valid_categories:
                        category = 'Other'  # Default to Other if invalid

                    # Create expense
                    Expense.objects.create(
                        user=request.user,
                        date=expense_date,
                        title=title,
                        amount=amount,
                        category=category,
                        notes=notes if notes else None
                    )
                    imported_count += 1

                except Exception as e:
                    errors.append(f"Row {index + 2}: {str(e)}")

            if imported_count > 0:
                messages.success(request, f'Successfully imported {imported_count} expenses.')

            if errors:
                for error in errors[:5]:  # Show first 5 errors
                    messages.warning(request, error)
                if len(errors) > 5:
                    messages.warning(request, f'... and {len(errors) - 5} more errors.')

        except Exception as e:
            messages.error(request, f'Error processing file: {str(e)}')

    return redirect('import_export')


@login_required
def import_export_view(request):
    """View for import/export page"""
    return render(request, 'expenses/import_export.html')


def check_budget_alerts(user, category, amount, expense_date):
    """Check if adding this expense triggers any budget alerts"""
    alerts = []

    # Get current month
    current_month = date(expense_date.year, expense_date.month, 1)

    # Check category-specific budget
    if category != 'Overall':
        category_budget = Budget.objects.filter(
            user=user,
            category=category,
            month=current_month
        ).first()

        if category_budget:
            # Calculate current spending in this category for the month
            current_spending = Expense.objects.filter(
                user=user,
                category=category,
                date__year=expense_date.year,
                date__month=expense_date.month
            ).aggregate(total=Sum('amount'))['total'] or 0

            new_total = current_spending + amount
            remaining = category_budget.amount - new_total

            if new_total >= category_budget.amount:
                alerts.append(f"⚠️ You've exceeded your {category} budget of ${category_budget.amount:.2f}!")
            elif new_total >= category_budget.amount * 0.9:
                alerts.append(f"⚠️ You're close to your {category} budget limit. Remaining: ${remaining:.2f}")

    # Check overall budget
    overall_budget = Budget.objects.filter(
        user=user,
        category='Overall',
        month=current_month
    ).first()

    if overall_budget:
        # Calculate total spending for the month
        total_spending = Expense.objects.filter(
            user=user,
            date__year=expense_date.year,
            date__month=expense_date.month
        ).aggregate(total=Sum('amount'))['total'] or 0

        new_total = total_spending + amount
        remaining = overall_budget.amount - new_total

        if new_total >= overall_budget.amount:
            alerts.append(f"🚨 You've exceeded your overall monthly budget of ${overall_budget.amount:.2f}!")
        elif new_total >= overall_budget.amount * 0.9:
            alerts.append(f"⚠️ You're approaching your overall budget limit. Remaining: ${remaining:.2f}")

    return alerts
