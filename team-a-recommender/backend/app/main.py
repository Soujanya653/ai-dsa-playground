from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict

from app.core.recommender import ProblemRecommender

app = FastAPI(title="AI-DSA Problem Recommender")

# Initialize recommender once at startup
recommender = ProblemRecommender()


class RecommendRequest(BaseModel):
    query: str
    top_k: int = 5


class RecommendResponse(BaseModel):
    results: List[Dict]


@app.get("/")
def health_check():
    return {"status": "ok"}


@app.post("/recommend", response_model=RecommendResponse)
def recommend_problems(request: RecommendRequest):
    try:
        results = recommender.recommend(
            query=request.query,
            top_k=request.top_k,
        )
        return {"results": results}

    except ValueError as e:
        # Bad user input
        raise HTTPException(status_code=400, detail=str(e))

    except Exception as e:
        # Unexpected error
        raise HTTPException(status_code=500, detail="Internal server error")

