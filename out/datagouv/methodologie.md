# Méthodologie du baromètre des prix de cession d'entreprises

Document joint au jeu de données. Version 1, millésime 2025, établi le 16 septembre 2026.

## Source

Annonces de ventes et cessions publiées au Bulletin officiel des annonces civiles et commerciales (BODACC), jeu `annonces-commerciales` de la Direction de l'information légale et administrative, sous Licence Ouverte. Périmètre : `familleavis = "vente"`.

Volume source : 47 758 annonces publiées en 2025. Le BODACC compte 891 234 annonces de ventes et cessions depuis l'origine, avec un flux annuel stable (48 919 en 2022, 47 862 en 2023, 47 700 en 2024).

## Extraction du prix

Le BODACC ne comporte pas de champ dédié au prix. Celui-ci figure dans le texte libre décrivant l'origine du fonds, sous des formulations qui varient selon les greffes : « au prix stipulé de », « moyennant le prix de », « au prix de ».

Cinq motifs d'extraction sont appliqués, couvrant les écritures rencontrées (40.000,00 EUR, 40 000 euros, 40000.00, 1 250 000 €). Les montants inférieurs à 500 € et supérieurs à 500 000 000 € sont écartés comme aberrants ou symboliques.

**Taux d'extraction : 71 %**, soit 33 696 transactions valorisées sur 47 758 annonces.

## Classification sectorielle

Le BODACC ne porte pas de code NAF. La classification s'appuie sur la description d'activité rédigée par le greffe, via un jeu de règles par mots-clés organisé du plus spécifique au plus général.

**Taux de couverture : 85 %.** Les annonces non classées sont exclues des agrégats sectoriels mais comptées dans les totaux.

Cette classification n'est pas une nomenclature officielle. Pour la fiabiliser, une jointure du numéro SIREN vers le code NAF via l'API Recherche d'entreprises est possible et documentée dans le dépôt.

## Périmètre retenu, et pourquoi il diffère des agrégations usuelles

C'est le choix structurant de ce baromètre.

**Le commerce de proximité est exclu** : hôtellerie et restauration, boulangerie et alimentation, commerce de détail, coiffure et esthétique.

La valeur de ces fonds tient au bail, à l'emplacement et au pas-de-porte, pas à une capacité bénéficiaire qui survivrait au départ de l'exploitant. Économiquement, ces opérations relèvent davantage d'une transaction immobilière que d'une cession d'entreprise. Les agréger avec les autres produit une médiane nationale autour de 108 000 €, arithmétiquement exacte mais qui ne décrit ni l'un ni l'autre marché.

Après application, 7 890 cessions d'entreprises subsistent, dont 2 126 à 300 000 € et plus.

**La santé et la pharmacie** figurent dans le détail sectoriel mais sont exclues de la médiane nationale et des agrégats régionaux. Une officine se valorise sur une licence et un chiffre d'affaires réglementés, sans équivalent dans les autres secteurs, et sa concentration géographique inégale créait des écarts régionaux artificiels.

## Seuil de publication

Aucune médiane n'est publiée pour une cellule comptant moins de **30 transactions**. Un quartile calculé sur 8 ventes est de la fausse précision.

## Limite d'interprétation

Le prix publié au BODACC est le prix du fonds de commerce ou des titres cédés. **Ce n'est pas une valeur d'entreprise.** Il ne comprend ni la dette reprise, ni la trésorerie laissée dans la société, ni le compte courant d'associé. Deux cessions affichées au même prix peuvent recouvrir deux valeurs d'entreprise très différentes.

## Reproductibilité

Le code qui produit ces agrégats est public et réutilisable : https://github.com/ccappart/passage-barometre

Chaque transaction source reste consultable individuellement sur bodacc.fr. Ce jeu ne contient que des agrégats : aucune annonce individuelle n'est redistribuée.

## Producteur

Passage Transmission, cabinet de conseil en cession et reprise de PME. https://passage.ac
