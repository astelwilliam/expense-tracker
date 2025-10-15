# expenses/models.py
from django.db import models
from django.contrib.auth.models import User

class Expense(models.Model):
    CATEGORY_CHOICES = [
        ('Food', 'Food'),
        ('Travel', 'Travel'),
        ('Utilities', 'Utilities'),
        ('Entertainment', 'Entertainment'),
        ('Other', 'Other'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField()
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='Other')
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.title} - {self.amount}"


class Budget(models.Model):
    CATEGORY_CHOICES = [
        ('Food', 'Food'),
        ('Travel', 'Travel'),
        ('Utilities', 'Utilities'),
        ('Entertainment', 'Entertainment'),
        ('Other', 'Other'),
        ('Overall', 'Overall Monthly Budget'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='Overall')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    month = models.DateField()  # Will store the first day of the month
    is_overall = models.BooleanField(default=False)

    class Meta:
        unique_together = ['user', 'category', 'month']

    def __str__(self):
        return f"{self.user.username} - {self.category} Budget: {self.amount} ({self.month.strftime('%B %Y')})"


class RecurringExpense(models.Model):
    FREQUENCY_CHOICES = [
        ('monthly', 'Monthly'),
        ('weekly', 'Weekly'),
        ('daily', 'Daily'),
    ]

    CATEGORY_CHOICES = [
        ('Food', 'Food'),
        ('Travel', 'Travel'),
        ('Utilities', 'Utilities'),
        ('Entertainment', 'Entertainment'),
        ('Rent', 'Rent'),
        ('Subscriptions', 'Subscriptions'),
        ('Salary', 'Salary'),
        ('Other', 'Other'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='Other')
    frequency = models.CharField(max_length=20, choices=FREQUENCY_CHOICES, default='monthly')
    start_date = models.DateField()
    end_date = models.DateField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    notes = models.TextField(blank=True, null=True)
    last_generated = models.DateField(blank=True, null=True)

    def __str__(self):
        return f"{self.title} - {self.amount} ({self.frequency})"

    def should_generate_expense(self, target_date):
        """Check if an expense should be generated for the given date"""
        if not self.is_active:
            return False

        if target_date < self.start_date:
            return False

        if self.end_date and target_date > self.end_date:
            return False

        # Check based on frequency
        if self.frequency == 'monthly':
            # Generate on the same day of month as start_date
            return target_date.day == self.start_date.day
        elif self.frequency == 'weekly':
            # Generate on the same weekday as start_date
            return target_date.weekday() == self.start_date.weekday()
        elif self.frequency == 'daily':
            # Generate every day
            return True

        return False
