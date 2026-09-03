# -*- coding: utf-8 -*-
"""Genera las figuras de la encuesta (datos ILUSTRATIVOS, n=169) para 1.12.4."""
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

OUT = "_figs"
os.makedirs(OUT, exist_ok=True)
N = 169

# Paleta sobria
C = ["#2E5A88", "#4E8FCB", "#88B7DD", "#A7C7E7", "#C9DCEE"]
ACC = ["#1F4E79", "#C0504D", "#9BBB59", "#8064A2", "#4BACC6"]

plt.rcParams.update({
    "font.family": "serif",
    "font.size": 11,
    "axes.titlesize": 12,
    "figure.dpi": 150,
})


def pct(v, total=N):
    return f"{v/total*100:.1f}%"


def save(fig, name):
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, name), bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print("ok", name)


def bar_chart(labels, values, name, ylabel="Número de encuestados",
              colors=None, rotate=0, total=N, annot_pct=True):
    fig, ax = plt.subplots(figsize=(6.3, 3.5))
    colors = colors or C[: len(values)]
    bars = ax.bar(range(len(values)), values, color=colors, edgecolor="#33333322")
    ax.set_xticks(range(len(labels)))
    ax.set_xticklabels(labels, rotation=rotate, ha="center" if rotate == 0 else "right")
    ax.set_ylabel(ylabel)
    ax.set_ylim(0, max(values) * 1.18)
    for b, v in zip(bars, values):
        txt = f"{v}\n({pct(v, total)})" if annot_pct else str(v)
        ax.text(b.get_x() + b.get_width() / 2, v + max(values) * 0.01, txt,
                ha="center", va="bottom", fontsize=8.5)
    ax.spines[["top", "right"]].set_visible(False)
    save(fig, name)


def pie_chart(labels, values, name, colors=None):
    fig, ax = plt.subplots(figsize=(5.6, 3.8))
    colors = colors or C[: len(values)]
    wedges, _, autot = ax.pie(
        values, colors=colors, autopct=lambda p: f"{p:.1f}%",
        startangle=90, pctdistance=0.75,
        wedgeprops=dict(edgecolor="white", linewidth=1.5),
        textprops=dict(fontsize=9))
    ax.legend(wedges, [f"{l} ({v})" for l, v in zip(labels, values)],
              loc="center left", bbox_to_anchor=(0.98, 0.5), fontsize=8.5, frameon=False)
    ax.axis("equal")
    save(fig, name)


def grouped_bar(group_labels, series, name, ylabel="Número de encuestados"):
    # series: dict nombre -> list (uno por grupo)
    fig, ax = plt.subplots(figsize=(6.6, 3.7))
    n_series = len(series)
    x = np.arange(len(group_labels))
    w = 0.8 / n_series
    for i, (sname, vals) in enumerate(series.items()):
        off = (i - (n_series - 1) / 2) * w
        bars = ax.bar(x + off, vals, w, label=sname, color=ACC[i], edgecolor="#33333322")
        for b, v in zip(bars, vals):
            if v > 0:
                ax.text(b.get_x() + b.get_width() / 2, v + 0.5, str(v),
                        ha="center", va="bottom", fontsize=7.5)
    ax.set_xticks(x)
    ax.set_xticklabels(group_labels)
    ax.set_ylabel(ylabel)
    ax.legend(fontsize=8.5, frameon=False, ncol=n_series)
    ax.spines[["top", "right"]].set_visible(False)
    ax.set_ylim(0, max(max(v) for v in series.values()) * 1.2)
    save(fig, name)


# ---------------- DEMOGRÁFICAS ----------------
pie_chart(["Masculino", "Femenino", "Prefiero no indicar"], [98, 67, 4],
          "fig01_genero.png", colors=[C[0], ACC[1], C[3]])

bar_chart(["18-24", "25-30", "31-40", "41-50", "Mayor de 50"],
          [61, 52, 38, 13, 5], "fig02_edad.png")

bar_chart(["Menos de\n3 meses", "3 a 6\nmeses", "6 meses\na 1 año", "Más de\n1 año"],
          [47, 58, 39, 25], "fig03_antiguedad.png")

# ---------------- CONTENIDO ----------------
# Q1 plan entrenamiento
pie_chart(["Entrenador certificado", "Internet o una aplicación", "Sin plan definido"],
          [24, 71, 74], "fig04_q1_plan_entreno.png")
# Q2 plan nutricional
pie_chart(["Nutricionista certificado", "Internet o una aplicación", "Sin plan definido"],
          [15, 62, 92], "fig05_q2_plan_nutricion.png")
# Q3 frecuencia semanal
bar_chart(["1 a 2 días", "3 a 4 días", "5 a 6 días", "7 días"],
          [22, 79, 56, 12], "fig06_q3_frecuencia.png")
# Q4 dificultades (multi-selección)
bar_chart(["Estancamiento\nde metas", "Lesiones por\nmala ejecución",
           "Confusión sobre\nqué comer", "Abandono\ntemporal", "Ninguna\ndificultad"],
          [112, 58, 121, 74, 18], "fig07_q4_dificultades.png",
          ylabel="Menciones (selección múltiple)")
# Q5 gasto mensual disponible
bar_chart(["No puedo\npagar", "Menos de\nQ200", "Q200 a\nQ400", "Q400 a\nQ800", "Más de\nQ800"],
          [61, 48, 39, 17, 4], "fig08_q5_gasto.png")
# Q6 conocimiento cálculo calorías (Likert)
bar_chart(["1\nMuy bajo", "2", "3", "4", "5\nMuy alto"],
          [44, 51, 41, 22, 11], "fig09_q6_conocimiento.png", colors=C)
# Q7 dispositivo
pie_chart(["Teléfono inteligente", "Computadora portátil", "Tableta", "Computadora de escritorio"],
          [139, 18, 7, 5], "fig10_q7_dispositivo.png", colors=[C[0], C[1], ACC[2], C[3]])
# Q8 facilidad de uso (Likert)
bar_chart(["1\nMuy difícil", "2", "3", "4", "5\nMuy fácil"],
          [3, 9, 28, 69, 60], "fig11_q8_facilidad.png", colors=C)
# Q9 disposición a usar
bar_chart(["Definitivamente\nsí", "Probablemente\nsí", "No estoy\nseguro/a",
           "Probablemente\nno", "Definitivamente\nno"],
          [88, 57, 17, 5, 2], "fig12_q9_disposicion.png",
          colors=["#1F7A3D", "#5DAE66", "#C9C24A", "#D08A4E", "#C0504D"])
# Q10 mayor beneficio
bar_chart(["Ahorro en\nasesorías", "Acceso a\nplanes 24/7", "Seguimiento\nautomático",
           "Alimentos\nlocales", "Otro"],
          [54, 41, 33, 36, 5], "fig13_q10_beneficio.png")

# ---------------- CRUZADAS ----------------
# C1 Disposición x Género
grouped_bar(["Masculino", "Femenino", "Prefiero no indicar"],
            {"Sí (def. + prob.)": [86, 56, 3],
             "No estoy seguro/a": [9, 8, 0],
             "No (prob. + def.)": [3, 3, 1]},
            "fig14_cruce_disposicion_genero.png")
# C2 Facilidad x Edad
grouped_bar(["18-24", "25-30", "31-40", "41-50", ">50"],
            {"Baja (1-2)": [2, 3, 3, 3, 1],
             "Media (3)": [7, 8, 8, 3, 2],
             "Alta (4-5)": [52, 41, 27, 7, 2]},
            "fig15_cruce_facilidad_edad.png")

print("TOTAL figuras:", len(os.listdir(OUT)))
