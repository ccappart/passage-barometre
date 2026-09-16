"""Classification sectorielle a partir du texte libre `activite` du BODACC.

Le BODACC ne porte pas de code NAF : l'activite est decrite en francais par le
greffe. On classe par mots-cles, en visant les familles qui correspondent a
l'ICP de Passage (PME de services, industrie, BTP) plutot qu'une nomenclature
exhaustive. L'ordre compte : la premiere famille qui matche gagne, donc les
regles les plus specifiques passent en premier.
"""
import re
import unicodedata

def _sansaccent(s):
    return "".join(c for c in unicodedata.normalize("NFD", s.lower())
                   if unicodedata.category(c) != "Mn")

# Ordre volontaire : du plus specifique au plus general.
FAMILLES = [
    ("Santé et pharmacie", r"pharmaci|officine|laboratoire d analyse|orthop|opticien|audiopro|infirmier|kinesi|dentaire|veterinaire"),
    ("Boulangerie et alimentation", r"boulanger|patisser|boucher|charcuter|poissonner|primeur|epicer|alimentation|caviste|fromager|chocolater|glacier"),
    ("Hôtellerie et restauration", r"restaur|brasserie|hotel|pizzer|creperie|traiteur|bar\b|cafe\b|debit de boisson|snack|fast.?food|chambre d hote"),
    ("BTP et construction", r"batiment|construction|maconner|couvertur|charpent|plomberi|electricit[eé] gener|chauffage|menuiser|peintur|carrelage|terrassement|travaux public|renovation|isolation|platrerie|serrurerie"),
    ("Industrie et production", r"industri|fabrication|usinage|mecanique de precision|metallurg|chaudronner|plasturg|imprimerie|menuiserie industrielle|assemblage|production de"),
    ("Transport et logistique", r"transport|logistique|messagerie|demenagement|fret|taxi|ambulanc|vtc|entreposage"),
    ("Automobile", r"garage|carrosserie|reparation de vehicul|nettoyage de vehicul|concession|pieces detachees|controle technique|station.service"),
    ("Services aux entreprises", r"conseil|ingenier|bureau d etude|comptab|expertise|informatique|logiciel|numerique|communication|publicit|marketing|agence web|formation profession|recrutement|interim|securite privee|nettoyage de locaux|proprete|laverie|pressing|blanchisserie|auto.?ecole|enseignement de (?:la )?conduite"),
    ("Commerce de détail", r"commerce de detail|vente au detail|pret.a.porter|habillement|chaussur|bijouter|librairie|fleurist|tabac|presse|meuble|electromenager|jardiner|animalerie|magasin"),
    ("Commerce de gros", r"commerce de gros|negoce|grossiste|import.export|distribution de"),
    ("Coiffure, beauté, bien-être", r"coiffur|esthetique|beaute|institut|barbier|onglerie|manucure|pedicure|soins du visage|soins des pieds|spa\b|massage|salle de sport|fitness"),
    ("Immobilier", r"immobili|agence immobiliere|syndic|gestion locative|marchand de biens"),
]
FAMILLES = [(nom, re.compile(_sansaccent(motif), re.I)) for nom, motif in FAMILLES]


def classe(activite: str) -> str:
    """Famille d'activite, ou 'Non classé' si aucun mot-cle ne matche."""
    if not activite:
        return "Non classé"
    a = _sansaccent(activite)
    for nom, motif in FAMILLES:
        if motif.search(a):
            return nom
    return "Non classé"
