import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from dotenv import load_dotenv
load_dotenv()
import time
import json
import re
from agent.agent import agent
from ragas.metrics import AnswerCorrectness, AnswerRelevancy
from ragas.llms import LangchainLLMWrapper
from ragas.embeddings import LangchainEmbeddingsWrapper
from ragas import evaluate, EvaluationDataset, SingleTurnSample
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings

# Gemini config for Ragas
ragas_llm = LangchainLLMWrapper(ChatGoogleGenerativeAI(model="gemini-2.5-flash-lite"))
ragas_embeddings = LangchainEmbeddingsWrapper(GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001"))

answer_correctness = AnswerCorrectness(llm=ragas_llm, embeddings=ragas_embeddings)
answer_relevancy = AnswerRelevancy(llm=ragas_llm, embeddings=ragas_embeddings)

def ask_agent(question: str) -> str:
    raw_response = agent.invoke({
        "messages": [{"role": "user", "content": question}]
    })
    last_message = raw_response["messages"][-1].content
    if isinstance(last_message, list):
        return last_message[0]["text"]
    return last_message

############################
# Stock ground truths are built from TODAY's cached data
# (importing agent.agent above already refreshed data/stock_cache.json),
# so they stay correct when prices change tomorrow.
############################
STOCK_NAMES = {"MSFT": "Microsoft", "AAPL": "Apple", "GOOGL": "Google", "TSLA": "Tesla", "IBM": "IBM"}

def load_stocks() -> dict:
    """Parse the stock cache into {"TSLA": {"close": "390.22", "change": "+35.50", "pct": 10.0, "high": ..., "low": ...}, ...}"""
    with open("data/stock_cache.json", encoding="utf-8") as f:
        text = json.load(f)["data"]
    stocks = {}
    for block in text.strip().split("\n\n"):
        if block.startswith("Best performer"):
            continue  # summary header written by market.py, not a stock
        ticker = block.splitlines()[0].strip()
        change = re.search(r"One-Month Change: ([+-][\d.]+) \(([+-][\d.]+)%\)", block)
        if change is None:
            raise ValueError(f"No stock data for {ticker} in the cache (fetch error?):\n{block}")
        stocks[ticker] = {
            "close": re.search(r"Latest Close: ([\d.]+)", block).group(1),
            "change": change.group(1),
            "pct": float(change.group(2)),
            "high": re.search(r"One-Month High: ([\d.]+)", block).group(1),
            "low": re.search(r"One-Month Low: ([\d.]+)", block).group(1),
        }
    return stocks

def describe(ticker: str) -> str:
    """e.g. 'Tesla (TSLA) (+10.0%)'"""
    return f"{STOCK_NAMES.get(ticker, ticker)} ({ticker}) ({stocks[ticker]['pct']:+.1f}%)"

stocks = load_stocks()
best = max(stocks, key=lambda t: stocks[t]["pct"])
went_up = [t for t in stocks if stocks[t]["pct"] > 0]
went_down = [t for t in stocks if stocks[t]["pct"] <= 0]
aapl = stocks["AAPL"]

test_cases = [
    # transactions (fixed dataset, so these numbers never change)
    {"question": "How much did I spend on food?",
     "ground_truth": "You spent 24,502.48 INR on food, which is 41.5% of your total spending."},
    {"question": "What is my highest spending category?",
     "ground_truth": "Your highest spending category is Food at 24,502.48 INR, which is 41.5% of your total spending."},
    {"question": "How much did I spend on transportation?",
     "ground_truth": "You spent 9,203.80 INR on transportation, which is 15.6% of your total spending."},
    # ambiguous question 
    {"question": "what is the highest expenses?",
     "ground_truth": "Food is your highest expense category, with a total spending of 24,502.48 INR, which accounts for 41.5% of your total spending. "
                     "The single largest expense transaction was 4,800 INR for Household on December 5, 2021."},

    # RAG (personal context PDF)
    {"question": "What is my budget for the phone?",
     "ground_truth": "Your budget for the mobile phone is between €900 and €1,000. You plan to buy it in the next two to three weeks, "
                     "and you can pay in four installments."},

    # market data (built from today's cache
    {"question": "Which tech stock performed best over the last month?",
     "ground_truth": f"{STOCK_NAMES[best]} ({best}) performed best, with a change of {stocks[best]['pct']:+.1f}% "
                     f"({stocks[best]['change']}) over the last month, closing at {stocks[best]['close']}."},
    {"question": "Which tech stocks went up and which went down this month?",
     "ground_truth": f"Went up: {', '.join(describe(t) for t in went_up) or 'none'}. "
                     f"Went down: {', '.join(describe(t) for t in went_down) or 'none'}."},
    {"question": "What is the latest price of Apple stock and how did it move this month?",
     "ground_truth": f"Apple (AAPL) closed at {aapl['close']}, a change of {aapl['pct']:+.1f}% ({aapl['change']}) over the last month, "
                     f"with a high of {aapl['high']} and a low of {aapl['low']}."},
]

print("Ground truths for today's stock questions:")
for tc in test_cases[-3:]:
    print("  -", tc["ground_truth"])

print("Running agent on test cases...")
answers = []
for tc in test_cases:
    print(f"  Q: {tc['question']}")
    answer = ask_agent(tc["question"])
    answers.append(answer)
    print(f"  A: {answer[:80]}...")
    time.sleep(10)  # To avoid hitting rate limits

samples = [
    SingleTurnSample(
        user_input=tc["question"],
        response=answers[i],
        reference=tc["ground_truth"]
    )
    for i, tc in enumerate(test_cases)
]

dataset = EvaluationDataset(samples=samples)

print("\nEvaluating with Ragas...")
result = evaluate(
    dataset,
    metrics=[answer_correctness, answer_relevancy]
)

print("\n=== RESULTS ===")
print(result)

df = result.to_pandas()
print(df[["user_input", "answer_correctness", "answer_relevancy"]])
print(df[["user_input", "response", "reference", "answer_correctness"]].to_string())
