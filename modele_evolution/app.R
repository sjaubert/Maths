# =============================================================================
# Portraits de phase interactifs — Modèles d'évolution
# Application Shiny avec intégration numérique (RK4 pur R) et ggplot2
#
# Cliquez sur le graphique pour ajouter des trajectoires
# depuis les conditions initiales de votre choix.
#
# Compatible shinylive (WebAssembly) — pas de dépendance compilée.
# =============================================================================

library(shiny)
library(ggplot2)

# ---------------------------------------------------------------------------
# Définition des systèmes d'EDO
# ---------------------------------------------------------------------------

systeme_1 <- function(t, state, params) {
  x <- state["x"]; y <- state["y"]
  list(c(sin(x^2 + y^2), sin(x * y)))
}

systeme_2 <- function(t, state, params) {
  x <- state["x"]; y <- state["y"]
  list(c(sin(x) * sin(y), cos(x * y)))
}

systeme_3 <- function(t, state, params) {
  x <- state["x"]; y <- state["y"]
  list(c(y * (y - 1) * (y + 1), sin(x + y)))
}

systeme_4 <- function(t, state, params) {
  x <- state["x"]; y <- state["y"]
  g <- params$g
  L <- params$L
  # x = theta, y = theta_dot
  # theta_dot_dot = - (g/L) * sin(theta)
  list(c(y, - (g / L) * sin(x)))
}

# ---------------------------------------------------------------------------
# Métadonnées des systèmes
# ---------------------------------------------------------------------------

systemes <- list(
  list(
    nom    = "Système 1",
    label  = expression(dot(x) == sin(x^2 + y^2) * "," ~~ dot(y) == sin(xy)),
    func   = systeme_1,
    xlim   = c(-3.5, 3.5),
    ylim   = c(-3.5, 3.5),
    params = list()
  ),
  list(
    nom    = "Système 2",
    label  = expression(dot(x) == sin(x) * sin(y) * "," ~~ dot(y) == cos(xy)),
    func   = systeme_2,
    xlim   = c(-5, 5),
    ylim   = c(-5, 5),
    params = list()
  ),
  list(
    nom    = "Système 3",
    label  = expression(dot(x) == y(y - 1)(y + 1) * "," ~~ dot(y) == sin(x + y)),
    func   = systeme_3,
    xlim   = c(-5, 5),
    ylim   = c(-3, 3),
    params = list()
  ),
  list(
    nom    = "Pendule Simple",
    label  = expression(dot(theta) == omega * "," ~~ dot(omega) == -frac(g, L) * sin(theta)),
    func   = systeme_4,
    xlim   = c(-10, 10), # ~ -3pi a +3pi
    ylim   = c(-6, 6),
    params = list(g = 9.81, L = 1)
  )
)

# ---------------------------------------------------------------------------
# Palette de couleurs pour les trajectoires
# ---------------------------------------------------------------------------

palette_trajectoires <- c(
  "#E63946", "#457B9D", "#2A9D8F", "#E9C46A", "#F4A261",
  "#264653", "#A8DADC", "#D62828", "#023E8A", "#6A0572",
  "#118AB2", "#EF476F", "#06D6A0", "#FFD166", "#073B4C",
  "#9B2226", "#AE2012", "#BB3E03", "#CA6702", "#EE9B00",
  "#94D2BD", "#0A9396", "#005F73", "#001219", "#B5179E"
)

# ---------------------------------------------------------------------------
# Intégrateur Runge-Kutta 4 pur R (remplace deSolve pour compatibilité wasm)
# ---------------------------------------------------------------------------

