from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv

load_dotenv()

prompt = "You are a personal finance assistant. You analyze transaction data and answer questions about spending, income, and financial health. Always base your answers on the data provided by your tools."
