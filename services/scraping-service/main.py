
from fastapi import FastAPI
from app.scraper.middleware import Middleware
from app.scraper.routes.aldi_routes import  router as aldi_product_router
from app.scraper.routes.tesco_routes import  router as tesco_product_router
from app.scraper.routes.iceland_routes import  router as iceland_product_router
from app.scraper.routes.sainsbury_routes import  router as sainsbury_product_router

app = FastAPI(
    title="Scraping Service API",
    description="Service for scraping product data from UK retailers",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Apply middleware
Middleware.setup_middleware(app)

# Include routers
app.include_router(aldi_product_router)
app.include_router(tesco_product_router)
app.include_router(iceland_product_router)
app.include_router(sainsbury_product_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
         "main:app",
         host="0.0.0.0",
         port=5001,
         reload=True 
         #if os.environ.get("ENVIRONMENT") == "development" else False
     )
















# import uvicorn
# import os

# if __name__ == "__main__":
#     # Get port from environment variable or use default
#     #port = int(os.environ.get("PORT", 5001))
    
#     # Run the application
#     uvicorn.run(
#         "app.routes:app",
#         host="0.0.0.0",
#         port=5001,
#         reload=True 
#         #if os.environ.get("ENVIRONMENT") == "development" else False
#     )