rk4_integrate <- function(sys_func, x0, y0, tmax, dt, params = NULL) {
  n_steps <- max(1, round(abs(tmax / dt)))
  xs <- numeric(n_steps + 1)
  ys <- numeric(n_steps + 1)
  ts <- numeric(n_steps + 1)
  xs[1] <- x0; ys[1] <- y0; ts[1] <- 0
  h <- dt

  for (i in seq_len(n_steps)) {
    state <- c(x = xs[i], y = ys[i])
    k1 <- unlist(sys_func(ts[i], state, params))
    k2 <- unlist(sys_func(ts[i] + h/2, state + h/2 * k1, params))
    k3 <- unlist(sys_func(ts[i] + h/2, state + h/2 * k2, params))
    k4 <- unlist(sys_func(ts[i] + h,   state + h   * k3, params))
    new_state <- state + h / 6 * (k1 + 2*k2 + 2*k3 + k4)
    xs[i+1] <- new_state[1]
    ys[i+1] <- new_state[2]
    ts[i+1] <- ts[i] + h
    # Arrêter si divergence
    if (any(!is.finite(new_state)) || max(abs(new_state)) > 100) {
      xs <- xs[1:i]; ys <- ys[1:i]; ts <- ts[1:i]
      break
    }
  }
  data.frame(time = ts, x = xs, y = ys)
}

# ---------------------------------------------------------------------------
# Fonction d'intégration d'une trajectoire (avant + arrière)
# ---------------------------------------------------------------------------

integrer_trajectoire <- function(sys_func, x0, y0, tmax = 20, dt = 0.02, params = NULL) {
  # Intégration vers l'avant
  sol_fwd <- tryCatch(
    rk4_integrate(sys_func, x0, y0, tmax, dt, params),
    error = function(e) data.frame(time = 0, x = x0, y = y0)
  )

  # Intégration vers l'arrière (dt négatif)
  sol_bwd <- tryCatch(
    rk4_integrate(sys_func, x0, y0, tmax, -dt, params),
    error = function(e) data.frame(time = 0, x = x0, y = y0)
  )

  # Combiner (arrière inversé + avant)
  sol_bwd <- sol_bwd[nrow(sol_bwd):1, ]
  rbind(sol_bwd, sol_fwd[-1, ])
}

# ---------------------------------------------------------------------------
# Fonction pour générer la grille du champ de vecteurs
# ---------------------------------------------------------------------------

generer_champ <- function(sys_func, xlim, ylim, n = 25, params = NULL) {
  x_seq <- seq(xlim[1], xlim[2], length.out = n)
  y_seq <- seq(ylim[1], ylim[2], length.out = n)
  grid  <- expand.grid(x = x_seq, y = y_seq)

  derivees <- t(sapply(1:nrow(grid), function(i) {
    res <- sys_func(0, c(x = grid$x[i], y = grid$y[i]), params)
    unlist(res)
  }))

  grid$dx <- derivees[, 1]
  grid$dy <- derivees[, 2]

  # Normaliser pour l'affichage
  norme <- sqrt(grid$dx^2 + grid$dy^2)
  norme[norme == 0] <- 1e-10
  scale_factor <- min(diff(x_seq)[1], diff(y_seq)[1]) * 0.4
  grid$dx_norm <- grid$dx / norme * scale_factor
  grid$dy_norm <- grid$dy / norme * scale_factor
  grid$vitesse <- norme

  grid
}

# ---------------------------------------------------------------------------
# Générer des trajectoires de fond (grille régulière)
# ---------------------------------------------------------------------------

generer_fond <- function(sys_func, xlim, ylim, nx = 8, ny = 8, tmax = 15, params = NULL) {
  x_seq <- seq(xlim[1] * 0.9, xlim[2] * 0.9, length.out = nx)
  y_seq <- seq(ylim[1] * 0.9, ylim[2] * 0.9, length.out = ny)
  init  <- expand.grid(x0 = x_seq, y0 = y_seq)

  all_traj <- do.call(rbind, lapply(1:nrow(init), function(i) {
    traj <- integrer_trajectoire(sys_func, init$x0[i], init$y0[i],
                                  tmax = tmax, dt = 0.03, params = params)
    # Couper si sort du domaine
    in_dom <- traj$x >= xlim[1] * 1.2 & traj$x <= xlim[2] * 1.2 &
              traj$y >= ylim[1] * 1.2 & traj$y <= ylim[2] * 1.2
    # Garder la plus longue séquence continue dans le domaine
    rle_dom <- rle(in_dom)
    if (any(rle_dom$values)) {
      best <- which.max(rle_dom$lengths * rle_dom$values)
      end_idx <- sum(rle_dom$lengths[1:best])
      start_idx <- end_idx - rle_dom$lengths[best] + 1
      traj <- traj[start_idx:end_idx, ]
    }
    traj$id <- i
    traj
  }))

  all_traj
}


