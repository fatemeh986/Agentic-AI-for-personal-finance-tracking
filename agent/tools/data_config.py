### For the current dataset
COLUMN_DATE = "Date"
COLUMN_AMOUNT = "INR"
COLUMN_TYPE = "Income/Expense"
COLUMN_CATEGORY = "Category"
LABEL_INCOME = "Income"
LABEL_EXPENSE = "Expense"
TWO_COLUMN_STRUCTURE = False



# ### For my own bank account data

# TWO_COLUMN_STRUCTURE = True
# COLUMN_DATE = "Date"
# COLUMN_AMOUNT = "Amount"
# COLUMN_CATEGORY = None 
# LABEL_INCOME = "Credit"
# LABEL_EXPENSE = "Debit"

# import pandas as pd
# def create_amount_column(csv_path):
#     df = pd.read_csv(csv_path)
#     df[LABEL_EXPENSE] = df[LABEL_EXPENSE].fillna(0)
#     df[LABEL_INCOME] = df[LABEL_INCOME].fillna(0)

#     # Create a unified Amount column — debit is positive expense, credit is positive income
#     df['Amount']=df[LABEL_EXPENSE].where(
#         df[LABEL_EXPENSE]>0, df[LABEL_INCOME]
#     )

#     # Create a unified Type column
#     df['Income/Expense']=df.apply(
#         lambda row:'Expense' if row[LABEL_EXPENSE]>0 else 'Income', axis=1
#     )

#     return df