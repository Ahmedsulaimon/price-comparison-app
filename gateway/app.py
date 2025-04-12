from flask import Flask
import routes 

app = routes.app

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5003, debug=True)