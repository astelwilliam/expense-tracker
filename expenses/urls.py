# expenses/urls.py
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
]
