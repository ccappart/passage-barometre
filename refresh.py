"""Rafraîchissement du baromètre : recalcule, compare au publié, ne publie rien.

Ce script fait le travail déterministe et s'arrête là. Il ne touche jamais au
dépôt du site et ne pousse jamais. Il produit :

  1. un rapport de diff entre les chiffres recalculés et ceux actuellement
     publiés sur la page, avec un seuil de significativité ;
  2. un export CSV prêt à déposer sur data.gouv.fr ;
  3. de la matière chiffrée pour des posts.

La décision de publier reste humaine, comme pour la prospection : on prépare,
Charles valide.

Usage :
    python3 refresh.py            # millésime en cours, sans recollecte
    python3 refresh.py --collecte # recollecte d'abord depuis l'API BODACC
    python3 refresh.py --annee 2026 --collecte
"""
from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parent
sys.path.insert(0, str(RACINE))

from barometre import HORS_MEDIANE, SEUIL_CELLULE, agrege, charge, croise, stats
from secteurs import classe

# Page qui porte les chiffres publiés. Lecture seule : ce script n'y écrit jamais.
PAGE = Path.home() / "startup-spark-studio-88" / "src" / "pages" / "VendrePrixCession.tsx"

# En dessous, un écart n'est que du bruit d'échantillonnage et ne justifie pas
# de republier. Mesuré sur 2025 : la médiane mensuelle varie de 5,5 % sans que
# le marché ait bougé.
SEUIL_SIGNIFICATIF = 0.06


def _euros(n: float) -> str:
    return f"{n:,.0f} €".replace(",", " ")


def lit_publie() -> dict:
    """Chiffres actuellement en ligne, relus dans le code de la page."""
    if not PAGE.exists():
        return {"secteurs": {}, "regions": {}}
    src = PAGE.read_text(encoding="utf-8")
    # `brut` porte la médiane en euros, `n` le nombre de cessions.
    secteurs = {
        m.group(1): {"mediane": int(m.group(2)), "n": int(m.group(3))}
        for m in re.finditer(r'\{ nom: "([^"]+)", brut: (\d+), n: (\d+),', src)
    }
    regions = {
        m.group(1): {"n": int(m.group(2)), "mediane": int(re.sub(r"\D", "", m.group(3)))}
        for m in re.finditer(r'\{ nom: "([^"]+)", n: (\d+), mediane: "([^"]+)" \}', src)
    }
    return {"secteurs": secteurs, "regions": regions}


def compare(publie: dict, calcule: dict) -> tuple[list[str], list[str]]:
    """Deux listes : les écarts à traiter, et les cellules simplement non affichées.

    La page ne montre qu'un extrait (les 8 premières régions par exemple). Une
    cellule absente de la page n'est donc pas forcément nouvelle : le plus
    souvent elle est juste hors du tableau. Confondre les deux produirait une
    alerte à chaque passage.
    """
    lignes, non_affiches = [], []
    for cle, libelle in (("secteurs", "secteur"), ("regions", "région")):
        anciens = publie.get(cle, {})
        nouveaux = calcule[cle]
        tronque = 0 < len(anciens) < len(nouveaux)
        for nom, v in sorted(nouveaux.items()):
            ancien = anciens.get(nom)
            if not ancien:
                texte = f"  {libelle} « {nom} » : {v['n']} cessions, médiane {_euros(v['mediane'])}"
                (non_affiches if tronque else lignes).append(
                    texte if tronque else f"  NOUVEAU {texte.strip()}"
                )
                continue
            if not ancien["mediane"]:
                continue
            ecart = (v["mediane"] - ancien["mediane"]) / ancien["mediane"]
            if abs(ecart) >= SEUIL_SIGNIFICATIF:
                sens = "hausse" if ecart > 0 else "baisse"
                lignes.append(
                    f"  {sens.upper():7} {libelle} « {nom} » : {_euros(ancien['mediane'])} "
                    f"-> {_euros(v['mediane'])} ({ecart:+.0%}, n={ancien['n']} -> {v['n']})"
                )
        for nom in sorted(set(anciens) - set(nouveaux)):
            lignes.append(f"  SORTI    {libelle} « {nom} » passe sous le seuil de {SEUIL_CELLULE} cessions")
    return lignes, non_affiches


def export_datagouv(L: list, annee: int, chemin: Path) -> int:
    """CSV agrégé, publiable en open data. Aucune ligne individuelle, donc
    aucune redistribution de la base source : uniquement des agrégats."""
    lignes = []
    for cle, libelle in (("secteur", "secteur"), ("region", "région")):
        for nom, v in sorted(agrege(L, cle).items()):
            lignes.append({
                "millesime": annee,
                "dimension": libelle,
                "valeur": nom,
                "cessions": v["n"],
                "prix_median_eur": v["mediane"],
                "premier_quartile_eur": v["q1"],
                "troisieme_quartile_eur": v["q3"],
            })
    for nom, v in sorted(croise(L, "secteur", "region").items()):
        sect, reg = nom.split(" | ")
        lignes.append({
            "millesime": annee, "dimension": "secteur x région", "valeur": f"{sect} / {reg}",
            "cessions": v["n"], "prix_median_eur": v["mediane"],
            "premier_quartile_eur": v["q1"], "troisieme_quartile_eur": v["q3"],
        })
    with open(chemin, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(lignes[0].keys()))
        w.writeheader()
        w.writerows(lignes)
    return len(lignes)


