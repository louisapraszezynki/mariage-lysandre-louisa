import os
import uuid

from flask import (
    Blueprint,
    current_app,
    redirect,
    render_template,
    request,
    send_from_directory,
    url_for,
)
from werkzeug.utils import secure_filename

from auth import current_email
from models import Document, Prestataire, db

bp = Blueprint("documents", __name__, url_prefix="/documents")

EXTENSIONS_AUTORISEES = {"pdf", "jpg", "jpeg", "png", "docx", "xlsx"}


@bp.before_request
def exiger_connexion():
    if not current_email():
        return redirect(url_for("home"))


def extension_autorisee(nom_fichier):
    return (
        "." in nom_fichier
        and nom_fichier.rsplit(".", 1)[1].lower() in EXTENSIONS_AUTORISEES
    )


@bp.route("/")
def liste():
    documents = Document.query.order_by(Document.date_ajout.desc()).all()
    prestataires = Prestataire.query.order_by(Prestataire.nom).all()
    return render_template(
        "documents.html", documents=documents, prestataires=prestataires
    )


@bp.route("/ajouter", methods=["POST"])
def ajouter():
    fichier = request.files.get("fichier")
    if fichier and fichier.filename and extension_autorisee(fichier.filename):
        nom_original = fichier.filename
        nom_assaini = secure_filename(nom_original) or "document"
        nom_sur_disque = f"{uuid.uuid4().hex}_{nom_assaini}"
        fichier.save(os.path.join(current_app.config["UPLOAD_DIR"], nom_sur_disque))

        prestataire_id = request.form.get("prestataire_id") or None
        document = Document(
            nom_original=nom_original,
            nom_fichier=nom_sur_disque,
            signe=bool(request.form.get("signe")),
            prestataire_id=prestataire_id,
        )
        db.session.add(document)
        db.session.commit()
    return redirect(url_for("documents.liste"))


@bp.route("/<int:document_id>/signer", methods=["POST"])
def signer(document_id):
    document = db.get_or_404(Document, document_id)
    document.signe = not document.signe
    db.session.commit()
    return redirect(url_for("documents.liste"))


@bp.route("/<int:document_id>/supprimer", methods=["POST"])
def supprimer(document_id):
    document = db.get_or_404(Document, document_id)
    chemin = os.path.join(current_app.config["UPLOAD_DIR"], document.nom_fichier)
    if os.path.exists(chemin):
        os.remove(chemin)
    db.session.delete(document)
    db.session.commit()
    return redirect(url_for("documents.liste"))


@bp.route("/<int:document_id>/telecharger")
def telecharger(document_id):
    document = db.get_or_404(Document, document_id)
    return send_from_directory(
        current_app.config["UPLOAD_DIR"],
        document.nom_fichier,
        as_attachment=True,
        download_name=document.nom_original,
    )
