from django.urls import path
from . import views

urlpatterns = [
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('', views.home_view, name='home'),
    path('add/', views.add_expense_view, name='add_expense'),
    path('delete/<int:expense_id>/', views.delete_expense_view, name='delete_expense'),
    path('day/', views.expenses_day_view, name='expenses_day'),
    path('week/', views.expenses_week_view, name='expenses_week'),
    path('month/', views.expenses_month_view, name='expenses_month'),
    path('reports/', views.monthly_reports_view, name='monthly_reports'),
    path('budgets/', views.budgets_view, name='budgets'),
    path('budgets/add/', views.add_budget_view, name='add_budget'),
    path('budgets/edit/<int:budget_id>/', views.edit_budget_view, name='edit_budget'),
    path('budgets/delete/<int:budget_id>/', views.delete_budget_view, name='delete_budget'),
    path('recurring/', views.recurring_expenses_view, name='recurring_expenses'),
    path('recurring/add/', views.add_recurring_expense_view, name='add_recurring_expense'),
    path('recurring/edit/<int:recurring_id>/', views.edit_recurring_expense_view, name='edit_recurring_expense'),
    path('recurring/delete/<int:recurring_id>/', views.delete_recurring_expense_view, name='delete_recurring_expense'),
    path('recurring/generate/', views.generate_recurring_expenses_view, name='generate_recurring_expenses'),
    path('export/', views.export_expenses_view, name='export_expenses'),
    path('import/', views.import_expenses_view, name='import_expenses'),
    path('import-export/', views.import_export_view, name='import_export'),
]
