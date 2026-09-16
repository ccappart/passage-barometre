"""Extraction du prix de cession dans le texte libre d'une annonce BODACC.

Le BODACC ne porte pas le prix dans un champ dedie : il est noye dans
`origineFonds`, en francais, avec des formats d'ecriture heterogenes selon le
greffe. D'ou cette batterie de motifs, testee sur des cas reels.
"""
import re
from typing import Optional

# Les greffes ecrivent indifferemment 40.000,00 / 40 000,00 / 40000.00 / 40000
MONTANT = r"([0-9][0-9  .,]{2,20})"
DEVISE = r"(?:EUR|euros?|€)"

MOTIFS = [
    re.compile(rf"prix\s+stipul[ée]s?\s+(?:de\s+)?{MONTANT}\s*{DEVISE}", re.I),
    re.compile(rf"moyennant\s+(?:le\s+)?prix\s+(?:de\s+)?{MONTANT}\s*{DEVISE}", re.I),
    re.compile(rf"au\s+prix\s+de\s+{MONTANT}\s*{DEVISE}", re.I),
    re.compile(rf"prix\s*:\s*{MONTANT}\s*{DEVISE}", re.I),
    re.compile(rf"c[ée]d[ée]\s+(?:pour|au\s+prix\s+de)\s+{MONTANT}\s*{DEVISE}", re.I),
]


def normalise(brut: str) -> Optional[float]:
    """Convertit '40.000,00' ou '40 000' ou '40000.00' en float."""
    s = brut.strip().replace(" ", "").replace(" ", "")
    if not s:
        return None
    # Le dernier separateur decide : s'il est suivi de 1 ou 2 chiffres, c'est
    # la virgule decimale ; sinon c'est un separateur de milliers.
    dernier_point, dernier_virgule = s.rfind("."), s.rfind(",")
    coupe = max(dernier_point, dernier_virgule)
    if coupe == -1:
        entier, dec = s, ""
    else:
        suffixe = s[coupe + 1:]
        if len(suffixe) <= 2 and suffixe.isdigit():
            entier, dec = s[:coupe], suffixe
        else:
            entier, dec = s, ""
    entier = re.sub(r"[.,]", "", entier)
    if not entier.isdigit():
        return None
    try:
        return float(f"{entier}.{dec or 0}")
    except ValueError:
        return None


def extrait(texte: str) -> Optional[float]:
    """Prix en euros, ou None si aucun motif ne matche ou si le montant est aberrant."""
    if not texte:
        return None
    for motif in MOTIFS:
        m = motif.search(texte)
        if not m:
            continue
        v = normalise(m.group(1))
        # Bornes de vraisemblance : sous 500 EUR c'est une coquille ou un euro
        # symbolique mal ecrit, au-dela de 500 M EUR c'est une erreur de saisie.
        if v is not None and 500 <= v <= 500_000_000:
            return v
    return None
