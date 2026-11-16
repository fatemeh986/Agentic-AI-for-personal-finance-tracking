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
- Tools: total spending by category (with % share), monthly income vs expense summary,
  top 10 biggest expenses, balance per month
- All calculations (totals, percentages) are done in Pandas, not by the LLM

### ✅ Phase 2 — Market data + financial news (complete)
- Fetches live stock prices for MSFT, AAPL, GOOGL, TSLA, IBM
  via Alpha Vantage — including one-month trend and price range
- Stocks are ranked in Python (best → worst performer), so the LLM never has to compare numbers
- Caches stock data daily so the API is only called once per day (only complete results are cached)
- Searches latest financial news via Tavily API
- Agent combines your personal transaction data with live market
  signals to give specific investment suggestions

### ✅ Phase 3 — RAG chatbot + persistent memory (complete)
- Chainlit chat UI replaces CLI
- RAG retrieval from a personal financial context document (PDF) via Qdrant vector store
- Conversation history within a chat, so follow-up questions work ("And how much on transport?")
- Long-term memory across sessions via Mem0: the agent remembers user goals, income and preferences
- Only what the **user** says is stored in memory, never the agent's answers — this prevents
  *memory poisoning* (a wrong answer being saved and reused as a "fact")

### ✅ Phase 4 — Deployment to AWS ECS Fargate (complete)
- Containerized with Docker, image stored in Amazon ECR
- Deployed on AWS ECS Fargate (serverless containers)
- Logged and monitored via CloudWatch
- Secure IAM role for AWS access

### 🔲 Phase 5 — Real bank data + Neo4j graph
### 🔲 Phase 6 — Product launch

---

## Evaluation & Observability

All agent runs are traced automatically with **LangSmith** — every tool call, LLM call, latency, and token count is visible in the dashboard.

### Prompt optimization (measured with LangSmith)
- Latency reduced from **7.45s → 2.76s** (−63%) after prompt refinement
- Token usage reduced from **3,207 → 1,700** per run (−47%)
- The agent now calls only the tools a question needs instead of all tools on every question

### Answer quality (Ragas)
Answer quality is measured with **Ragas** (`answer_correctness`, `answer_relevancy`) on 8 test questions
covering the three data sources of the agent: transactions, the RAG document, and live market data.
Gemini 2.5 Flash Lite is used both as the agent and as the Ragas judge.

| Metric | Score |
|---|---|
| answer_correctness | **0.89** |
| answer_relevancy | **0.82** |

| Question | Data source | answer_correctness |
|---|---|---|
| How much did I spend on food? | Transactions | 1.00 |
| What is my highest spending category? | Transactions | 1.00 |
| How much did I spend on transportation? | Transactions | 1.00 |
| What is the highest expenses? *(ambiguous)* | Transactions | 0.87 |
| What is my budget for the phone? | RAG (PDF) | 0.61 |
| Which tech stock performed best over the last month? | Market data | 0.73 |
| Which tech stocks went up and which went down? | Market data | 0.91 |
| What is the latest price of Apple stock? | Market data | 0.99 |

**How the test set is built**
- Ground truths are full sentences with the exact numbers, e.g. *"You spent 24,502.48 INR on food, which is 41.5% of your total spending."*
- Stock prices change every day, so the stock ground truths are **generated from the live data** at the start of each run instead of being hard-coded.

**What the evaluation caught and how it was fixed**

| Problem | Cause | Fix |
|---|---|---|
| "Highest spending category" was wrong (*Other, 37,868*) | Income rows were summed together with expenses | Filter expense rows before grouping |
| The agent invented stock trends ("all 5 stocks are up") | A string-formatting bug made the stock tool return only the ticker names | Fixed the tool + prompt rule: *if a tool returns no data, say so — never guess* |
| Wrong best-performing stock (said Apple +3.7% when Tesla was +10.0%) | LLMs are unreliable at comparing numbers | The tool now ranks stocks in Python and states the best/worst performer (score 0.38 → 0.73) |
| Wrong percentages (said 12.07% instead of 15.6%) | LLM arithmetic | Percentages are computed in Pandas inside the tool |
| A wrong answer was repeated in later chats | Mem0 stored the agent's wrong answer as a fact about the user | Only user messages are stored in memory; the prompt says tool data always wins over memory |
| "Biggest expense" answered with a single transaction | Ambiguous question + a misleading example in the prompt | Prompt rule: answer both the top category and the largest single transaction |

**Lesson learned:** let the tools do the math, and let the LLM explain the results.

To run the evaluation:
```bash
python evaluation.py
```
It prints the overall scores and a per-question table (agent answer, ground truth, score).
LLM answers and the LLM judge vary slightly between runs, so the average of a few runs is more reliable than a single run.

---

## Project Structure

I structured the project into different directories and files to make development easier and more organized.

