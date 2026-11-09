# ADR 0004 : Durcissement de l'image Docker et politique de scan

Date : 2026-11-09
Statut : Accepté

## Contexte
Un premier scan Trivy de l'image a signalé 49 failles de gravité HIGH ou
CRITICAL sur le système Debian, et 5 sur des paquets Python. Après analyse :
- Seules 2 des 49 failles Debian avaient un correctif disponible (paquet
  zlib1g). Les 47 autres n'en ont pas, on ne peut donc pas les corriger.
- Les 5 failles Python (msgpack, urllib3) venaient de copies embarquées dans
  pip, jamais utilisées par l'API.
- pip-audit ne trouvait aucune faille dans les dépendances de l'application.
Il faut décider ce qui doit bloquer la CI, sans la faire échouer en
permanence pour des failles qu'on ne peut pas corriger.

## Options envisagées
1. Ne pas scanner : simple, mais on ignore les failles connues.
2. Bloquer sur toute faille détectée : très strict, mais la CI serait
   rouge en permanence à cause des failles sans correctif.
3. Bloquer seulement sur les failles HIGH ou CRITICAL qui ont un correctif,
   et durcir l'image pour réduire la surface d'attaque.

## Décision
Nous choisissons l'option 3 :
- mettre à jour zlib1g dans l'image ;
- supprimer pip de l'image finale (un conteneur n'a pas besoin d'installer
  des paquets une fois construit) ;
- séparer requirements.txt (production) et requirements-dev.txt (tests),
  pour que l'image n'embarque pas pytest ni httpx ;
- exécuter pip-audit et Trivy (avec --ignore-unfixed) dans la CI, et rendre
  ces contrôles obligatoires avant toute fusion.

## Conséquences
Positives :
- L'image contient moins de paquets, donc moins de failles possibles.
- Une faille grave et corrigeable bloque la fusion automatiquement.
- La CI reste utilisable : elle ne s'arrête pas pour des failles sans
  correctif.

Négatives :
- Risque résiduel : ne bloquer que les failles HIGH ou CRITICAL avec
  correctif disponible signifie qu'une faille grave sans correctif peut
  rester dans l'image déployée. Ce risque est accepté, mais il impose un
  suivi : relancer régulièrement Trivy sans l'option --ignore-unfixed pour
  réévaluer ces failles (par exemple une fois par mois).
- Les builds dépendent de ce que Debian publie le jour du build : deux
  builds du même code peuvent donner des images différentes.
- On ne peut plus faire pip install dans un conteneur en marche : il faut
  reconstruire l'image.
- Seules les dépendances directes sont épinglées ; leurs propres
  dépendances peuvent changer d'un build à l'autre.
- La ligne qui met à jour zlib1g deviendra inutile quand l'image de base
  sera republiée avec le correctif : il faudra penser à la retirer.
