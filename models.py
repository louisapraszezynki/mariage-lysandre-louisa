from datetime import date

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Prestataire(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(200), nullable=False)
    type = db.Column(db.String(120))
    contact_nom = db.Column(db.String(200))
    telephone = db.Column(db.String(50))
    email = db.Column(db.String(200))
    notes = db.Column(db.Text)

    documents = db.relationship("Document", backref="prestataire")


class Document(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nom_original = db.Column(db.String(255), nullable=False)
    nom_fichier = db.Column(db.String(255), nullable=False)
    signe = db.Column(db.Boolean, default=False, nullable=False)
    prestataire_id = db.Column(db.Integer, db.ForeignKey("prestataire.id"))
    date_ajout = db.Column(db.Date, default=date.today, nullable=False)


class CategorieBudget(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(200), nullable=False)

    lignes = db.relationship(
        "LigneBudget", backref="categorie", cascade="all, delete-orphan"
    )


class LigneBudget(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    categorie_id = db.Column(
        db.Integer, db.ForeignKey("categorie_budget.id"), nullable=False
    )
    libelle = db.Column(db.String(200), nullable=False)
    fourchette_basse = db.Column(db.Numeric(10, 2))
    fourchette_haute = db.Column(db.Numeric(10, 2))
    montant_vise = db.Column(db.Numeric(10, 2))
    montant_final = db.Column(db.Numeric(10, 2))
    notes = db.Column(db.Text)

    paiements = db.relationship(
        "Paiement", backref="ligne", cascade="all, delete-orphan"
    )

    @property
    def montant_reference(self):
        if self.montant_final is not None:
            return self.montant_final
        if self.montant_vise is not None:
            return self.montant_vise
        return None

    @property
    def total_paye(self):
        return sum((p.montant for p in self.paiements), start=0)

    @property
    def reste_a_payer(self):
        ref = self.montant_reference
        if ref is None:
            return None
        return ref - self.total_paye


class Paiement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ligne_id = db.Column(db.Integer, db.ForeignKey("ligne_budget.id"), nullable=False)
    montant = db.Column(db.Numeric(10, 2), nullable=False)
    date = db.Column(db.Date, default=date.today, nullable=False)
    note = db.Column(db.String(255))


class Invite(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(200), nullable=False)
    cote = db.Column(db.String(20), nullable=False)  # "Lysandre" ou "Louisa"
    a_repondu = db.Column(db.Boolean, default=False, nullable=False)
    presence = db.Column(db.String(20), default="en attente", nullable=False)
    notes = db.Column(db.Text)
