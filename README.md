# Roguelike Terminal

Un jeu de type roguelike en Python jouable dans le terminal, 
développé dans le cadre d'un projet de 2e année de classe préparatoire.

## Fonctionnalités

- Héros avec système d'XP, niveaux et statistiques évolutives
- Inventaire limité à 10 équipements
- 4 sorts : téléportation, soin, invisibilité, amélioration d'armure
- Monstres variés : Goblin, Bat, Ghost, Ork, Blob, Dragon
- Monstres rapides (2 actions par tour) et monstres invisibles
- Pièges cachés sur le sol
- Déplacements en 8 directions (ZQSD + diagonales)
- Génération procédurale des salles et du donjon

## Contrôles

| Touche | Action |
|--------|--------|
| Z / Q / S / D | Déplacement (haut/gauche/bas/droite) |
| A / E / W / C | Déplacement en diagonale |
| U | Utiliser un équipement |
| R | Supprimer un équipement |
| I | Afficher la description complète du héros |
| H | Afficher les actions disponibles |
| K | Se suicider |

## Lancement

```bash
python projet.py
```

## Technologies

- Python 3
- Bibliothèque standard uniquement (`random`, `math`, `copy`)
