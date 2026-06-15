import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from dotenv import load_dotenv
load_dotenv()
import time
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

test_cases = [
    {"question": "How much did I spend on food?", "ground_truth": "24502.48"},
    {"question": "What is my highest spending category?", "ground_truth": "Other at 37868"},
    {"question": "How much did I spend on transportation?", "ground_truth": "9203.80"},
]

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