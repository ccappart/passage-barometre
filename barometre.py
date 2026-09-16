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

SEUIL_CELLULE = 30   # transactions minimum pour publier une mediane


def charge(chemin, prix_min=0):
    out = []
    for l in open(chemin, encoding="utf-8"):
        x = json.loads(l)
        if x["prix"] and x["prix"] >= prix_min:
            x["secteur"] = classe(x["activite"])
            out.append(x)
    return out


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
        "national": stats([x["prix"] for x in L]),
        "par_secteur": agrege(L, "secteur"),
        "par_region": agrege(L, "region"),
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
