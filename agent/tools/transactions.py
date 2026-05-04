import pandas as pd

class PersonalFinance():
    def __init__(self, csv_path):
        self.df = pd.read_csv(csv_path)

    def total_spent_category(self):
        total_spent_by_category = self.df.groupby(['Category'])['INR'].sum()
        return total_spent_by_category
    
    def monthly_summary(self):
        df_copy = self.df.copy()
        df_copy['Date'] = pd.to_datetime(df_copy['Date']).dt.to_period("M")
        self.income_expense_monthly = df_copy.groupby(['Income/Expense','Date'])['INR'].sum()
        return self.income_expense_monthly
    
    def ten_biggest_expenses(self):
        biggest_expenses = self.df[self.df['Income/Expense']=='Expense'].sort_values('INR', ascending=False).head(10)
        return biggest_expenses
    
    def balance_estimate(self):
        self.monthly_summary()
        # unstack() turns the Income/Expense index level into columns (it may in a month the data doesn't have income or expense)
        # so we get a clean table with one column for Income, one for Expense
        pivot = self.income_expense_monthly.unstack(level=0).fillna(0)
        pivot['Balance'] = pivot.get('Income',0) - pivot.get('Expense',0)
        return pivot