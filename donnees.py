"""Données des exercices 2 et 3 du TD (Faculté des Sciences de Sfax)."""

# ======================================================================
# Exercice 2 : problème de transport dépôts -> magasins
# ======================================================================
NOMS_DEPOTS = ["D1", "D2"]
NOMS_MAGASINS = ["M1", "M2", "M3"]

COUTS = [[5, 3, 4],      # coût unitaire D1 -> M1, M2, M3
         [6, 7, 2]]      # coût unitaire D2 -> M1, M2, M3
OFFRES = [8, 9]          # containers disponibles dans D1, D2
DEMANDES = [4, 5, 8]     # containers demandés par M1, M2, M3

# ======================================================================
# Exercice 3 : voyageur de commerce (graphe non complet, symétrique)
# ======================================================================
N_VILLES = 8
PENALITE = 100           # coût d'une arête inexistante ("-" dans le tableau)

# (ville_a, ville_b): distance   -> villes numérotées de 1 à 8 comme dans le TD
_ARETES = {
    (1, 2): 14, (1, 3): 15, (1, 8): 17,
    (2, 3): 13, (2, 4): 14, (2, 5): 20, (2, 8): 21,
    (3, 4): 11, (3, 5): 21, (3, 6): 17, (3, 7): 9, (3, 8): 9,
    (4, 5): 11, (4, 6): 10, (4, 7): 8, (4, 8): 20,
    (5, 6): 15, (5, 7): 18,
    (6, 7): 9,
    (7, 8): 13,
}


def _construire_distances():
    d = [[PENALITE] * N_VILLES for _ in range(N_VILLES)]
    for i in range(N_VILLES):
        d[i][i] = 0
    for (a, b), w in _ARETES.items():
        d[a - 1][b - 1] = w
        d[b - 1][a - 1] = w
    return d


DIST = _construire_distances()          # indices 0..7 (ville k = indice k-1)
TOUR_INITIAL = list(range(N_VILLES))    # 1-2-3-4-5-6-7-8-(1)
