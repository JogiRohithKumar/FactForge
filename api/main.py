# api/main.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
from api.service import get_prediction, extract_text_from_url_async

app = FastAPI(
    title="FactForge Production Gateway",
    version="1.2.0",
    description="Asynchronous processing matrix equipped with internal prediction caching handles and batch processing pipelines."
)

class NewsRequest(BaseModel):
    text: str

class URLRequest(BaseModel):
    url: str

# New schemas for batch arrays
class BatchNewsRequest(BaseModel):
    articles: List[str]

@app.get("/")
async def root():
    return {"service": "FactForge Core Engine", "status": "nominal"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "cache_lookup": "active"}

@app.post("/predict")
async def predict_text(request: NewsRequest):
    if not request.text.strip():
        raise HTTPException(status_code=400, detail="Input text stream cannot be blank.")
    return get_prediction(request.text)

@app.post("/predict-url")
async def predict_url(request: URLRequest):
    """Asynchronously ingests, extracts, and runs inference across scraped link content."""
    try:
        scraped_text = await extract_text_from_url_async(str(request.url))
        if not scraped_text.strip():
            raise HTTPException(status_code=422, detail="Unable to isolate clean data profiles from target URL.")
        return get_prediction(scraped_text)
    except ValueError as val_err:
        raise HTTPException(status_code=400, detail=str(val_err))
    except Exception as general_err:
        raise HTTPException(status_code=500, detail=f"Internal Microservice Exception: {str(general_err)}")

@app.post("/predict/batch")
async def predict_batch(request: BatchNewsRequest):
    """
    Processes an array of text articles in bulk.
    Leverages internal prediction caching loops for ultra-fast evaluations.
    """
    if not request.articles:
        raise HTTPException(status_code=400, detail="Article payload collection cannot be empty.")
        
    results = []
    for index, text in enumerate(request.articles):
        if not text.strip():
            results.append({"index": index, "error": "Empty text sequence encountered."})
            continue
            
        prediction = get_prediction(text)
        results.append({
            "index": index,
            "text_preview": text[:40] + "...",
            "is_fake": prediction["is_fake"],
            "confidence": prediction["confidence"]
        })
        
    return {"processed_count": len(results), "batch_results": results}