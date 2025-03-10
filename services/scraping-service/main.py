# import sys
# import os
# sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# from flask import Flask


# def create_app():
#     app = Flask(__name__)
    
#     return app

# app = create_app()

# if __name__ == '__main__':
#     app.run(
#        "app.routes:app",
#         host='0.0.0.0',
#         port=5001,
#         debug=True
#     )

import uvicorn
import os

if __name__ == "__main__":
    # Get port from environment variable or use default
    #port = int(os.environ.get("PORT", 5001))
    
    # Run the application
    uvicorn.run(
        "app.routes:app",
        host="0.0.0.0",
        port=5001,
        reload=True 
        #if os.environ.get("ENVIRONMENT") == "development" else False
    )