```text
.
├── agent/
│   ├── tools/
│   │   ├── transactions.py   # Pandas analytics on the transactions CSV
│   │   ├── market.py         # Alpha Vantage stock data + daily cache
│   │   ├── news.py           # Tavily news search
│   │   └── data_config.py    # column names of the CSV
│   ├── agent.py              # LLM, tools, RAG (Qdrant) and the agent
│   ├── prompts.py            # system prompt
│   ├── memory.py             # Mem0 long-term memory
│   └── state.py              # (planned)
├── data/
│   ├── expense_data_1.csv    # transactions dataset
│   ├── RAG-data.pdf          # personal financial context document
│   └── stock_cache.json      # daily stock cache
├── ui/
│   └── app.py                # Chainlit chat UI
├── api/
│   └── main.py               # (planned)
├── evaluation.py             # Ragas evaluation
├── Dockerfile
├── requirements.txt
└── README.md
```

Gemini 2.5 Flash Lite is used for this application, but you can use any other API or LLM model; the LangChain documentation is very useful to start with.

https://docs.langchain.com/oss/python/langchain/agents

## Technologies Used

This project currently uses:

| Tool | Purpose |
|---|---|
| Python 3.11 | Language |
| LangChain + LangGraph | Agent framework and tool orchestration |
| Gemini 2.5 Flash Lite | LLM (replaceable with any LangChain-compatible model) |
| Pandas | Transaction data analysis |
| Qdrant | Vector store for RAG |
| Mem0 | Persistent memory across sessions |
| Chainlit | Chat UI |
| Alpha Vantage | Live stock price data |
| Tavily | Financial news search |
| LangSmith | Tracing and observability |
| Ragas | Answer quality evaluation |
| Docker + AWS ECS Fargate | Containerization and deployment |

You can replace Gemini with any other model supported by LangChain.
See the LangChain documentation for available integrations:
https://docs.langchain.com/oss/python/langchain/overview

---

## Installation

**1 — Clone the repository**
```bash
git clone https://github.com/fatemeh986/Agentic-AI-for-personal-finance-tracking.git
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
All package versions are pinned in `requirements.txt`, so the local setup and the Docker image use exactly the same versions.

---


## Environment Variables

Create a `.env` file in the root directory with your API keys:

```
GOOGLE_API_KEY=your_gemini_api_key
ALPHA_VANTAGE_API_KEY=your_alpha_vantage_api_key
TAVILY_API_KEY=your_tavily_api_key
MEM0_API_KEY=your_mem0_api_key
LANGCHAIN_API_KEY=your_langsmith_api_key
LANGSMITH_PROJECT=finance-agent
LANGSMITH_TRACING=true
```

- Gemini API key: https://aistudio.google.com
- Alpha Vantage API key (free): https://www.alphavantage.co
- Tavily API key (free tier available): https://tavily.com
- Mem0: https://mem0.ai
- LangSmith (free tier): https://smith.langchain.com

**Rate limits on free tiers:** the Gemini free tier allows a limited number of requests per day
(one question uses 2–3 requests), and Alpha Vantage allows 25 requests per day.
When the Gemini limit is reached, the chat shows a friendly message instead of crashing.

---

## How to Run

```bash
chainlit run ui/app.py
```

Example questions to ask the agent:

- *"In which category do I spend the most?"*
- *"What is my balance for each month?"*
- *"Which tech stock performed best over the last month?"*
- *"Based on my expenses, which stocks should I consider investing in?"*
- *"How can I save more money to reach my goal?"*

To use your own data, replace `data/expense_data_1.csv` with your own CSV file.
Make sure it contains these columns: `Date`, `Category`, `Income/Expense`, `INR`

---

## How It Works

```
Your question
      ↓
Relevant memories from past sessions are added (Mem0)
      ↓
LangGraph agent reads the question + chat history and decides which tools are needed
      ↓
Calls only relevant tools: transactions / market / news / RAG
      ↓
Gemini reads the tool results and writes a specific, data-driven answer
      ↓
Answer appears in the Chainlit chat UI
      ↓
The user's message is saved to long-term memory, and the run is traced in LangSmith
```

## Deployment

The application is containerized with Docker and deployed on AWS ECS Fargate.

### Infrastructure

| Component | Value |
|-----------|-------|
| **Runtime** | AWS ECS Fargate |
| **Region** | eu-west-3 |
| **Cluster** | `financial-agent-cluster` |
| **Service** | `financial-agent-service` |
| **Compute** | 1 vCPU, 3GB memory |
| **Container Registry** | Amazon ECR: `financial-agent:v1` |
| **Monitoring** | CloudWatch Logs + LangSmith |

**Note:** a Fargate task gets a new public IP every time it restarts, so there is no permanent public URL yet.
A load balancer with a stable address is planned.

### Logs & Monitoring

All agent interactions are traced in **LangSmith**: https://smith.langchain.com

For AWS ECS details: [AWS ECS Documentation](https://docs.aws.amazon.com/ecs/)

---

## How to Contribute

1. Create a feature branch
2. Test locally with `chainlit run ui/app.py`
3. Run `python evaluation.py` and check the scores
4. Check logs and LangSmith traces
5. Push to GitHub
6. Open a pull request

---
