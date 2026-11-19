from fastapi import FastAPI

from app.api import admin, auth, query


app = FastAPI(title = "OpsPilot AI")

app.include_router(admin.router)
app.include_router(auth.router)
app.include_router(query.router)