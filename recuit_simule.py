"""Recuit Simulé pour le voyageur de commerce (Exercice 3).

Conforme à l'énoncé : 5 itérations (paliers de température) avec une
variation empirique de T (T <- alpha * T). À chaque palier on effectue
`n_essais` tentatives de déplacement.
"""
import math
import random

from tabou import cout_tour


def recuit_simule_tsp(dist, tour0, T0=30.0, alpha=0.5, n_iterations=5,
                      n_essais=15, seed=42):
    """Recuit simulé.

    - Voisinage  : échange de 2 villes tirées au hasard (ville 1 fixe).
    - Acceptation: Δ <= 0 -> toujours ; Δ > 0 -> avec probabilité exp(-Δ / T).
    - Refroidissement empirique : T_{k+1} = alpha * T_k  (30, 15, 7.5, 3.75, 1.9).
    """
    rng = random.Random(seed)
    n = len(tour0)
    tour = list(tour0)
    c = cout_tour(tour, dist)
    best, best_c = tour[:], c

    historique = [dict(iteration=0, tour=tour[:], cout=c, meilleur_tour=best[:],
                       meilleur_cout=best_c, candidat=None, accepte=True,
                       T=T0, info="Solution initiale 1-2-3-4-5-6-7-8-1")]

    T = T0
    etape = 0
    for palier in range(1, n_iterations + 1):
        for _ in range(n_essais):
            etape += 1
            i, j = sorted(rng.sample(range(1, n), 2))
            cand = tour[:]
            cand[i], cand[j] = cand[j], cand[i]
            cand_c = cout_tour(cand, dist)
            delta = cand_c - c
            p = 1.0 if delta <= 0 else math.exp(-delta / T)
            accepte = rng.random() < p

            if accepte:
                tour, c = cand, cand_c
                if c < best_c:
                    best, best_c = tour[:], c

            historique.append(dict(
                iteration=etape, palier=palier, tour=tour[:], cout=c,
                meilleur_tour=best[:], meilleur_cout=best_c, candidat=cand,
                cout_candidat=cand_c, accepte=accepte, T=T,
                info=(f"Palier {palier}/{n_iterations}   T = {T:.2f}   "
                      f"Δ = {delta:+d}   p = {p:.2f}   -> "
                      f"{'ACCEPTÉ' if accepte else 'refusé'}")))
        T *= alpha

    return best, best_c, historique
