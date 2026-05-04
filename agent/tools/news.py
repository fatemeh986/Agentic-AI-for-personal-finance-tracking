from tavily import TavilyClient
from dotenv import load_dotenv
import os

load_dotenv()
tvly_api_key=os.getenv("TAVILY_API_KEY")

def search_news(query:str = "latest tech stock market news for investors"):
    tavily_client = TavilyClient(api_key=tvly_api_key)
    response = tavily_client.search(query)
    results = response.get("results",[])
    formatted=""
    for result in results:
        formatted += f"Title: {result['title']}\nSummary: {result['content']}\nURL: {result['url']}\n\n"
    return formatted