import pandas as pd

class PersonalFinance():
    def __init__(self, csv_path):
        self.df = pd.read_csv(csv_path)

    def total_spent_category(self):
        total_spent_by_category = self.df.groupby(['Category'])['INR'].sum()
        return total_spent_by_category
    
    def monthly_summary(self):
        self.df['Date'] = pd.to_datetime(self.df['Date'])
        filtered_df_dec = self.df.loc[
            (self.df['Date'] >= '2021-12-01') & (self.df['Date'] < '2021-12-31')
        ]
        filtered_df_jan = self.df.loc[
            (self.df['Date'] >= '2022-01-01') & (self.df['Date'] < '2022-01-31')
        ]
        self.income_expense_dec = filtered_df_dec.groupby(['Income/Expense'])['INR'].sum()
        self.income_expense_jan = filtered_df_jan.groupby(['Income/Expense'])['INR'].sum()
        return self.income_expense_dec, self.income_expense_jan
    
    def ten_biggest_expenses(self):
        biggest_expenses = self.df[self.df['Income/Expense']=='Expense'].sort_values('INR', ascending=False).head(10)
        return biggest_expenses
    
    def balance_estimate(self):
        self.monthly_summary()
        in_vs_ex_dec = self.income_expense_dec['Income'] - self.income_expense_dec['Expense']
        in_vs_ex_jan = self.income_expense_jan['Income'] - self.income_expense_jan['Expense']
        return in_vs_ex_dec, in_vs_ex_jan
    
# x = Analysis("data/expense_data_1.csv")
# print(x.total_spent_category())