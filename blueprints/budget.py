from datetime import date
from decimal import Decimal, InvalidOperation

from flask import Blueprint, redirect, render_template, request, url_for

from auth import current_email
from models import CategorieBudget, LigneBudget, Paiement, db

bp = Blueprint("budget", __name__, url_prefix="/budget")


@bp.before_request
def exiger_connexion():
    if not current_email():
        return redirect(url_for("home"))


def _decimal_ou_none(valeur):
    valeur = (valeur or "").strip().replace(",", ".")
    if not valeur:
        return None
    try:
        return Decimal(valeur)
    except InvalidOperation:
        return None


@bp.route("/")
def liste():
    categories = CategorieBudget.query.order_by(CategorieBudget.nom).all()

    total_prevu = total_reference = total_paye = total_restant = Decimal("0")
    reste_inconnu = False

    for categorie in categories:
        for ligne in categorie.lignes:
            total_prevu += ligne.montant_prevu or 0
            total_paye += ligne.total_paye
            if ligne.montant_reference is not None:
                total_reference += ligne.montant_reference
                total_restant += ligne.reste_a_payer
            else:
                reste_inconnu = True

    totaux = {
        "prevu": total_prevu,
        "reference": total_reference,
        "paye": total_paye,
        "restant": total_restant,
        "reste_inconnu": reste_inconnu,
    }
    return render_template(
        "budget.html", categories=categories, totaux=totaux, today=date.today().isoformat()
    )


@bp.route("/categories/ajouter", methods=["POST"])
def ajouter_categorie():
    nom = (request.form.get("nom") or "").strip()
    if nom:
        db.session.add(CategorieBudget(nom=nom))
        db.session.commit()
    return redirect(url_for("budget.liste"))


@bp.route("/categories/<int:categorie_id>/supprimer", methods=["POST"])
def supprimer_categorie(categorie_id):
    categorie = db.get_or_404(CategorieBudget, categorie_id)
    db.session.delete(categorie)
    db.session.commit()
    return redirect(url_for("budget.liste"))


@bp.route("/lignes/ajouter", methods=["POST"])
def ajouter_ligne():
    ligne = LigneBudget(
        categorie_id=request.form.get("categorie_id"),
        libelle=(request.form.get("libelle") or "").strip() or "Sans nom",
        montant_prevu=_decimal_ou_none(request.form.get("montant_prevu")),
        montant_final=_decimal_ou_none(request.form.get("montant_final")),
        notes=(request.form.get("notes") or "").strip() or None,
    )
    db.session.add(ligne)
    db.session.commit()
    return redirect(url_for("budget.liste"))


@bp.route("/lignes/<int:ligne_id>/modifier", methods=["POST"])
def modifier_ligne(ligne_id):
    ligne = db.get_or_404(LigneBudget, ligne_id)
    ligne.libelle = (request.form.get("libelle") or ligne.libelle).strip()
    ligne.montant_prevu = _decimal_ou_none(request.form.get("montant_prevu"))
    ligne.montant_final = _decimal_ou_none(request.form.get("montant_final"))
    ligne.notes = (request.form.get("notes") or "").strip() or None
    db.session.commit()
    return redirect(url_for("budget.liste"))


@bp.route("/lignes/<int:ligne_id>/supprimer", methods=["POST"])
def supprimer_ligne(ligne_id):
    ligne = db.get_or_404(LigneBudget, ligne_id)
    db.session.delete(ligne)
    db.session.commit()
    return redirect(url_for("budget.liste"))


@bp.route("/lignes/<int:ligne_id>/paiements/ajouter", methods=["POST"])
def ajouter_paiement(ligne_id):
    montant = _decimal_ou_none(request.form.get("montant"))
    if montant is not None:
        date_paiement = request.form.get("date") or date.today().isoformat()
        paiement = Paiement(
            ligne_id=ligne_id,
            montant=montant,
            date=date.fromisoformat(date_paiement),
            note=(request.form.get("note") or "").strip() or None,
        )
        db.session.add(paiement)
        db.session.commit()
    return redirect(url_for("budget.liste"))


@bp.route("/paiements/<int:paiement_id>/supprimer", methods=["POST"])
def supprimer_paiement(paiement_id):
    paiement = db.get_or_404(Paiement, paiement_id)
    db.session.delete(paiement)
    db.session.commit()
    return redirect(url_for("budget.liste"))
