import time
import logging
from fastapi import FastAPI, Depends, HTTPException, Security, BackgroundTasks
from fastapi.security import APIKeyHeader
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, HttpUrl
from typing import List, Dict, Any, Optional

from api.config import settings
from api.service import IngestionMLPipeline

# Structural Telemetry & Core Logging Configuration
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("FactForgeLogger")

app = FastAPI(title=settings.APP_NAME, version=settings.VERSION)
api_key_header = APIKeyHeader(name="Authorization", auto_error=False)

# Global Performance State Tracking Matrices
SYSTEM_METRICS: Dict[str, Any] = {
    "total_inferences_computed": 0,
    "average_latency_ms": 0.0,
    "total_failures_logged": 0,
    "user_feedback_loops": {"false_positives": 0, "false_negatives": 0}
}

# Explicit Core Dependency Injection Pattern
async def verify_auth_token(header_token: Optional[str] = Depends(api_key_header)) -> str:
    if not header_token or header_token != f"Bearer {settings.API_BEARER_TOKEN}":
        raise HTTPException(status_code=401, detail="Invalid or missing authorization credentials.")
    return header_token

# Unified Payload Validation Contracts
class SingleTextPayload(BaseModel):
    text: str

class BatchTextPayload(BaseModel):
    texts: List[str]

class URLPayload(BaseModel):
    url: str

class FeedbackPayload(BaseModel):
    prediction_id: str
    feedback_type: str  # false_positive / false_negative
    user_notes: Optional[str] = None

# Operational Controllers & Route Endpoints
@app.get("/health", tags=["Telemetry"])
async def get_system_health():
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "environment": settings.ENVIRONMENT
    }

@app.get("/metrics", tags=["Telemetry"])
async def get_system_metrics(auth: str = Depends(verify_auth_token)):
    return SYSTEM_METRICS

@app.post("/predict", tags=["Inference"])
async def predict_single_text(payload: SingleTextPayload, auth: str = Depends(verify_auth_token)):
    start_time = time.perf_counter()
    try:
        pipeline = IngestionMLPipeline()
        result = pipeline.compute_ensemble_inference(payload.text)
        
        # Calculate processing metrics
        latency = (time.perf_counter() - start_time) * 1000
        SYSTEM_METRICS["total_inferences_computed"] += 1
        SYSTEM_METRICS["average_latency_ms"] = ((SYSTEM_METRICS["average_latency_ms"] * (SYSTEM_METRICS["total_inferences_computed"] - 1)) + latency) / SYSTEM_METRICS["total_inferences_computed"]
        
        result["latency_ms"] = round(latency, 2)
        return result
    except Exception as e:
        SYSTEM_METRICS["total_failures_logged"] += 1
        logger.error(f"Inference Failure: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal Inference Failure: {str(e)}")

@app.post("/predict-url", tags=["Inference"])
async def predict_url_stream(payload: URLPayload, auth: str = Depends(verify_auth_token)):
    start_time = time.perf_counter()
    try:
        pipeline = IngestionMLPipeline()
        extracted_text = await pipeline.async_network_scrape(str(payload.url))
        result = pipeline.compute_ensemble_inference(extracted_text)
        
        latency = (time.perf_counter() - start_time) * 1000
        SYSTEM_METRICS["total_inferences_computed"] += 1
        result["latency_ms"] = round(latency, 2)
        return result
    except Exception as e:
        SYSTEM_METRICS["total_failures_logged"] += 1
        logger.error(f"URL Ingestion Failure: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/predict-batch", tags=["Inference"])
async def predict_batch_stream(payload: BatchTextPayload, auth: str = Depends(verify_auth_token)):
    try:
        pipeline = IngestionMLPipeline()
        results = [pipeline.compute_ensemble_inference(text) for text in payload.texts]
        return {"batch_results": results, "count": len(results)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Batch Processing Failure: {str(e)}")

@app.post("/feedback", tags=["Telemetry"])
async def log_user_feedback(payload: FeedbackPayload):
    if payload.feedback_type == "false_positive":
        SYSTEM_METRICS["user_feedback_loops"]["false_positives"] += 1
    elif payload.feedback_type == "false_negative":
        SYSTEM_METRICS["user_feedback_loops"]["false_negatives"] += 1
    return {"status": "success", "message": "Feedback captured for pipeline optimization."}