"""智服通 AgentOps — FastAPI 后端入口."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.api.chat import router as chat_router
from backend.api.eval import router as eval_router
from backend.api.health import router as health_router
from backend.api.kb import router as kb_router
from backend.api.ops import router as ops_router
from backend.api.sessions import router as sessions_router
from backend.api.traces import router as traces_router
from backend.config import settings

app = FastAPI(
    title="智服通 AgentOps",
    description="B2B 智能客服 Agent 运营中台 API",
    version="0.2.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router, tags=["health"])
app.include_router(chat_router, prefix="/api", tags=["chat"])
app.include_router(sessions_router, prefix="/api", tags=["sessions"])
app.include_router(traces_router, prefix="/api", tags=["traces"])
app.include_router(eval_router, prefix="/api", tags=["eval"])
app.include_router(kb_router, prefix="/api", tags=["kb"])
app.include_router(ops_router, prefix="/api", tags=["ops"])


@app.on_event("startup")
def _startup() -> None:
    from backend.db.store import get_full_store, get_ops_store

    for getter in (get_ops_store, get_full_store):
        store = getter()
        if store:
            store.init_db()


@app.get("/")
def root() -> dict[str, str]:
    return {
        "service": "agentops",
        "status": "running",
        "version": "0.2.0",
        "storage": settings.storage,
        "ops_db": settings.ops_db,
        "semantic": settings.semantic_backend,
        "llm_mode": settings.llm_mode,
        "llm_model": settings.llm_model,
        "llm_base_url": settings.llm_base_url,
        "langgraph": str(settings.use_langgraph),
    }
