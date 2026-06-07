#=====================================================
# RESEAU DE PETRI : Multi-participants - p1 à p13
#=====================================================

from collections import deque
from copy import deepcopy
import random


# =====================================================
# PLACES
# =====================================================
places = [
    "p1", "p2", "p3", "p4", "p5", "p6",   # Participant A
    "p7", "p8", "p9", "p10", "p11", "p12", # Participant B
    "p13"  # Fonds de garantie
]


# =====================================================
# MARQUAGE INITIAL
# =====================================================
initial_marking = {
    # A
    "p1": 1, "p2": 0, "p3": 0, "p4": 0, "p5": 0, "p6": 0,

    # B
    "p7": 1, "p8": 0, "p9": 0, "p10": 0, "p11": 0, "p12": 0,

    # Fonds de garantie
    "p13": 3
}


# =====================================================
# TRANSITIONS
# =====================================================
transitions = {

    # -------- Participant A --------
    "T1": ({"p1": 1}, {"p2": 1}),
    "T2": ({"p2": 1}, {"p3": 1}),
    "T3": ({"p3": 1}, {"p4": 1}),
    "T4": ({"p3": 1}, {"p5": 1}),

    # clôture A : défaut + fonds
    "T5": ({"p5": 1, "p13": 1}, {"p6": 1}),


    # -------- Participant B --------
    "T6": ({"p7": 1}, {"p8": 1}),
    "T7": ({"p8": 1}, {"p9": 1}),
    "T8": ({"p9": 1}, {"p10": 1}),
    "T9": ({"p9": 1}, {"p11": 1}),

    # clôture B : défaut + fonds
    "T10": ({"p11": 1, "p13": 1}, {"p12": 1}),
}


# =====================================================
# OUTILS
# =====================================================
def is_enabled(marking, transition):
    inp, _ = transition
    return all(marking[p] >= w for p, w in inp.items())


def fire(marking, transition):
    inp, out = transition
    new_m = deepcopy(marking)

    for p, w in inp.items():
        new_m[p] -= w
    for p, w in out.items():
        new_m[p] += w

    return new_m


def enabled_transitions(marking):
    return [t for t in transitions if is_enabled(marking, transitions[t])]


# =====================================================
# SIMULATION
# =====================================================
def is_final_state(m):
    return (m["p4"] == 1 or m["p6"] == 1) and (m["p10"] == 1 or m["p12"] == 1)


def simulate(marking):
    m = deepcopy(marking)

    while True:
        enabled = enabled_transitions(m)

        if not enabled:
            print("\nDeadlock atteint")
            break

        t = random.choice(enabled)
        print("\nTransition :", t)
        m = fire(m, transitions[t])
        print(m)

        if is_final_state(m):
            print("État final atteint")
            break

    return m


# =====================================================
# ACCESSIBILITE
# =====================================================
def reachable_states(initial):
    visited = set()
    queue = deque()

    def encode(m):
        return tuple(sorted(m.items()))

    queue.append(initial)

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
# DEADLOCK
# =====================================================
def is_terminal_state(m):
    return (m["p4"] == 1 or m["p6"] == 1) and (m["p10"] == 1 or m["p12"] == 1)


def detect_deadlock_states(states):
    deadlocks = []

    for s in states:
        m = dict(s)

        if len(enabled_transitions(m)) == 0:
            if is_terminal_state(m):
                continue
            deadlocks.append(m)

    return deadlocks


# =====================================================
# BORNE
# =====================================================
def bounded_analysis(states):
    max_tokens = {p: 0 for p in places}

    for s in states:
        m = dict(s)
        for p in places:
            max_tokens[p] = max(max_tokens[p], m[p])

    return max_tokens


# =====================================================
# VIVACITE
# =====================================================
def simple_liveness(states):
    liveness = {}
    for t in transitions:
        liveness[t] = any(
            is_enabled(dict(s), transitions[t]) for s in states
        )
    return liveness
#Propriete 1- ETAPE 4
def check_atomicity(states):
    for s in states:
        m = dict(s)
        if m["p3"] >= 1:
            if not (is_enabled(m, transitions["T3"]) or 
                    is_enabled(m, transitions["T4"])):
                return False
        if m["p9"] >= 1:
            if not (is_enabled(m, transitions["T9"]) or 
                    is_enabled(m, transitions["T10"])):
                return False
    return True

#Propriete 4 - ETAPE 4
def check_liveness(states):
    for s in states:
        m = dict(s)
        if m["p5"] >= 1 and m["p13"] == 0:
            return False
        if m["p11"] >= 1 and m["p13"] == 0:  # manque cette ligne
            return False
        
    return True


# =====================================================
# INVARIANT FONDS
# =====================================================
def check_p_invariant(states):
    for s in states:
        m = dict(s)
        if m["p13"] + m["p6"] + m["p12"] != 3:
            return False
    return True


# =====================================================
# EXECUTION
# =====================================================
print("=== MODEL CHECKING=== ")

states = reachable_states(initial_marking)

#Nombre d'états atteignables 
print("Nombre d'états atteignables :", len(states))

#Interblocage
deadlocks = detect_deadlock_states(states)
print("Nombre de deadlocks :", len(deadlocks))

#Bornitude
print("\nBornitude (max tokens par place) :")
print(bounded_analysis(states))

#vivacité des transitions
#Propriete 1
print("Atomicité :", check_atomicity(states))
#Propriete 4
print("Vivacité (P5→P6 toujours possible) :", check_liveness(states))
 
print("\nVivacité des transitions :")
for t, alive in simple_liveness(states).items():
    print(f"  {t} : {'✓ vivante' if alive else '✗ morte'}")
    
#invariant   
print("\nInvariant Fonds de garantie:", check_p_invariant(states))
