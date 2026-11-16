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
    try:
        results = client.search(user_message, filters={"user_id":user_id})
    except Exception as e:
        # If Mem0 is down, answer without memory instead of crashing the whole chat
        print(f"Error searching memories: {e}")
        return ""
    memories = results.get("results",[])
    if not memories:
        return ""
    context = "Relevant context from past conversations:\n"
    context += "\n".join([f"- {m['memory']}" for m in memories])
    return context

def save_user_message(user_id:str, user_message:str):
    """
    Called AFTER the agent answers.
    Saves ONLY what the user said (goals, preferences, plans) to Mem0.
    We do NOT save the agent's answer: if the agent makes a mistake, Mem0 would store
    that mistake as a "fact" about the user and reuse it in every future question
    (this is called memory poisoning). Numbers always come fresh from the tools anyway.
    """
    try:
        messages = [
            {"role":"user", "content":user_message},
        ]
        client.add(messages, user_id=user_id)
        print(f"Memory saved successfully for user {user_id}")
    except Exception as e:
        print(f"Error saving interaction: {e}")