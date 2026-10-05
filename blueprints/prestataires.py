from flask import Blueprint, redirect, render_template, request, url_for

from auth import current_email
from models import Prestataire, db

bp = Blueprint("prestataires", __name__, url_prefix="/prestataires")


@bp.before_request
def exiger_connexion():
    if not current_email():
        return redirect(url_for("home"))


@bp.route("/")
def liste():
    prestataires = Prestataire.query.order_by(Prestataire.nom).all()
    return render_template("prestataires.html", prestataires=prestataires)


@bp.route("/ajouter", methods=["POST"])
def ajouter():
    nom = (request.form.get("nom") or "").strip()
    if nom:
        db.session.add(
            Prestataire(
                nom=nom,
                type=(request.form.get("type") or "").strip() or None,
                contact_nom=(request.form.get("contact_nom") or "").strip() or None,
                telephone=(request.form.get("telephone") or "").strip() or None,
                email=(request.form.get("email") or "").strip() or None,
                notes=(request.form.get("notes") or "").strip() or None,
            )
        )
        db.session.commit()
    return redirect(url_for("prestataires.liste"))


@bp.route("/<int:prestataire_id>")
def fiche(prestataire_id):
    prestataire = db.get_or_404(Prestataire, prestataire_id)
    return render_template("prestataire_fiche.html", prestataire=prestataire)


@bp.route("/<int:prestataire_id>/modifier", methods=["POST"])
def modifier(prestataire_id):
    prestataire = db.get_or_404(Prestataire, prestataire_id)
    prestataire.nom = (request.form.get("nom") or prestataire.nom).strip()
    prestataire.type = (request.form.get("type") or "").strip() or None
    prestataire.contact_nom = (request.form.get("contact_nom") or "").strip() or None
    prestataire.telephone = (request.form.get("telephone") or "").strip() or None
    prestataire.email = (request.form.get("email") or "").strip() or None
    prestataire.notes = (request.form.get("notes") or "").strip() or None
    db.session.commit()
    return redirect(url_for("prestataires.fiche", prestataire_id=prestataire.id))


@bp.route("/<int:prestataire_id>/supprimer", methods=["POST"])
def supprimer(prestataire_id):
    prestataire = db.get_or_404(Prestataire, prestataire_id)
    db.session.delete(prestataire)
    db.session.commit()
    return redirect(url_for("prestataires.liste"))
