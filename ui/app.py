import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import chainlit as cl
from agent.agent import agent
from agent.memory import get_relevant_memories, save_interaction


@cl.on_chat_start
async def on_chat_start():
    cl.user_session.set("agent", agent)

@cl.on_message
async def on_message(message: cl.Message):
    agent = cl.user_session.get("agent")
    user_id = cl.context.session.id

    # 1-get relevant past memories BEFORE calling agent
    past_context = get_relevant_memories(message.content, user_id)

    # 2-build the full message with memory context attached
    full_message = message.content
    if past_context:
        full_message = f"{past_context}\n\nUser question: {message.content}"

    # 3-call agent and stream response
    response = cl.Message(content="")
    final_answer = ""
    async for chunk in agent.astream(
        {"messages": [{"role": "user", "content": full_message}]},
        stream_mode="values"
    ):
        last = chunk["messages"][-1]
        if(
            hasattr(last, "content")
            and last.content
            and not getattr(last, "tool_calls", [])
        ):
            response.content = last.content
            final_answer=last.content
    await response.send()

    # 4—save the exchange AFTER agent responds
    save_interaction(user_id, message.content, final_answer)