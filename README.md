# Agentic AI for Personal Finance Tracking

This project is an agentic AI application for personal finance tracking. I am developing it step by step, and in each version I explain what has been implemented and how to run it.

The main goal of this project is to build a personal finance AI agent that can analyze transactions, income, and expenses. The agent should help detect unusual spending patterns, identify unnecessary expenses, summarize monthly spending, and eventually use market and financial news to provide useful financial insights.

The dataset in this repository is downloaded from Kaggle. On my local system, I use my own transaction data, but you can also replace the dataset with your own data.

---

## Current Version

So far, I have developed a basic version of the agentic AI application that can be run from the CLI.

This first version focuses on:

- Reading transaction data from a CSV file
- Answering simple finance-related questions
- Using an LLM to generate natural language responses
- Structuring the project in a way that can be extended later

For the first basic version, the main logic is implemented in three files:

- `transactions.py`
- `agent.py`
- `prompt.py`

---

## Project Structure

I structured the project into different directories and files to make development easier and more organized.

```text
.
├── agent
│   ├── tools
│   │   ├── transactions.py
│   │   ├── market.py
│   │   └── news.py
│   ├── agent.py
│   ├── prompt.py
│   ├── memory.py
│   └── state.py
├── data
│   └── expense_data_1.csv
├── ui
│   └── app.py
├── api
│   └── main.py
├── requirements.txt
└── README.md
```

But for the basic version, I just wrote simple codes in 3 main files, transactions.py, agent.py and prompt.py.
The Gemini 2.5 flash is used for this application but you can use any other API or LLM model and the LangChain documentation is very useful to start with.
https://docs.langchain.com/oss/python/langchain/overview

https://docs.langchain.com/oss/python/langchain/agents

## Technologies Used

This project currently uses:

* Python
* LangChain
* Gemini 2.5 Flash
* Pandas
* CSV transaction data

Gemini 2.5 Flash is currently used as the main LLM, but you can replace it with another model or API provider.

LangChain is used to build the agent workflow. The LangChain documentation is a useful starting point:

https://docs.langchain.com/oss/python/langchain/overview

## Installation

1- First, clone the repository:

```bash
git clone https://github.com/your-username/Agentic-AI-for-personal-finance-tracking.git
```

2- Go into the project folder:

```bash
cd Agentic-AI-for-personal-finance-tracking
```

3- Create and activate a virtual environment:

```bash
python -m venv venv
```
On Windows:
```bash
venv\Scripts\activate
```
On Linux/macOS:
```bash
source venv/bin/activate
```

4- Install backages:
```bash
pip install -r requirements.txt
```

## Environment Variables

Create a .env file in the root directory and add your API key. for example:
```bash
GOOGLE_API_KEY=your_api_key_here
```

## How to Run:

You can run the basic CLI version with:
```bash
python agentic.py
```

After running the script, you can ask questions about your transaction data. Check the tools in agent.py file to see which tools the agent uses so far to answer your questions.