"""Fabrique les pages de save the date des trois packages.

Part de invites/modele.html (le modèle commun aux packages ; defilant.html,
l'original, n'est pas utilisé), met le texte de « La date » propre à chaque
package, garde ou retire les listes « Où dîner le vendredi soir ? » et
« Où dormir ? », intègre les
photos, puis écrit invites/save-the-date-<code>.html : un fichier autonome,
prêt à publier.

    python3 save_the_date/build.py
"""

import base64
import json
import os
import re

ICI = os.path.dirname(os.path.abspath(__file__))
SORTIE = os.path.join(ICI, "invites")
MODELE = os.path.join(SORTIE, "modele.html")

LOGEMENT = {
    "fr": "Votre logement est prévu sur place.",
    "en": "Your accommodation is arranged on site.",
    "ja": "宿泊先は会場にご用意しております。",
}

# Les noms des packages restent entre nous : ils n'apparaissent jamais dans les pages.
# Les codes rendent les adresses impossibles à deviner d'un package à l'autre.
VERSIONS = [
    {
        "code": "mcgx5jk",
        "package": "Full package : dès le vendredi soir avec le dîner, logement, jusqu'au dimanche matin",
        "restaurants": False,
        "hebergements": False,
        "jours_entoures": True,
        "texte": {
            "fr": "Nous vous attendons dès le vendredi 3 au soir pour un dîner privilégié avec les mariés, "
                  "toute la journée du samedi pour profiter du lieu, de la cérémonie, du cocktail et de la soirée, "
                  "jusqu'au dimanche 5 pour le petit-déjeuner.\n" + LOGEMENT["fr"],
            "en": "We look forward to welcoming you from Friday the 3rd in the evening for a special dinner with the bride and groom, "
                  "all day Saturday to enjoy the venue, the ceremony, the cocktail reception and the party, "
                  "until breakfast on Sunday the 5th.\n" + LOGEMENT["en"],
            "ja": "3日（金）の夜は新郎新婦との特別なディナー、4日（土）は一日を通して会場と挙式、カクテル、パーティーをお楽しみいただき、"
                  "5日（日）の朝食まで、皆さまをお待ちしております。\n" + LOGEMENT["ja"],
        },
    },
    {
        "code": "nxdst2i",
        "package": "Semi full package : dès le vendredi soir sans dîner, logement, jusqu'au dimanche matin",
        "restaurants": True,
        "hebergements": False,
        "jours_entoures": True,
        "texte": {
            "fr": "Votre logement est prévu sur place dès le vendredi 3 au soir, afin que vous ayez le temps de profiter du lieu magique de notre mariage.\n"
                  "Nous comptons sur votre présence le samedi 4, de la cérémonie de notre mariage jusqu’à la soirée, "
                  "ainsi que le dimanche 5 pour le petit-déjeuner.",
            "en": "Your accommodation is arranged on site from Friday the 3rd in the evening, so that you have time to enjoy the magical setting of our wedding.\n"
                  "We look forward to having you with us on Saturday the 4th, from our wedding ceremony through to the evening party, "
                  "and on Sunday the 5th for breakfast.",
            "ja": "3日（金）の夜から会場に宿泊先をご用意しておりますので、私たちの結婚式の素敵な会場をゆっくりお楽しみください。\n"
                  "4日（土）は挙式から夜のパーティーまで、そして5日（日）の朝食にも、ぜひご一緒いただければ幸いです。",
        },
    },
    {
        "code": "wjivri8",
        "package": "Semi package : le samedi seulement (cérémonie, cocktail et dîner)",
        "restaurants": False,
        "hebergements": True,
        "jours_entoures": False,
        "texte": {
            "fr": "Nous serions ravis de vous compter parmi nous samedi 4 au Relais du Château de Chambord "
                  "pour la cérémonie de notre mariage, ainsi que le cocktail et le dîner qui suivront.\n"
                  "Les horaires seront communiqués dans le faire-part à venir.",
            "en": "We would be delighted to have you with us on Saturday the 4th at the Relais du Château de Chambord "
                  "for our wedding ceremony, as well as the cocktail reception and dinner that follow.\n"
                  "Timings will be shared in the formal invitation to come.",
            "ja": "4日（土）、Relais du Château de Chambord にて行われる挙式と、その後のカクテルパーティーおよびディナーに、ぜひお越しください。\n"
                  "詳しい時間は、後日お送りする招待状にてお知らせいたします。",
        },
    },
]

PHRASE_HTML = re.compile(r'(<p class="weekend st" data-i18n="weekend">).*?(</p>)')
PHRASE_JS = re.compile(r"(\n *weekend: )(\"(?:[^\"\\]|\\.)*\"|'(?:[^'\\]|\\.)*'),")
# Parties facultatives du modèle, entourées de marques dans le HTML et dans le script.
BLOCS = {"restaurants": "diner-vendredi", "hebergements": "dormir"}


def bloc_html(nom):
    return re.compile(rf"\n *<!-- {nom}\b.*?<!-- /{nom} -->", re.S)


def bloc_js(nom):
    return re.compile(rf"\n *// {nom}\n.*?// /{nom}", re.S)


def marques(nom):
    return re.compile(rf"\n *(<!-- /?{nom}\b[^>]*-->|// /?{nom}$)", re.M)


def page(source, version):
    textes = version["texte"]
    source = PHRASE_HTML.sub(lambda m: m.group(1) + textes["fr"] + m.group(2), source, count=1)
    langues = iter(["fr", "en", "ja"])
    source = PHRASE_JS.sub(lambda m: m.group(1) + json.dumps(textes[next(langues)], ensure_ascii=False) + ",", source)

    for option, nom in BLOCS.items():
        if version[option]:
            source = marques(nom).sub("", source)
        else:
            source = bloc_html(nom).sub("", source)
            source = bloc_js(nom).sub("", source)

    if not version["jours_entoures"]:
        source = source.replace('<td class="day-weekend">', "<td>")

    def integrer(m):
        with open(os.path.join(ICI, m.group(1)), "rb") as f:
            return 'src="data:image/jpeg;base64,' + base64.b64encode(f.read()).decode() + '"'

    source = re.sub(r'src="(img/[\w-]+\.jpg)"', integrer, source)

    fin_style = source.index("</style>") + len("</style>")
    tete, corps = source[:fin_style], source[fin_style:].strip()
    return f"""<!doctype html>
<html lang="fr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<meta name="robots" content="noindex">
<meta property="og:title" content="Louisa &amp; Lysandre · Save the date">
<meta property="og:description" content="Samedi 4 septembre 2027, château de Chambord.">
<meta property="og:type" content="website">
{tete}
</head>
<body>
{corps}
</body>
</html>
"""


def main():
    with open(MODELE, encoding="utf-8") as f:
        source = f.read()
    assert PHRASE_HTML.search(source) and len(PHRASE_JS.findall(source)) == 3, "phrase de la date introuvable"
    for nom in BLOCS.values():
        assert bloc_html(nom).search(source) and len(bloc_js(nom).findall(source)) == 3, f"partie « {nom} » introuvable"

    for version in VERSIONS:
        nom = f"save-the-date-{version['code']}.html"
        with open(os.path.join(SORTIE, nom), "w", encoding="utf-8") as f:
            f.write(page(source, version))
        print(f"{nom}  ←  {version['package']}")


if __name__ == "__main__":
    main()
