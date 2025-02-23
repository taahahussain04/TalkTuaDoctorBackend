from __future__ import annotations
from livekit.agents import (
    AutoSubscribe,
    JobContext,
    WorkerOptions,
    cli,
    llm
)
from livekit.agents.multimodal import MultimodalAgent
from livekit.plugins import openai
from dotenv import load_dotenv
import os
from prompts import INSTRUCTIONS, WELCOME_MESSAGE, LOOKUP_PATIENT_ID_MESSAGE 
from api import AssistantFunc
from ai_agent import get_research_agent_response  # Import the research agent function

load_dotenv()

async def entrypoint(ctx: JobContext):
    await ctx.connect(auto_subscribe=AutoSubscribe.SUBSCRIBE_ALL)
    await ctx.wait_for_participant()
    
    model = openai.realtime.RealtimeModel(
        instructions=f"{INSTRUCTIONS}\n\nWhen a patient describes their symptoms, use the research_symptoms function to provide medical insights.",
        voice="shimmer",
        temperature=0.8,
        modalities=["audio", "text"]
    )
    assistant_fnc = AssistantFunc()  # Use the original AssistantFunc class
    assistant = MultimodalAgent(model=model, fnc_ctx=assistant_fnc)
    assistant.start(ctx.room)
    
    session = model.sessions[0]
    session.conversation.item.create(
        llm.ChatMessage(
            role="assistant",
            content=WELCOME_MESSAGE
        )
    )
    session.response.create()


if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint))