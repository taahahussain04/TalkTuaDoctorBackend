from phi.agent import Agent
from phi.vectordb.pineconedb import PineconeDB
from phi.model.openai import OpenAIChat
from phi.tools.googlesearch import GoogleSearch
from phi.tools.duckduckgo import DuckDuckGo
import os
from phi.knowledge.website import WebsiteKnowledgeBase

def get_research_agent_response(symptoms_query, use_knowledge_base=True):
    # First create/update knowledge base with relevant URLs for the symptoms
    knowledge_base = create_and_update_knowledge_base(symptoms_query)
    knowledge_base.update()
    
    researchAgent = Agent(
        model=OpenAIChat(model="gpt-4o"),
        temperature=0.8,
        reasoning=True,
        description='''
        You are a cutting-edge research aggregator and updater, serving as the central hub that collects the 
        latest updates from trusted health organizations, research institutions, and regulatory bodies.
        You ensure the AI doctor's knowledge base remains current with real-time, evidence-based information.''',
        instructions=['''Analyze the provided symptoms using the knowledge base and external search.
        Provide evidence-based insights and potential solutions in a digestible format.
        '''],
        tools=[DuckDuckGo()],
        show_tool_calls=True,
        knowledge_base=knowledge_base if use_knowledge_base else None
    )
    
    response = researchAgent.run_tools(symptoms_query)
    return response

def get_google_search_agent(query):
    googleSearchAgent = Agent(
        model=OpenAIChat(model="gpt-4o"),
        temperature=0.8,
        reasoning=True,
        tools=[GoogleSearch()],
        description="You are a search agent that returns only URLs.",
        instructions=[
            "Search for the given query and return only a list of URLs.",
            "Return exactly 10 relevant URLs total.",
            "Do not include any other text or explanations."
        ],
        show_tool_calls=False,
        debug_mode=False,
    )
    
    response = googleSearchAgent.run_tools(query)
    return [url for url in response if url.startswith('http')]


