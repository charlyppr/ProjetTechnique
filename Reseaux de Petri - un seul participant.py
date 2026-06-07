# =====================================================
# RESEAU DE PETRI : 1 PARTICIPANT
# =====================================================
from collections import deque
from copy import deepcopy
import random

#l'utilisation des listes, dictionnaires et des tuples  
#places - états
places = ["P1", "P2", "P3", "P4", "P5", "P6"]

# Marquage initial
initial_marking = {
    "P1": 1,  # position ouverte
    "P2": 0,  # alerte
    "P3": 0,  # appel émis
    "P4": 0,  # position réglée
    "P5": 0,  # défaut
    "P6": 0,  # clôturée 
}

# Transitions (input -> output)
transitions = {
    "T1": ({"P1": 1}, {"P2": 1}),
    "T2": ({"P2": 1}, {"P3": 1}),

    # Deux possibilités depuis P3
    "T3": ({"P3": 1}, {"P4": 1}),  # collatéral reçu
    "T4": ({"P3": 1}, {"P5": 1}),  # délai expiré

    "T5": ({"P5": 1}, {"P6": 1}),  # liquidation

}

#  Une transition T est franchissable si et seulement
#si chaque place en entrée contient suffisamment de jetons 
def is_enabled(marking, transition):
    inp, _ = transition
    return all(marking[p] >= w for p, w in inp.items())

# Quand on franchit une transition T, on passe du marquage M au marquage M'
def fire(marking, transition):
    inp, out = transition
    new_m = deepcopy(marking)

    for p, w in inp.items():
        new_m[p] -= w

    for p, w in out.items():
        new_m[p] += w

    return new_m

# l'application de is_enabled sur toutes les transitions
def enabled_transitions(marking):
    return [t for t in transitions if is_enabled(marking, transitions[t])]

# =====================================================
# 1. SIMULATION
# =====================================================
#ARRET: verifier que le participant ont terminé 
def is_final_state(m):
    return m["P4"] == 1 or m["P6"] == 1

def simulate(marking):
    print("=== SIMULATION ===")
    m = deepcopy(marking)
    step = 0
    while True:
        enabled = enabled_transitions(m)
        print(f"\nEtat {step} :", m)
        if not enabled:
            print("\n>> DEADLOCK atteint")
            break
        t = random.choice(enabled)
        print("Transition :", t)
        m = fire(m, transitions[t])
        step += 1
        if is_final_state(m):
            print("\n>> État final atteint")
            break
    return m
# =====================================================
# 2. MODEL CHECKING : ACCESSIBILITE
# =====================================================

def encode(m):
    return tuple(sorted(m.items()))


def reachable_states(initial):
    visited = set()
    queue = deque([initial])

    while queue:
        m = queue.popleft()
        key = encode(m)

        if key in visited:
            continue

        visited.add(key)

        for t in transitions:
            if is_enabled(m, transitions[t]):
                queue.append(fire(m, transitions[t]))

    return visited

# =====================================================
# 3. DEADLOCKS
# =====================================================

def detect_deadlocks(states):
    deadlocks = []

    for s in states:
        m = dict(s)
        if len(enabled_transitions(m)) == 0:
            # états finaux acceptés
            if m["P4"] == 1 or m["P6"] == 1:
                continue

            deadlocks.append(m)

    return deadlocks

# =====================================================
# 4. BORNE (BORNITUDE)
# =====================================================

def bounded_analysis(states):
    max_tokens = {p: 0 for p in places}

    for s in states:
        m = dict(s)
        for p in places:
            max_tokens[p] = max(max_tokens[p], m[p])

    return max_tokens

# =====================================================
# 5. VIVACITE 
# =====================================================

def simple_liveness(states):
    liveness = {}
    for t in transitions:
        liveness[t] = any(
            is_enabled(dict(s), transitions[t])
            for s in states
        )
    return liveness
#Propriete 1 - ETAPE 4
def check_atomicity(states):
    for s in states:
        m = dict(s)
        if m["P3"] >= 1:
            if not (is_enabled(m, transitions["T3"]) or 
                    is_enabled(m, transitions["T4"])):
                return False
    return True 
#Propriete 4 - ETAPE 4
def check_liveness(states):
    for s in states:
        m = dict(s)
        if m["P5"] >= 1:
            if not is_enabled(m, transitions["T5"]):
                return False
    return True
#======================================================
#INVARIANT :P4 et P6 ne sont jamais marquées simultanément
# =====================================================
def check_p_invariant(states):
    for s in states:
        m = dict(s)
        if m["P4"] + m["P6"] > 1:
            return False
    return True
#======================================================
# EXECUTION COMPLETE
# =====================================================


# Simulation
final_state = simulate(initial_marking)

# Analyse complète
states = reachable_states(initial_marking)

#Nombre d'etats atteignables 
print("Nombre d'etats atteignables :", len(states))

#interblocage
deadlocks = detect_deadlocks(states)
print("Nombre de deadlocks :", len(deadlocks))

#Bornitude
print("\nBornitude :")
print(bounded_analysis(states))

#Vivacité

#Propriete 1 
print("Atomicité :", check_atomicity(states))
#Propriete 4
print("Vivacité (P5→P6 toujours possible) :", check_liveness(states))
#simple vivacity
print("\nVivacité des transitions :")
for t, alive in simple_liveness(states).items():
    print(f"  {t} : {'✓ vivante' if alive else '✗ morte'}")
    
#Invariant 
print("\nInvariant:", check_p_invariant(states))


