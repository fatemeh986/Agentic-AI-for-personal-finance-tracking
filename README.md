# Agentic AI for Personal Finance Tracking

This project is an agentic AI application for personal finance tracking.
I am building it step by step, and each version documents what has been
implemented and how to run it.

The main goal is to build a personal finance AI agent that can analyze
transactions, income, and expenses — detect unusual spending patterns,
summarize monthly activity, cross-reference live market data and financial
news, and provide actionable investment advice.

The dataset in this repository is downloaded from Kaggle:
**Personal Budget Transactions Dataset** by Ismet Semedov.
On my local system I use my own transaction data, but you can replace
the CSV with your own as long as it contains `Date`, `Category`,
`Income/Expense`, and `INR` columns.

---

## Current Version

### ✅ Phase 1 — Core agent + transaction analysis (complete)
- Reads personal transaction data from a CSV file
- Answers natural language questions about spending and income
- Tools: total spending by category, monthly income vs expense summary,
  top 10 biggest expenses, balance estimate per month
- Runs entirely from the CLI

### ✅ Phase 2 — Market data + financial news (complete)
- Fetches live stock prices for MSFT, AAPL, GOOGL, TSLA, IBM
  via Alpha Vantage — including one-month trend and price range
- Caches stock data daily so the API is only called once per day
- Searches latest financial news via Tavily API
- Agent combines your personal transaction data with live market
  signals to give specific investment suggestions

### 🔲 Phase 3 — RAG chatbot + memory (in progress)
### 🔲 Phase 4 — Real bank data + Neo4j graph
### 🔲 Phase 5 — Backend + deployment
### 🔲 Phase 6 — Product launch

---

## Project Structure

I structured the project into different directories and files to make development easier and more organized.

```text
.
├── agent/
│   ├── tools/
│   │   ├── transactions.py
│   │   ├── market.py
│   │   └── news.py
│   ├── agent.py
│   ├── prompts.py
│   ├── memory.py
│   └── state.py
├── data/
│   └── expense_data_1.csv
├── ui/
│   └── app.py
├── api/
│   └── main.py
├── requirements.txt
└── README.md
```

The Gemini 2.5 flash is used for this application but you can use any other API or LLM model and the LangChain documentation is very useful to start with.

https://docs.langchain.com/oss/python/langchain/agents

## Technologies Used

This project currently uses:

| Tool | Purpose |
|---|---|
| Python 3.11 | Language |
| LangChain + LangGraph | Agent framework and tool orchestration |
| Gemini 2.5 Flash Lite | LLM (replaceable with any LangChain-compatible model) |
| Pandas | Transaction data analysis |
| Alpha Vantage | Live stock price data |
| Tavily | Financial news search |
| python-dotenv | Environment variable management |

You can replace Gemini with any other model supported by LangChain.
See the LangChain documentation for available integrations:
https://docs.langchain.com/oss/python/langchain/overview

---

## Installation

**1 — Clone the repository**
```bash
git clone https://github.com/your-username/Agentic-AI-for-personal-finance-tracking.git
cd Agentic-AI-for-personal-finance-tracking
```

**2 — Create and activate a virtual environment**
```bash
python -m venv venv
```
Windows:
```bash
venv\Scripts\activate
```
Linux / macOS:
```bash
source venv/bin/activate
```

**3 — Install dependencies**
```bash
pip install -r requirements.txt
```
---


## Environment Variables

Create a `.env` file in the root directory with your API keys:

```
GOOGLE_API_KEY=your_gemini_api_key
ALPHA_VANTAGE_API_KEY=your_alpha_vantage_api_key
TAVILY_API_KEY=your_tavily_api_key
```

- Gemini API key: https://aistudio.google.com
- Alpha Vantage API key (free): https://www.alphavantage.co
- Tavily API key (free tier available): https://tavily.com

---

## How to Run

```bash
python agent/agent.py
```

After running, type your question in the terminal. Examples:

- *"In which category do I spend the most?"*
- *"What is my balance for each month?"*
- *"Based on my expenses, which stocks should I consider investing in?"*
- *"How can I save money and where should I invest it?"*

The agent will automatically decide which tools to call based on your question.

---

## How It Works

```
Your question
      ↓
LangGraph agent thinks: which tools do I need?
      ↓
Calls tools: transactions + market prices + news
      ↓
Gemini reads all results and writes a specific answer
      ↓
Printed in your terminal
```