# =============================================================================
# Interface utilisateur (UI)
# =============================================================================

ui <- fluidPage(
  tags$head(
    tags$style(HTML("
      body {
        background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
        color: #e0e0e0;
        font-family: 'Segoe UI', 'Helvetica Neue', Arial, sans-serif;
      }
      .well {
        background-color: rgba(255,255,255,0.05);
        border: 1px solid rgba(255,255,255,0.1);
        border-radius: 12px;
      }
      h2 {
        color: #a8dadc;
        font-weight: 300;
        letter-spacing: 1px;
      }
      h4 {
        color: #f1faee;
        font-weight: 400;
      }
      .btn-danger {
        background: linear-gradient(135deg, #e63946, #d62828);
        border: none; border-radius: 8px;
      }
      .btn-danger:hover {
        background: linear-gradient(135deg, #d62828, #9b2226);
      }
      .selectize-input {
        background-color: rgba(255,255,255,0.08) !important;
        color: #f1faee !important;
        border: 1px solid rgba(255,255,255,0.15) !important;
        border-radius: 8px !important;
      }
      .selectize-dropdown {
        background-color: #302b63 !important;
        color: #f1faee !important;
        border: 1px solid rgba(255,255,255,0.15) !important;
      }
      .selectize-dropdown-content .option {
        color: #f1faee !important;
      }
      .selectize-dropdown-content .active {
        background-color: rgba(168,218,220,0.3) !important;
      }
      .shiny-input-container label { color: #a8dadc; }
      #info_panel {
        background: rgba(255,255,255,0.05);
        border: 1px solid rgba(168,218,220,0.2);
        border-radius: 10px;
        padding: 12px 16px;
        margin-top: 10px;
        font-size: 13px;
        line-height: 1.6;
      }
      .slider-container .irs--shiny .irs-bar {
        background: #457b9d;
      }
    "))
  ),

  titlePanel(
    h2("\U0001f30c Portraits de phase — Modèles d'évolution", align = "center")
  ),

  sidebarLayout(
    sidebarPanel(
      width = 3,
      selectInput("systeme", h4("\U0001f4d0 Système d'EDO"),
        choices = c(
          "ẋ = sin(x²+y²), ẏ = sin(xy)"     = "1",
          "ẋ = sin(x)sin(y), ẏ = cos(xy)"    = "2",
          "ẋ = y(y-1)(y+1), ẏ = sin(x+y)"    = "3",
          "Pendule Simple"                  = "4"
        ),
        selected = "1"
      ),
      conditionalPanel(
        condition = "input.systeme == '4'",
        hr(style = "border-color: rgba(255,255,255,0.1);"),
        h4("\u2699\ufe0f Paramètres Pendule"),
        sliderInput("param_g", "Gravité g :", min = 1, max = 20, value = 9.81, step = 0.1),
        sliderInput("param_L", "Longueur L :", min = 0.1, max = 5, value = 1, step = 0.1)
      ),
      hr(style = "border-color: rgba(255,255,255,0.1);"),
      h4("\U0001f3af Conditions initiales"),
      p("Cliquez sur le graphique pour ajouter une trajectoire,",
        "ou entrez les coordonnées manuellement :"),
      fluidRow(
        column(6, numericInput("x0", "x₀ :", value = 1, step = 0.1)),
        column(6, numericInput("y0", "y₀ :", value = 1, step = 0.1))
      ),
      actionButton("ajouter", "\u2795 Ajouter trajectoire",
                    class = "btn btn-primary btn-block",
                    style = "width:100%; background: linear-gradient(135deg, #457b9d, #1d3557);
                             border:none; border-radius:8px; margin-bottom:10px;"),
      actionButton("effacer", "\U0001f5d1 Effacer tout",
                    class = "btn btn-danger btn-block",
                    style = "width:100%;"),
      hr(style = "border-color: rgba(255,255,255,0.1);"),
      h4("\u2699\ufe0f Options"),
      sliderInput("tmax", "Durée d'intégration :", min = 2, max = 40,
                   value = 15, step = 1),
      checkboxInput("show_field", "Afficher le champ de vecteurs", value = TRUE),
      checkboxInput("show_fond", "Trajectoires de fond", value = TRUE),
      div(id = "info_panel",
        HTML("<b>\U0001f4a1 Astuce :</b> Cliquez directement sur le graphique
              pour placer un point de départ. Changez de système avec le menu
              déroulant ci-dessus.")
      ),
      hr(style = "border-color: rgba(255,255,255,0.1);"),
      div(style = "text-align: center; color: #a8dadc; font-size: 13px; margin-top: 20px; opacity: 0.8;",
          tags$b("S. Jaubert"), br(),
          "Pôle Formation UIMM - CVDL"
      )
    ),

    mainPanel(
      width = 9,
      plotOutput("phase_plot", click = "plot_click",
                  height = "700px", width = "100%")
    )
  )
)


# =============================================================================
# Serveur
# =============================================================================

server <- function(input, output, session) {

  # Stockage réactif des trajectoires utilisateur
  trajectoires <- reactiveVal(list())

  # Quand le système change, effacer les trajectoires

  observeEvent(input$systeme, {
    trajectoires(list())
  })

  # Clic sur le graphique → ajouter une trajectoire
  observeEvent(input$plot_click, {
    x0 <- input$plot_click$x
    y0 <- input$plot_click$y
    if (!is.null(x0) && !is.null(y0)) {
      idx <- as.integer(input$systeme)
      sys <- systemes[[idx]]
      
      # Récupération des paramètres dynamiques
      params_dyn <- sys$params
      if (idx == 4) {
        params_dyn$g <- input$param_g
        params_dyn$L <- input$param_L
      }
      
      traj <- integrer_trajectoire(sys$func, x0, y0, tmax = input$tmax, params = params_dyn)

      # Couper au domaine
      traj <- traj[traj$x >= sys$xlim[1] * 1.3 & traj$x <= sys$xlim[2] * 1.3 &
                    traj$y >= sys$ylim[1] * 1.3 & traj$y <= sys$ylim[2] * 1.3, ]

      current <- trajectoires()
      n <- length(current) + 1
      couleur <- palette_trajectoires[((n - 1) %% length(palette_trajectoires)) + 1]
      current[[n]] <- list(data = traj, couleur = couleur, x0 = x0, y0 = y0)
      trajectoires(current)
    }
  })

  # Bouton Ajouter
  observeEvent(input$ajouter, {
    x0 <- input$x0
    y0 <- input$y0
    if (!is.null(x0) && !is.null(y0)) {
      idx <- as.integer(input$systeme)
      sys <- systemes[[idx]]
      
      params_dyn <- sys$params
      if (idx == 4) {
        params_dyn$g <- input$param_g
        params_dyn$L <- input$param_L
      }
      
      traj <- integrer_trajectoire(sys$func, x0, y0, tmax = input$tmax, params = params_dyn)
      traj <- traj[traj$x >= sys$xlim[1] * 1.3 & traj$x <= sys$xlim[2] * 1.3 &
                    traj$y >= sys$ylim[1] * 1.3 & traj$y <= sys$ylim[2] * 1.3, ]

      current <- trajectoires()
      n <- length(current) + 1
      couleur <- palette_trajectoires[((n - 1) %% length(palette_trajectoires)) + 1]
      current[[n]] <- list(data = traj, couleur = couleur, x0 = x0, y0 = y0)
      trajectoires(current)
    }
  })

  # Bouton Effacer
  observeEvent(input$effacer, {
    trajectoires(list())
  })

  # ----- Rendu du graphique -----
  output$phase_plot <- renderPlot({

    idx <- as.integer(input$systeme)
    sys <- systemes[[idx]]

    # Thème sombre élégant
    theme_phase <- theme_minimal(base_size = 14) +
      theme(
        plot.background  = element_rect(fill = "#1a1a2e", color = NA),
        panel.background = element_rect(fill = "#16213e", color = NA),
        panel.grid.major = element_line(color = "grey25", linewidth = 0.3),
        panel.grid.minor = element_blank(),
        axis.text        = element_text(color = "#a8a8b3", size = 11),
        axis.title       = element_text(color = "#a8dadc", size = 13),
        plot.title       = element_text(color = "#f1faee", size = 18,
                                         hjust = 0.5, face = "bold",
                                         margin = margin(b = 5)),
        plot.subtitle    = element_text(color = "#a8dadc", size = 13,
                                         hjust = 0.5,
                                         margin = margin(b = 15)),
        plot.margin      = margin(15, 20, 15, 15)
      )

    # Titres
    titres <- c(
      expression(dot(x) == sin(x^2 + y^2) * "," ~~ dot(y) == sin(xy)),
      expression(dot(x) == sin(x) %.% sin(y) * "," ~~ dot(y) == cos(xy)),
      expression(dot(x) == y(y - 1)(y + 1) * "," ~~ dot(y) == sin(x + y)),
      expression(dot(theta) == omega * "," ~~ dot(omega) == -frac(g, L) * sin(theta))
    )

    p <- ggplot() +
      coord_cartesian(xlim = sys$xlim, ylim = sys$ylim) +
      labs(
        title    = paste("Système", idx),
        subtitle = titres[idx],
        x = "x", y = "y"
      ) +
      theme_phase

    # Champ de vecteurs
    if (input$show_field) {
      params_dyn <- sys$params
      if (idx == 4) {
        params_dyn$g <- input$param_g
        params_dyn$L <- input$param_L
      }
      champ <- generer_champ(sys$func, sys$xlim, sys$ylim, n = 22, params = params_dyn)
      p <- p +
        geom_segment(
          data = champ,
          aes(x = x - dx_norm / 2, y = y - dy_norm / 2,
              xend = x + dx_norm / 2, yend = y + dy_norm / 2,
              alpha = vitesse),
          arrow = arrow(length = unit(0.06, "cm"), type = "closed"),
          color = "#4a6fa5",
          linewidth = 0.35
        ) +
        scale_alpha_continuous(range = c(0.2, 0.7), guide = "none")
    }

    # Trajectoires de fond (grises)
    if (input$show_fond) {
      params_dyn <- sys$params
      if (idx == 4) {
        params_dyn$g <- input$param_g
        params_dyn$L <- input$param_L
      }
      fond <- generer_fond(sys$func, sys$xlim, sys$ylim,
                           nx = 10, ny = 10, tmax = input$tmax, params = params_dyn)
      p <- p +
        geom_path(data = fond, aes(x = x, y = y, group = id),
                   color = "#5c6b80", linewidth = 0.25, alpha = 0.5)
    }

    # Axes passant par l'origine
    p <- p +
      geom_hline(yintercept = 0, color = "grey50", linewidth = 0.4) +
      geom_vline(xintercept = 0, color = "grey50", linewidth = 0.4)

    # Trajectoires utilisateur
    traj_list <- trajectoires()
    if (length(traj_list) > 0) {
      for (tr in traj_list) {
        p <- p +
          geom_path(data = tr$data, aes(x = x, y = y),
                     color = tr$couleur, linewidth = 0.9, alpha = 0.9) +
          geom_point(data = data.frame(x = tr$x0, y = tr$y0),
                      aes(x = x, y = y),
                      color = tr$couleur, size = 3, shape = 16) +
          geom_point(data = data.frame(x = tr$x0, y = tr$y0),
                      aes(x = x, y = y),
                      color = "white", size = 1.2, shape = 16)
        # Flèche directionnelle au milieu de la trajectoire
        n_pts <- nrow(tr$data)
        if (n_pts > 10) {
          mid <- round(n_pts * 0.6)
          p <- p +
            geom_segment(
              data = data.frame(
                x = tr$data$x[mid], y = tr$data$y[mid],
                xend = tr$data$x[mid + 1], yend = tr$data$y[mid + 1]
              ),
              aes(x = x, y = y, xend = xend, yend = yend),
              arrow = arrow(length = unit(0.25, "cm"), type = "closed"),
              color = tr$couleur, linewidth = 1.2
            )
        }
      }
    }

    p

  }, bg = "#1a1a2e")
}

# =============================================================================
# Lancement
# =============================================================================

shinyApp(ui = ui, server = server)
