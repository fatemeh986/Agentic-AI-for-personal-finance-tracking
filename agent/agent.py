from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import create_agent
from prompts import prompt
from tools.transactions import PersonalFinance
from langchain_core.tools import tool

load_dotenv()
llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash")

financial_summary = PersonalFinance("data/expense_data_1.csv")

@tool
def get_total_spent_by_category() -> str:
    """Return total spending grouped by category."""
    result = financial_summary.total_spent_category()
    return result.to_string()

@tool
def get_monthly_summary() -> str:
    """Return incomes vs spenses summary for December and January."""
    dec, jan = financial_summary.monthly_summary()
    return f"December:\n{dec.to_string()}\n\nJanuary:\n{jan.to_string()}"

@tool
def get_ten_biggest_spenses() -> str:
    """Return 10 biggest spenses transactions"""
    result=financial_summary.ten_biggest_expenses()
    return result.to_string()

@tool
def get_balance_estimate() -> str:
    """Return estimated balance for December and January."""
    dec, jan = financial_summary.balance_estimate()
    return f"December balance: {dec}\nJanuary balance: {jan}"

tools=[
    get_total_spent_by_category,
    get_monthly_summary,
    get_ten_biggest_spenses,
    get_balance_estimate
]

agent = create_agent(
    model = llm,
    tools=tools,
    system_prompt=prompt
)

query = input("Ask your financial question: ")

raw_response = agent.invoke({"messages": [{"role": "user", "content": query}]})

# print(raw_response["messages"][-1].content)
last_message = raw_response["messages"][-1].content
if isinstance(last_message, list):
    print(last_message[0]["text"])
else:
    print(last_message)