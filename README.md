# Baromètre des prix de cession d'entreprises

Chaîne complète qui transforme les annonces BODACC en chiffres publiables. Elle
alimente la page [prix de vente d'une entreprise](https://passage.ac/vendre/prix-de-cession)
de passage.ac.

Son intérêt : publier des **prix conclus**, là où le marché publie des méthodes
de valorisation théoriques ou des prix demandés.

## Pourquoi le BODACC

Trois raisons, dans l'ordre d'importance.

1. **Le droit.** Les articles L342-1 et L342-2 du code de la propriété
   intellectuelle protègent le producteur d'une base contre l'extraction d'une
   partie substantielle, et contre l'extraction répétée de parties non
   substantielles qui nuirait à son exploitation normale. Les CGU de Passage
   interdisent d'ailleurs exactement cela chez elle, article 5.
2. **La qualité.** Les plateformes d'annonces publient des prix *demandés* sur
   le marché visible. Le BODACC publie des prix *conclus*, sur l'ensemble du
   marché, y compris les cessions de gré à gré qui n'ont jamais été annoncées
   nulle part.
3. **La traçabilité.** Chaque ligne conserve son `url_complete` vers bodacc.fr,
   donc n'importe quel chiffre publié est sourçable à la transaction près.

## Données

- Source : API Opendatasoft de la DILA, jeu `annonces-commerciales`, licence ouverte.
- Périmètre : `familleavis="vente"`, soit les ventes et cessions.
- Volume : 891 234 annonces depuis l'origine, environ 47 700 par an, stable
  (48 919 en 2022, 47 862 en 2023, 47 700 en 2024, 47 758 en 2025).

## Fichiers

| Fichier | Rôle |
|---|---|
| `prix.py` | Extraction du prix dans le texte libre. 5 motifs, testés sur 8 formats réels de greffes. |
| `collecte.py` | Appels à l'API, découpés par mois car l'offset plafonne à 10 000. Écrit un JSONL. |
| `secteurs.py` | Classification sectorielle par mots-clés sur le champ `activite`. |
| `barometre.py` | Agrégation en médianes et quartiles, avec seuil de publication et périmètre éditorial. |
| `refresh.py` | Rafraîchissement : recalcule, compare aux chiffres publiés sur la page, exporte le CSV open data, sort la matière pour les posts. Ne publie rien. |
| `collecte_semestre.py` | Collecte bornée à un semestre, pour les millésimes intermédiaires. |
| `barometre_semestre.py` | Agrégation d'un semestre et comparaison au même semestre de l'année précédente. |
| `incertitude.py` | Intervalles de confiance par bootstrap, sur une médiane et sur un écart entre deux périodes. |
| `export_semestre.py` | CSV open data du millésime semestriel, avec intervalles et verdict de significativité. |
| `publie_maj.py` | Mise à jour du jeu data.gouv existant. Simulation par défaut, `--go` pour exécuter. |

```bash
python3 collecte.py 2025             # ~15 min, écrit data/bodacc-2025.jsonl
python3 barometre.py 300000          # agrégation du segment haut
python3 refresh.py --annee 2026 --collecte   # cycle complet, avec diff

python3 collecte_semestre.py 2026 1  # ~7 min, écrit data/bodacc-2026-s1.jsonl
python3 barometre_semestre.py        # comparaison S1 2026 contre S1 2025
python3 incertitude.py               # ce qui est un mouvement, ce qui est du bruit
python3 export_semestre.py           # CSV open data du millésime semestriel
python3 publie_maj.py --go           # met à jour le jeu data.gouv (clé dans l'environnement)
```

Le rafraîchissement s'utilise via l'agent `passage-barometre` (`~/.claude/agents/`),
qui lit le diff, arbitre s'il faut republier, et prépare la mise à jour de la page.
Rien n'est publié sans validation.

## Périmètre

C'est le choix éditorial central, et il explique l'écart avec les chiffres
publiés ailleurs.

**Le commerce de proximité est exclu** : hôtellerie et restauration, boulangerie
et alimentation, commerce de détail, coiffure et esthétique. La valeur d'un bar
ou d'une boutique tient au bail et à l'emplacement, pas à une capacité
bénéficiaire qui survivrait au départ du dirigeant. C'est une opération
immobilière déguisée en cession d'entreprise, et les inclure écrase la médiane.

**La santé et la pharmacie** restent dans le détail sectoriel mais sortent de la
médiane annoncée et du tableau régional : une officine se valorise sur une
licence réglementée, et sa concentration géographique créait de faux écarts
entre régions.

## Résultats 2025

- 47 758 annonces collectées, soit le compte exact renvoyé par l'API.
- **71 % portent un prix exploitable**, soit 33 696 transactions.
- Après application du périmètre : 7 890 cessions d'entreprises, dont **2 126 à
  300 000 € et plus**.
- **Médiane publiée : 500 000 €** sur 1 258 transactions hors santé. Premier
  quartile 360 000 €, troisième 850 000 €.
- Classifieur sectoriel : **85 % de couverture**.
- 8 secteurs et 12 régions dépassent le seuil de 30 transactions.

Retirer 73 % du volume n'a pas fragilisé le baromètre : 8 secteurs franchissent
toujours le seuil, et la médiane devient enfin représentative d'une cession
d'entreprise.

## Règles de publication

- **Seuil de 30 transactions par cellule.** En dessous, aucune médiane n'est
  publiée : un chiffre calculé sur 8 ventes est de la fausse précision.
- **Les 15 % non classés ne disparaissent pas.** Ils sont exclus des moyennes
  sectorielles mais comptés dans le total national, et le taux de couverture
  doit être affiché sur la page.
- **Tout chiffre publié est daté et sourcé**, conformément à la règle standing.

## Pourquoi nos chiffres diffèrent des autres

Les agrégations qui circulent aboutissent à une médiane autour de 108 000 €.
C'est arithmétiquement exact et analytiquement faux : près de 6 cessions sur 10
au BODACC sont des fonds de commerce de proximité, qui tirent la médiane vers le
bas et décrivent un marché immobilier plutôt qu'un marché d'entreprises.

## Limites connues

- Le prix du BODACC est le prix du **fonds ou des parts cédées**, pas une
  valeur d'entreprise retraitée. Il ne dit rien de la dette reprise ni de la
  trésorerie. À énoncer sur la page.
- La classification par mots-clés n'est pas une nomenclature NAF. Elle a été
  validée par contrôle manuel sur 14 annonces tirées au hasard, ce qui a révélé
  et corrigé une inversion d'ordre entre boulangerie et restauration. Pour
  fiabiliser, joindre le SIREN au NAF via `recherche-entreprises.api.gouv.fr`.
- 2026 est incomplet à la date de construction, 32 083 annonces au 16/09.

## Millésime 2026-S1

Premier millésime intermédiaire, publié le 18 septembre 2026.

- 22 444 annonces sur le premier semestre 2026, 74 % avec un prix exploitable.
- 676 cessions retenues hors santé, contre 684 sur le même semestre 2025.
- **Médiane 495 000 €** contre 500 000 €, soit -1 %.
- Sur 18 évolutions testées, **une seule ressort à 95 %**, ce qui est exactement
  le nombre de fausses détections attendu quand on teste 18 cellules à ce seuil.
  Aucun mouvement de marché ne peut donc être affirmé.

Deux règles nouvelles, nées de ce millésime.

**Un semestre ne se compare qu'au même semestre.** Le taux d'extraction du prix
suit un profil saisonnier reproductible, de 87 % en janvier à 62 % en mai, et le
même creux apparaît en 2025 et en 2026. Comparer un semestre à une année pleine
mélangerait la saison et le marché.

**L'incertitude se publie avec le chiffre.** Chaque médiane porte désormais son
intervalle de confiance à 95 % par bootstrap, et chaque évolution son verdict de
significativité. Sans cette colonne, un lecteur aurait titré sur le commerce de
gros à +38 % ou la Bretagne à -46 %, qui sont l'un et l'autre des effets de
taille d'échantillon.

## Cadence

Arbitrée sur mesure, pas au feeling.

- **Pas de page quotidienne** : personne ne cherche « les cessions du 16 septembre », et produire à grande échelle des pages à faible valeur est le motif que Google sanctionne.
- **Pas de page mensuelle** non plus : la médiane mensuelle oscille de 100 000 € à 120 000 € avec un écart-type de 5,5 %, donc un commentaire mensuel décrirait du bruit. Et sur le segment retenu, seuls 3 à 5 secteurs atteignent le seuil de 30 sur un mois.
- **Une page métier par mois**, le baromètre national rafraîchi, les pages millésime à l'année.

## Suite

1. Republication du jeu agrégé sur data.gouv.fr avec attribution à passage.ac.
   C'est le levier de backlink du projet, et il n'est pas encore actionné.
   reprendre.cc a publié son index BODACC là-bas mais son sitemap ne compte que
   20 URLs fonctionnelles et aucune page programmatique : la donnée est prise,
   la couche éditoriale est libre.
2. Les pages métier, en commençant par celles dont la demande est mesurée.
3. Jointure SIREN vers NAF pour fiabiliser la classification sectorielle.
