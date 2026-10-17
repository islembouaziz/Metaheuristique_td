"""Point d'entrée : choisir l'algorithme à lancer.

Usage :
    python main.py                  # menu interactif
    python main.py 1                # Ex.2 transport  – Tabou
    python main.py 2                # Ex.3 TSP        – Tabou
    python main.py 3                # Ex.3 TSP        – Recuit simulé
    python main.py 3 --gif          # + enregistre assets/ex3_recuit.gif
    python main.py 3 --mp4          # + enregistre assets/ex3_recuit.mp4
    python main.py 3 --no-show      # sans ouvrir la fenêtre matplotlib
"""
import sys

import donnees as D
import visualisation as vis
from recuit_simule import recuit_simule_tsp
from tabou import (cout_tour, optimum_transport, optimum_tsp, tabou_transport,
                   tabou_tsp)

MENU = """
╔══════════════════════════════════════════════════════╗
║   TD Métaheuristiques — Faculté des Sciences de Sfax ║
╠══════════════════════════════════════════════════════╣
║ 1) Exercice 2 : Transport          → Recherche Tabou ║
║ 2) Exercice 3 : Voyageur de commerce → Recherche Tabou║
║ 3) Exercice 3 : Voyageur de commerce → Recuit Simulé ║
║ 0) Quitter                                           ║
╚══════════════════════════════════════════════════════╝"""


def fmt_tour(t):
    return "-".join(str(v + 1) for v in t) + "-1"


# ----------------------------------------------------------------------
def lancer_ex2():
    print("\n=== Exercice 2 : Transport — Recherche Tabou ===")
    best, c, hist = tabou_transport(D.COUTS, D.OFFRES, D.DEMANDES)
    print(f"{'it':>3} | {'coût':>5} | {'meilleur':>8} | mouvement (i1,i2,j1,j2,d)")
    for h in hist:
        print(f"{h['iteration']:>3} | {h['cout']:>5} | {h['meilleur_cout']:>8} | "
              f"{h['mouvement']}")
    print("\nMeilleure solution (lignes = dépôts, colonnes = magasins) :")
    for nom, ligne in zip(D.NOMS_DEPOTS, best):
        print(f"  {nom} : {ligne}")
    print(f"Coût minimal trouvé : {c}   |   optimum exact : "
          f"{optimum_transport(D.COUTS, D.OFFRES, D.DEMANDES)}")
    anim = vis.animer_transport(hist, D.COUTS, D.NOMS_DEPOTS, D.NOMS_MAGASINS,
                                D.OFFRES, D.DEMANDES)
    return anim, "ex2_tabou"


def lancer_ex3_tabou():
    print("\n=== Exercice 3 : TSP — Recherche Tabou ===")
    best, c, hist = tabou_tsp(D.DIST, D.TOUR_INITIAL)
    print(f"Solution initiale : {fmt_tour(D.TOUR_INITIAL)}  "
          f"(coût {cout_tour(D.TOUR_INITIAL, D.DIST)})")
    for h in hist[1:]:
        print(f"  it {h['iteration']:>2} : {fmt_tour(h['tour'])}  coût {h['cout']:>3}"
              f"  | {h['info']}")
    opt_t, opt_c = optimum_tsp(D.DIST)
    print(f"\nMeilleur tour : {fmt_tour(best)}  coût = {c}")
    print(f"Optimum exact (force brute) : {fmt_tour(opt_t)}  coût = {opt_c}")
    anim = vis.animer_tsp(hist, D.DIST, "Exercice 3 — TSP : Recherche Tabou",
                          intervalle=800)
    return anim, "ex3_tabou"


def lancer_ex3_recuit():
    print("\n=== Exercice 3 : TSP — Recuit Simulé (5 paliers) ===")
    best, c, hist = recuit_simule_tsp(D.DIST, D.TOUR_INITIAL)
    print(f"Solution initiale : {fmt_tour(D.TOUR_INITIAL)}  "
          f"(coût {cout_tour(D.TOUR_INITIAL, D.DIST)})")
    for h in hist[1:]:
        print(f"  essai {h['iteration']:>2} | {h['info']} | coût {h['cout']}")
    opt_t, opt_c = optimum_tsp(D.DIST)
    print(f"\nMeilleur tour : {fmt_tour(best)}  coût = {c}")
    print(f"Optimum exact (force brute) : {fmt_tour(opt_t)}  coût = {opt_c}")
    anim = vis.animer_tsp(hist, D.DIST, "Exercice 3 — TSP : Recuit Simulé",
                          intervalle=350)
    return anim, "ex3_recuit"


ALGOS = {"1": lancer_ex2, "2": lancer_ex3_tabou, "3": lancer_ex3_recuit}


def executer(choix, gif=False, mp4=False, show=True):
    anim, nom = ALGOS[choix]()
    fps = 2 if choix == "1" else (1.25 if choix == "2" else 3)
    if gif:
        vis.sauvegarder(anim, f"assets/{nom}.gif", fps=fps)
    if mp4:
        vis.sauvegarder(anim, f"assets/{nom}.mp4", fps=fps)
    if show:
        vis.afficher()


def main():
    args = sys.argv[1:]
    gif, mp4, show = "--gif" in args, "--mp4" in args, "--no-show" not in args
    choix = next((a for a in args if a in ALGOS), None)
    if choix:
        executer(choix, gif, mp4, show)
        return
    while True:
        print(MENU)
        choix = input("Votre choix : ").strip()
        if choix == "0":
            break
        if choix not in ALGOS:
            print("Choix invalide.")
            continue
        rep = input("Enregistrer l'animation ? (g = GIF, m = MP4, Entrée = non) : ")
        executer(choix, gif=rep.strip().lower() == "g",
                 mp4=rep.strip().lower() == "m")


if __name__ == "__main__":
    main()
