# À publier sur data.gouv.fr : jeu ligne à ligne

Préparé le 2026-09-19. Je ne peux pas téléverser à ta place (ça demande ta clé
API), donc voici exactement quoi remplir.

## 1. Créer le jeu de données

Organisation : **Passage Transmission**
Titre : **Cessions d'entreprises au BODACC, ligne à ligne, avec prix et secteur**
Licence : **Licence Ouverte / Open Licence 2.0** (la même que le baromètre)
Couverture temporelle : 2025-01-01 au 2026-06-30
Couverture spatiale : France
Mots-clés : cession, transmission, entreprise, bodacc, prix, pme, fonds-de-commerce

Description : copier-coller **le contenu de `description-lignes.md`**, tel quel.

> IMPORTANT : c'est la DESCRIPTION qui rend le lien cliquable vers
> passagetransmission.fr. Vérifié le 2026-09-19 : les pages d'organisation
> n'affichent aucun lien, même quand le champ `url` de l'organisation est
> rempli. Si le lien ne figure pas dans la description, il n'existe nulle part.

## 2. Ajouter les 2 ressources

| Fichier | Titre à saisir | Format |
|---|---|---|
| `cessions-bodacc-lignes.csv` (19 Mo) | Cessions BODACC ligne à ligne, 2025 et 2026-S1 (CSV) | csv |
| `methodologie-lignes.txt` | Méthodologie : extraction du prix, classification, limites | txt |

Une version compressée `cessions-bodacc-lignes.csv.gz` (4,1 Mo) est fournie si
le téléversement de 19 Mo pose problème. Préférer le CSV non compressé :
data.gouv en fait une prévisualisation et une API, pas sur un .gz.

## 3. Après publication, à vérifier

Ouvrir la page du jeu et contrôler que le lien est bien suivi :

    curl -s <url-de-la-page> | grep -o '<a href="https://passagetransmission.fr[^"]*"[^>]*>'

Le résultat doit montrer la balise SANS attribut `rel`. Avec un `rel="nofollow"`,
le lien ne transmet rien et il faudra le dire.

## 4. Ce que ça vaut, sans exagérer

Ce sera le 2e lien suivi depuis data.gouv.fr. Google consolide très largement
la valeur des liens par domaine référent : ce 2e lien n'apportera quasiment
pas d'autorité de plus que le premier.

L'intérêt réel est ailleurs. Un jeu de 70 202 lignes exploitables est
citable par des journalistes, des chercheurs et des réutilisateurs, et ce sont
ces citations, depuis des domaines DIFFÉRENTS, qui font bouger l'autorité.
data.gouv.fr expose d'ailleurs les réutilisations d'un jeu de données, ce qui
donne un canal de suivi.