def angles_posts(L: list, annee: int) -> list[str]:
    """Matière chiffrée pour des posts. Des faits, pas des posts rédigés :
    la voix reste celle de Charles."""
    par_sect = agrege(L, "secteur")
    hors_sante = [x for x in L if x["secteur"] not in HORS_MEDIANE]
    haut = sorted(par_sect.items(), key=lambda kv: -kv[1]["mediane"])
    sorties = []

    sans_sante = [(k, v) for k, v in haut if k not in HORS_MEDIANE]
    if sans_sante:
        k, v = sans_sante[0]
        dernier = sans_sante[-1]
        sorties.append(
            f"Écart entre secteurs : {k} à {_euros(v['mediane'])} contre "
            f"{dernier[0]} à {_euros(dernier[1]['mediane'])}, soit un facteur "
            f"{v['mediane'] / dernier[1]['mediane']:.1f} sur le même segment de prix."
        )

    ecarts = sorted(
        ((k, v) for k, v in par_sect.items() if k not in HORS_MEDIANE and v["q1"]),
        key=lambda kv: -(kv[1]["q3"] / kv[1]["q1"]),
    )
    if ecarts:
        k, v = ecarts[0]
        sorties.append(
            f"Dispersion : en {k}, le troisième quartile est {v['q3'] / v['q1']:.1f} fois le premier "
            f"({_euros(v['q1'])} contre {_euros(v['q3'])}). À taille comparable, deux entreprises "
            f"du même métier ne valent pas le même prix."
        )

    par_reg = agrege(hors_sante, "region")
    if len(par_reg) >= 2:
        tri = sorted(par_reg.items(), key=lambda kv: -kv[1]["mediane"])
        sorties.append(
            f"Géographie : {tri[0][0]} à {_euros(tri[0][1]['mediane'])} contre "
            f"{tri[-1][0]} à {_euros(tri[-1][1]['mediane'])}, sur {len(hors_sante)} cessions {annee}."
        )
    return sorties


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--annee", type=int, default=2025)
    ap.add_argument("--collecte", action="store_true", help="recollecter depuis l'API avant de calculer")
    ap.add_argument("--prix-min", type=int, default=300000)
    args = ap.parse_args()

    donnees = RACINE / "data" / f"bodacc-{args.annee}.jsonl"
    if args.collecte or not donnees.exists():
        print(f"Collecte {args.annee} depuis l'API BODACC...", flush=True)
        from collecte import annee as collecte_annee
        lignes = collecte_annee(args.annee)
        donnees.parent.mkdir(exist_ok=True)
        with open(donnees, "w", encoding="utf-8") as f:
            for l in lignes:
                f.write(json.dumps(l, ensure_ascii=False) + "\n")
        print(f"  {len(lignes)} annonces écrites\n")

    L = charge(donnees, args.prix_min)
    for x in L:
        x["secteur"] = classe(x["activite"])
    hors_sante = [x for x in L if x["secteur"] not in HORS_MEDIANE]
    calcule = {
        "secteurs": agrege(L, "secteur"),
        "regions": agrege(hors_sante, "region"),
    }

    nat = stats([x["prix"] for x in hors_sante])
    print(f"=== BAROMÈTRE {args.annee}, segment >= {args.prix_min:,} €".replace(",", " ") + " ===")
    print(f"  {len(L)} cessions retenues, {len(hors_sante)} hors santé")
    print(f"  médiane annoncée : {_euros(nat['mediane'])}  (Q1 {_euros(nat['q1'])}, Q3 {_euros(nat['q3'])})")

    print("\n=== ÉCARTS AVEC CE QUI EST PUBLIÉ ===")
    ecarts, non_affiches = compare(lit_publie(), calcule)
    if ecarts:
        print("\n".join(ecarts))
        print(f"\n  {len(ecarts)} écart(s) au-dessus du seuil de {SEUIL_SIGNIFICATIF:.0%}. Republication à envisager.")
    else:
        print(f"  Aucun écart au-dessus de {SEUIL_SIGNIFICATIF:.0%}. Rien à republier, la page reste juste.")
    if non_affiches:
        print(f"\n  Pour information, {len(non_affiches)} cellule(s) calculée(s) mais hors du tableau publié :")
        print("\n".join(non_affiches))

    sortie = RACINE / "out"
    sortie.mkdir(exist_ok=True)
    csv_path = sortie / f"barometre-cessions-{args.annee}.csv"
    n = export_datagouv(L, args.annee, csv_path)
    print(f"\n=== EXPORT OPEN DATA ===\n  {n} lignes agrégées -> {csv_path}")

    print("\n=== MATIÈRE POUR LES POSTS ===")
    for a in angles_posts(L, args.annee):
        print(f"  . {a}")

    print("\nAucune publication automatique. La page et data.gouv.fr attendent une validation.")


if __name__ == "__main__":
    main()
