# Publication sur data.gouv.fr : tout est prêt, à toi de jouer

Je ne peux pas publier à ta place : le connecteur data.gouv.fr dont je dispose est en lecture seule, et la publication exige la clé API de ton compte. Voici le dossier complet, il te reste 5 minutes de saisie.

**Où aller :** https://www.data.gouv.fr/admin/datasets/new/

---

## 1. Titre

```
Baromètre des prix de cession d'entreprises en France
```

## 2. Description, à coller telle quelle

```markdown
Prix de cession réellement payés lors des ventes d'entreprises en France, agrégés par secteur d'activité et par région, à partir des annonces publiées au BODACC.

Ce jeu de données répond à une question que peu de sources traitent : combien se vend réellement une entreprise ? Le marché publie abondamment des méthodes de valorisation théoriques et des prix demandés. Ce baromètre publie des prix conclus.

## Millésime 2025

- 47 758 annonces de ventes et cessions dépouillées
- 33 696 transactions dont le prix a pu être extrait, soit 71 %
- Prix médian publié : **500 000 €** sur 1 258 cessions d'entreprises à 300 000 € et plus
- Premier quartile 360 000 €, troisième quartile 850 000 €

## Périmètre, et pourquoi il diffère des agrégations usuelles

Le commerce de proximité est exclu : hôtellerie et restauration, boulangerie et alimentation, commerce de détail, coiffure et esthétique. La valeur de ces fonds tient au bail et à l'emplacement, pas à une capacité bénéficiaire qui survivrait au départ de l'exploitant. Les agréger avec les autres produit une médiane nationale autour de 108 000 €, exacte arithmétiquement mais qui ne décrit ni l'un ni l'autre marché.

La santé et la pharmacie figurent dans le détail sectoriel mais sont exclues de la médiane nationale et des agrégats régionaux : une officine se valorise sur une licence réglementée, et sa concentration géographique créait des écarts régionaux artificiels.

Aucune médiane n'est publiée pour une cellule comptant moins de 30 transactions.

## Contenu

40 lignes agrégées : 1 médiane nationale, 8 secteurs, 12 régions, 19 croisements secteur et région. Chaque ligne porte le nombre de cessions, le prix médian et les deux quartiles.

## Limite d'interprétation

Le prix publié au BODACC est celui du fonds ou des titres cédés. Ce n'est pas une valeur d'entreprise : il ne comprend ni la dette reprise, ni la trésorerie, ni le compte courant d'associé.

## Reproductibilité

Le code qui produit ces agrégats est public : https://github.com/ccappart/passage-barometre

Ce jeu ne contient que des agrégats, aucune annonce individuelle n'est redistribuée. Chaque transaction source reste consultable sur bodacc.fr.

Producteur : Passage Transmission, conseil en cession et reprise de PME. https://passage.ac/vendre/prix-de-cession
```

## 3. Métadonnées

| Champ | Valeur |
|---|---|
| Licence | Licence Ouverte 2.0 (`lov2`) |
| Fréquence de mise à jour | Annuelle |
| Couverture temporelle | 01/01/2025 au 31/12/2025 |
| Couverture spatiale | France |
| Tags | `bodacc`, `cession-entreprise`, `prix`, `valorisation`, `pme`, `transmission-entreprise`, `fonds-de-commerce`, `open-data` |

## 4. Fichiers à téléverser

Les deux sont dans `~/passage-barometre/out/datagouv/` :

1. **`barometre-cessions-entreprises-2025.csv`** : le jeu agrégé, 40 lignes.
   Intitulé : `Baromètre des prix de cession, millésime 2025 (CSV)`
2. **`methodologie.md`** : la méthode complète, en type « documentation ».
   Intitulé : `Méthodologie : extraction, classification, périmètre et limites`

Ajoute aussi 2 liens en ressources de type `documentation` :
- `https://github.com/ccappart/passage-barometre` sous l'intitulé `Code source du pipeline`
- `https://passage.ac/vendre/prix-de-cession` sous l'intitulé `Baromètre commenté`

---

## Deux décisions à prendre

**Sous quelle identité publier.** Un compte personnel, ou une organisation « Passage Transmission » que tu crées sur data.gouv.fr. L'organisation est plus crédible, elle donne une page dédiée et elle est réutilisable pour de futurs jeux. Elle demande 5 minutes de plus.

**Ce que tu acceptes de rendre public.** Rien ici n'est sensible : ce sont des agrégats de données déjà publiques, et le code est déjà ouvert. Mais tu publies sous ton nom une méthode qui assume un écart avec les chiffres du marché, et tu devras pouvoir la défendre. C'est précisément ce qui fait sa valeur.

## Après la publication

Ajoute le lien du jeu dans la section « Méthode et sources » de la page `/vendre/prix-de-cession`, et dans le README du dépôt. La boucle est alors fermée : la page cite le jeu, le jeu cite la page, le code prouve les deux.
