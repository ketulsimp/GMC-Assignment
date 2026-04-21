from routers import auth, google_auth
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from starlette.middleware.sessions import SessionMiddleware

app = FastAPI()

# 🔹 Session Middleware (Needed for OAuth)
app.add_middleware(
    SessionMiddleware, 
    # to generate secret_key run: openssl rand -hex 32
    secret_key="07236367cef3194c6237067352340905904c1e4a547f09f72d1383d5868c15da"
)  # Replace with a secure, random key!

# 🔹 Registering Routers
app.include_router(auth.router)
app.include_router(google_auth.router)

# 🔹 Root Endpoint
@app.get("/")
def home():
    with open("index.html") as f:
        return HTMLResponse(f.read())
