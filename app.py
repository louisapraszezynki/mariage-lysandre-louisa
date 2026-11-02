import os
import shutil
import tempfile

from flask import Flask, render_template, send_file

from models import db

DATA_DIR = os.environ.get("DATA_DIR") or os.path.join(os.path.dirname(__file__), "data")
UPLOAD_DIR = os.path.join(DATA_DIR, "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

app = Flask(__name__)
app.config.update(
    SQLALCHEMY_DATABASE_URI=f"sqlite:///{os.path.join(DATA_DIR, 'mariage.db')}",
    SQLALCHEMY_ENGINE_OPTIONS={"connect_args": {"timeout": 15}},
    MAX_CONTENT_LENGTH=30 * 1024 * 1024,
    UPLOAD_DIR=UPLOAD_DIR,
)

db.init_app(app)
with app.app_context():
    from sqlalchemy import inspect

    inspecteur = inspect(db.engine)
    if "ligne_budget" in inspecteur.get_table_names():
        colonnes = {c["name"] for c in inspecteur.get_columns("ligne_budget")}
        if "fourchette_basse" in colonnes:
            # Ancien schéma budget (fourchette basse/haute/souhait) : on repart
            # sur le nouveau modèle simplifié, les autres données ne sont pas touchées.
            db.metadata.tables["paiement"].drop(db.engine, checkfirst=True)
            db.metadata.tables["ligne_budget"].drop(db.engine, checkfirst=True)
            db.metadata.tables["categorie_budget"].drop(db.engine, checkfirst=True)
    db.create_all()

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
    return render_template("index.html")


@app.route("/admin/backup")
def backup():
    archive_base = os.path.join(tempfile.gettempdir(), "mariage-backup")
    archive_path = shutil.make_archive(archive_base, "zip", DATA_DIR)
    return send_file(archive_path, as_attachment=True, download_name="mariage-backup.zip")


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=7860)  # sans connexion : accessible uniquement depuis cet ordinateur
