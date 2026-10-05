from flask import Blueprint, redirect, render_template, request, url_for

from auth import current_email
from models import Invite, db

bp = Blueprint("invites", __name__, url_prefix="/invites")


@bp.before_request
def exiger_connexion():
    if not current_email():
        return redirect(url_for("home"))


@bp.route("/")
def liste():
    invites = Invite.query.order_by(Invite.nom).all()
    compteurs = {
        "total": len(invites),
        "lysandre": sum(1 for i in invites if i.cote == "Lysandre"),
        "louisa": sum(1 for i in invites if i.cote == "Louisa"),
        "confirmes": sum(1 for i in invites if i.presence == "oui"),
        "en_attente": sum(1 for i in invites if i.presence == "en attente"),
    }
    return render_template("invites.html", invites=invites, compteurs=compteurs)


@bp.route("/ajouter", methods=["POST"])
def ajouter():
    nom = (request.form.get("nom") or "").strip()
    if nom:
        db.session.add(
            Invite(
                nom=nom,
                cote=request.form.get("cote") or "Lysandre",
                a_repondu=bool(request.form.get("a_repondu")),
                presence=request.form.get("presence") or "en attente",
                notes=(request.form.get("notes") or "").strip() or None,
            )
        )
        db.session.commit()
    return redirect(url_for("invites.liste"))


@bp.route("/<int:invite_id>/modifier", methods=["POST"])
def modifier(invite_id):
    invite = db.get_or_404(Invite, invite_id)
    invite.a_repondu = bool(request.form.get("a_repondu"))
    invite.presence = request.form.get("presence") or "en attente"
    db.session.commit()
    return redirect(url_for("invites.liste"))


@bp.route("/<int:invite_id>/supprimer", methods=["POST"])
def supprimer(invite_id):
    invite = db.get_or_404(Invite, invite_id)
    db.session.delete(invite)
    db.session.commit()
    return redirect(url_for("invites.liste"))
