import os
import shutil
import tempfile

from authlib.integrations.flask_client import OAuth
from flask import Flask, redirect, render_template, send_file, session, url_for

from auth import ALLOWED_EMAILS, current_email
from models import db

DATA_DIR = os.environ.get("DATA_DIR") or os.path.join(os.path.dirname(__file__), "data")
UPLOAD_DIR = os.path.join(DATA_DIR, "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

app = Flask(__name__)
app.secret_key = os.environ["FLASK_SECRET_KEY"]
app.config.update(
    SESSION_COOKIE_SECURE=True,
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
    PERMANENT_SESSION_LIFETIME=60 * 60 * 24 * 30,
    SQLALCHEMY_DATABASE_URI=f"sqlite:///{os.path.join(DATA_DIR, 'mariage.db')}",
    SQLALCHEMY_ENGINE_OPTIONS={"connect_args": {"timeout": 15}},
    MAX_CONTENT_LENGTH=30 * 1024 * 1024,
    UPLOAD_DIR=UPLOAD_DIR,
)

db.init_app(app)
with app.app_context():
    db.create_all()

oauth = OAuth(app)
oauth.register(
    name="google",
    client_id=os.environ["GOOGLE_CLIENT_ID"],
    client_secret=os.environ["GOOGLE_CLIENT_SECRET"],
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_kwargs={"scope": "openid email profile"},
)


@app.context_processor
def injecter_etat_connexion():
    return {"logged_in": bool(current_email())}


from blueprints.budget import bp as budget_bp
from blueprints.documents import bp as documents_bp
from blueprints.invites import bp as invites_bp
from blueprints.prestataires import bp as prestataires_bp

app.register_blueprint(documents_bp)
app.register_blueprint(budget_bp)
app.register_blueprint(prestataires_bp)
app.register_blueprint(invites_bp)


@app.route("/")
def home():
    if current_email():
        return render_template("index.html")
    return render_template("login.html")


@app.route("/login")
def login():
    redirect_uri = url_for("auth_callback", _external=True, _scheme="https")
    return oauth.google.authorize_redirect(redirect_uri)


@app.route("/auth/callback")
def auth_callback():
    token = oauth.google.authorize_access_token()
    userinfo = token.get("userinfo") or oauth.google.get("userinfo", token=token).json()
    email = (userinfo.get("email") or "").lower()

    session.clear()
    if email in ALLOWED_EMAILS:
        session.permanent = True
        session["email"] = email
        return redirect(url_for("home"))
    return render_template("denied.html"), 403


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))


@app.route("/admin/backup")
def backup():
    if not current_email():
        return redirect(url_for("home"))

    archive_base = os.path.join(tempfile.gettempdir(), "mariage-backup")
    archive_path = shutil.make_archive(archive_base, "zip", DATA_DIR)
    return send_file(archive_path, as_attachment=True, download_name="mariage-backup.zip")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=7860)
