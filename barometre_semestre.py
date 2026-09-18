"""Barometre d'un semestre, et comparaison au meme semestre de l'annee d'avant.

Regle de comparabilite : un semestre ne se compare qu'au meme semestre de
l'annee precedente. Comparer un semestre a une annee pleine melangerait un
effet de saison avec un effet de marche.

Le seuil de publication de 30 transactions par cellule s'applique aux DEUX
periodes : une evolution n'est publiee que si les deux points sont publiables.
"""
import csv
import json
import sys
from pathlib import Path
from collections import defaultdict

RACINE = Path(__file__).resolve().parent
sys.path.insert(0, str(RACINE))
from secteurs import classe
from barometre import SEUIL_CELLULE, PROXIMITE, HORS_MEDIANE, stats


def charge_periode(chemin, debut, fin, prix_min=0, hors_proximite=True):
    """Transactions exploitables dont la date de parution tombe dans [debut, fin]."""
    out = []
    for l in open(chemin, encoding="utf-8"):
        x = json.loads(l)
        d = x.get("date") or ""
        if not (debut <= d[:10] <= fin):
            continue
        if not x["prix"] or x["prix"] < prix_min:
            continue
        x["secteur"] = classe(x["activite"])
        if x["secteur"] == "Non classé":
            continue
        if hors_proximite and x["secteur"] in PROXIMITE:
            continue
        out.append(x)
    return out


def compte_brut(chemin, debut, fin):
    """Annonces totales et annonces avec prix lisible sur la periode."""
    tot = avec = 0
    for l in open(chemin, encoding="utf-8"):
        x = json.loads(l)
        d = x.get("date") or ""
        if not (debut <= d[:10] <= fin):
            continue
        tot += 1
        if x["prix"]:
            avec += 1
    return tot, avec


def paquets(lignes, cle):
    p = defaultdict(list)
    for x in lignes:
        k = x.get(cle)
        if k and k != "Non classé":
            p[k].append(x["prix"])
    return p


def agrege(lignes, cle, seuil=SEUIL_CELLULE):
    return {k: stats(v) for k, v in paquets(lignes, cle).items() if len(v) >= seuil}


def barometre(chemin, debut, fin, prix_min):
    L = charge_periode(chemin, debut, fin, prix_min)
    national = [x["prix"] for x in L if x["secteur"] not in HORS_MEDIANE]
    return {
        "periode": [debut, fin],
        "transactions_retenues": len(L),
        "national": stats(national) if national else None,
        "par_secteur": agrege(L, "secteur"),
        "par_region": agrege([x for x in L if x["secteur"] not in HORS_MEDIANE], "region"),
        "_lignes": L,
    }


def evolution(avant, apres):
    """Variation de la mediane, cellule par cellule, uniquement si les deux points sont publiables."""
    out = {}
    for dim in ("par_secteur", "par_region"):
        for k, ap in apres[dim].items():
            av = avant[dim].get(k)
            if not av:
                continue
            out.setdefault(dim, {})[k] = {
                "avant": av["mediane"], "apres": ap["mediane"],
                "n_avant": av["n"], "n_apres": ap["n"],
                "var_pct": round((ap["mediane"] - av["mediane"]) / av["mediane"] * 100, 1),
            }
    return out


if __name__ == "__main__":
    prix_min = int(sys.argv[1]) if len(sys.argv) > 1 else 300000
    src26 = RACINE / "data" / "bodacc-2026-s1.jsonl"
    src25 = RACINE / "data" / "bodacc-2025.jsonl"

    brut26 = compte_brut(src26, "2026-01-01", "2026-06-30")
    brut25 = compte_brut(src25, "2025-01-01", "2025-06-30")

    # Perimetre entreprises, tous prix : la marche intermediaire de l'ecremage.
    ent26 = len(charge_periode(src26, "2026-01-01", "2026-06-30", 0))
    ent25 = len(charge_periode(src25, "2025-01-01", "2025-06-30", 0))

    b26 = barometre(src26, "2026-01-01", "2026-06-30", prix_min)
    b25 = barometre(src25, "2025-01-01", "2025-06-30", prix_min)

    res = {
        "millesime": "2026-S1",
        "source": "BODACC, DILA, licence ouverte",
        "prix_minimum_retenu": prix_min,
        "seuil_publication_cellule": SEUIL_CELLULE,
        "perimetre": "hors commerce de proximite ; sante et pharmacie hors mediane nationale et hors regions",
        "volumes": {
            "2026-S1": {"annonces": brut26[0], "avec_prix": brut26[1], "cessions_entreprises": ent26},
            "2025-S1": {"annonces": brut25[0], "avec_prix": brut25[1], "cessions_entreprises": ent25},
        },
        "2026-S1": {k: v for k, v in b26.items() if k != "_lignes"},
        "2025-S1": {k: v for k, v in b25.items() if k != "_lignes"},
        "evolution": evolution(b25, b26),
    }
    out = RACINE / "out"
    out.mkdir(exist_ok=True)
    chemin = out / f"barometre-2026s1-min{prix_min}.json"
    json.dump(res, open(chemin, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

    print(f"ANNONCES      2025-S1 {brut26 and brut25[0]:>6}   2026-S1 {brut26[0]:>6}")
    print(f"AVEC PRIX     2025-S1 {brut25[1]:>6}   2026-S1 {brut26[1]:>6}")
    print(f"CESSIONS ENT. 2025-S1 {ent25:>6}   2026-S1 {ent26:>6}")
    print(f"RETENUES>={prix_min}  2025-S1 {b25['transactions_retenues']:>6}   2026-S1 {b26['transactions_retenues']:>6}")
    if b25["national"] and b26["national"]:
        a, b = b25["national"], b26["national"]
        print(f"\nNATIONAL  mediane {a['mediane']:>8} -> {b['mediane']:>8}  "
              f"({(b['mediane']-a['mediane'])/a['mediane']*100:+.1f} %)  n {a['n']} -> {b['n']}")
        print(f"          q1       {a['q1']:>8} -> {b['q1']:>8}")
        print(f"          q3       {a['q3']:>8} -> {b['q3']:>8}")
    for dim in ("par_secteur", "par_region"):
        print(f"\n{dim.upper()}")
        for k, v in sorted(res["evolution"].get(dim, {}).items(), key=lambda kv: -kv[1]["var_pct"]):
            print(f"  {k:<34} {v['avant']:>8} -> {v['apres']:>8}  {v['var_pct']:+6.1f} %   n {v['n_avant']:>3} -> {v['n_apres']:>3}")
        manquants = [k for k in b26[dim] if k not in res["evolution"].get(dim, {})]
        sortis = [k for k in b25[dim] if k not in b26[dim]]
        if manquants:
            print(f"  (publiable en 2026-S1 seulement : {', '.join(manquants)})")
        if sortis:
            print(f"  (sous le seuil de 30 en 2026-S1 : {', '.join(sortis)})")
    print(f"\necrit : {chemin}")
