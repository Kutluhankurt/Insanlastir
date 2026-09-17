from fastapi import FastAPI

from app.api.humanize import router as humanize_router

app = FastAPI(title="İnsanlaştır — Turkish Human Writing Naturalizer", version="0.1.0")
app.include_router(humanize_router)


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}
