"""Export open data du millesime semestriel.

Une ligne par (periode, dimension, valeur). Deux ajouts par rapport au fichier
annuel v1 :

1. L'intervalle de confiance a 95 % de la mediane, par bootstrap. Sur une
   cellule de 40 transactions, une mediane bouge de plusieurs dizaines de
   milliers d'euros par simple tirage : publier le point sans son incertitude
   invite a lire du bruit comme une tendance.
2. La variation face au meme semestre de l'annee precedente, assortie du
   verdict de significativite. Une variation dont l'intervalle contient zero
   est marquee "non" : elle n'est pas distinguable du hasard d'echantillonnage.
"""
import csv
import random
import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parent
sys.path.insert(0, str(RACINE))
from barometre import HORS_MEDIANE
from barometre_semestre import charge_periode, paquets, stats
from incertitude import ic_mediane, ic_ecart, med

random.seed(20260918)
SEUIL = 30
PMIN = 300000
JOURNAL = []   # evolutions testees, reutilisees telles quelles par l'infographie

ENTETE = ["periode", "dimension", "valeur", "cessions", "prix_median_eur",
          "ic95_median_bas_eur", "ic95_median_haut_eur",
          "premier_quartile_eur", "troisieme_quartile_eur",
          "prix_minimum_retenu_eur", "inclus_dans_mediane_nationale",
          "variation_mediane_vs_meme_semestre_pct",
          "ic95_variation_bas_pct", "ic95_variation_haut_pct",
          "variation_significative"]


def cellules(lignes):
    """national + secteurs + regions, chaque cellule rendue avec ses prix bruts."""
    nat = [x["prix"] for x in lignes if x["secteur"] not in HORS_MEDIANE]
    out = [("national", "France entière, hors santé et pharmacie", nat, "oui")]
    for k, v in sorted(paquets(lignes, "secteur").items()):
        out.append(("secteur", k, v, "non" if k in HORS_MEDIANE else "oui"))
    hors = [x for x in lignes if x["secteur"] not in HORS_MEDIANE]
    for k, v in sorted(paquets(hors, "region").items()):
        out.append(("région", k, v, "oui"))
    return out


def rows(lignes, periode, ref=None):
    out = []
    for dim, val, prix, inclus in cellules(lignes):
        if len(prix) < SEUIL:
            continue
        s = stats(prix)
        lo, hi = ic_mediane(prix)
        var = sig = v_lo = v_hi = ""
        if ref is not None:
            r = ref.get((dim, val))
            if r and len(r) >= SEUIL:
                var = round((s["mediane"] - med(r)) / med(r) * 100, 1)
                b_lo, b_hi = ic_ecart(r, prix)
                v_lo, v_hi = round(b_lo, 1), round(b_hi, 1)
                sig = "oui" if b_lo * b_hi > 0 else "non"
                JOURNAL.append({"dimension": dim, "valeur": val,
                                "mediane_avant": med(r), "mediane_apres": s["mediane"],
                                "n_avant": len(r), "n_apres": s["n"],
                                "var": var, "lo": v_lo, "hi": v_hi,
                                "significatif": sig == "oui"})
        out.append([periode, dim, val, s["n"], s["mediane"], round(lo), round(hi),
                    s["q1"], s["q3"], PMIN, inclus, var, v_lo, v_hi, sig])
    return out


if __name__ == "__main__":
    L25 = charge_periode(RACINE / "data" / "bodacc-2025.jsonl", "2025-01-01", "2025-06-30", PMIN)
    L26 = charge_periode(RACINE / "data" / "bodacc-2026-s1.jsonl", "2026-01-01", "2026-06-30", PMIN)
    ref = {(d, v): p for d, v, p, _ in cellules(L25)}

    lignes = rows(L25, "2025-S1") + rows(L26, "2026-S1", ref=ref)

    dossier = RACINE / "out" / "datagouv"
    dossier.mkdir(parents=True, exist_ok=True)
    chemin = dossier / "barometre-cessions-entreprises-2026-s1.csv"
    with open(chemin, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(ENTETE)
        w.writerows(lignes)
    import json
    json.dump(JOURNAL, open(RACINE / "out" / "evolutions-2026s1.json", "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    sig = sum(1 for l in lignes if l[-1] == "oui")
    testees = sum(1 for l in lignes if l[-1] in ("oui", "non"))
    print(f"{len(lignes)} lignes ecrites dans {chemin}")
    print(f"variations testees : {testees}, significatives a 95 % : {sig}")
