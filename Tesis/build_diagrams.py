# -*- coding: utf-8 -*-
"""Diagramas para Capitulo II (teoria) y Capitulo III (arquitectura)."""
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Circle, Rectangle
import numpy as np

OUT = "_figs"
os.makedirs(OUT, exist_ok=True)
plt.rcParams.update({"font.family": "serif"})

BLUE = "#2E5A88"; LBLUE = "#A7C7E7"; MBLUE = "#4E8FCB"
GREEN = "#9BBB59"; ORANGE = "#D08A4E"; RED = "#C0504D"; GRAY = "#6E7B8B"


def box(ax, x, y, w, h, text, fc=LBLUE, ec=BLUE, fs=10, tc="black", bold=False, round=0.04):
    p = FancyBboxPatch((x, y), w, h, boxstyle=f"round,pad=0.01,rounding_size={round}",
                       linewidth=1.6, edgecolor=ec, facecolor=fc, zorder=2)
    ax.add_patch(p)
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=fs,
            color=tc, fontweight="bold" if bold else "normal", zorder=3, wrap=True)


def arrow(ax, x1, y1, x2, y2, color=GRAY, style="-|>", lw=1.6, rad=0.0):
    a = FancyArrowPatch((x1, y1), (x2, y2), arrowstyle=style, mutation_scale=14,
                        color=color, lw=lw, zorder=1,
                        connectionstyle=f"arc3,rad={rad}")
    ax.add_patch(a)


