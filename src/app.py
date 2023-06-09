from fastapi import FastAPI
from src.routers import recipes

app = FastAPI()
app.include_router(recipes.router)


@app.get("/")
def read_root():
    return {"message": "it's working! it's working!!"}
