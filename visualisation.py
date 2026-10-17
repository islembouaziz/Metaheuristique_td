"""Animations matplotlib des algorithmes (aucun calcul d'optimisation ici).

- animer_transport : Exercice 2 (matrice d'affectation + courbe de coût)
- animer_tsp       : Exercice 3 (graphe + tour courant + courbe de coût)
- sauvegarder      : export GIF (Pillow) ou MP4 (ffmpeg) pour le README
"""
import math
import os

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.animation import FuncAnimation, PillowWriter
from matplotlib.patches import Rectangle

from donnees import PENALITE

BLEU, VERT, ROUGE, ORANGE = "#1f77b4", "#2ca02c", "#d62728", "#ff7f0e"


# ----------------------------------------------------------------------
# Exercice 2
# ----------------------------------------------------------------------
def animer_transport(historique, couts, noms_depots, noms_magasins,
                     offres, demandes, intervalle=1100):
    m, n = len(couts), len(couts[0])
    fig, (ax_m, ax_c) = plt.subplots(1, 2, figsize=(12, 5),
                                     gridspec_kw={"width_ratios": [1.1, 1]})
    fig.suptitle("Exercice 2 — Transport : Recherche Tabou", fontweight="bold")
    vmax = max(max(max(l) for l in h["solution"]) for h in historique)
    tous = [h["cout"] for h in historique]
    ymin, ymax = min(tous) - 2, max(tous) + 2

    def maj(k):
        h = historique[k]
        ax_m.clear()
        ax_c.clear()
        x = np.array(h["solution"])
        ax_m.imshow(x, cmap="Blues", vmin=0, vmax=vmax * 1.6)
        for i in range(m):
            for j in range(n):
                ax_m.text(j, i - 0.05, str(x[i, j]), ha="center", va="center",
                          fontsize=22, fontweight="bold")
                ax_m.text(j, i + 0.33, f"coût unit. {couts[i][j]}", ha="center",
                          fontsize=8, color="dimgray")
        for (i, j) in h["tabou"]:
            ax_m.text(j - 0.42, i - 0.32, "T", color="purple",
                      fontsize=10, fontweight="bold")
        if h["mouvement"]:
            i1, i2, j1, j2, d = h["mouvement"]
            for (i, j) in ((i1, j1), (i2, j2)):
                ax_m.add_patch(Rectangle((j - .5, i - .5), 1, 1, fill=False,
                                         ec=ROUGE, lw=3.5))
            for (i, j) in ((i1, j2), (i2, j1)):
                ax_m.add_patch(Rectangle((j - .5, i - .5), 1, 1, fill=False,
                                         ec=VERT, lw=3.5))
            ax_m.set_xlabel(f"Mouvement : ±{d} container(s)   "
                            "rouge = case diminuée · vert = case augmentée · "
                            "T = tabou", fontsize=8)
        else:
            ax_m.set_xlabel("Solution initiale (coin Nord-Ouest)", fontsize=9)
        ax_m.set_xticks(range(n))
        ax_m.set_xticklabels([f"{noms_magasins[j]}\n(demande {demandes[j]})"
                              for j in range(n)])
        ax_m.set_yticks(range(m))
        ax_m.set_yticklabels([f"{noms_depots[i]}\n(offre {offres[i]})"
                              for i in range(m)])
        ax_m.set_xlim(-.5, n - .5)
        ax_m.set_ylim(m - .5, -.5)
        ax_m.set_title(f"Itération {h['iteration']}  —  coût = {h['cout']}   "
                       f"(meilleur = {h['meilleur_cout']})")

        its = range(k + 1)
        ax_c.plot(its, [historique[t]["cout"] for t in its], "o-", color=BLEU,
                  label="coût courant")
        ax_c.plot(its, [historique[t]["meilleur_cout"] for t in its], "s--",
                  color=VERT, label="meilleur coût")
        ax_c.set_xlim(-.5, len(historique) - .5)
        ax_c.set_ylim(ymin, ymax)
        ax_c.set_xlabel("itération")
        ax_c.set_ylabel("coût total de transport")
        ax_c.grid(alpha=.3)
        ax_c.legend(loc="upper left")
        ax_c.set_title("Évolution du coût")

    fig.tight_layout()
    return FuncAnimation(fig, maj, frames=len(historique), interval=intervalle,
                         repeat=True)


# ----------------------------------------------------------------------
# Exercice 3
# ----------------------------------------------------------------------
def _aretes(tour):
    n = len(tour)
    return [(tour[k], tour[(k + 1) % n]) for k in range(n)]


