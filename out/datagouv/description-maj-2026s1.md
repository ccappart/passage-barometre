Prix de cession réellement payés lors des ventes d'entreprises en France, agrégés par secteur d'activité et par région, à partir des annonces publiées au BODACC.

Ce jeu de données répond à une question que peu de sources traitent : combien se vend réellement une entreprise ? Le marché publie abondamment des méthodes de valorisation théoriques et des prix demandés. Ce baromètre publie des prix conclus.

## Correction du 18 septembre 2026, à lire avant réutilisation

Les deux millésimes ont été recalculés. Une cession dont le fonds compte plusieurs établissements est publiée au BODACC **une fois par greffe concerné, et chaque annonce porte le prix total de l'opération**. Sans dédoublonnage, une même vente à 4 millions d'euros répartie sur 9 sites entrait 9 fois dans les agrégats.

Les fichiers actuels sont dédoublonnés. Les valeurs diffèrent donc de la première version déposée les 17 et 18 septembre 2026 : le millésime 2025 passe de 1 258 à 1 076 cessions retenues et sa médiane de 500 000 à 480 000 euros. Toute reprise des chiffres antérieurs doit être mise à jour.

## Millésimes disponibles

**2026-S1**, premier semestre 2026. 22 444 annonces de vente dépouillées, 16 588 transactions dont le prix a pu être extrait, soit 74 %. Après application du périmètre et dédoublonnage, 888 cessions d'entreprises à 300 000 euros et plus, dont 593 hors santé et pharmacie. Prix médian : **480 111 euros**. Premier quartile 350 000 euros, troisième quartile 757 768 euros.

Le fichier semestriel contient également le **premier semestre 2025 recalculé à l'identique**, qui sert de base de comparaison : 579 cessions, médiane 481 000 euros.

**2025**, année pleine. 47 758 annonces dépouillées, 33 696 transactions valorisées, 7 177 cessions d'entreprises après périmètre, dont 1 880 à 300 000 euros et plus. Sur les 1 076 retenues hors santé, prix médian **480 000 euros**, premier quartile 353 000 euros, troisième quartile 779 453 euros.

## Ce que dit le premier semestre 2026 : rien ne bouge

La médiane nationale passe de 481 000 à 480 111 euros d'un premier semestre à l'autre, soit -0,2 %. Sur 18 évolutions sectorielles et régionales testées, **une seule ressort comme statistiquement distinguable du hasard d'échantillonnage**, et elle est à prendre avec prudence : tester 18 cellules à 95 % de confiance produit en moyenne une fausse détection.

Autrement dit : le marché de la cession d'entreprises est stable d'un semestre à l'autre. Les écarts sectoriels apparents s'expliquent par la taille des échantillons et non par un mouvement de marché.

C'est la raison d'être des colonnes d'intervalle de confiance de ce millésime.

## Règle de comparabilité

Un semestre ne se compare qu'au même semestre de l'année précédente. Comparer un semestre à une année pleine mélangerait un effet de saison avec un effet de marché : le taux d'extraction du prix varie de 87 % en janvier à 62 % en mai, et ce profil se reproduit d'une année sur l'autre.

## L'incertitude est publiée avec le chiffre

Chaque médiane est accompagnée de son intervalle de confiance à 95 %, obtenu par bootstrap sur 4 000 rééchantillonnages. Sur une cellule de 40 transactions, une médiane bouge de plusieurs dizaines de milliers d'euros par simple tirage. Publier le point sans son incertitude invite à lire du bruit comme une tendance.

Les lignes 2026-S1 portent en plus la variation face au même semestre 2025, l'intervalle de confiance de cette variation, et un indicateur de significativité. Une variation dont l'intervalle contient zéro est marquée « non ».

## Périmètre, et pourquoi il diffère des agrégations usuelles

Le commerce de proximité est exclu : hôtellerie et restauration, boulangerie et alimentation, commerce de détail, coiffure et esthétique. La valeur de ces fonds tient au bail et à l'emplacement, pas à une capacité bénéficiaire qui survivrait au départ de l'exploitant. Les agréger avec les autres produit une médiane nationale autour de 108 000 euros, exacte arithmétiquement mais qui ne décrit ni l'un ni l'autre marché.

La santé et la pharmacie figurent dans le détail sectoriel mais sont exclues de la médiane nationale et des agrégats régionaux : une officine se valorise sur une licence réglementée, et sa concentration géographique créait des écarts régionaux artificiels.

Aucune médiane n'est publiée pour une cellule comptant moins de 30 transactions. Ce seuil s'applique aussi au semestre, où les compteurs sont divisés par deux. Le dédoublonnage fait en outre sortir quelques cellules du périmètre publiable : le millésime 2025 compte 36 lignes au lieu de 40.

## Limite d'interprétation

Le prix publié au BODACC est celui du fonds ou des titres cédés. Ce n'est pas une valeur d'entreprise : il ne comprend ni la dette reprise, ni la trésorerie, ni le compte courant d'associé.

## Reproductibilité

Le code qui produit ces agrégats est public : https://github.com/ccappart/passage-barometre

Ce jeu ne contient que des agrégats, aucune annonce individuelle n'est redistribuée. Chaque transaction source reste consultable sur bodacc.fr.

Producteur : Passage Transmission, conseil en ingénierie de transmission d'entreprise. https://passagetransmission.fr/vendre/prix-de-cession
