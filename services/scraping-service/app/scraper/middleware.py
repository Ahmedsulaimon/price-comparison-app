from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware



class Middleware:
    """Scraper for Aldi grocery products."""
    
    @staticmethod
    def setup_middleware(app: FastAPI):
       """Set up CORS and other middlewares."""
       app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Restrict in production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        )
