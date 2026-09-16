# Baromètre des cessions : prototype

Chaîne complète qui transforme les annonces BODACC en chiffres publiables sur
passage.ac. Construit le 16/09/2026 pour répondre à une question simple : est-ce
que les chiffres tiennent avant d'investir dans les pages ?

**Réponse : oui, avec une réserve de fond sur le segment couvert (voir plus bas).**

## Pourquoi le BODACC plutôt qu'un scraping de Fusacq ou Alvo

Trois raisons, dans l'ordre d'importance.

1. **Le droit.** Les articles L342-1 et L342-2 du code de la propriété
   intellectuelle protègent le producteur d'une base contre l'extraction d'une
   partie substantielle, et contre l'extraction répétée de parties non
   substantielles qui nuirait à son exploitation normale. Les CGU de Passage
   interdisent d'ailleurs exactement cela chez elle, article 5.
2. **La qualité.** Fusacq et Alvo publient des prix *demandés* sur le marché
   visible. Le BODACC publie des prix *conclus*, sur l'ensemble du marché, y
   compris les cessions de gré à gré qui n'ont jamais été annoncées nulle part.
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
| `barometre.py` | Agrégation en médianes et quartiles, avec seuil de publication. |

```bash
python3 collecte.py 2025          # ~15 min, écrit data/bodacc-2025.jsonl
python3 barometre.py 0            # baromètre tout marché
python3 barometre.py 300000       # baromètre segment haut
```

## Ce que le prototype a mesuré sur 2025

- 47 758 annonces collectées, soit le compte exact renvoyé par l'API.
- **71 % portent un prix exploitable**, soit 33 696 transactions.
- Médiane nationale : **108 200 €**. Premier quartile 50 000 €, troisième 250 000 €.
- 7 052 transactions à 300 000 € ou plus, 3 635 à 500 000 €, 1 394 au-delà du million.
- Classifieur sectoriel : **85 % de couverture**, 12 familles.
- **134 croisements secteur x région** dépassent le seuil de 30 transactions.

## Règles de publication

- **Seuil de 30 transactions par cellule.** En dessous, aucune médiane n'est
  publiée : un chiffre calculé sur 8 ventes est de la fausse précision.
- **Les 15 % non classés ne disparaissent pas.** Ils sont exclus des moyennes
  sectorielles mais comptés dans le total national, et le taux de couverture
  doit être affiché sur la page.
- **Tout chiffre publié est daté et sourcé**, conformément à la règle standing.

## La réserve, et elle est sérieuse

Le BODACC « ventes et cessions » est massivement du **fonds de commerce**, pas
de la cession de titres de PME. Après correction du classifieur, l'hôtellerie
restauration pèse encore 11 210 transactions sur 33 696, et la médiane nationale
est à 108 200 €.

L'ICP de Passage, c'est la PME à 500 k€ - 5 M€ de chiffre d'affaires. **Ce n'est
pas le même marché.** Publier des centaines de pages sur le prix des fonds de
commerce enfoncerait le site dans le segment que la décision stratégique écarte
justement du commercial.

D'où le filtre à 300 000 € : il ramène l'échantillon à 7 052 transactions dont
la médiane monte à 500 000 €, et les 41 croisements publiables décrivent alors
un marché qui ressemble à celui de Passage.

## Limites connues

- Le prix du BODACC est le prix du **fonds ou des parts cédées**, pas une
  valeur d'entreprise retraitée. Il ne dit rien de la dette reprise ni de la
  trésorerie. À énoncer sur la page.
- La classification par mots-clés n'est pas une nomenclature NAF. Elle a été
  validée par contrôle manuel sur 14 annonces tirées au hasard, ce qui a révélé
  et corrigé une inversion d'ordre entre boulangerie et restauration. Pour
  fiabiliser, joindre le SIREN au NAF via `recherche-entreprises.api.gouv.fr`.
- 2026 est incomplet à la date de construction, 32 083 annonces au 16/09.

## Suite possible

1. Une page baromètre nationale, actualisée mensuellement.
2. Les croisements les plus demandés, en respectant le seuil de 30.
3. Republication du jeu agrégé en open data sur data.gouv.fr avec attribution à
   passage.ac. C'est là qu'est le vrai levier : reprendre.cc a publié son index
   BODACC sur data.gouv mais son sitemap ne compte que 20 URLs fonctionnelles et
   zéro page programmatique. La donnée est prise, la couche SEO est libre.
