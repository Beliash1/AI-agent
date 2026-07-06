from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import logger
from api.agent_routes import router as agent_router
from config import FRONTEND_ORIGIN

app = FastAPI(title="Cici Agent API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_ORIGIN],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(agent_router)


@app.get("/health")
async def health():
    """მარტივი health-check — სასარგებლოა Docker/monitoring-ისთვის."""
    return {"status": "ok"}
