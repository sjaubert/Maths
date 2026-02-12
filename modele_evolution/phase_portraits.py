"""
Portraits de phase de trois systèmes d'équations différentielles ordinaires (EDO).

Systèmes reproduits à partir de l'illustration euler.jpg :
  1) ẋ = sin(x² + y²),  ẏ = sin(xy)
  2) ẋ = sin(x)·sin(y), ẏ = cos(xy)
  3) ẋ = y(y-1)(y+1),   ẏ = sin(x+y)

Utilise matplotlib pour tracer les lignes de courant (streamplot).
"""

import numpy as np
import matplotlib.pyplot as plt


# ---------------------------------------------------------------------------
# Définition des trois systèmes
# ---------------------------------------------------------------------------

def systeme_1(x, y):
    """ẋ = sin(x² + y²), ẏ = sin(xy)"""
    dx = np.sin(x**2 + y**2)
    dy = np.sin(x * y)
    return dx, dy


def systeme_2(x, y):
    """ẋ = sin(x)·sin(y), ẏ = cos(xy)"""
    dx = np.sin(x) * np.sin(y)
    dy = np.cos(x * y)
    return dx, dy


def systeme_3(x, y):
    """ẋ = y(y-1)(y+1), ẏ = sin(x+y)"""
    dx = y * (y - 1) * (y + 1)
    dy = np.sin(x + y)
    return dx, dy


# ---------------------------------------------------------------------------
# Configuration des tracés
# ---------------------------------------------------------------------------

systemes = [
    {
        "nom": r"$\dot{x} = \sin(x^2+y^2),\;\dot{y} = \sin(xy)$",
        "func": systeme_1,
        "xlim": (-3.5, 3.5),
        "ylim": (-3.5, 3.5),
        "densite": 3.0,
    },
    {
        "nom": r"$\dot{x} = \sin(x)\sin(y),\;\dot{y} = \cos(xy)$",
        "func": systeme_2,
        "xlim": (-5, 5),
        "ylim": (-5, 5),
        "densite": 3.0,
    },
    {
        "nom": r"$\dot{x} = y(y-1)(y+1),\;\dot{y} = \sin(x+y)$",
        "func": systeme_3,
        "xlim": (-5, 5),
        "ylim": (-3, 3),
        "densite": 3.0,
    },
]


def tracer_portrait(ax, systeme, n_points=500):
    """Trace le portrait de phase d'un système sur l'axe donné."""
    xlim = systeme["xlim"]
    ylim = systeme["ylim"]
    x = np.linspace(xlim[0], xlim[1], n_points)
    y = np.linspace(ylim[0], ylim[1], n_points)
    X, Y = np.meshgrid(x, y)

    DX, DY = systeme["func"](X, Y)

    # Normaliser la vitesse pour la coloration
    speed = np.sqrt(DX**2 + DY**2)
    # Éviter division par zéro pour le line-width
    speed_safe = np.where(speed == 0, 1e-10, speed)

    # Épaisseur de ligne proportionnelle à la vitesse (entre 0.3 et 1.5)
    lw = 0.3 + 1.2 * speed / speed_safe.max()

    ax.streamplot(
        X, Y, DX, DY,
        color="black",
        linewidth=lw,
        density=systeme["densite"],
        arrowsize=0.5,
        arrowstyle="->",
    )

    # Axes x et y passant par l'origine
    ax.axhline(0, color="black", linewidth=0.6)
    ax.axvline(0, color="black", linewidth=0.6)

    ax.set_xlim(xlim)
    ax.set_ylim(ylim)
    ax.set_aspect("equal")
    ax.set_title(systeme["nom"], fontsize=14, pad=10)
    ax.set_xlabel("x")
    ax.set_ylabel("y")


# ---------------------------------------------------------------------------
# Tracé principal
# ---------------------------------------------------------------------------

def main():
    fig, axes = plt.subplots(3, 1, figsize=(8, 22))
    fig.suptitle("Portraits de phase — Modèles d'évolution", fontsize=16, y=0.98)

    for ax, sys in zip(axes, systemes):
        tracer_portrait(ax, sys)

    plt.tight_layout(rect=[0, 0, 1, 0.97])
    plt.savefig("phase_portraits.png", dpi=200, bbox_inches="tight")
    print("Figure sauvegardée dans phase_portraits.png")
    plt.show()


if __name__ == "__main__":
    main()
