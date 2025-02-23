import os
import typer
from typing import Optional
from rich.prompt import Prompt

from phi.agent import Agent
from phi.knowledge.pdf import PDFKnowledgeBase, PDFReader
from phi.vectordb.pineconedb import PineconeDB
from phi.model.openai import OpenAIChat
import dotenv

dotenv.load_dotenv()

api_key = os.getenv("PINECONE_API_KEY")
index_name = "msf-diagnosis-and-treatment-guidelines"

vector_db = PineconeDB(
    name=index_name,
    dimension=1536,
    metric="cosine",
    spec={"serverless": {"cloud": "aws", "region": "us-east-1"}},
    api_key=api_key,
    use_hybrid_search=True,
    hybrid_alpha=0.5,
)

knowledge_base = PDFKnowledgeBase(
    path="/Users/yusufshaikh/Downloads/guideline-170-en.pdf",
    vector_db=vector_db,
    reader=PDFReader(chunk=True),
)

# Comment out after first run
# knowledge_base.load(recreate=True, upsert=True)


def get_rag_agent(query):
    ragAgent = Agent(
        model=OpenAIChat(model="gpt-4"),
        temperature=0.7,
        reasoning=True,
        description='''
        You are an expert medical knowledge assistant specializing in symptom analysis and medical information retrieval.
        You have access to the MSF Clinical Guidelines - Diagnosis and Treatment Manual through the RAG knowledge base.
        Your role is to provide accurate, evidence-based information about symptoms while maintaining medical accuracy.
        ''',
        instructions=[
            "Provide concise, focused responses using only the most relevant section from the MSF Clinical Guidelines.",
            "Reference only one specific section of the guidelines that best matches the query.",
            "Include a direct quote or careful paraphrase from that section at the end of your response, clearly attributing it to 'MSF Clinical Guidelines'.",
            "Keep responses brief and to the point, avoiding unnecessary elaboration.",
            "If a topic isn't covered in the MSF Guidelines, state this briefly.",
            "Structure your response in 2-3 sentences MAXIMUM, leading with 'According to the MSF Clinical Guidelines...'",
            "Focus only on the most relevant information, avoiding tangential details."
        ],
        tools=[],
        show_tool_calls=True,
        debug_mode=True,
        knowledge_base=knowledge_base
    )
    
    response = ragAgent.run(query)
    # Ensure we return a string
    if hasattr(response, 'content'):
        return str(response.content)
    elif isinstance(response, (list, tuple)):
        return str(response[0]) if response else ""
    else:
        return str(response)


