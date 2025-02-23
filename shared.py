from phi.vectordb.pineconedb import PineconeDB
from phi.knowledge.website import WebsiteKnowledgeBase
from ai_agent import get_google_search_agent
import os

api_key = os.getenv("PINECONE_API_KEY")
index_name = "thai-recipe-hybrid-search"

pincone_db = PineconeDB(
    name=index_name,
    dimension=1536,
    metric="cosine",
    spec={"serverless": {"cloud": "aws", "region": "us-east-1"}},
    api_key=api_key,
    use_hybrid_search=True,
    hybrid_alpha=0.5,
)
def create_and_update_knowledge_base(query: str) -> WebsiteKnowledgeBase:
    knowledge_base = WebsiteKnowledgeBase(
        urls=get_google_search_agent(query),
        max_links=10,
        vector_db=pincone_db
    )
    knowledge_base.update()
    return knowledge_base