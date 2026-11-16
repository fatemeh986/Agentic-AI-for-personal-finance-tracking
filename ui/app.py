import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import chainlit as cl
from agent.agent import agent
from agent.memory import get_relevant_memories, save_user_message

# Mem0 stores memories per user_id. It must stay the SAME across sessions,
# otherwise memories saved yesterday are never found today.
# There is no login yet, so everyone shares one id. When you add Chainlit
# authentication, replace this with cl.user_session.get("user").identifier
USER_ID = "default_user"


def to_text(content) -> str:
    """Gemini sometimes returns a list of parts instead of a plain string. Always return a string."""
    if isinstance(content, list):
        return "".join(
            part.get("text", "") if isinstance(part, dict) else str(part)
            for part in content
        )
    return content or ""


@cl.on_chat_start
async def on_chat_start():
    # Conversation history for THIS chat, so follow-up questions have context
    cl.user_session.set("history", [])


@cl.on_message
async def on_message(message: cl.Message):
    history = cl.user_session.get("history")

    # 1-get relevant past memories BEFORE calling agent
    past_context = get_relevant_memories(message.content, USER_ID)

    # 2-build the full message with memory context attached
    full_message = message.content
    if past_context:
        full_message = f"{past_context}\n\nUser question: {message.content}"

    # 3-call agent with the previous turns + the new question
    final_answer = ""
    try:
        async for chunk in agent.astream(
            {"messages": history + [{"role": "user", "content": full_message}]},
            stream_mode="values"
        ):
            last = chunk["messages"][-1]
            # keep only the AI's final text answer (not the user message, tool results or tool-call requests)
            if last.type == "ai" and last.content and not last.tool_calls:
                final_answer = to_text(last.content)
    except Exception as e:
        # e.g. Gemini free tier daily limit (429 RESOURCE_EXHAUSTED) or a network error
        print(f"Error calling the agent: {e}")
        if "RESOURCE_EXHAUSTED" in str(e) or "429" in str(e):
            msg = "The AI model has reached its usage limit for now. Please try again later."
        else:
            msg = "Sorry, something went wrong while answering. Please try again."
        await cl.Message(content=msg).send()
        return  # don't add a failed turn to history or memory

    if not final_answer:
        final_answer = "Sorry, I could not produce an answer. Please try again."
    await cl.Message(content=final_answer).send()

    # 4-remember this turn for the next question in the same chat
    # (store the plain question, not the memory context, to keep the history short)
    history.append({"role": "user", "content": message.content})
    history.append({"role": "assistant", "content": final_answer})
    cl.user_session.set("history", history)

    # 5—save ONLY the user's message to long-term memory (see save_user_message for why)
    save_user_message(USER_ID, message.content)
