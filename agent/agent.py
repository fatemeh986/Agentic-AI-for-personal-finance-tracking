import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain.agents import create_agent
from agent.prompts import prompt
from tools.transactions import PersonalFinance
from langchain_core.tools import tool
from tools.news import search_news
from tools.market import tech_stock_price
from qdrant_client.models import Distance, VectorParams
from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter


load_dotenv()
llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash-lite")

############################
######## For RAG
############################
# gemini_api = os.getenv("GOOGLE_API_KEY")
# chat = init_chat_model("google_genai:gemini-2.5-flash-lite")
embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")

qdrant_client = QdrantClient(":memory:")

vector_size = len(embeddings.embed_query("sample text"))

if not qdrant_client.collection_exists("test"):
    qdrant_client.create_collection(
        collection_name="test",
        vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE)
    )
vector_store= QdrantVectorStore(
    client=qdrant_client,
    collection_name="test",
    embedding=embeddings
)
### load pdf 
file_path = "data/RAG-data.pdf"
loader = PyPDFLoader(file_path)

docs = loader.load()

## chunking
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=100
)
all_splits = text_splitter.split_documents(docs)
## storing documents
document_ids = vector_store.add_documents(documents=all_splits)

print("Pre-fetching stock prices at startup...")
tech_stock_price()
print("Stock prices ready.")   

financial_summary = PersonalFinance("data/expense_data_1.csv")

@tool
def get_total_spent_by_category() -> str:
    """Return total spending grouped by category."""
    result = financial_summary.total_spent_category()
    return result.to_string()

@tool
def get_monthly_summary() -> str:
    """Return income vs expenses summary for each month in the dataset."""
    monthly_summary = financial_summary.monthly_summary()
    return monthly_summary.to_string()

@tool
def get_ten_biggest_spenses() -> str:
    """Return 10 biggest spenses transactions"""
    result=financial_summary.ten_biggest_expenses()
    return result.to_string()

@tool
def get_balance_estimate() -> str:
    """Return estimated balance for December and January."""
    result = financial_summary.balance_estimate()
    return result.to_string()

@tool
def get_market_news() -> str:
    """Return the latest mwrket news specially tech companies"""
    return search_news()

@tool
def market_stock_prices() -> str:
    """Return daily stock prices of tech companies"""
    return tech_stock_price()

# RAG
@tool(response_format="content_and_artifact")
def retrieve_context(query: str):
    """Search the user's personal financial context document for relevant information."""
    retrieved_docs = vector_store.similarity_search(query, k=2)
    serialized = "\n\n".join(
        f"Source: {doc.metadata}\nContent: {doc.page_content}"
        for doc in retrieved_docs
    )
    return serialized, retrieved_docs



tools=[
    get_total_spent_by_category,
    get_monthly_summary,
    get_ten_biggest_spenses,
    get_balance_estimate,
    get_market_news,
    market_stock_prices,
    retrieve_context
]

agent = create_agent(
    model = llm,
    tools=tools,
    system_prompt=prompt
)

# def save_interaction(user_id:str, user_input:str, assistant_response:str):
#     """Save the interaction to Mem0"""
#     try:
#         interaction = [
#             {"role":"user", "content":user_input},
#             {"role":"assistant", "content":assistant_response}
#         ]
#         result = memory.add(interaction, user_id=user_id)
#         print(f"Memory saved successfully: {len(result.get('results', []))} memories added")
#     except Exception as e:
#         print(f"Error saving interaction: {e}")

# query = input("Ask your financial question: ")

# raw_response = agent.invoke({"messages": [{"role": "user", "content": query}]})

# print(raw_response["messages"][-1].content)
# last_message = raw_response["messages"][-1].content
# if isinstance(last_message, list):
#     print(last_message[0]["text"])
# else:
#     print(last_message)