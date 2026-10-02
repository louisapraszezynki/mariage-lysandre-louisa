---
title: Mariage Lysandre Louisa
emoji: 🌿
colorFrom: green
colorTo: gray
sdk: docker
app_port: 7860
pinned: false
---

# Mariage de Lysandre & Louisa

Site pour centraliser l'organisation du mariage (château de Chambord).

Accès protégé par connexion Google, restreint aux adresses listées dans le
secret `ALLOWED_EMAILS` du Space. Le Space lui-même est public (sinon
Hugging Face bloquerait l'accès avant même d'atteindre l'écran de
connexion) — la protection réelle du contenu est assurée par ce filtre
Google + liste d'emails.

## Secrets du Space requis

- `GOOGLE_CLIENT_ID`
- `GOOGLE_CLIENT_SECRET`
- `FLASK_SECRET_KEY`
- `ALLOWED_EMAILS` (emails séparés par des virgules)
