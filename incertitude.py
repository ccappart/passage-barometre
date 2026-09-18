"""Intervalle de confiance de la mediane, et test de l'ecart entre deux periodes.

Sur une cellule de 40 a 150 transactions, une mediane bouge beaucoup par simple
tirage. Sans cette etape, on publierait du bruit comme une tendance. Bootstrap
non parametrique, 4000 reechantillonnages, intervalle a 95 %.
"""
import json
import random
import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parent
sys.path.insert(0, str(RACINE))
from barometre import HORS_MEDIANE
from barometre_semestre import charge_periode, paquets

N_TIRAGES = 4000
random.seed(20260918)


def med(v):
    s = sorted(v)
    return s[min(int(len(s) * .5), len(s) - 1)]


def ic_mediane(v, n=N_TIRAGES):
    k = len(v)
    t = sorted(med([v[random.randrange(k)] for _ in range(k)]) for _ in range(n))
    return t[int(n * .025)], t[int(n * .975)]


def ic_ecart(a, b, n=N_TIRAGES):
    """IC 95 % de (mediane_b - mediane_a), en points de pourcentage."""
    ka, kb = len(a), len(b)
    t = []
    for _ in range(n):
        ma = med([a[random.randrange(ka)] for _ in range(ka)])
        mb = med([b[random.randrange(kb)] for _ in range(kb)])
        t.append((mb - ma) / ma * 100)
    t.sort()
    return t[int(n * .025)], t[int(n * .975)]


if __name__ == "__main__":
    pmin = 300000
    L25 = charge_periode(RACINE / "data" / "bodacc-2025.jsonl", "2025-01-01", "2025-06-30", pmin)
    L26 = charge_periode(RACINE / "data" / "bodacc-2026-s1.jsonl", "2026-01-01", "2026-06-30", pmin)

    n25 = [x["prix"] for x in L25 if x["secteur"] not in HORS_MEDIANE]
    n26 = [x["prix"] for x in L26 if x["secteur"] not in HORS_MEDIANE]
    lo, hi = ic_ecart(n25, n26)
    print(f"NATIONAL  {med(n25):>8} -> {med(n26):>8}  "
          f"ecart {(med(n26)-med(n25))/med(n25)*100:+.1f} %  IC95 [{lo:+.1f} ; {hi:+.1f}]  "
          f"{'SIGNIFICATIF' if lo*hi > 0 else 'non distinguable du bruit'}")
    print(f"          IC95 mediane 2025-S1 {ic_mediane(n25)}   2026-S1 {ic_mediane(n26)}")

    for dim, cle, src25, src26 in (
        ("SECTEUR", "secteur", L25, L26),
        ("REGION", "region",
         [x for x in L25 if x["secteur"] not in HORS_MEDIANE],
         [x for x in L26 if x["secteur"] not in HORS_MEDIANE]),
    ):
        print(f"\n{dim}")
        p25, p26 = paquets(src25, cle), paquets(src26, cle)
        for k in sorted(set(p25) & set(p26)):
            a, b = p25[k], p26[k]
            if len(a) < 30 or len(b) < 30:
                continue
            lo, hi = ic_ecart(a, b)
            ecart = (med(b) - med(a)) / med(a) * 100
            verdict = "SIGNIFICATIF" if lo * hi > 0 else "bruit"
            print(f"  {k:<30} {ecart:+6.1f} %  IC95 [{lo:+6.1f} ; {hi:+6.1f}]  n {len(a):>3}/{len(b):>3}  {verdict}")
