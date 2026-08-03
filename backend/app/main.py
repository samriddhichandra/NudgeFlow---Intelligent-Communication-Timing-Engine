from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import events, nudges, delivery_reports, recommendation, analytics

app = FastAPI(
    title="Intelligent Communication Timing Engine",
    description="Predicts the best time and channel to send the next nudge based on "
    "historical engagement data.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(events.router, prefix="/api/events", tags=["Events"])
app.include_router(nudges.router, prefix="/api/nudges", tags=["Nudges"])
app.include_router(
    delivery_reports.router, prefix="/api/delivery-reports", tags=["Delivery Reports"]
)
app.include_router(
    recommendation.router, prefix="/api/recommendation", tags=["Recommendation"]
)
app.include_router(analytics.router, prefix="/api/users", tags=["Analytics"])


@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "ok"}


@app.get("/", tags=["Health"])
def root():
    return {"service": "Intelligent Communication Timing Engine", "docs": "/docs"}
