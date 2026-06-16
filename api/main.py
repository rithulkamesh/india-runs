import sys
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

sys.path.insert(0, ".")

from src.data.loader import build_id_index, load_candidates

from api.routes.candidates import router as candidates_router
from api.routes.graph import router as graph_router
from api.routes.health import router as health_router
from api.routes.rank import router as rank_router
from api.routes.rankings import router as rankings_router
from api.routes.system import router as system_router

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_DATA_PATH = PROJECT_ROOT / "data" / "candidates.jsonl"


@asynccontextmanager
async def lifespan(app: FastAPI):
    import threading

    from api.routes.rankings import warm

    data_path = str(DEFAULT_DATA_PATH)
    candidates = load_candidates(data_path)
    id_index = build_id_index(candidates)
    app.state.candidates = candidates
    app.state.id_index = id_index
    app.state.candidate_count = len(candidates)
    # Precompute the ranking off the request path so the dashboard loads instantly.
    threading.Thread(target=warm, args=(app.state,), daemon=True).start()
    yield
    app.state.candidates = []
    app.state.id_index = {}
    app.state.candidate_count = 0


app = FastAPI(
    title="India Runs — Candidate Discovery Engine",
    description="FastAPI backend for ranking, searching, and graph-based exploration of engineering candidates.",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router)
app.include_router(candidates_router)
app.include_router(rank_router)
app.include_router(rankings_router)
app.include_router(system_router)
app.include_router(graph_router)


@app.get("/")
def root() -> dict:
    return {
        "name": "India Runs Candidate Discovery Engine",
        "version": "1.0.0",
        "docs": "/docs",
        "endpoints": {
            "health": "/api/health",
            "candidates": "/api/candidates",
            "rank": "/api/rank",
            "graph": "/api/graph/{candidate_id}",
        },
    }
