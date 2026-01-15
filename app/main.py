from fastapi import FastAPI

app = FastAPI(title="Bulletin Board Bot - health")


@app.get("/health")
async def health():
    return {"status": "ok"}
