# Agentic-AI-for-personal-finance-tracking

In this project I am developing an entire agentic AI application step by step. In every step I explain what I have done and how to run it.
By developing the application to the new version, I'll update README.
This is a personal finance AI Agent that based on my transactions and bank incomes and expenses, I try to find the anomalies in them, how much I spend and which one is unnecessary or I spent too much for that monthly. At the end, based on market and financial news, I want to try that whether my agent gives me good advice.
The data here is downloaded from kaggle but on my system I use my transactions data, you can use yours as well.

So far, I developed a besic agentic AI that it can be run it in CDI by running `python agentic.py` command in terminal.

## Project structure:
As you see I tried to structure the application to different directories and files to make it easier during development.

```
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
│       ├── images
│       └── labels
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
