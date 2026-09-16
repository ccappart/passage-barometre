"""Collecte des annonces BODACC de vente et cession, avec prix.

Source : API Opendatasoft de la DILA, jeu `annonces-commerciales`, licence
ouverte. Chaque annonce reste tracable par son `url_complete`, ce qui permet de
sourcer n'importe quel chiffre publie.

L'API plafonne l'offset a 10 000 : on decoupe donc par mois, chaque mois pesant
environ 4 000 annonces.
"""
import json
import sys
from pathlib import Path
import time
import urllib.parse
import urllib.request
from calendar import monthrange

RACINE = Path(__file__).resolve().parent
sys.path.insert(0, str(RACINE))
from prix import extrait

BASE = ("https://bodacc-datadila.opendatasoft.com/api/explore/v2.1"
        "/catalog/datasets/annonces-commerciales/records")
CHAMPS = ("id,dateparution,departement_nom_officiel,region_nom_officiel,ville,"
          "registre,listeetablissements,url_complete")


def _appel(url, essais=4):
    for i in range(essais):
        try:
            with urllib.request.urlopen(url, timeout=90) as r:
                return json.loads(r.read())
        except Exception:
            if i == essais - 1:
                raise
            time.sleep(2 * (i + 1))


def mois(annee, m):
    """Toutes les annonces de vente du mois, avec leur prix quand il est lisible."""
    dernier = monthrange(annee, m)[1]
    where = (f"familleavis=\"vente\" and dateparution>=date'{annee}-{m:02d}-01' "
             f"and dateparution<=date'{annee}-{m:02d}-{dernier}'")
    out, offset = [], 0
    while True:
        url = (f"{BASE}?where={urllib.parse.quote(where)}"
               f"&select={urllib.parse.quote(CHAMPS)}&limit=100&offset={offset}")
        d = _appel(url)
        res = d.get("results", [])
        for r in res:
            le = r.get("listeetablissements")
            # Le champ revient tantot en objet, tantot en chaine JSON selon
            # l'annonce : on normalise avant tout acces.
            if isinstance(le, str):
                texte = le
                try:
                    le = json.loads(le)
                except json.JSONDecodeError:
                    le = {}
            else:
                texte = json.dumps(le, ensure_ascii=False) if le else ""
            etab = (le or {}).get("etablissement") or {} if isinstance(le, dict) else {}
            if isinstance(etab, list):
                etab = etab[0] if etab else {}
            if not isinstance(etab, dict):
                etab = {}
            out.append({
                "id": r.get("id"),
                "date": r.get("dateparution"),
                "departement": r.get("departement_nom_officiel"),
                "region": r.get("region_nom_officiel"),
                "ville": r.get("ville"),
                "siren": (r.get("registre") or [None])[0],
                "activite": (etab.get("activite") or "").strip(),
                "prix": extrait(texte),
                "url": r.get("url_complete"),
            })
        offset += 100
        if len(res) < 100 or offset >= min(d.get("total_count", 0), 9900):
            break
    return out


def annee(a, journal=True):
    tout = []
    for m in range(1, 13):
        lot = mois(a, m)
        if not lot:
            continue
        tout += lot
        if journal:
            avec = sum(1 for x in lot if x["prix"])
            print(f"  {a}-{m:02d} : {len(lot):>5} annonces, {avec:>5} avec prix", flush=True)
    return tout


if __name__ == "__main__":
    a = int(sys.argv[1]) if len(sys.argv) > 1 else 2025
    lignes = annee(a)
    dossier = RACINE / "data"
    dossier.mkdir(exist_ok=True)
    chemin = dossier / f"bodacc-{a}.jsonl"
    with open(chemin, "w", encoding="utf-8") as f:
        for l in lignes:
            f.write(json.dumps(l, ensure_ascii=False) + "\n")
    print(f"\n{len(lignes)} annonces ecrites dans {chemin}")
