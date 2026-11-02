# Mariage de Lysandre & Louisa

Mariage le samedi 4 septembre 2027 au château de Chambord.

Ce dépôt contient deux choses :

1. le **save the date** envoyé aux invités ;
2. une petite **application d'organisation** (budget, invités, prestataires, documents).

## Save the date

Dossier `save_the_date/` :

- `defilant.html` : **la version finale**, une page qui se découvre en défilant
  (photos des fiançailles, date, plan d'accès, décompte). Disponible en
  français, anglais et japonais (bouton en haut à droite, ou `#fr`, `#en`,
  `#ja` à la fin de l'adresse).
- `img/` : les photos utilisées par la page, en version allégée.
- `index.html` et `affiche.html` : premières pistes, gardées pour mémoire.

Les polices viennent de Google Fonts, aucune installation n'est nécessaire :
il suffit d'ouvrir `defilant.html` dans un navigateur.

Les photos originales en haute définition (`save_the_date/photos_engagement/`)
ne sont volontairement pas dans le dépôt.

## Application d'organisation

Application Flask (`app.py`, `blueprints/`, `templates/`), sans connexion :
elle tourne sur votre ordinateur et n'est accessible que depuis celui-ci.

Pour la lancer :

```sh
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

python app.py                      # puis http://localhost:7860
```

Les données sont enregistrées dans `data/` (ou dans le dossier indiqué par
`DATA_DIR`), qui n'est pas versionné.
