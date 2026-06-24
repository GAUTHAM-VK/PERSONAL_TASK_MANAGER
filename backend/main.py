from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import database
from routers import auth_router, tasks_router

app = FastAPI(
    title="Personal Task Manager API",
    description=(
        "Multi-user task manager. Register, log in, and you'll receive a "
        "session token. Click the **Authorize** button above and paste the "
        "token (just the raw value, no 'Bearer ' prefix needed - Swagger adds "
        "that for you) to unlock the protected endpoints below."
    ),
    version="1.0.0",
)

# Allow the Streamlit frontend (running on a different port) to call this API.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    database.init_db()


@app.get("/", tags=["Health"])
def root():
    return {"status": "ok", "message": "Task Manager API is running."}


app.include_router(auth_router.router)
app.include_router(tasks_router.router)
