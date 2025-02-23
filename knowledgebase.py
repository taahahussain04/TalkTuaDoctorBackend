from phi.knowledge.website import WebsiteKnowledgeBase
from phi.vectordb.pgvector import PgVector

knowledge_base = WebsiteKnowledgeBase(
    urls=[""],
    # Number of links to follow from the seed URLs
    max_links=10,
    # Table name: ai.website_documents
    vector_db=PgVector(
        table_name="website_documents",
        db_url="postgresql+psycopg://ai:ai@localhost:5532/ai",
    ),
)