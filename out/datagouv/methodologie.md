# Méthodologie du baromètre des prix de cession d'entreprises

Document joint au jeu de données. Version 3, millésimes 2025 (année pleine) et 2026-S1, établie le 18 septembre 2026.

## Source

Annonces de ventes et cessions publiées au Bulletin officiel des annonces civiles et commerciales (BODACC), jeu `annonces-commerciales` de la Direction de l'information légale et administrative, sous Licence Ouverte. Périmètre : `familleavis = "vente"`.

Volumes source : 47 758 annonces publiées en 2025, 22 444 sur le premier semestre 2026, 22 937 sur le premier semestre 2025. Le flux annuel est stable depuis 2022 (48 919 en 2022, 47 862 en 2023, 47 700 en 2024).

La période d'une ligne est celle de la **date de parution** de l'annonce, pas celle de la signature de l'acte. Les deux diffèrent de quelques semaines, mais l'écart joue de la même façon d'un millésime à l'autre.

## Extraction du prix

Le BODACC ne comporte pas de champ dédié au prix. Celui-ci figure dans le texte libre décrivant l'origine du fonds, sous des formulations qui varient selon les greffes : « au prix stipulé de », « moyennant le prix de », « au prix de ».

Cinq motifs d'extraction sont appliqués, couvrant les écritures rencontrées (40.000,00 EUR, 40 000 euros, 40000.00, 1 250 000 €). Les montants inférieurs à 500 € et supérieurs à 500 000 000 € sont écartés comme aberrants ou symboliques.

Taux d'extraction : **71 % sur 2025**, **74 % sur le premier semestre 2026**, 75 % sur le premier semestre 2025.

Ce taux suit un profil saisonnier marqué et reproductible : 87 % en janvier 2025 et 84 % en janvier 2026, 65 % en mai 2025 et 62 % en mai 2026. C'est une raison de plus de ne comparer qu'à période identique.

## Dédoublonnage

Une cession dont le fonds compte plusieurs établissements est publiée **une fois par greffe concerné, et chaque annonce porte le prix total de l'opération**. Sans correction, une vente à 4 millions d'euros répartie sur 9 sites entre 9 fois dans les agrégats, avec 9 fois 4 millions d'euros.

Clé de dédoublonnage : identifiant SIREN de l'annonce et prix exact, dans une fenêtre de 60 jours. Deux annonces qui partagent l'acquéreur et le montant à l'euro près, à moins de deux mois d'intervalle, décrivent la même opération.

Vérification sur le premier semestre 2026 : 92 groupes concernés, dont 88 % étalés sur 30 jours ou moins, ce qui est la signature d'une publication multi-greffes et non de deux ventes distinctes.

Le résultat ne dépend pas du réglage. Avec une fenêtre de 30, 60, 90 jours ou sans limite, la médiane 2025 tombe à 480 000 € dans les quatre cas, et le nombre de transactions varie de moins de 2 %. La fenêtre de 60 jours est retenue parce qu'elle est la plus conservatrice des quatre.

Effet mesuré : le millésime 2025 passe de 1 258 à 1 076 cessions retenues et sa médiane de 500 000 à 480 000 €. L'effet sur les médianes est modéré, celui sur les comptages et les valeurs agrégées est massif : la valeur échangée du premier semestre 2026 tombe de 969 à 749 millions d'euros.

Cette correction a été appliquée le 18 septembre 2026, après la première publication du jeu. Les chiffres antérieurs sont caducs.

## Classification sectorielle

Le BODACC ne porte pas de code NAF. La classification s'appuie sur la description d'activité rédigée par le greffe, via un jeu de règles par mots-clés organisé du plus spécifique au plus général.

Taux de couverture : **85 %**. Les annonces non classées sont exclues des agrégats sectoriels mais comptées dans les totaux.

Cette classification n'est pas une nomenclature officielle. Pour la fiabiliser, une jointure du numéro SIREN vers le code NAF via l'API Recherche d'entreprises est possible et documentée dans le dépôt.

## Périmètre retenu, et pourquoi il diffère des agrégations usuelles

C'est le choix structurant de ce baromètre.

**Le commerce de proximité est exclu** : hôtellerie et restauration, boulangerie et alimentation, commerce de détail, coiffure et esthétique.

La valeur de ces fonds tient au bail, à l'emplacement et au pas-de-porte, pas à une capacité bénéficiaire qui survivrait au départ de l'exploitant. Économiquement, ces opérations relèvent davantage d'une transaction immobilière que d'une cession d'entreprise. Les agréger avec les autres produit une médiane nationale autour de 108 000 €, arithmétiquement exacte mais qui ne décrit ni l'un ni l'autre marché.

**La santé et la pharmacie** figurent dans le détail sectoriel mais sont exclues de la médiane nationale et des agrégats régionaux. Une officine se valorise sur une licence et un chiffre d'affaires réglementés, sans équivalent dans les autres secteurs, et sa concentration géographique inégale créait des écarts régionaux artificiels.

## Seuil de publication

Aucune médiane n'est publiée pour une cellule comptant moins de **30 transactions**. Un quartile calculé sur 8 ventes est de la fausse précision.

Ce seuil mord davantage sur un semestre : les compteurs y sont divisés par deux. Le dédoublonnage fait sortir quelques cellules supplémentaires : le millésime 2025 publie 36 lignes au lieu de 40, et le Centre-Val de Loire n'y figure plus. Une évolution n'est calculée que lorsque les deux semestres franchissent le seuil.

## Incertitude, ajoutée en version 2

Chaque médiane publiée est accompagnée de son intervalle de confiance à 95 %, obtenu par **bootstrap non paramétrique, 4 000 rééchantillonnages avec remise** (graine fixée à 20260918, donc reproductible).

Pour les évolutions, c'est l'écart lui-même qui est rééchantillonné : l'intervalle porte sur la variation en pourcentage de la médiane entre les deux semestres. La colonne `variation_significative` vaut « oui » lorsque cet intervalle ne contient pas zéro.

Avertissement sur les comparaisons multiples : 18 évolutions sont testées. À 95 % de confiance, en l'absence de tout mouvement réel, une détection positive est attendue en moyenne par pur hasard. Une seule cellule ressort effectivement, ce qui est exactement le nombre attendu sous l'hypothèse de stabilité. Aucun mouvement de marché ne peut donc être affirmé sur ce semestre.

## Limite d'interprétation

Le prix publié au BODACC est le prix du fonds de commerce ou des titres cédés. **Ce n'est pas une valeur d'entreprise.** Il ne comprend ni la dette reprise, ni la trésorerie laissée dans la société, ni le compte courant d'associé. Deux cessions affichées au même prix peuvent recouvrir deux valeurs d'entreprise très différentes.

## Reproductibilité

Le code qui produit ces agrégats est public et réutilisable : https://github.com/ccappart/passage-barometre

Chaque transaction source reste consultable individuellement sur bodacc.fr. Ce jeu ne contient que des agrégats : aucune annonce individuelle n'est redistribuée.

## Producteur

Passage Transmission, conseil en ingénierie de transmission d'entreprise. https://passagetransmission.fr
