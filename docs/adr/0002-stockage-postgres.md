# ADR 0002 : Stockage des URLs dans Postgres

Date : 2026-11-05
Statut : Accepté

## Contexte
L'API stockait les URLs raccourcies dans un dictionnaire Python en mémoire.
Deux problèmes :
- Les données sont perdues à chaque redémarrage du conteneur.
- Si on lance plusieurs instances de l'API, chacune a ses propres données :
  un lien créé sur l'une est introuvable sur l'autre.

Il faut donc séparer l'application (sans état) de ses données.

## Options envisagées
1. Dictionnaire en mémoire : trivial, mais données perdues au redémarrage
   et non partageables entre instances.
2. SQLite : simple et persistant, mais c'est un fichier local, qui ne se
   partage pas proprement entre plusieurs conteneurs.
3. Postgres : persistant, partageable entre instances, standard du marché,
   bien outillé dans le cloud, mais c'est un service de plus à exploiter.
4. Base NoSQL (type DynamoDB) : très scalable pour des accès par clé, mais
   plus de choses à apprendre et lié à un fournisseur cloud.

## Décision
Nous choisissons Postgres, car il règle les deux problèmes (persistance et
partage entre instances) avec une technologie standard et portable.

## Conséquences
Positives :
- Les données survivent aux redémarrages et aux déploiements.
- On peut faire tourner plusieurs instances de l'API en parallèle.
- Les services managés existent chez tous les fournisseurs cloud.

Négatives :
- Une base à exploiter : sauvegardes, mises à jour, supervision.
- L'API dépend du réseau et de la disponibilité de la base.
- Les tests et la CI ont besoin d'une base Postgres.
- Un coût supplémentaire dans le cloud.
- La base est un point de défaillance unique : si elle tombe, l'API ne peut
  plus ni créer ni rediriger de liens. Les données restent intactes, mais
  le service est indisponible jusqu'au retour de la base.

## Pistes pour limiter ce risque (à traiter plus tard)
- Un cache Redis pour servir les redirections même si la base est lente.
- Une base managée avec réplica et bascule automatique dans le cloud.
- Des sauvegardes régulières, testées par une restauration réelle.
