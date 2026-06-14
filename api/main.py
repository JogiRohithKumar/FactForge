from fastapi import FastAPI
from pydantic import BaseModel
from api.service import get_prediction

app = FastAPI()

# Add this to handle the root URL
@app.get("/")
async def root():
    return {"message": "FactForge API is running"}

class NewsRequest(BaseModel):
    text: str

@app.post("/predict")
async def predict(request: NewsRequest):
    return get_prediction(request.text)