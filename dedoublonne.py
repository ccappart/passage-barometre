"""Dedoublonnage des annonces : une transaction, une ligne.

Une cession dont le fonds compte plusieurs etablissements est publiee une fois
par greffe concerne, et CHAQUE annonce porte le prix total de l'operation. Un
deal a 4 M EUR reparti sur 9 sites entre ainsi 9 fois dans le fichier, avec 9
fois 4 M EUR. Sur les medianes l'effet est modere, sur les comptages et les
valeurs agregees il est massif.

Cle retenue : (SIREN de l'annonce, prix exact), dans une fenetre de 60 jours.
Deux annonces qui partagent l'acquereur et le montant a l'euro pres, a moins de
deux mois d'intervalle, decrivent la meme operation. Verification sur le premier
semestre 2026 : 92 groupes concernes, dont 88 % etales sur 30 jours ou moins,
ce qui est la signature d'une publication multi-greffes et non de deux ventes
distinctes.

Le resultat ne depend pas du reglage : avec une fenetre de 30, 60, 90 jours ou
sans limite, la mediane 2025 tombe a 480 000 EUR dans tous les cas, et le compte
varie de moins de 2 %. La fenetre de 60 jours est retenue parce qu'elle est la
plus conservatrice des quatre qui convergent.

Effet mesure : le millesime 2025 passe de 1 258 a 1 076 cessions et sa mediane
de 500 000 a 480 000 EUR.
"""
import datetime

FENETRE_JOURS = 60


def _jour(s):
    return datetime.date.fromisoformat((s or "")[:10])


def dedoublonne(lignes, fenetre=FENETRE_JOURS):
    """Une ligne par operation, la plus ancienne annonce faisant foi."""
    ancre, out = {}, []
    for x in sorted(lignes, key=lambda x: (x.get("date") or "", x.get("id") or "")):
        cle = (x.get("siren"), x.get("prix"))
        if not x.get("date"):
            out.append(x)
            continue
        j = _jour(x["date"])
        if cle in ancre and (j - ancre[cle]).days <= fenetre:
            continue
        ancre[cle] = j
        out.append(x)
    return out


def compte_doublons(lignes, fenetre=FENETRE_JOURS):
    """Nombre de lignes retirees, pour le journal de rafraichissement."""
    return len(lignes) - len(dedoublonne(lignes, fenetre))
