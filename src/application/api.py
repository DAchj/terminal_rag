from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from application.routers import health, chat, knowledge, auth

app = FastAPI(title="RAG API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(chat.router)
app.include_router(knowledge.router)
app.include_router(auth.router)
