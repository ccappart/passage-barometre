"""Collecte d'un semestre d'annonces BODACC de vente.

Meme source et meme normalisation que collecte.py, mais borne aux mois d'un
semestre. Sert au millesime intermediaire : le premier semestre se compare au
premier semestre de l'annee precedente, jamais a une annee pleine.
"""
import json
import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parent
sys.path.insert(0, str(RACINE))
from collecte import mois

def semestre(annee, s=1, journal=True):
    debut = 1 if s == 1 else 7
    tout = []
    for m in range(debut, debut + 6):
        lot = mois(annee, m)
        if not lot:
            continue
        tout += lot
        if journal:
            avec = sum(1 for x in lot if x["prix"])
            print(f"  {annee}-{m:02d} : {len(lot):>5} annonces, {avec:>5} avec prix", flush=True)
    return tout

if __name__ == "__main__":
    a = int(sys.argv[1])
    s = int(sys.argv[2]) if len(sys.argv) > 2 else 1
    lignes = semestre(a, s)
    dossier = RACINE / "data"
    dossier.mkdir(exist_ok=True)
    chemin = dossier / f"bodacc-{a}-s{s}.jsonl"
    with open(chemin, "w", encoding="utf-8") as f:
        for l in lignes:
            f.write(json.dumps(l, ensure_ascii=False) + "\n")
    print(f"\n{len(lignes)} annonces ecrites dans {chemin}")