def save(fig, name):
    fig.savefig(os.path.join(OUT, name), dpi=150, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print("ok", name)


# ---------- 1. Estructura de una red neuronal artificial ----------
def red_neuronal():
    fig, ax = plt.subplots(figsize=(7, 4.2))
    layers = [3, 5, 5, 1]
    labels = ["Capa de\nentrada", "Capa oculta", "Capa oculta", "Capa de\nsalida"]
    xs = np.linspace(0.1, 0.9, len(layers))
    coords = []
    for li, (n, x) in enumerate(zip(layers, xs)):
        ys = np.linspace(0.18, 0.82, n) if n > 1 else [0.5]
        col = []
        for y in ys:
            c = Circle((x, y), 0.028, facecolor=LBLUE if 0 < li < len(layers)-1 else (GREEN if li==0 else ORANGE),
                       edgecolor=BLUE, lw=1.4, zorder=3)
            ax.add_patch(c)
            col.append((x, y))
        coords.append(col)
        ax.text(x, 0.05, labels[li], ha="center", va="center", fontsize=9, color=BLUE)
    # connections
    for li in range(len(coords) - 1):
        for (x1, y1) in coords[li]:
            for (x2, y2) in coords[li + 1]:
                ax.plot([x1, x2], [y1, y2], color="#BBBBBB", lw=0.5, zorder=1)
    ax.set_xlim(0, 1); ax.set_ylim(0, 0.95); ax.axis("off")
    save(fig, "figd1_red_neuronal.png")


# ---------- 2. Relacion IA - ML - DL - RNA ----------
def ia_ml_dl():
    fig, ax = plt.subplots(figsize=(6.0, 4.4))
    data = [("Inteligencia Artificial", 0.02, "#DCE6F1"),
            ("Aprendizaje Automático", 0.13, "#BBD3EA"),
            ("Aprendizaje Profundo", 0.24, "#8FB8DE"),
            ("Redes Neuronales\nArtificiales", 0.35, "#5D93C4")]
    for txt, pad, color in data:
        w = 1 - 2 * pad
        r = FancyBboxPatch((pad, pad * 0.85), w, 0.92 - pad * 1.7,
                           boxstyle="round,pad=0.005,rounding_size=0.02",
                           linewidth=1.5, edgecolor=BLUE, facecolor=color, zorder=1)
        ax.add_patch(r)
    ax.text(0.5, 0.86, "Inteligencia Artificial", ha="center", fontsize=11, fontweight="bold", color=BLUE)
    ax.text(0.5, 0.72, "Aprendizaje Automático", ha="center", fontsize=10, fontweight="bold", color=BLUE)
    ax.text(0.5, 0.58, "Aprendizaje Profundo", ha="center", fontsize=10, fontweight="bold", color="white")
    ax.text(0.5, 0.40, "Redes Neuronales\nArtificiales", ha="center", fontsize=10, fontweight="bold", color="white")
    ax.set_xlim(0, 1); ax.set_ylim(0, 0.95); ax.axis("off")
    save(fig, "figd2_ia_ml_dl.png")


# ---------- 3. Sistema: entrada-proceso-salida-retroalimentacion ----------
def sistema():
    fig, ax = plt.subplots(figsize=(7.2, 3.0))
    box(ax, 0.04, 0.45, 0.20, 0.30, "Entrada", fc=GREEN, tc="white", bold=True)
    box(ax, 0.40, 0.45, 0.20, 0.30, "Proceso", fc=MBLUE, tc="white", bold=True)
    box(ax, 0.76, 0.45, 0.20, 0.30, "Salida", fc=ORANGE, tc="white", bold=True)
    arrow(ax, 0.24, 0.60, 0.40, 0.60)
    arrow(ax, 0.60, 0.60, 0.76, 0.60)
    # retroalimentacion
    arrow(ax, 0.86, 0.45, 0.14, 0.20, color=RED, rad=-0.25)
    ax.text(0.5, 0.10, "Retroalimentación", ha="center", fontsize=10, color=RED, fontweight="bold")
    ax.set_xlim(0, 1); ax.set_ylim(0, 0.85); ax.axis("off")
    save(fig, "figd3_sistema.png")


# ---------- 4. Arquitectura cliente-servidor ----------
def cliente_servidor():
    fig, ax = plt.subplots(figsize=(7.4, 3.6))
    box(ax, 0.03, 0.35, 0.24, 0.34, "Cliente\n(navegador web)\nReact + HTML5/CSS3", fc=GREEN, tc="white", bold=True, fs=9)
    box(ax, 0.40, 0.55, 0.30, 0.26, "Servidor de aplicación\nFastAPI (API REST)", fc=MBLUE, tc="white", bold=True, fs=9)
    box(ax, 0.40, 0.18, 0.30, 0.26, "Motor neuronal\nPython + TensorFlow/Keras", fc=BLUE, tc="white", bold=True, fs=9)
    box(ax, 0.78, 0.35, 0.20, 0.34, "Base de datos\nMySQL", fc=ORANGE, tc="white", bold=True, fs=9)
    arrow(ax, 0.27, 0.55, 0.40, 0.62, color=GRAY)
    arrow(ax, 0.40, 0.58, 0.27, 0.50, color=GRAY)
    ax.text(0.335, 0.66, "Petición\nJSON", ha="center", fontsize=7.5, color=BLUE)
    arrow(ax, 0.55, 0.55, 0.55, 0.44, color=GRAY, style="<|-|>")
    arrow(ax, 0.70, 0.52, 0.78, 0.52, color=GRAY, style="<|-|>")
    ax.text(0.74, 0.56, "SQL", ha="center", fontsize=7.5, color=BLUE)
    ax.set_xlim(0, 1); ax.set_ylim(0.1, 0.85); ax.axis("off")
    save(fig, "figd4_cliente_servidor.png")


# ---------- 5. Patron MVC ----------
def mvc():
    fig, ax = plt.subplots(figsize=(6.4, 3.8))
    box(ax, 0.36, 0.70, 0.28, 0.20, "Controlador", fc=MBLUE, tc="white", bold=True)
    box(ax, 0.06, 0.20, 0.28, 0.20, "Modelo", fc=BLUE, tc="white", bold=True)
    box(ax, 0.66, 0.20, 0.28, 0.20, "Vista", fc=ORANGE, tc="white", bold=True)
    arrow(ax, 0.42, 0.70, 0.22, 0.40, color=GRAY)
    ax.text(0.24, 0.57, "actualiza", fontsize=8, color=GRAY)
    arrow(ax, 0.58, 0.70, 0.78, 0.40, color=GRAY)
    ax.text(0.66, 0.57, "selecciona", fontsize=8, color=GRAY)
    arrow(ax, 0.34, 0.27, 0.66, 0.27, color=GRAY, style="-|>", rad=-0.2)
    ax.text(0.5, 0.13, "consulta datos", ha="center", fontsize=8, color=GRAY)
    arrow(ax, 0.72, 0.40, 0.55, 0.70, color=GRAY)
    ax.text(0.70, 0.57, "eventos\ndel usuario", fontsize=8, color=GRAY)
    ax.set_xlim(0, 1); ax.set_ylim(0.05, 0.95); ax.axis("off")
    save(fig, "figd5_mvc.png")


# ---------- 6. Flujo de datos por la API REST ----------
def flujo():
    fig, ax = plt.subplots(figsize=(7.6, 2.7))
    pasos = [("Usuario\ningresa datos", GREEN), ("React\n(interfaz)", MBLUE),
             ("API REST\nFastAPI", BLUE), ("Modelo\nneuronal", "#3A6EA5"),
             ("MySQL", ORANGE)]
    xs = np.linspace(0.02, 0.80, len(pasos))
    w = 0.16
    for (txt, col), x in zip(pasos, xs):
        box(ax, x, 0.40, w, 0.34, txt, fc=col, tc="white", bold=True, fs=8.5)
    for i in range(len(pasos) - 1):
        arrow(ax, xs[i] + w, 0.57, xs[i + 1], 0.57, color=GRAY)
    arrow(ax, xs[-1] + w/2, 0.40, xs[1] + w/2, 0.22, color=RED, rad=0.25)
    ax.text(0.5, 0.08, "Respuesta: plan de entrenamiento y nutrición (formato JSON)",
            ha="center", fontsize=8.5, color=RED, fontweight="bold")
    ax.set_xlim(0, 1); ax.set_ylim(0.02, 0.80); ax.axis("off")
    save(fig, "figd6_flujo_api.png")


# ---------- 7. Modelo entidad-relacion simplificado ----------
def er():
    fig, ax = plt.subplots(figsize=(7.4, 4.0))
    box(ax, 0.02, 0.55, 0.22, 0.26, "USUARIO\n— id_usuario\n— nombre\n— rol", fc=LBLUE, fs=8.5)
    box(ax, 0.39, 0.70, 0.24, 0.26, "PERFIL_BIOMÉTRICO\n— peso, edad\n— estatura, objetivo", fc=LBLUE, fs=8.5)
    box(ax, 0.39, 0.34, 0.24, 0.26, "PLAN\n— id_plan\n— calorías\n— macronutrientes", fc=LBLUE, fs=8.5)
    box(ax, 0.76, 0.70, 0.22, 0.24, "ALIMENTO\n— id_alimento\n— nombre, kcal", fc="#D6E4C4", ec=GREEN, fs=8.5)
    box(ax, 0.76, 0.36, 0.22, 0.24, "EJERCICIO\n— id_ejercicio\n— grupo muscular", fc="#D6E4C4", ec=GREEN, fs=8.5)
    arrow(ax, 0.24, 0.66, 0.39, 0.78, color=GRAY, style="-")
    arrow(ax, 0.24, 0.64, 0.39, 0.45, color=GRAY, style="-")
    arrow(ax, 0.63, 0.78, 0.76, 0.80, color=GRAY, style="-")
    arrow(ax, 0.63, 0.45, 0.76, 0.46, color=GRAY, style="-")
    ax.set_xlim(0, 1); ax.set_ylim(0.30, 0.98); ax.axis("off")
    save(fig, "figd7_er.png")


red_neuronal()
ia_ml_dl()
sistema()
cliente_servidor()
mvc()
flujo()
er()
print("diagramas listos")
