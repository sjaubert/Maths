"""
Portraits de phase interactifs — Modèles d'évolution
Réécriture en Python (Matplotlib + Scipy) de l'application R Shiny.

Fonctionnalités :
- 4 systèmes dynamiques dont le Pendule Simple.
- Paramètres modifiables (Masse/Longueur) pour le pendule.
- Clic sur le graphique pour générer des trajectoires.
- Intégration numérique précise (RK45 via scipy).
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import RadioButtons, Slider, Button
from scipy.integrate import solve_ivp

# =============================================================================
# Définition des systèmes
# =============================================================================

def systeme_1(t, state, params):
    """ẋ = sin(x² + y²), ẏ = sin(xy)"""
    x, y = state
    return [np.sin(x**2 + y**2), np.sin(x * y)]

def systeme_2(t, state, params):
    """ẋ = sin(x)·sin(y), ẏ = cos(xy)"""
    x, y = state
    return [np.sin(x) * np.sin(y), np.cos(x * y)]

def systeme_3(t, state, params):
    """ẋ = y(y-1)(y+1), ẏ = sin(x+y)"""
    x, y = state
    return [y * (y - 1) * (y + 1), np.sin(x + y)]

def systeme_4(t, state, params):
    """Pendule Simple: ẋ = ω, ẏ = -(g/L)sin(θ)"""
    theta, omega = state
    g = params.get('g', 9.81)
    L = params.get('L', 1.0)
    return [omega, -(g / L) * np.sin(theta)]

# Liste des systèmes avec métadonnées
SYSTEMES = [
    {
        "id": 0,
        "nom": r"1) $\dot{x} = \sin(x^2+y^2),\;\dot{y} = \sin(xy)$",
        "func": systeme_1,
        "xlim": (-3.5, 3.5),
        "ylim": (-3.5, 3.5),
        "params": {}
    },
    {
        "id": 1,
        "nom": r"2) $\dot{x} = \sin(x)\sin(y),\;\dot{y} = \cos(xy)$",
        "func": systeme_2,
        "xlim": (-5, 5),
        "ylim": (-5, 5),
        "params": {}
    },
    {
        "id": 2,
        "nom": r"3) $\dot{x} = y(y-1)(y+1),\;\dot{y} = \sin(x+y)$",
        "func": systeme_3,
        "xlim": (-5, 5),
        "ylim": (-3, 3),
        "params": {}
    },
    {
        "id": 3,
        "nom": "4) Pendule Simple",
        "func": systeme_4,
        "xlim": (-10, 10),
        "ylim": (-6, 6),
        "params": {'g': 9.81, 'L': 1.0}
    }
]

# =============================================================================
# Classe de l'application interactive
# =============================================================================

class PhasePortraitApp:
    def __init__(self):
        # Configuration de la fenêtre
        self.fig = plt.figure(figsize=(12, 8))
        if self.fig.canvas.manager:
            self.fig.canvas.manager.set_window_title("Portraits de Phase Interactifs")
        
        # Layout : Grille pour UI (gauche) et Plot (droite)
        # On laisse de la place à gauche pour les contrôles
        plt.subplots_adjust(left=0.30, bottom=0.1)
        
        self.ax = self.fig.add_subplot(111)
        self.current_sys_idx = 0
        self.user_trajectories = [] # Liste de (x, y) arrays
        
        # --- UI Elements (Axes) ---
        ax_color = 'lightgoldenrodyellow'
        
        # Radio Buttons pour le choix du système
        bg_radio = plt.axes([0.02, 0.6, 0.22, 0.25], facecolor=ax_color)
        self.radio = RadioButtons(bg_radio, [s['nom'] for s in SYSTEMES], active=0)
        self.radio.on_clicked(self.change_system)
        
        # Sliders pour le Pendule (cachés par défaut si pas système 4)
        self.ax_g = plt.axes([0.05, 0.45, 0.18, 0.03], facecolor=ax_color)
        self.ax_L = plt.axes([0.05, 0.40, 0.18, 0.03], facecolor=ax_color)
        
        self.slider_g = Slider(self.ax_g, 'Gravité g', 1.0, 20.0, valinit=9.81)
        self.slider_L = Slider(self.ax_L, 'Longueur L', 0.1, 5.0, valinit=1.0)
        
        self.slider_g.on_changed(self.update_params)
        self.slider_L.on_changed(self.update_params)
        
        # Bouton Clear
        ax_clear = plt.axes([0.05, 0.25, 0.18, 0.05])
        self.btn_clear = Button(ax_clear, 'Effacer Trajectoires', hovercolor='0.975')
        self.btn_clear.on_clicked(self.clear_trajectories)
        
        # Gestion des événements souris
        self.fig.canvas.mpl_connect('button_press_event', self.on_click)
        
        # Initialisation
        self.update_ui_visibility()
        self.draw_system()

    def get_current_system(self):
        return SYSTEMES[self.current_sys_idx]

    def update_ui_visibility(self):
        """Affiche ou cache les sliders selon le système."""
        if self.current_sys_idx == 3: # Pendule
            self.ax_g.set_visible(True)
            self.ax_L.set_visible(True)
        else:
            self.ax_g.set_visible(False)
            self.ax_L.set_visible(False)

    def change_system(self, label):
        # Trouver l'index correspondant au label
        for i, s in enumerate(SYSTEMES):
            if s['nom'] == label:
                self.current_sys_idx = i
                break
        
        self.user_trajectories = [] # Reset user traj on change
        self.update_ui_visibility()
        self.draw_system()

    def update_params(self, val):
        """Callback pour les sliders."""
        sys = self.get_current_system()
        if self.current_sys_idx == 3:
            sys['params']['g'] = self.slider_g.val
            sys['params']['L'] = self.slider_L.val
            self.draw_system()

    def clear_trajectories(self, event):
        self.user_trajectories = []
        self.draw_system()

    def draw_system(self):
        self.ax.clear()
        sys = self.get_current_system()
        params = sys['params']
        
        # Grille pour le champ de vecteurs
        xlim = sys['xlim']
        ylim = sys['ylim']
        x = np.linspace(xlim[0], xlim[1], 25)
        y = np.linspace(ylim[0], ylim[1], 25)
        X, Y = np.meshgrid(x, y)
        
        # Calcul vectorisé (simple adaptation des fonctions pour meshgrid)
        # Note: nos fonctions attendent (x,y), ici il faut passer les arrays
        if self.current_sys_idx == 0:
            U = np.sin(X**2 + Y**2)
            V = np.sin(X * Y)
        elif self.current_sys_idx == 1:
            U = np.sin(X) * np.sin(Y)
            V = np.cos(X * Y)
        elif self.current_sys_idx == 2:
            U = Y * (Y - 1) * (Y + 1)
            V = np.sin(X + Y)
        elif self.current_sys_idx == 3:
            g = params['g']
            L = params['L']
            U = Y # Y est omega
            V = -(g/L) * np.sin(X) # X est theta

        # Normalisation pour l'affichage (éviter les flèches géantes)
        M = np.hypot(U, V)
        M[M == 0] = 1
        U_norm = U / M
        V_norm = V / M
        
        self.ax.quiver(X, Y, U_norm, V_norm, M, pivot='mid', cmap='viridis', width=0.003)
        
        # Dessiner les trajectoires utilisateur
        for traj in self.user_trajectories:
            self.ax.plot(traj[0], traj[1], 'r-', linewidth=1.5, alpha=0.8)
            self.ax.plot(traj[0][0], traj[1][0], 'ro', markersize=4) # point de départ

        self.ax.set_xlim(xlim)
        self.ax.set_ylim(ylim)
        self.ax.set_title(sys['nom'])
        self.ax.axhline(0, color='black', alpha=0.3)
        self.ax.axvline(0, color='black', alpha=0.3)
        
        self.fig.canvas.draw_idle()

    def on_click(self, event):
        """Gestion du clic pour ajouter une trajectoire."""
        if event.inaxes != self.ax:
            return
        
        x0, y0 = event.xdata, event.ydata
        sys = self.get_current_system()
        
        # Intégration numérique
        t_span = (0, 10)
        sol = solve_ivp(
            fun=lambda t, y: sys['func'](t, y, sys['params']),
            t_span=t_span,
            y0=[x0, y0],
            dense_output=True,
            max_step=0.05
        )
        
        # Intégration arrière (pour voir d'où on vient)
        sol_back = solve_ivp(
            fun=lambda t, y: sys['func'](t, y, sys['params']),
            t_span=(0, -10),
            y0=[x0, y0],
            dense_output=True,
            max_step=0.05
        )
        
        # Combiner avant et arrière
        t_eval = np.linspace(0, 10, 200)
        y_fwd = sol.sol(t_eval)
        
        t_eval_back = np.linspace(0, -10, 200)
        y_back = sol_back.sol(t_eval_back)
        
        full_x = np.concatenate((y_back[0][::-1], y_fwd[0]))
        full_y = np.concatenate((y_back[1][::-1], y_fwd[1]))
        
        self.user_trajectories.append((full_x, full_y))
        self.draw_system()

if __name__ == "__main__":
    app = PhasePortraitApp()
    plt.show()
