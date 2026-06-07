import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from dotenv import load_dotenv
load_dotenv()

from agent.agent import agent
from ragas.metrics.collections import answer_correctness, answer_relevancy
from ragas.llms import LangchainLLMWrapper
from ragas.embeddings import LangchainEmbeddingsWrapper
from ragas import evaluate, EvaluationDataset, SingleTurnSample
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings

# Gemini config for Ragas
ragas_llm = LangchainLLMWrapper(ChatGoogleGenerativeAI(model="gemini-2.5-flash-lite"))
ragas_embeddings = LangchainEmbeddingsWrapper(GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001"))

answer_correctness.llm = ragas_llm
answer_correctness.embeddings = ragas_embeddings
answer_relevancy.llm = ragas_llm
answer_relevancy.embeddings = ragas_embeddings

def ask_agent(question: str) -> str:
    raw_response = agent.invoke({
        "messages": [{"role": "user", "content": question}]
    })
    last_message = raw_response["messages"][-1].content
    if isinstance(last_message, list):
        return last_message[0]["text"]
    return last_message

test_cases = [
    {"question": "How much did I spend on food?", "ground_truth": "24502.48"},
    {"question": "What is my highest spending category?", "ground_truth": "Other at 37868"},
    {"question": "How much did I spend on transportation?", "ground_truth": "9203.80"},
    {"question": "What is my second highest expense category?", "ground_truth": "Food at 24502.48"},
    {"question": "How much did I spend on Apparel?", "ground_truth": "3388"},
]

print("Running agent on test cases...")
answers = []
for tc in test_cases:
    print(f"  Q: {tc['question']}")
    answer = ask_agent(tc["question"])
    answers.append(answer)
    print(f"  A: {answer[:80]}...")

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