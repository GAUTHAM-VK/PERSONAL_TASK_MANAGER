from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import database
from routers import auth_router, tasks_router

load_dotenv()  # <-- ONLY HERE

app = FastAPI(
    title="Bridgeon Personal Task Manager API",
    description=(
        "Multi-user task manager API. Users can register, log in, "
        "and manage their personal tasks securely."
    ),
    version="1.0.0",
)

# Allow frontend requests (Streamlit running on another port)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create tables when server starts
@app.on_event("startup")
def on_startup():
    database.init_db()

# Health route
@app.get("/", tags=["Health"])
def root():
    return {
        "status": "ok",
        "message": "Bridgeon Personal Task Manager API is running."
    }

# Include routers
app.include_router(auth_router.router)
app.include_router(tasks_router.router)