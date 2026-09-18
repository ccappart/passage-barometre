"""Agregation du BODACC en baromètre publiable.

Regle de publication : on ne publie une mediane que si la cellule compte au
moins N transactions (defaut 30). En dessous, un chiffre n'est pas
statistiquement defendable et l'exposer serait de la fausse precision.
"""
import json
import sys
from pathlib import Path
from collections import defaultdict

RACINE = Path(__file__).resolve().parent
sys.path.insert(0, str(RACINE))
from secteurs import classe
from dedoublonne import dedoublonne

SEUIL_CELLULE = 30   # transactions minimum pour publier une mediane

# PERIMETRE EDITORIAL (arbitrage Charles, 16/09/2026)
#
# Le commerce de proximite est exclu du barometre. Raison : la valeur d'un bar,
# d'une boulangerie, d'un salon de coiffure ou d'une boutique tient d'abord au
# bail et a l'emplacement, pas a une capacite beneficiaire transmissible. C'est
# une transaction immobiliere deguisee, pas une cession d'entreprise. Les y
# melanger ecrase la mediane (108 200 EUR tous secteurs contre 657 500 EUR sans
# eux sur le segment haut) et decrit un marche qui n'est pas celui de Passage.
PROXIMITE = {
    "Hôtellerie et restauration",
    "Boulangerie et alimentation",
    "Commerce de détail",
    "Coiffure, beauté, bien-être",
}

# La sante reste dans le tableau mais sort de la mediane annoncee : une officine
# se valorise sur une licence et un chiffre d'affaires reglemente, pas comme une
# PME ordinaire. Avec elle la mediane passe de 500 000 a 657 500 EUR, ce qui
# ferait croire a un dirigeant industriel qu'il est tres en dessous du marche.
HORS_MEDIANE = {"Santé et pharmacie"}


def charge(chemin, prix_min=0, hors_proximite=True):
    """Transactions exploitables. Par defaut, hors commerce de proximite."""
    out = []
    for l in open(chemin, encoding="utf-8"):
        x = json.loads(l)
        if not x["prix"] or x["prix"] < prix_min:
            continue
        x["secteur"] = classe(x["activite"])
        if x["secteur"] == "Non classé":
            continue
        if hors_proximite and x["secteur"] in PROXIMITE:
            continue
        out.append(x)
    # Voir dedoublonne.py : une meme operation est publiee une fois par greffe.
    return dedoublonne(out)


def stats(valeurs):
    v = sorted(valeurs)
    n = len(v)
    def q(p):
        return v[min(int(n * p), n - 1)]
    return {
        "n": n,
        "mediane": round(q(.5)),
        "q1": round(q(.25)),
        "q3": round(q(.75)),
        "min": round(v[0]),
        "max": round(v[-1]),
    }


def agrege(lignes, cle):
    paquets = defaultdict(list)
    for x in lignes:
        k = x.get(cle)
        if k and k != "Non classé":
            paquets[k].append(x["prix"])
    return {
        k: stats(v) for k, v in paquets.items() if len(v) >= SEUIL_CELLULE
    }


def croise(lignes, a, b):
    paquets = defaultdict(list)
    for x in lignes:
        ka, kb = x.get(a), x.get(b)
        if ka and kb and ka != "Non classé":
            paquets[(ka, kb)].append(x["prix"])
    return {f"{k[0]} | {k[1]}": stats(v)
            for k, v in paquets.items() if len(v) >= SEUIL_CELLULE}


if __name__ == "__main__":
    prix_min = int(sys.argv[1]) if len(sys.argv) > 1 else 0
    L = charge(RACINE / "data" / "bodacc-2025.jsonl", prix_min)
    res = {
        "millesime": 2025,
        "source": "BODACC, DILA, licence ouverte",
        "prix_minimum_retenu": prix_min,
        "transactions_retenues": len(L),
        "seuil_publication_cellule": SEUIL_CELLULE,
        "perimetre": "hors commerce de proximite (CHR, boulangerie, détail, coiffure)",
        # La mediane annoncee exclut aussi la sante, qui reste dans le detail.
        "national": stats([x["prix"] for x in L if x["secteur"] not in HORS_MEDIANE]),
        "national_hors_medianne_note": "santé et pharmacie exclue de cette médiane",
        "national_toutes_familles": stats([x["prix"] for x in L]),
        # Le detail sectoriel montre la sante, c'est un secteur comme un autre.
        "par_secteur": agrege(L, "secteur"),
        # Les regions, elles, l'excluent : sa repartition geographique n'a rien
        # a voir avec celle des PME et ferait ressortir des ecarts regionaux qui
        # ne sont qu'une concentration d'officines.
        "par_region": agrege([x for x in L if x["secteur"] not in HORS_MEDIANE], "region"),
        "secteur_x_region": croise(L, "secteur", "region"),
    }
    sortie = RACINE / "out"
    sortie.mkdir(exist_ok=True)
    chemin = sortie / f"barometre-2025-min{prix_min}.json"
    json.dump(res, open(chemin, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"transactions retenues : {len(L)}")
    print(f"cellules secteur      : {len(res['par_secteur'])}")
    print(f"cellules region       : {len(res['par_region'])}")
    print(f"cellules croisees     : {len(res['secteur_x_region'])}")
    print(f"ecrit : {chemin}")
