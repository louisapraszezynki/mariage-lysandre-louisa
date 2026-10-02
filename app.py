import os

from authlib.integrations.flask_client import OAuth
from flask import Flask, redirect, render_template, session, url_for

app = Flask(__name__)
app.secret_key = os.environ["FLASK_SECRET_KEY"]
app.config.update(
    SESSION_COOKIE_SECURE=True,
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
    PERMANENT_SESSION_LIFETIME=60 * 60 * 24 * 30,
)

ALLOWED_EMAILS = {
    email.strip().lower()
    for email in os.environ.get("ALLOWED_EMAILS", "").split(",")
    if email.strip()
}

oauth = OAuth(app)
oauth.register(
    name="google",
    client_id=os.environ["GOOGLE_CLIENT_ID"],
    client_secret=os.environ["GOOGLE_CLIENT_SECRET"],
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_kwargs={"scope": "openid email profile"},
)


def current_email():
    email = session.get("email")
    if email and email in ALLOWED_EMAILS:
        return email
    session.pop("email", None)
    return None


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


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=7860)
