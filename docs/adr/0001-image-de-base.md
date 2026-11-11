# ADR 0001 : Choix de l'image de base Docker

Date : 2026-11-11 (décision prise à la création du Dockerfile, ADR rédigé
après coup à partir de mesures)
Statut : Accepté, à réexaminer

## Contexte
L'API est écrite en Python 3.14 et tourne dans un conteneur. Il faut choisir
l'image de base. Critères : taille, nombre de failles connues (Trivy, gravité
HIGH et CRITICAL), compatibilité avec nos dépendances, possibilité
d'appliquer des correctifs de sécurité.

Mesures du 2026-11-11 :

| Image | Taille sur disque | Paquets système | Failles système |
|---|---|---|---|
| python:3.14 | 1,63 Go | 469 | 388 (373 HIGH, 15 CRITICAL) |
| python:3.14-slim | 181 Mo | 87 | 49 (HIGH) |
| python:3.14-alpine | 73,9 Mo | 30 | 0 |

Les 5 failles Python détectées (msgpack, setuptools, urllib3) sont
identiques pour les trois images : elles viennent de pip, que l'on supprime
de l'image finale (voir ADR 0004).

## Options envisagées
1. python:3.14 (complète) : 1,63 Go et 15 failles critiques. Contient des
   compilateurs et des outils inutiles à l'exécution.
2. python:3.14-slim : Debian allégée, 181 Mo, 49 failles dont seulement 2
   avaient un correctif disponible. Pas de compilateur.
3. python:3.14-alpine : la plus légère (73,9 Mo), aucune faille système
   détectée (Trivy a toutefois signalé que la détection pouvait y être moins
   précise). Test : pip install -r requirements.txt réussit, car psycopg-binary
   et pydantic-core ont des versions précompilées pour musl. Mais le
   Dockerfile devrait être adapté (apk au lieu d'apt-get, adduser au lieu de
   useradd) et l'application n'a pas été exécutée sur cette base.

## Décision
Nous choisissons python:3.14-slim pour l'instant, car :
- l'application est déjà testée et scannée en CI sur cette image ;
- apt permet d'appliquer des correctifs ciblés (c'est ce que fait le
  Dockerfile pour zlib1g) ;
- Debian (glibc) est l'environnement pour lequel les paquets Python
  précompilés sont le plus répandus.
Les mesures favorisent pourtant Alpine : la décision est à réexaminer par un
test sur une branche dédiée.

## Conséquences
Positives :
- Image environ 9 fois plus légère que l'image complète.
- Aucune faille critique ; les 49 failles HIGH sont documentées (ADR 0004).
- Aucune modification du Dockerfile nécessaire.

Négatives :
- Image environ 2,4 fois plus lourde qu'Alpine, avec 49 failles système
  détectées contre 0.
- Les mesures donnent l'avantage à Alpine (taille, 0 faille système
  détectée) : en gardant slim, on accepte un écart de taille et de failles
  tant que le test sur Alpine n'est pas fait. Le 0 faille d'Alpine est lui-même
  à confirmer, car Trivy signale une détection moins précise sur cette image.
- Le tag python:3.14-slim n'est pas figé : deux builds à des dates
  différentes peuvent produire des images différentes.

## Suivi
Tester Alpine sur une branche : adapter le Dockerfile, vérifier les tests, le
démarrage de la stack et les scans en CI, puis comparer.
