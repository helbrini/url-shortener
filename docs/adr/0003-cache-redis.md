# ADR 0003 : Cache Redis pour les redirections

Date : 2026-11-05
Statut : Accepté

## Contexte
Chaque redirection interroge Postgres. C'est plus lent qu'une lecture en
mémoire, cela charge la base à chaque clic, et si Postgres tombe (voir
ADR 0002), plus aucun lien ne fonctionne. Un cache permet de servir un lien
déjà consulté sans solliciter Postgres, tant que Redis est disponible et que
l'entrée n'a pas expiré (durée de vie d'une heure).

## Options envisagées
1. Pas de cache : simple, mais toute la charge de lecture va sur Postgres.
2. Cache en mémoire dans l'API : rapide, mais chaque instance a son propre
   cache, incohérent entre instances.
3. Redis : cache partagé entre instances, très rapide, expiration
   automatique, mais un service de plus à exploiter.

## Décision
Nous choisissons Redis avec le schéma cache-aside, principalement parce que
le cache est partagé entre toutes les instances de l'API.

## Conséquences
Positives :
- Redirections plus rapides pour les liens déjà consultés.
- Moins de charge sur Postgres.
- Les liens récemment utilisés continuent de fonctionner si Postgres tombe.

Négatives :
- Cohérence : si un lien est modifié ou supprimé en base alors qu'il est
  encore en cache, l'utilisateur continue d'être redirigé vers l'ancienne
  URL jusqu'à l'expiration (1 heure). Sans impact aujourd'hui, car les liens
  ne changent jamais, mais il faudra invalider le cache si on ajoute la
  modification ou la suppression.
- Un service de plus à exploiter et superviser.
- Si Redis tombe, l'API se rabat sur Postgres : plus lent, mais le
  service continue (testé en arrêtant le conteneur Redis).