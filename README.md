# Vérification Formelle d'Applications Critiques avec Réseaux de Petri

> Projet Technique GM 2026 — Équipe 6
> CY Tech (ING 1, S2)

Ce projet modélise et **vérifie formellement** un système financier critique à l'aide
des **réseaux de Petri**, puis prouve mathématiquement qu'il respecte un ensemble de
propriétés de sûreté et de vivacité — d'abord avec un vérificateur Python écrit
« à la main », ensuite avec l'outil professionnel **TINA**.

---

## 1. De quoi parle le projet ?

### Le problème : les systèmes critiques

Un *système critique* est un système dont la défaillance peut avoir des conséquences
graves (transport, aéronautique, médical, nucléaire… et **finance systémique**). Pour
ces systèmes, tester ne suffit pas : un test n'explore qu'une partie des comportements
possibles. Les **méthodes formelles** permettent au contraire de vérifier *mathématiquement*
et *exhaustivement* qu'un système respecte ses propriétés, en explorant **tous** ses
états atteignables.

### L'application choisie : les appels de marge d'une chambre de compensation (CCP)

Une **Chambre de Compensation Centrale (CCP)** s'interpose entre acheteurs et vendeurs
sur les marchés financiers. Si une partie fait défaut, la CCP absorbe le choc à sa place.
Pour cela, chaque participant dépose une **marge initiale** ; si le marché évolue
défavorablement, la CCP émet un **appel de marge** (« versez tant, sous 2 heures »).

Le cycle de vie d'une position suit alors deux scénarios :

- **Scénario normal** : le participant verse le collatéral → la position est *réglée*.
- **Scénario de défaut** : le délai expire → la CCP puise dans un **fonds de garantie**
  mutualisé pour liquider la position de force (*clôture*).

Le **fonds de garantie est une ressource partagée et limitée**. Si trop de participants
font défaut en même temps et que le fonds est épuisé, la CCP ne peut plus traiter les
défauts restants : le système se **bloque**. C'est exactement ce **risque systémique**
que le modèle doit détecter et prévenir (cf. la crise énergétique européenne de 2022).

---

## 2. Le modèle réseau de Petri

Un réseau de Petri est un graphe biparti **places ↔ transitions**, parcouru par des
**jetons**. Ici, chaque jeton représente une position d'un participant.

### Les places (états d'une position)

| Place | État | Signification |
| :---- | :---- | :---- |
| P1 | Position ouverte | La position est active, marge suffisante |
| P2 | En alerte | La marge approche du seuil critique |
| P3 | Appel émis | Le *margin call* est envoyé, en attente de collatéral |
| P4 | Position réglée | La marge est rétablie (état terminal sain) |
| P5 | Défaut déclenché | La procédure de défaut est en cours |
| P6 | Position clôturée | Liquidation forcée effectuée (état terminal) |
| P7 *(fonds)* | Fonds de garantie | Ressource partagée et **bornée** (modèle multi-participants) |

### Les transitions (événements)

| Transition | Événement | Condition |
| :---- | :---- | :---- |
| T1 | Franchir le seuil | la valorisation passe sous le seuil d'alerte |
| T2 | Émettre l'appel | un jeton est en *En alerte* |
| T3 | Recevoir le collatéral | un jeton en *Appel émis* **et** délai non expiré |
| T4 | Expirer le délai | un jeton en *Appel émis* **et** délai écoulé |
| T5 | Clôturer la position | un jeton en *Défaut* **et** le fonds contient ≥ 1 jeton |

Le point clé du modèle multi-participants : la clôture (T5/T10) consomme **simultanément**
un jeton de défaut **et** un jeton du fonds de garantie. C'est ce qui modélise
naturellement la concurrence entre participants pour une ressource partagée limitée.

---

## 3. Contenu du dépôt

| Fichier | Description |
| :---- | :---- |
| [Reseaux de Petri - un seul participant.py](Reseaux%20de%20Petri%20-%20un%20seul%20participant.py) | Modèle de base : une position, un seul participant. Sert à valider la structure (6 places, 5 transitions). |
| [Reseux de Petri - 2 participants.py](Reseux%20de%20Petri%20-%202%20participants.py) | Modèle complet : 2 participants (P1–P6 / P7–P12) + fonds de garantie partagé (P13, doté de 3 jetons). |
| [Rapport GM 2026 Équipe 6.pdf](Rapport%20GM%202026%20%C3%89quipe%206.pdf) | Rapport complet : état de l'art des méthodes formelles, modélisation, formalisation LTL/CTL des propriétés et vérification par model checking (TINA). |

Chaque script est volontairement écrit **sans bibliothèque externe** (uniquement
`collections`, `copy`, `random`), pour rendre la mécanique du model checking explicite
et lisible. Les places, le marquage initial et les transitions sont définis en clair
en tête de fichier et faciles à modifier.

---

## 4. Comment ça marche (le code)

