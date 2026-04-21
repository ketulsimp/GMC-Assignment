

from flask import Flask, render_template
from config import SECRET_KEY
from auth import auth_bp
from profile import profile_bp
import logging

API_SERVICE_NAME = 'GOOGLE OAUTH'
API_VERSION = 'v1'

logging.basicConfig(
    level=logging.DEBUG,
    format='[%(asctime)s] %(levelname)s in %(name)s: %(message)s'
)

logging.getLogger("werkzeug").setLevel(logging.ERROR)
logging.getLogger("pymongo").setLevel(logging.ERROR)
logging.getLogger("urllib3").setLevel(logging.ERROR)

app = Flask(__name__)

app.secret_key = SECRET_KEY

app.register_blueprint(auth_bp)
app.register_blueprint(profile_bp)

@app.route("/")
def home():
    return render_template("index.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
