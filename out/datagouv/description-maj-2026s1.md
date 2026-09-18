Prix de cession réellement payés lors des ventes d'entreprises en France, agrégés par secteur d'activité et par région, à partir des annonces publiées au BODACC.

Ce jeu de données répond à une question que peu de sources traitent : combien se vend réellement une entreprise ? Le marché publie abondamment des méthodes de valorisation théoriques et des prix demandés. Ce baromètre publie des prix conclus.

## Millésimes disponibles

**2026-S1**, publié le 18 septembre 2026. 22 444 annonces dépouillées, 16 588 transactions dont le prix a pu être extrait, soit 74 %. Après application du périmètre, 676 cessions d'entreprises à 300 000 euros et plus, hors santé et pharmacie. Prix médian : **495 000 euros**. Premier quartile 360 000 euros, troisième quartile 849 709 euros.

Le fichier semestriel contient également le **premier semestre 2025 recalculé à l'identique**, qui sert de base de comparaison.

**2025**, année pleine, publié le 17 septembre 2026. 47 758 annonces dépouillées, 33 696 transactions valorisées, 1 258 cessions retenues, prix médian 500 000 euros.

## Ce que dit le premier semestre 2026 : rien ne bouge

La médiane nationale passe de 500 000 à 495 000 euros, soit -1 %. Le premier quartile est inchangé à 360 000 euros. Sur 18 évolutions sectorielles et régionales testées, **une seule ressort comme statistiquement distinguable du hasard d'échantillonnage**, et elle est à prendre avec prudence : tester 18 cellules à 95 % de confiance produit en moyenne une fausse détection.

Autrement dit : le marché de la cession d'entreprises est stable d'un semestre à l'autre. Les écarts sectoriels apparents, jusqu'à +38 % ou -46 % sur certaines cellules, s'expliquent par la taille des échantillons et non par un mouvement de marché.

C'est la raison d'être des colonnes d'intervalle de confiance ajoutées dans ce millésime.

## Règle de comparabilité

Un semestre ne se compare qu'au même semestre de l'année précédente. Comparer un semestre à une année pleine mélangerait un effet de saison avec un effet de marché : le taux d'extraction du prix varie de 87 % en janvier à 62 % en mai, et ce profil se reproduit d'une année sur l'autre.

## Nouveauté du millésime 2026-S1 : l'incertitude est publiée

Chaque médiane est désormais accompagnée de son intervalle de confiance à 95 %, obtenu par bootstrap sur 4 000 rééchantillonnages. Sur une cellule de 40 transactions, une médiane bouge de plusieurs dizaines de milliers d'euros par simple tirage. Publier le point sans son incertitude invite à lire du bruit comme une tendance.

Les lignes 2026-S1 portent en plus la variation face au même semestre 2025 et un indicateur de significativité. Une variation dont l'intervalle contient zéro est marquée « non ».

## Périmètre, et pourquoi il diffère des agrégations usuelles

Le commerce de proximité est exclu : hôtellerie et restauration, boulangerie et alimentation, commerce de détail, coiffure et esthétique. La valeur de ces fonds tient au bail et à l'emplacement, pas à une capacité bénéficiaire qui survivrait au départ de l'exploitant. Les agréger avec les autres produit une médiane nationale autour de 108 000 euros, exacte arithmétiquement mais qui ne décrit ni l'un ni l'autre marché.

La santé et la pharmacie figurent dans le détail sectoriel mais sont exclues de la médiane nationale et des agrégats régionaux : une officine se valorise sur une licence réglementée, et sa concentration géographique créait des écarts régionaux artificiels.

Aucune médiane n'est publiée pour une cellule comptant moins de 30 transactions. Ce seuil s'applique aussi au semestre : sur une demi-année, les compteurs sont divisés par deux et trois régions sortent du périmètre publiable sur le premier semestre 2025.

## Limite d'interprétation

Le prix publié au BODACC est celui du fonds ou des titres cédés. Ce n'est pas une valeur d'entreprise : il ne comprend ni la dette reprise, ni la trésorerie, ni le compte courant d'associé.

## Reproductibilité

Le code qui produit ces agrégats est public : https://github.com/ccappart/passage-barometre

Ce jeu ne contient que des agrégats, aucune annonce individuelle n'est redistribuée. Chaque transaction source reste consultable sur bodacc.fr.

Producteur : Passage Transmission, conseil en ingénierie de transmission d'entreprise. https://passagetransmission.fr/vendre/prix-de-cession
