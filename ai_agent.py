from phi.agent import Agent

from phi.model.openai import OpenAIChat

from phi.tools.googlesearch import GoogleSearch
from phi.tools.duckduckgo import DuckDuckGo


researchAgent = Agent(
             model=OpenAIChat(model="gpt-4o"),
             temperature=0.8,
             reasoning=True,
              description='''
              You are a cutting-edge research aggregator and updater, serving as the central hub that collects the 
              latest updates from trusted health organizations, research institutions, and regulatory bodies.
              You ensure the AI doctor's knowledge base remains current with real-time, evidence-based information.''',
             instructions=['''Schedule regular checks for new studies, guideline revisions, and emerging health concerns. 
              Continuously update findings by researching common symptoms,
              identifying issues, and summarizing potential solutions in a digestible format.
              '''],
              tools=[DuckDuckGo()], 
              show_tool_calls=True)

def get_google_search_agent():

    googleSearchAgent  = Agent(
        model=OpenAIChat(model="gpt-4o"),
        temperature=0.8,
        reasoning=True,
        tools=[GoogleSearch()],
        description="You are a research and resource aggregator agent that finds evidence-based research papers and actionable websites on users' symptoms and their remedies.",
        instructions=[
            "Given a set of symptoms provided by the user, search for research papers that analyze these symptoms and offer treatment insights.",
            "Return the top 5 relevant research papers and 5 most relevant websites with practical guidance on how to manage or fix the symptoms.",
            "For research papers, search for at least 10 items and select the top 5 based on evidence and relevance; do the same for websites offering actionable advice."
        ],
        show_tool_calls=True,
        debug_mode=True,
    )

googleSearchAgent.print_response("persistent headache and fatigue", markdown=True)