Le réseau est représenté par trois objets : `places`, `transitions` (un dictionnaire
`nom → (préconditions, postconditions)`) et `initial_marking` (`place → nb_jetons`).
Deux fonctions implémentent la règle de franchissement :

- `is_enabled(marking, transition)` — vérifie qu'une transition est franchissable
  (chaque place d'entrée a assez de jetons) ;
- `fire(marking, transition)` — franchit la transition (consomme les jetons d'entrée,
  produit ceux de sortie).

À partir de là, le programme réalise deux choses :

1. **Une simulation** (`simulate`) : un chemin d'exécution aléatoire depuis le marquage
   initial jusqu'à un état terminal ou un blocage. C'est une illustration, **pas une preuve**.
2. **Une vérification exhaustive** : `reachable_states` construit tout le graphe
   d'accessibilité par un parcours en largeur (BFS), puis chaque propriété est testée
   sur **l'ensemble** des états atteignables.

---

## 5. Propriétés vérifiées

Sept propriétés critiques, issues des exigences réglementaires (EMIR), sont formalisées
en LTL/CTL dans le rapport et vérifiées par le code :

| # | Propriété | Fonction Python | Garantit que… |
| :- | :---- | :---- | :---- |
| P1 | **Atomicité** | `check_atomicity` | tout appel de marge aboutit à un règlement ou à une clôture (jamais en suspens). |
| P2 | **Conservation du fonds** | `check_p_invariant` | `fonds + clôtures_A + clôtures_B = 3` reste constant : aucun jeton du fonds n'est créé ni dupliqué. |
| P3 | **Absence de deadlock** | `detect_deadlock_states` | le système ne se bloque jamais hors des états terminaux légitimes. |
| P4 | **Vivacité du défaut** | `check_liveness` | tout défaut déclenché finit par mener à une clôture (tant que le fonds le permet). |
| P5 | **Bornitude** | `bounded_analysis` | aucune place n'accumule de jetons à l'infini ; le fonds ne dépasse jamais sa dotation. |
| P6 | **Exclusion mutuelle** | par construction | une position n'est jamais à la fois réglée *et* clôturée. |
| P7 | **Précédence** | par construction | aucun appel n'est émis sans passage préalable par l'alerte. |

Les sept propriétés sont **satisfaites** par le modèle. Ce résultat a été **recoupé**
avec l'outil TINA (modules `struct`, `tina`, `selt`) : 36 marquages atteignables,
4 marquages morts tous légitimes, et toutes les formules LTL retournent `TRUE`.
La convergence entre le vérificateur Python et TINA est totale.

### Le point clé : P4 dépend du dimensionnement du fonds

Avec 2 participants et un fonds de 3 jetons, la saturation est impossible (au plus
2 défauts simultanés) → toutes les propriétés tiennent. **Mais si le fonds devient
inférieur au nombre de défauts simultanés possibles**, le model checking révèle un
deadlock : des positions restent coincées en *Défaut* faute de jeton dans le fonds.
On peut le reproduire en réduisant `p13` à `1` dans le modèle 2 participants : la
détection de deadlock se déclenche et `check_liveness` renvoie `False`. C'est le risque
systémique réel que le modèle est conçu pour exposer.

---

## 6. Exécuter le projet

Prérequis : **Python 3.8+** (aucune dépendance externe).

```bash
# Modèle à un participant
python3 "Reseaux de Petri - un seul participant.py"

# Modèle à deux participants + fonds de garantie partagé
python3 "Reseux de Petri - 2 participants.py"
```

Chaque script affiche une simulation, puis le nombre d'états atteignables, les deadlocks
détectés, la bornitude (jetons max par place), la vivacité des transitions et le verdict
de chaque propriété.

### Aller plus loin

- **Modifier le scénario** : changez le marquage initial (`initial_marking`) ou la
  dotation du fonds (`p13`) pour explorer des cas de saturation.
- **Vérification LTL/CTL avancée** : exporter le modèle vers un outil de model checking
  professionnel (**TINA**, SPIN…) avec les formules détaillées dans le rapport.

---

## 7. Hypothèses et limites

- **Cycle de vie unique** : une position va du début à la clôture, sans réouverture.
- **Temps abstrait** : seul l'ordre des états est modélisé, pas les durées réelles
  (le délai de 1–2 h n'est pas chiffré ; cela relèverait des réseaux de Petri *temporisés*).
- **Passage à l'échelle** : un modèle à N participants donne un espace d'états de l'ordre
  de 6^N, ce qui dépasse vite le model checking explicite. Des extensions temporisées
  (UPPAAL) ou stochastiques (PRISM) seraient nécessaires au-delà du périmètre du projet.

---

## Auteurs

**Équipe 6 — GM 2026 :** Soumaya Toumi · Théo Gimenes · Ewan Clabaut · Charly Pupier · Grace Bidi Sinda

Voir le rapport complet pour la méthodologie détaillée, l'état de l'art des méthodes
formelles et les annexes de correspondance (places / formules SELT).
