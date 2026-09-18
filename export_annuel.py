"""Export open data du millesime annuel, au schema deja publie.

Meme entete que le fichier 2025 depose sur data.gouv.fr : on corrige les
valeurs, pas la structure, pour ne pas casser les reutilisations.
"""
import csv
import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parent
sys.path.insert(0, str(RACINE))
from barometre import charge, agrege, croise, stats, HORS_MEDIANE

ENTETE = ["millesime", "dimension", "valeur", "cessions", "prix_median_eur",
          "premier_quartile_eur", "troisieme_quartile_eur",
          "prix_minimum_retenu_eur", "inclus_dans_mediane_nationale"]


def lignes(L, annee, prix_min):
    out = []
    nat = stats([x["prix"] for x in L if x["secteur"] not in HORS_MEDIANE])
    out.append([annee, "national", "France entière, hors santé et pharmacie",
                nat["n"], nat["mediane"], nat["q1"], nat["q3"], prix_min, "oui"])
    for nom, v in sorted(agrege(L, "secteur").items()):
        out.append([annee, "secteur", nom, v["n"], v["mediane"], v["q1"], v["q3"],
                    prix_min, "non" if nom in HORS_MEDIANE else "oui"])
    hors = [x for x in L if x["secteur"] not in HORS_MEDIANE]
    for nom, v in sorted(agrege(hors, "region").items()):
        out.append([annee, "région", nom, v["n"], v["mediane"], v["q1"], v["q3"], prix_min, "oui"])
    for nom, v in sorted(croise(L, "secteur", "region").items()):
        sect, reg = nom.split(" | ")
        out.append([annee, "secteur x région", f"{sect} / {reg}", v["n"], v["mediane"],
                    v["q1"], v["q3"], prix_min, "non" if sect in HORS_MEDIANE else "oui"])
    return out


if __name__ == "__main__":
    annee = int(sys.argv[1]) if len(sys.argv) > 1 else 2025
    prix_min = int(sys.argv[2]) if len(sys.argv) > 2 else 300000
    L = charge(RACINE / "data" / f"bodacc-{annee}.jsonl", prix_min)
    rows = lignes(L, annee, prix_min)
    chemin = RACINE / "out" / "datagouv" / f"barometre-cessions-entreprises-{annee}.csv"
    with open(chemin, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(ENTETE)
        w.writerows(rows)
    par = {}
    for r in rows:
        par[r[1]] = par.get(r[1], 0) + 1
    print(f"{len(rows)} lignes -> {chemin}")
    print("  ", par)
    print(f"   transactions retenues : {len(L)}")