def animer_tsp(historique, dist, titre, intervalle=450):
    n = len(dist)
    pos = [(math.cos(math.pi / 2 - 2 * math.pi * i / n),
            math.sin(math.pi / 2 - 2 * math.pi * i / n)) for i in range(n)]
    fig, (ax_g, ax_c) = plt.subplots(1, 2, figsize=(12.5, 5.6),
                                     gridspec_kw={"width_ratios": [1, 1.1]})
    fig.suptitle(titre, fontweight="bold")
    tous = [h["cout"] for h in historique]
    ymin = min(h["meilleur_cout"] for h in historique) - 5
    ymax = tous[0] * 1.35

    def trait(a, b, **kw):
        ax_g.plot([pos[a][0], pos[b][0]], [pos[a][1], pos[b][1]], **kw)

    def maj(k):
        h = historique[k]
        ax_g.clear()
        ax_c.clear()

        # arêtes existantes du graphe (fond)
        for a in range(n):
            for b in range(a + 1, n):
                if dist[a][b] != PENALITE:
                    trait(a, b, color="#dddddd", lw=1, zorder=1)
        # meilleur tour (halo vert)
        for a, b in _aretes(h["meilleur_tour"]):
            trait(a, b, color=VERT, lw=9, alpha=.25, zorder=2)
        # candidat refusé (pointillé orange)
        if h.get("candidat") and not h["accepte"]:
            courantes = {frozenset(e) for e in _aretes(h["tour"])}
            for a, b in _aretes(h["candidat"]):
                if frozenset((a, b)) not in courantes:
                    trait(a, b, color=ORANGE, lw=2, ls=":", zorder=3)
        # tour courant
        for a, b in _aretes(h["tour"]):
            manquante = dist[a][b] == PENALITE
            trait(a, b, color=ROUGE if manquante else BLEU, lw=2.6,
                  ls="--" if manquante else "-", zorder=4)
            mx, my = (pos[a][0] + pos[b][0]) / 2, (pos[a][1] + pos[b][1]) / 2
            ax_g.text(mx, my, "∞" if manquante else str(dist[a][b]), fontsize=8,
                      ha="center", va="center", zorder=5,
                      bbox=dict(boxstyle="round,pad=.15", fc="white", ec="none"))
        # villes
        for i, (x, y) in enumerate(pos):
            ax_g.scatter(x, y, s=650, c="gold" if i == 0 else "white",
                         edgecolors="black", zorder=6)
            ax_g.text(x, y, str(i + 1), ha="center", va="center",
                      fontweight="bold", zorder=7)
        ax_g.set_xlim(-1.35, 1.35)
        ax_g.set_ylim(-1.35, 1.35)
        ax_g.set_aspect("equal")
        ax_g.axis("off")
        parcours = "-".join(str(v + 1) for v in h["tour"]) + "-1"
        ax_g.set_title(f"{parcours}   (coût = {h['cout']})", fontsize=11)
        ax_g.text(0, -1.3, h["info"], ha="center", fontsize=9)

        its = range(k + 1)
        ax_c.plot(its, [historique[t]["cout"] for t in its], "-", color=BLEU,
                  label="coût courant")
        ax_c.plot(its, [historique[t]["meilleur_cout"] for t in its], "--",
                  color=VERT, lw=2, label="meilleur coût")
        if "cout_candidat" in h:      # recuit : points acceptés / refusés
            for t in its:
                ht = historique[t]
                if "cout_candidat" in ht:
                    ax_c.scatter(t, ht["cout_candidat"], s=22, zorder=3,
                                 c=VERT if ht["accepte"] else ROUGE,
                                 marker="o" if ht["accepte"] else "x")
            ax_c.scatter([], [], c=VERT, s=22, label="candidat accepté")
            ax_c.scatter([], [], c=ROUGE, marker="x", s=22,
                         label="candidat refusé")
        ax_c.set_xlim(-.5, len(historique) - .5)
        ax_c.set_ylim(ymin, ymax)
        ax_c.set_xlabel("itération" if "T" not in h else "essai")
        ax_c.set_ylabel("longueur du tour")
        ax_c.grid(alpha=.3)
        ax_c.legend(loc="upper right", fontsize=8)
        ax_c.set_title("Évolution du coût")

    fig.tight_layout()
    return FuncAnimation(fig, maj, frames=len(historique), interval=intervalle,
                         repeat=True)


# ----------------------------------------------------------------------
def sauvegarder(anim, chemin, fps=2):
    """Enregistre l'animation (.gif via Pillow, .mp4 via ffmpeg)."""
    os.makedirs(os.path.dirname(chemin) or ".", exist_ok=True)
    if chemin.lower().endswith(".gif"):
        anim.save(chemin, writer=PillowWriter(fps=fps), dpi=80)
    else:
        anim.save(chemin, writer="ffmpeg", fps=fps, dpi=120)
    print(f"  -> animation enregistrée : {chemin}")


def afficher():
    plt.show()
