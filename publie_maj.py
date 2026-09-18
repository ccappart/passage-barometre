"""Mise a jour du jeu data.gouv.fr existant avec le millesime 2026-S1.

Le jeu n'est PAS recree : on garde la meme URL, donc les liens entrants et le
referencement acquis. On met a jour la description, la frequence, la couverture
temporelle, on remplace la methodologie et on ajoute la ressource semestrielle.

La cle API n'est jamais ecrite dans ce fichier ni dans le depot : le script la
lit dans l'environnement.

    export DATAGOUV_API_KEY="..."      # cle personnelle, jamais commitee
    python3 publie_maj.py              # simulation, n'envoie rien
    python3 publie_maj.py --go         # execute la mise a jour

La cle se cree sur https://www.data.gouv.fr/admin/me/ , onglet API.
"""
import json
import mimetypes
import os
import sys
import urllib.error
import urllib.request
import uuid
from pathlib import Path

RACINE = Path(__file__).resolve().parent
API = "https://www.data.gouv.fr/api/1"

DATASET = "6aabb33e4335f654c08041a8"
RES_METHODO = "8c3026ba-294c-4061-8a70-cc30778e5d88"

CSV_2026 = RACINE / "out" / "datagouv" / "barometre-cessions-entreprises-2026-s1.csv"
METHODO = RACINE / "out" / "datagouv" / "methodologie.txt"
DESCRIPTION = RACINE / "out" / "datagouv" / "description-maj-2026s1.md"

GO = "--go" in sys.argv
CLE = os.environ.get("DATAGOUV_API_KEY", "")


def _entetes(extra=None):
    h = {"X-API-KEY": CLE, "User-Agent": "passage-barometre/2.0"}
    h.update(extra or {})
    return h


def appel(methode, chemin, corps=None, entetes=None):
    url = f"{API}{chemin}"
    if not GO:
        print(f"  [simulation] {methode} {url}")
        return {"simulation": True}
    req = urllib.request.Request(url, data=corps, method=methode,
                                 headers=_entetes(entetes))
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            return json.loads(r.read() or b"{}")
    except urllib.error.HTTPError as e:
        detail = e.read().decode("utf-8", "replace")[:600]
        raise SystemExit(f"ECHEC {methode} {chemin} : HTTP {e.code}\n{detail}")


def multipart(fichier: Path):
    """Corps multipart/form-data minimal, sans dependance externe."""
    limite = f"----passage{uuid.uuid4().hex}"
    typ = mimetypes.guess_type(fichier.name)[0] or "application/octet-stream"
    corps = b"".join([
        f"--{limite}\r\n".encode(),
        f'Content-Disposition: form-data; name="file"; filename="{fichier.name}"\r\n'.encode(),
        f"Content-Type: {typ}\r\n\r\n".encode(),
        fichier.read_bytes(),
        f"\r\n--{limite}--\r\n".encode(),
    ])
    return corps, {"Content-Type": f"multipart/form-data; boundary={limite}"}


def main():
    if GO and not CLE:
        raise SystemExit("DATAGOUV_API_KEY absente de l'environnement. "
                         "export DATAGOUV_API_KEY=\"...\" puis relancer.")
    for f in (CSV_2026, METHODO, DESCRIPTION):
        if not f.exists():
            raise SystemExit(f"fichier manquant : {f}")

    print("1. Metadonnees du jeu (description, frequence, couverture, tags)")
    meta = {
        "description": DESCRIPTION.read_text(encoding="utf-8"),
        "frequency": "semiannual",
        "temporal_coverage": {"start": "2025-01-01", "end": "2026-06-30"},
        "tags": ["entreprise", "mediane", "prix-cession", "region",
                 "secteur-activite", "bodacc", "transmission-entreprise", "pme"],
    }
    appel("PUT", f"/datasets/{DATASET}/", json.dumps(meta).encode(),
          {"Content-Type": "application/json"})

    print("2. Remplacement du fichier de methodologie (version 2)")
    corps, ent = multipart(METHODO)
    appel("POST", f"/datasets/{DATASET}/resources/{RES_METHODO}/upload/", corps, ent)
    appel("PUT", f"/datasets/{DATASET}/resources/{RES_METHODO}/", json.dumps({
        "title": "Méthodologie : extraction, classification, périmètre, incertitude",
        "description": "Version 2, millésimes 2025 et 2026-S1. Ajoute le protocole "
                       "de bootstrap et la règle de comparabilité semestrielle.",
        "type": "documentation",
    }).encode(), {"Content-Type": "application/json"})

    print("3. Ajout de la ressource millesime 2026-S1")
    corps, ent = multipart(CSV_2026)
    rep = appel("POST", f"/datasets/{DATASET}/upload/", corps, ent)
    rid = (rep.get("id") or (rep.get("resource") or {}).get("id")) if isinstance(rep, dict) else None
    if rid:
        appel("PUT", f"/datasets/{DATASET}/resources/{rid}/", json.dumps({
            "title": "Baromètre des prix de cession, millésime 2026-S1 et rappel 2025-S1 (CSV)",
            "description": "38 lignes. Premier semestre 2026 et premier semestre 2025 "
                           "recalculé à l'identique. Chaque médiane porte son intervalle "
                           "de confiance à 95 %, chaque évolution son verdict de "
                           "significativité.",
            "type": "main",
        }).encode(), {"Content-Type": "application/json"})
    elif GO:
        print("  ressource creee, identifiant non renvoye : renseigner le titre a la main")

    print("\nTermine." if GO else "\nSimulation terminee, rien n'a ete envoye. Relancer avec --go.")
    print("https://www.data.gouv.fr/datasets/barometre-des-prix-de-cession-dentreprises-en-france/")


if __name__ == "__main__":
    main()
