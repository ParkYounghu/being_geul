import os
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from starlette.middleware.sessions import SessionMiddleware
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import routes
from routes import auth, programs, admin
from services import db
from utils import get_flashed_messages

app = FastAPI(title="정부지원사업 웹사이트")

# Add Session Middleware
# IMPORTANT: Change the secret_key for production
app.add_middleware(SessionMiddleware, secret_key=os.getenv("SECRET_KEY", "your-default-secret-key"))

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Setup templates
templates = Jinja2Templates(directory="templates")
templates.env.globals['get_flashed_messages'] = get_flashed_messages


# Include routers
app.include_router(auth.router)
app.include_router(programs.router)
app.include_router(admin.router)


@app.on_event("startup")
async def startup_event():
    # This is another place to ensure the DB is initialized.
    # It runs after the app is fully loaded.
    db.init_db()


@app.get("/")
async def root(request: Request):
    """
    Redirects the root URL to the main programs list.
    """
    return RedirectResponse(url="/programs")

# The following is for local development with `uvicorn main:app --reload`
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
