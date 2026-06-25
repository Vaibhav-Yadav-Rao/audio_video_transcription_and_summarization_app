
from flask import Flask
from routes.auth_routes      import auth
from routes.upload_routes    import upload
from routes.dashboard_routes import dash
from routes.summarize_routes import summ
from database.db import init_db
from pyngrok import ngrok
import os

app = Flask(__name__, template_folder="templates", static_folder="static")
app.secret_key = os.environ.get("SECRET_KEY", "change-me-in-production-32chars!")

app.register_blueprint(auth)
app.register_blueprint(upload)
app.register_blueprint(dash)
app.register_blueprint(summ)

if __name__ == "__main__":
    init_db()
    ngrok.kill()
    public_url = ngrok.connect(5000)
    print(f"\n🚀  Public URL: {public_url}\n")
    app.run(host="0.0.0.0", port=5000, debug=True, use_reloader=False)
