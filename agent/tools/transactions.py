import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
import pandas as pd
from data_config import (
    COLUMN_DATE,
    COLUMN_AMOUNT,
    COLUMN_TYPE,
    COLUMN_CATEGORY,
    LABEL_INCOME,
    LABEL_EXPENSE,
    TWO_COLUMN_STRUCTURE
)

class PersonalFinance():
    def __init__(self, csv_path):
        if TWO_COLUMN_STRUCTURE:
            from data_config import create_amount_column
            self.df = create_amount_column(csv_path)
        else:
            self.df = pd.read_csv(csv_path)

    def total_spent_category(self):
        # Uses COLUMN_CATEGORY and LABEL_EXPENSE from config
        total_spent_by_category = self.df.groupby(COLUMN_CATEGORY)[COLUMN_AMOUNT].sum()
        return total_spent_by_category
    
    def monthly_summary(self):
        df_copy = self.df.copy()
        df_copy[COLUMN_DATE] = pd.to_datetime(df_copy[COLUMN_DATE]).dt.to_period("M")
        self.income_expense_monthly = df_copy.groupby([COLUMN_TYPE,COLUMN_DATE])[COLUMN_AMOUNT].sum()
        return self.income_expense_monthly
    
    # def ten_biggest_expenses(self):
    #     biggest_expenses = self.df[self.df[COLUMN_TYPE]==LABEL_EXPENSE].sort_values(COLUMN_AMOUNT, ascending=False).head(10)
    #     return biggest_expenses
    def ten_biggest_expenses(self):
        expenses = self.df[self.df[COLUMN_TYPE] == LABEL_EXPENSE]
        result = expenses.sort_values(COLUMN_AMOUNT, ascending=False).head(10)
        cols = [c for c in [COLUMN_DATE, COLUMN_CATEGORY, COLUMN_AMOUNT] if c in result.columns]
        return result[cols].reset_index(drop=True)
    
    def balance_estimate(self):
        self.monthly_summary()
        # unstack() turns the Income/Expense index level into columns (it may in a month the data doesn't have income or expense)
        # so we get a clean table with one column for Income, one for Expense
        pivot = self.income_expense_monthly.unstack(level=0).fillna(0)
        pivot['Balance'] = pivot.get(LABEL_INCOME,0) - pivot.get(LABEL_EXPENSE,0)
        return pivot