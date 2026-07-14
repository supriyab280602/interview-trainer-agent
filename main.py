import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from config import settings

# Route Imports
from api.auth_routes import router as auth_router
from api.profile_routes import router as profile_router
from api.resume_routes import router as resume_router
from api.interview_routes import router as interview_router
from api.analytics_routes import router as analytics_router

# Service Imports
from services.cloudant_service import CloudantService
from services.cos_service import COSService
from services.granite_service import GraniteService
from services.rag_service import RAGService
from services.auth_service import AuthService
from services.resume_service import ResumeService
from services.evaluation_service import EvaluationService
from services.interview_service import InterviewService
from services.analytics_service import AnalyticsService

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("FastAPIServer")


def seed_rag_knowledge_base(rag_service: RAGService) -> None:
    """
    Seed standard RAG knowledge base documents upon startup.
    This ensures that default interview rubrics and templates (STAR) 
    are immediately queryable even in a clean setup.
    """
    try:
        logger.info("Checking and seeding RAG knowledge base...")
        # Clear collection first to prevent duplicate seeding bloat during reloads
        rag_service.clear_collection("kb_questions")

        # 1. STAR Method Documentation
        star_doc = (
            "STAR Method Guide:\n"
            "- Situation: Set the scene by describing the context of the challenge or task.\n"
            "- Task: State the target objective and what needed to be done.\n"
            "- Action: Detail the specific actions YOU took to solve the problem (focus on your contributions, tools, and technical decisions).\n"
            "- Result: Quantify outcomes and lessons learned (e.g., improved load speed by 25%)."
        )
        rag_service.ingest_document(
            text=star_doc,
            source_metadata={"source": "Internal STAR Docs", "category": "Behavioral", "domain": "General"}
        )

        # 2. HR Interview Guide
        hr_doc = (
            "HR / Personality Rubric:\n"
            "- 'Tell me about yourself': Focus on 1-minute career timeline, key tech stack, and interest in the job role. Avoid personal history.\n"
            "- 'What are your strengths?': Name 2 concrete skills backed by quick examples (e.g., quick learning of FastAPI, or test-driven design).\n"
            "- 'What are your weaknesses?': Present a real technical weakness but frame it as a learning progress (e.g., 'I used to struggle with CSS layouts, but I've been taking courses to master grid and flexbox')."
        )
        rag_service.ingest_document(
            text=hr_doc,
            source_metadata={"source": "HR Best Practices", "category": "HR", "domain": "General"}
        )

        # 3. Technical Interview Guide (Software & Backend Engineering)
        tech_backend = (
            "Software & Backend Engineering Reference Rubric:\n"
            "- Asynchronous processing (async/await) is crucial for database calls and REST API throughput in Python/FastAPI.\n"
            "- Design principles: SOLID principles, separation of routing (Controller) from business logic (Service) and database (Repository).\n"
            "- Database scaling: indexing frequently filtered columns, caching read-heavy workloads with Redis, and connection pooling."
        )
        rag_service.ingest_document(
            text=tech_backend,
            source_metadata={"source": "Tech Coding Guide", "category": "Technical", "domain": "Software Engineering"}
        )

        # 4. Technical Interview Guide (AI/ML & Cloud Computing)
        tech_ai_cloud = (
            "AI/ML & Cloud Computing Reference Rubric:\n"
            "- RAG (Retrieval-Augmented Generation) connects LLMs to real-time external data. Embeddings represent semantic meaning, and vector stores perform similarity search.\n"
            "- Model inference parameters: Temperature controls randomness (higher = creative, 0 = deterministic), Max New Tokens limits length.\n"
            "- Cloud architecture: Deploying applications in Docker containers, managing sessions in distributed memory caches, and storing media assets in Cloud Object Storage (COS) buckets."
        )
        rag_service.ingest_document(
            text=tech_ai_cloud,
            source_metadata={"source": "AI & Cloud Standards", "category": "Technical", "domain": "Artificial Intelligence"}
        )

        logger.info("RAG knowledge base successfully seeded.")
    except Exception as e:
        logger.error(f"Error seeding RAG knowledge base: {str(e)}", exc_info=True)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    FastAPI Lifespan events to manage connections cleanly.
    """
    logger.info("FastAPI application starting up...")
    
    # Initialize Core Cloud and Database services
    db_service = CloudantService()
    cos_service = COSService()
    granite_service = GraniteService()
    rag_service = RAGService()

    # Seed knowledge base
    seed_rag_knowledge_base(rag_service)

    # Initialize Higher Business services
    auth_service = AuthService(db_service)
    resume_service = ResumeService(db_service, cos_service, granite_service)
    evaluation_service = EvaluationService(rag_service, granite_service)
    interview_service = InterviewService(db_service, resume_service, granite_service, rag_service, evaluation_service)
    analytics_service = AnalyticsService(db_service)

    # Store references on app state for dependency injection
    app.state.db_service = db_service
    app.state.cos_service = cos_service
    app.state.granite_service = granite_service
    app.state.rag_service = rag_service
    app.state.auth_service = auth_service
    app.state.resume_service = resume_service
    app.state.evaluation_service = evaluation_service
    app.state.interview_service = interview_service
    app.state.analytics_service = analytics_service

    yield
    
    # Shutdown actions
    logger.info("FastAPI application shutting down...")
    await db_service.shutdown()


# Instantiate FastAPI Application
app = FastAPI(
    title=settings.APP_NAME,
    description="FastAPI Backend for IBM Internship Challenge AI Interview Trainer Agent",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS Middleware
# Enable easy communication with Streamlit client
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, restrict to Streamlit's specific URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Attach routes
app.include_router(auth_router)
app.include_router(profile_router)
app.include_router(resume_router)
app.include_router(interview_router)
app.include_router(analytics_router)


# Global Exception Handling
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    Global catch-all exception handler to return clean JSON error packages 
    instead of raw traceback logs to the client.
    """
    logger.error(f"Unhandled Exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "An unexpected server error occurred. Please try again later."}
    )

@app.get("/health", tags=["System Check"])
async def health_check():
    """
    Health check check for automated monitors.
    """
    return {"status": "healthy", "service": settings.APP_NAME}


if __name__ == "__main__":
    import uvicorn
    logger.info(f"Launching Uvicorn server on {settings.HOST}:{settings.PORT}")
    uvicorn.run("main:app", host=settings.HOST, port=settings.PORT, reload=settings.DEBUG)
