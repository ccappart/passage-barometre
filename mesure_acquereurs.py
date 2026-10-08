"""Age et adossement des societes qui achetent, sur le perimetre publie du barometre.

    python3 mesure_acquereurs.py                    # 1er semestre 2026, 300 000 EUR et plus
    python3 mesure_acquereurs.py --json

Pour chaque vente du perimetre (hors commerce de proximite, dedoublonnee), le
SIREN publie au BODACC est celui de la societe qui depose l'annonce, en pratique
l'acquereur. On interroge l'API Recherche d'entreprises (api.gouv.fr) pour :

  - sa date d'immatriculation, d'ou son age le jour de la parution ;
  - ses dirigeants personnes morales. Une societe neuve presidee ou geree par
    une autre societe est adossee a quelqu'un. On regarde alors l'age de cette
    societe mere : 3 ans ou plus, c'est une structure etablie (groupe, holding
    existante) ; moins, c'est une holding montee pour l'operation.

Les commissaires aux comptes, qui apparaissent aussi en personne morale, sont
ecartes. Limite : l'API ne donne que le premier niveau, pas l'actionnariat. Une
holding personnelle ancienne d'un repreneur compte comme "structure etablie".

Perimetre : ventes de fonds de commerce et d'actifs. Le BODACC ne publie aucune
cession de titres (voir README, limites connues).
"""
import datetime
import json
import sys
import time
import urllib.request
from pathlib import Path

RACINE = Path(__file__).resolve().parent
sys.path.insert(0, str(RACINE))
from barometre_semestre import charge_periode
from barometre import HORS_MEDIANE

API = "https://recherche-entreprises.api.gouv.fr/search?per_page=1&q="
CACHE = RACINE / "data" / "cache-entreprises.json"
ANS_ETABLIE = 3


def entreprise(siren, cache):
    if siren in cache:
        return cache[siren]
    for i in range(4):
        try:
            with urllib.request.urlopen(API + siren, timeout=30) as r:
                res = json.loads(r.read()).get("results") or []
            break
        except Exception:
            time.sleep(2 * (i + 1))
    else:
        res = []
    time.sleep(0.15)  # l'API tolere 7 appels par seconde
    e = next((x for x in res if x.get("siren") == siren), None)
    cache[siren] = None if not e else {
        "nom": e.get("nom_complet"), "creation": e.get("date_creation"),
        "categorie": e.get("categorie_entreprise"),
        "meres": [d.get("siren") for d in e.get("dirigeants") or []
                  if d.get("type_dirigeant") == "personne morale" and d.get("siren")
                  and "commissaire" not in (d.get("qualite") or "").lower()],
    }
    return cache[siren]


def age_ans(creation, date):
    a = datetime.date.fromisoformat(creation)
    b = datetime.date.fromisoformat(date[:10])
    return (b - a).days / 365.25


def main():
    debut, fin, prix_min = "2026-01-01", "2026-06-30", 300000
    ventes = charge_periode(RACINE / "data" / "bodacc-2026-s1.jsonl", debut, fin, prix_min)
    cache = json.loads(CACHE.read_text()) if CACHE.exists() else {}
    lignes, perdus = [], 0
    for i, v in enumerate(ventes):
        e = entreprise(v["siren"] or "", cache) if v.get("siren") else None
        if not e or not e["creation"]:
            perdus += 1
            continue
        age = age_ans(e["creation"], v["date"])
        if age < -0.1:  # societe creee apres la parution : SIREN mal attribue
            perdus += 1
            continue
        meres = [entreprise(s, cache) for s in e["meres"]]
        etablie = [m for m in meres if m and m["creation"] and age_ans(m["creation"], v["date"]) >= ANS_ETABLIE]
        if age >= 1:
            profil = "societe de 1 an ou plus"
        elif e["categorie"] in ("GE", "ETI") or etablie:
            profil = "neuve, adossee a une structure etablie"
        elif meres:
            profil = "neuve, holding elle aussi neuve"
        else:
            profil = "neuve, dirigee par des personnes physiques"
        lignes.append({"id": v["id"], "date": v["date"], "prix": v["prix"], "secteur": v["secteur"],
                       "siren": v["siren"], "nom": e["nom"], "age_ans": round(age, 2), "profil": profil,
                       "url": v["url"]})
        if i % 50 == 0:
            CACHE.write_text(json.dumps(cache))
    CACHE.write_text(json.dumps(cache))

    res = {"periode": f"{debut} au {fin}", "prix_min": prix_min, "ventes_perimetre": len(ventes),
           "non_identifies": perdus,
           "tout": resume(lignes),
           # Meme convention que la mediane publiee : la sante sort du chiffre national,
           # une officine se rachete par une SELARL creee pour l'occasion, quasi par construction.
           "hors_sante": resume([l for l in lignes if l["secteur"] not in HORS_MEDIANE])}
    sortie = RACINE / "out" / "acquereurs-2026s1.json"
    sortie.write_text(json.dumps({"resume": res, "lignes": lignes}, ensure_ascii=False, indent=1))
    if "--json" in sys.argv:
        print(json.dumps(res, ensure_ascii=False, indent=1))
        return
    print(f"\n  {len(ventes)} ventes du perimetre, {perdus} acquereurs non identifies")
    for cle, r in (("tout le perimetre", res["tout"]), ("hors sante et pharmacie", res["hors_sante"])):
        print(f"\n  {cle} : {r['acquereurs']} acquereurs, age median {r['age_median_mois']} mois, "
              f"< 6 mois {r['moins_6_mois_pct']} %, < 1 an {r['moins_1_an_pct']} %")
        for k, v in r["profils"].items():
            print(f"    {v['n']:>4}  {v['pct']:>5} %  {k}")
        print(f"    parmi les neuves : " + ", ".join(f"{k.split(', ')[1]} {v} %" for k, v in r["neuves"].items()))
    print(f"\n  detail : {sortie}\n")


def resume(lignes):
    n = len(lignes)
    ages = sorted(l["age_ans"] for l in lignes)
    med = ages[n // 2] if n % 2 else (ages[n // 2 - 1] + ages[n // 2]) / 2
    part = lambda f: round(100 * sum(1 for l in lignes if f(l)) / n, 1)
    profils = {}
    for l in lignes:
        profils[l["profil"]] = profils.get(l["profil"], 0) + 1
    neuves = {k: c for k, c in profils.items() if k.startswith("neuve")}
    tot = sum(neuves.values()) or 1
    return {
        "acquereurs": n, "age_median_mois": round(med * 12, 1),
        "moins_6_mois_pct": part(lambda l: l["age_ans"] < 0.5),
        "moins_1_an_pct": part(lambda l: l["age_ans"] < 1),
        "profils": {k: {"n": c, "pct": round(100 * c / n, 1)} for k, c in sorted(profils.items(), key=lambda x: -x[1])},
        "neuves": {k: round(100 * c / tot) for k, c in sorted(neuves.items(), key=lambda x: -x[1])},
    }


if __name__ == "__main__":
    main()
