# TODO: Enhance Expense Tracker with Categories, Monthly Reports, Charts, and Improved Styling

## Steps to Complete

- [x] Add 'category' field to Expense model with predefined choices (Food, Travel, Utilities, Entertainment, Other)
- [x] Create and run Django migration for the new category field
- [x] Update ExpenseForm to include category field as select dropdown
- [x] Modify add_expense.html template to display category field
- [x] Update home.html template to show category in expense list and extend base.html
- [x] Update login.html and signup.html templates to extend base.html
- [x] Add monthly_reports view that groups expenses by month/year and calculates totals
- [x] Create monthly_reports.html template with Chart.js pie chart (expenses by category) and bar chart (monthly totals)
- [x] Add URL for monthly_reports view in expenses/urls.py
- [x] Update base.html to include Chart.js CDN link and ensure all templates extend it
- [x] Enhance style.css with modern CSS: responsive design, color scheme, typography, animations (fade-in, hover effects, smooth transitions)
- [x] Update templates to use CSS classes for consistent styling and animations
- [x] Run migrations to apply model changes
- [x] Test adding expenses with categories
- [x] Test monthly reports view and charts rendering
- [x] Verify styling and animations across all pages

## Add Delete Functionality for Expenses

- [x] Add delete_expense_view in views.py with login_required, ownership check, and redirect
- [x] Add URL pattern for delete in expenses/urls.py
- [x] Update home.html to include delete buttons/forms for each expense
- [x] Add CSS styling for delete buttons in style.css
- [ ] Test deleting expenses and verify security (only own expenses)

## Phase 1 MVP Enhancements

- [x] Add 'notes' field to Expense model as optional TextField
- [x] Create and apply migration for the notes field
- [x] Update ExpenseForm to include notes field as textarea
- [x] Modify add_expense.html and home.html to display notes
- [x] Add filtering functionality: Create new views for day/week/month expense lists
- [x] Add URL patterns for the new filter views
- [x] Create templates for filtered views (extend base.html)
- [x] Enhance home page with basic monthly summary (total spent this month)
- [x] Update navigation to include links to filtered views

## Phase 2: Budgeting & Alerts

- [ ] Add Budget model with fields: user (ForeignKey), category (CharField with choices), amount (DecimalField), month (DateField), is_overall (BooleanField)
- [ ] Create and run migration for Budget model
- [ ] Add BudgetForm for creating/editing budgets
- [ ] Create budget management views: list_budgets, add_budget, edit_budget, delete_budget
- [ ] Add URL patterns for budget views
- [ ] Create budget templates: budgets.html, add_budget.html, edit_budget.html
- [ ] Update navigation to include "Budgets" link
- [ ] Add budget checking logic in expense creation to show alerts when nearing/exceeding budget
- [ ] Update home.html to display remaining budget widget
- [ ] Add budget alerts/messages in templates when spending approaches or exceeds budget limits
- [ ] Update monthly_reports.html to show budget vs actual spending comparisons
- [ ] Add CSS styling for budget-related elements and alerts
