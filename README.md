# Projet Technique GM-6 — Réseaux de Petri
Vérification formelle d'applications critiques avec Réseaux de Petri

**Résumé**
- **Objectif**: Modéliser et vérifier formellement des scénarios critiques à l'aide de réseaux de Petri, simuler des exécutions et effectuer des analyses (accessibilité, deadlocks, bornitude, vivacité, invariants).
- **Contenu principal**: deux implémentations Python (un participant / deux participants) et un rapport de projet détaillé.

**Structure du dépôt**
- **Fichiers de code**:
	- [Reseaux de Petri - un seul participant.py](Reseaux%20de%20Petri%20-%20un%20seul%20participant.py): modèle et analyses pour un participant (simulation, exploration de l'espace d'états, détection de deadlocks, bornitude, vivacité, invariants).
	- [Reseux de Petri - 2 participants.py](Reseux%20de%20Petri%20-%202%20participants.py): modèle multi-participants (p1..p13) incluant gestion du fonds de garantie et mêmes analyses que ci‑dessus.

- **Documentation**:
	- Le rapport de projet (fichier fourni séparément): "Rapport GM 2026 Équipe 6" contient la méthodologie, la modélisation, les propriétés critiques formalisées et les résultats de model checking.

**Comment exécuter**
- Pré-requis: `python3` (3.8+ recommandé). Les scripts n'utilisent que des modules standards (`collections`, `copy`, `random`).
- Lancer la simulation (exemples):

	- `python3 "Reseaux de Petri - un seul participant.py"`
	- `python3 "Reseux de Petri - 2 participants.py"`

Chaque script imprime une simulation (choix aléatoire de transitions franchissables) puis réalise une exploration complète des états atteignables et affiche les métriques suivantes: nombre d'états, deadlocks détectés, bornitude (jetons max par place), vivacité des transitions, et vérification des invariants/propriétés définies.

**Propriétés vérifiées (exemples)**
- **Atomicité**: depuis une place d'appel, au moins une des transitions de suite doit être franchissable.
- **Vivacité**: fermeture des défauts vers clôture si fonds disponibles (P5→P6, P11→P12).
- **Invariant fonds** (modèle multi‑participants): la somme des jetons du fonds + clôtures reste constante.

**Notes et extension**
- Les scripts sont conçus pour être lisibles et modifiables: les places, marquage initial et transitions sont définis en clair au début des fichiers.
- Pour automatiser des vérifications LTL/CTL plus avancées, exporter le modèle vers un outil de model checking (ex. TINA, SPIN) et utiliser les formules décrites dans le rapport.

**Auteurs & Références**
- Équipe 6 — voir le rapport de projet pour la liste complète et les annexes.
- Rapport : "Rapport GM 2026 Équipe 6".
