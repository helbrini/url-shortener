# ADR 0005 : Terraform pour l'infrastructure et état distant

Date : 2026-11-11

Statut : Accepté (état distant à mettre en place avec le compte Azure)

## Contexte
Le projet doit pouvoir créer son infrastructure Azure de façon reproductible
(groupe de ressources, réseau, environnement Container Apps). Constats faits
en pratiquant :
- Terraform compare un état voulu (le code) à un état connu (le fichier d'état) :
  un terraform destroy lancé deux fois ne fait rien la seconde fois.
- Un plan peut être sauvegardé puis appliqué tel quel (-out), ce qui sépare
  ce qui est validé de ce qui est exécuté.
- Le fichier d'état stocke les valeurs sensibles en clair, même pour une
  variable déclarée sensitive (par exemple l'URL de connexion à la base).
- Un état local ne peut pas être partagé en équipe sans conflit.
- Terraform est indépendant du cloud et très répandu : les compétences et les
  modules restent réutilisables si le projet change de fournisseur.

## Options envisagées
1. Console Azure à la main : rapide pour tester, mais non reproductible, non
   relu, non versionné.
2. Scripts avec l'outil az : reproductibles et versionnables, mais
   impératifs : nécessitent de gérer soi-même l'idempotence et la détection
   d'état (vérifications systématiques pour éviter les erreurs lors de
   réexécutions).
3. Terraform : déclaratif, plan relisible, état qui mémorise l'existant.
4. Bicep (outil propre à Azure) : déclaratif, sans fichier d'état à gérer
   (avantage face à Terraform), mais limité à l'écosystème Azure. Évalué sur
   documentation, non pratiqué.

## Décision
Nous choisissons Terraform avec un état distant dans un compte de stockage
Azure, car il permet une gestion déclarative robuste, le verrouillage de
l'état pour le travail en équipe et la réutilisabilité de compétences et de
modules indépendants du cloud.

## Conséquences
Positives :
- Infrastructure versionnée, relue en pull request et validée par la CI.
- Plan relisible avant toute modification.
- État partagé et verrouillé : deux personnes ne peuvent pas appliquer en
  même temps.

Négatives :
- Risque de fuite de secrets stockés en clair dans le fichier `.tfstate`,
  exigeant un contrôle d'accès RBAC très strict sur le conteneur du compte de
  stockage.
- Le stockage de l'état doit exister avant le reste : il faut le créer
  séparément, à la main ou par un petit Terraform dédié.
- Dérive : une modification manuelle dans la console Azure est détectée au
  prochain plan et annulée par Terraform. Toute modification doit donc passer
  par le code.
- Valider ne suffit pas : seul un plan avec un vrai compte détecte les
  erreurs propres à Azure (nom déjà pris, droit manquant).

## Suivi
Créer le compte de stockage de l'état et ajouter le bloc backend azurerm
quand l'accès Azure sera disponible, puis vérifier les droits RBAC sur le
conteneur.
