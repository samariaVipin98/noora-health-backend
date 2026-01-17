from config.db import init_db
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from fastapi import APIRouter
from routers import dialogue, notes, search
from fastapi.responses import JSONResponse
from fastapi import FastAPI


load_dotenv()

app = FastAPI()

# 1. CORS Setup (Allow your React app to talk to Python)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    init_db()

api_router = APIRouter()

#  Health check
@api_router.get("/ping")
def ping():
    return JSONResponse({"success": True, "message": "Backend is running"})


app.include_router(api_router, prefix="/api")
app.include_router(notes.router, prefix="/api")
app.include_router(dialogue.router, prefix="/api")
app.include_router(search.router, prefix="/api")
