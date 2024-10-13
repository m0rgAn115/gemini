from flask import Flask
from flask_cors import CORS
from config import configure_app
from endpoints import register_endpoints

app = Flask(__name__)
CORS(app)
configure_app(app)
register_endpoints(app)

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=5001)