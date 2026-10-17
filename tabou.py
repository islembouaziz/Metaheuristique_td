"""Recherche Tabou : Exercice 2 (transport) et Exercice 3 (voyageur de commerce).

Chaque fonction renvoie (meilleure_solution, meilleur_cout, historique).
`historique` est une liste de dictionnaires (un par itération) utilisée par
visualisation.py pour construire les animations.
"""
import itertools
import math

# ======================================================================
# EXERCICE 2 : TRANSPORT
# ======================================================================

def cout_transport(x, couts):
    """Coût total = somme x[i][j] * c[i][j]."""
    return sum(x[i][j] * couts[i][j]
               for i in range(len(x)) for j in range(len(x[0])))


def coin_nord_ouest(offres, demandes):
    """Solution initiale réalisable (méthode du coin Nord-Ouest)."""
    assert sum(offres) == sum(demandes), "Problème non équilibré"
    offres, demandes = list(offres), list(demandes)
    m, n = len(offres), len(demandes)
    x = [[0] * n for _ in range(m)]
    i = j = 0
    while i < m and j < n:
        q = min(offres[i], demandes[j])
        x[i][j] = q
        offres[i] -= q
        demandes[j] -= q
        if offres[i] == 0:
            i += 1
        else:
            j += 1
    return x


def voisinage_transport(x):
    """Mouvements « rectangle » : -d en (i1,j1) et (i2,j2), +d en (i1,j2) et (i2,j1).

    Ce mouvement conserve toutes les sommes de lignes et de colonnes,
    donc un voisin d'une solution réalisable est toujours réalisable.
    """
    m, n = len(x), len(x[0])
    for i1 in range(m):
        for i2 in range(i1 + 1, m):
            for j1 in range(n):
                for j2 in range(n):
                    if j1 == j2:
                        continue
                    for d in range(1, min(x[i1][j1], x[i2][j2]) + 1):
                        yield (i1, i2, j1, j2, d)


def appliquer_mouvement(x, mv):
    i1, i2, j1, j2, d = mv
    y = [ligne[:] for ligne in x]
    y[i1][j1] -= d
    y[i2][j2] -= d
    y[i1][j2] += d
    y[i2][j1] += d
    return y


def tabou_transport(couts, offres, demandes, n_iter=8, tenure=3):
    """Recherche Tabou pour le problème de transport.

    Liste tabou : après un mouvement, les cases qui ont DIMINUÉ ne peuvent pas
    ré-augmenter pendant `tenure` itérations (évite de défaire le mouvement).
    Aspiration : un mouvement tabou est accepté s'il bat le meilleur coût connu.
    """
    x = coin_nord_ouest(offres, demandes)
    c = cout_transport(x, couts)
    best, best_c = [l[:] for l in x], c
    tabou = {}   # case (i, j) -> dernière itération où elle reste tabou

    historique = [dict(iteration=0, solution=[l[:] for l in x], cout=c,
                       meilleur=[l[:] for l in best], meilleur_cout=best_c,
                       mouvement=None, tabou=[])]

    for it in range(1, n_iter + 1):
        choix, choix_c = None, math.inf
        for mv in voisinage_transport(x):
            i1, i2, j1, j2, _ = mv
            cand_c = cout_transport(appliquer_mouvement(x, mv), couts)
            est_tabou = tabou.get((i1, j2), 0) >= it or tabou.get((i2, j1), 0) >= it
            if est_tabou and cand_c >= best_c:        # pas d'aspiration
                continue
            if cand_c < choix_c:
                choix, choix_c = mv, cand_c
        if choix is None:                              # tout est tabou
            break

        i1, i2, j1, j2, _ = choix
        x = appliquer_mouvement(x, choix)
        c = choix_c
        tabou[(i1, j1)] = it + tenure
        tabou[(i2, j2)] = it + tenure
        if c < best_c:
            best, best_c = [l[:] for l in x], c

        historique.append(dict(
            iteration=it, solution=[l[:] for l in x], cout=c,
            meilleur=[l[:] for l in best], meilleur_cout=best_c, mouvement=choix,
            tabou=[cell for cell, fin in tabou.items() if fin > it]))

    return best, best_c, historique


def optimum_transport(couts, offres, demandes):
    """Optimum exact par énumération (vérification, petites instances)."""
    m, n = len(offres), len(demandes)
    meilleur = [math.inf]

    def rec(cell, off, dem, cout):
        if cell == m * n:
            if all(v == 0 for v in off) and all(v == 0 for v in dem):
                meilleur[0] = min(meilleur[0], cout)
            return
        i, j = divmod(cell, n)
        for q in range(min(off[i], dem[j]) + 1):
            off[i] -= q; dem[j] -= q
            rec(cell + 1, off, dem, cout + q * couts[i][j])
            off[i] += q; dem[j] += q

    rec(0, list(offres), list(demandes), 0)
    return meilleur[0]


# ======================================================================
# EXERCICE 3 : VOYAGEUR DE COMMERCE
# ======================================================================

def cout_tour(tour, dist):
    """Longueur du cycle (retour à la ville de départ inclus)."""
    n = len(tour)
    return sum(dist[tour[k]][tour[(k + 1) % n]] for k in range(n))


def tabou_tsp(dist, tour0, n_iter=15, tenure=4):
    """Recherche Tabou pour le TSP.

    Voisinage : échange de 2 villes (la ville de départ reste fixée).
    Liste tabou : paire de villes échangée, interdite pendant `tenure` itérations.
    Aspiration : un échange tabou est autorisé s'il améliore le meilleur coût.
    """
    n = len(tour0)
    tour = list(tour0)
    c = cout_tour(tour, dist)
    best, best_c = tour[:], c
    tabou = {}   # frozenset({ville_a, ville_b}) -> dernière itération tabou

    historique = [dict(iteration=0, tour=tour[:], cout=c, meilleur_tour=best[:],
                       meilleur_cout=best_c, candidat=None, accepte=True,
                       info="Solution initiale 1-2-3-4-5-6-7-8-1")]

    for it in range(1, n_iter + 1):
        choix, choix_c, choix_t = None, math.inf, None
        for i in range(1, n):
            for j in range(i + 1, n):
                cand = tour[:]
                cand[i], cand[j] = cand[j], cand[i]
                cand_c = cout_tour(cand, dist)
                cle = frozenset((tour[i], tour[j]))
                if tabou.get(cle, 0) >= it and cand_c >= best_c:
                    continue
                if cand_c < choix_c:
                    choix, choix_c, choix_t = cle, cand_c, cand
        if choix is None:
            break

        tour, c = choix_t, choix_c
        tabou[choix] = it + tenure
        if c < best_c:
            best, best_c = tour[:], c

        a, b = sorted(v + 1 for v in choix)
        historique.append(dict(
            iteration=it, tour=tour[:], cout=c, meilleur_tour=best[:],
            meilleur_cout=best_c, candidat=tour[:], accepte=True,
            info=f"Échange des villes {a} ↔ {b}  (tabou {tenure} it.)"))

    return best, best_c, historique


def optimum_tsp(dist):
    """Optimum exact par force brute (7! = 5040 tours) pour vérification."""
    n = len(dist)
    meilleur, meilleur_t = math.inf, None
    for perm in itertools.permutations(range(1, n)):
        t = [0] + list(perm)
        c = cout_tour(t, dist)
        if c < meilleur:
            meilleur, meilleur_t = c, t
    return meilleur_t, meilleur
