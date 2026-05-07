from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

from src.application.query_engine import QueryEngine
from src.application.indexer import IndexerService
from src.infrastructure.embeddings.gemini_embedder import GeminiEmbedder
from src.infrastructure.vector_store.chroma_store import ChromaVectorStore
from src.infrastructure.loaders.constitution_scraper import ConstitutionScraper

from src.infrastructure.llm.tag_generator import TagGenerator
from src.infrastructure.llm.gemini_llm import GeminiLLM

EMBEDDING_MODEL_ID = "gemini-embedding-2"
TAG_MODEL_ID = "gemini-3.1-flash-lite-preview"
MODEL_ID = "gemini-3.1-flash-lite-preview"

app = FastAPI(title="Konstytucja RP - System RAG")

embedder = GeminiEmbedder(model_name=EMBEDDING_MODEL_ID)
vector_store = ChromaVectorStore(persist_directory="./data/chroma", embedder=embedder)
llm = GeminiLLM(model_id=MODEL_ID)
tag_generator = TagGenerator(model_id=TAG_MODEL_ID)
scraper = ConstitutionScraper()

query_engine = QueryEngine(vector_store=vector_store, llm=llm)
indexer_service = IndexerService(loader=scraper, vector_store=vector_store, tag_generator=tag_generator)


# Modele API
class QuestionRequest(BaseModel):
    question: str = Field(..., description="Pytanie do systemu")


class AnswerResponse(BaseModel):
    answer: str = Field(..., description="Odpowiedź na zadane pytanie")
    sources: list[str] = Field(..., description="Źródła informacji")


@app.post("/query", response_model=AnswerResponse)
async def ask_question(request: QuestionRequest):
    try:
        response = query_engine.ask(request.question)
        return AnswerResponse(answer=response.answer, sources=response.sources)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/index")
async def trigger_indexing(background_tasks: BackgroundTasks):
    background_tasks.add_task(indexer_service.run)
    return {"message": "Proces indeksowania uruchomiony w tle."}


app.mount("/static", StaticFiles(directory="web"), name="static")


@app.get("/")
async def read_index():
    return FileResponse("web/index.html")
