from mem0 import MemoryClient
from dotenv import load_dotenv
import os


load_dotenv()
api_key=os.getenv("MEM0_API_KEY")
client = MemoryClient(api_key=api_key)

def get_relevant_memories(user_message:str, user_id:str)->str:
    """
    Called BEFORE the agent runs.
    Searches past conversations for anything relevant to what the user just asked.
    Returns a plain string to add as context to the agent.
    """
    results = client.search(user_message, filters={"user_id":user_id})
    memories = results.get("results",[])
    if not memories:
        return ""
    context = "Relevant context from past conversations:\n"
    context += "\n".join([f"- {m['memory']}" for m in memories])
    return context

def save_interaction(user_id:str, user_message:str, agent_response:str):
    """
    Called AFTER the agent answers.
    Save the interaction to Mem0"""
    try:
        messages = [
            {"role":"user", "content":user_message},
            {"role":"assistant", "content":agent_response}
        ]
        client.add(messages, user_id=user_id)
        print(f"Memory saved successfully for user {user_id}")
    except Exception as e:
        print(f"Error saving interaction: {e}")