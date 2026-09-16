# Format des skills Jarvis

Un skill = un dossier avec un `SKILL.md` (obligatoire) et, si besoin, des
fichiers annexes (scripts, templates, données de référence). Le format
reprend volontairement la convention des *Skills* de Claude : c'est un
mécanisme éprouvé, et ça permet à Alexis de porter un skill écrit pour
Jarvis vers Claude (et vice-versa) sans réécrire le fond.

```
skills/
└── mon-skill/
    ├── SKILL.md          # obligatoire
    └── ressources/        # optionnel : scripts, templates, données
```

## `SKILL.md`

```markdown
---
name: mon-skill
description: Une phrase — quand Jarvis doit s'en servir. C'est la SEULE
  partie chargée en permanence dans le prompt système (cf. progressive
  disclosure ci-dessous), donc elle doit donner assez de contexte pour
  que Jarvis sache quand la déclencher.
tags: [linkedin, contenu]
---

# Instructions

Le corps du fichier : la procédure complète, étape par étape, que Jarvis
doit suivre une fois le skill chargé. Peut référencer les fichiers du
dossier `ressources/`.
```

## Progressive disclosure (pourquoi deux niveaux)

Charger le corps complet de tous les skills dans chaque prompt système
serait ruineux en tokens dès qu'il y en a plus de quelques-uns. Jarvis
applique donc le même principe que Claude :

1. **Toujours en mémoire** : le nom + la description de chaque skill
   (`app/core/skills/registry.py` construit cet index au démarrage).
2. **Chargé à la demande** : le corps complet, uniquement quand l'agent
   décide qu'un skill s'applique et appelle l'outil `load_skill(name)`
   (`app/core/skills/loader.py`).

## Trois façons de remplir ce dossier

- **À la main** : écrire un `SKILL.md` directement (cf. `example-linkedin-post/`).
- **Depuis une tâche réussie** : `app/core/skills/generator.py` prend la
  description d'une tâche qu'Alexis vient de faire faire à Jarvis et en
  déduit un brouillon de `SKILL.md` — à relire et corriger avant de garder.
- **Import** : le format étant un simple dossier texte, importer un skill
  écrit ailleurs (ou exporté d'une autre instance de Jarvis) revient à
  copier son dossier ici.
