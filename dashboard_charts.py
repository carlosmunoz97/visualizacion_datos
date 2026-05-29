"""Gráficas parametrizadas para el dashboard interactivo (filtros y umbrales)."""

from __future__ import annotations

import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from matplotlib.patches import Patch

from config import (
    COLOR_ALERTA,
    COLOR_DESTACADO,
    COLOR_ESTADO,
    COLOR_FONDO,
    COLOR_METRICA,
    COLOR_NAVY,
    COLOR_NEUTRO,
    COLOR_NEUTRO_2,
    COLOR_REGION,
    COLOR_SEGMENTO_RETRASO,
    COLOR_TEXTO,
    COLOR_TEXTO_SEC,
    GRAY_PRESUP,
    GRAY_RETASO,
    ORDEN_ESTADO_A,
    ORDEN_REGION,
    ORDEN_SEGMENTO_RETRASO,
)
from data_loader import segmento_pct_retrasados


def fig_presupuesto_atencion_umbral(
    treemap_df: pd.DataFrame,
    *,
    umbral_pct: float = 5.0,
    titulo: str | None = None,
) -> go.Figure:
    """Barras de presupuesto; resalta en rojo los departamentos con % >= umbral."""
    plot_df = treemap_df.copy()
    if plot_df.empty:
        fig = go.Figure()
        fig.update_layout(title="Sin datos para el filtro aplicado", height=400)
        return fig

    plot_df["Presupuesto_Millones_USD"] = plot_df["Presupuesto_USD"] / 1_000_000
    regiones = [r for r in ORDEN_REGION if r in plot_df["Region"].unique()]
    plot_df["Region"] = pd.Categorical(plot_df["Region"], categories=regiones, ordered=True)
    plot_df = plot_df.sort_values(["Region", "Pct_Pais"], ascending=[True, False]).copy()

    destacar = plot_df["Pct_Pais"] >= umbral_pct
    plot_df["Color"] = np.where(destacar, COLOR_ALERTA, "#E5E7EB")
    plot_df["Texto_Barra"] = plot_df["Pct_Pais"].map(lambda x: f"{x:.1f}%")

    x_pos, x_labels, separadores, region_centers = [], [], [], {}
    pos, gap, indices = 0, 1.5, []

    for region in regiones:
        sub = plot_df[plot_df["Region"] == region]
        if sub.empty:
            continue
        posiciones = []
        for idx, row in sub.iterrows():
            x_pos.append(pos)
            indices.append(idx)
            if row["Pct_Pais"] >= umbral_pct:
                x_labels.append(f"<b style='color:{COLOR_ALERTA}'>{row['Departamento']}</b>")
            else:
                x_labels.append(
                    f"<span style='color:#9CA3AF'>{row['Departamento']}</span>"
                )
            posiciones.append(pos)
            pos += 1
        region_centers[region] = sum(posiciones) / len(posiciones)
        separadores.append(pos - 0.5 + gap / 2)
        pos += gap

    plot_df = plot_df.loc[indices].copy()
    plot_df["x_pos"] = x_pos

    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            x=plot_df["x_pos"],
            y=plot_df["Pct_Pais"],
            marker=dict(color=plot_df["Color"], line=dict(color="white", width=0.5)),
            text=plot_df["Texto_Barra"],
            textposition="outside",
            cliponaxis=False,
            customdata=plot_df[
                ["Region", "Departamento", "Presupuesto_Millones_USD", "Proyectos", "Pct_Pais"]
            ],
            hovertemplate=(
                "<b>%{customdata[1]}</b><br>Región: %{customdata[0]}<br>"
                "% presupuesto: %{customdata[4]:.2f}%<br>"
                "Presupuesto: USD %{customdata[2]:,.1f} M<br>"
                "Proyectos: %{customdata[3]}<extra></extra>"
            ),
        )
    )

    for sep in separadores[:-1]:
        fig.add_vline(x=sep, line_width=1, line_dash="dot", line_color="#D6DEE6")

    max_y = max(float(plot_df["Pct_Pais"].max()), umbral_pct, 1.0)
    for region, center in region_centers.items():
        fig.add_annotation(
            x=center, y=max_y * 1.22, text=f"<b>{region}</b>", showarrow=False,
            font=dict(size=11, color="#64748B"),
        )

    if umbral_pct > 0:
        fig.add_hline(
            y=umbral_pct,
            line_dash="dash",
            line_color=COLOR_DESTACADO,
            annotation_text=f"Umbral {umbral_pct:.1f} %",
            annotation_position="top right",
        )

    titulo_final = titulo or (
        f"Presupuesto por departamento (resaltado: ≥ {umbral_pct:.1f} %)"
    )
    fig.update_layout(
        title=dict(text=f"<b>{titulo_final}</b>", x=0.02, font=dict(size=18, color=COLOR_NAVY)),
        height=620,
        plot_bgcolor="white",
        paper_bgcolor="white",
        showlegend=False,
        bargap=0.18,
        margin=dict(t=100, l=75, r=45, b=150),
    )
    fig.update_xaxes(
        tickmode="array", tickvals=plot_df["x_pos"], ticktext=x_labels, tickangle=-45,
    )
    fig.update_yaxes(title_text="% del presupuesto", ticksuffix="%", range=[0, max_y * 1.35])
    return fig


def fig_ejecucion_umbral(
    datos: pd.DataFrame,
    orden_x: list,
    presup_depto: pd.DataFrame,
    *,
    umbral_retraso: float,
    titulo: str,
    region: str | None = None,
) -> go.Figure:
    if datos.empty:
        fig = go.Figure()
        fig.update_layout(title="Sin datos para el filtro aplicado", height=400)
        return fig

    retraso_por_depto = (
        datos[datos["Estado"] == "Retrasado"]
        .groupby("Departamento", observed=True)["Proyectos"]
        .sum()
    )
    totales = datos.groupby("Departamento", observed=True)["Proyectos"].sum()
    pct_ret = (100 * retraso_por_depto / totales).fillna(0)
    top_deptos = set(pct_ret[pct_ret >= umbral_retraso].index)

    color_estado = {
        "En Planeación": "#D1D5DB",
        "En Ejecución": "#9CA3AF",
        "Finalizado": "#6B7280",
        "Retrasado": COLOR_ALERTA,
    }
    fig = px.bar(
        datos,
        x="Departamento",
        y="Proyectos",
        color="Estado",
        color_discrete_map=color_estado,
        barmode="stack",
        category_orders={"Estado": ORDEN_ESTADO_A},
        custom_data=["Pct"],
        title=titulo,
    )
    fig.update_traces(
        hovertemplate=(
            "<b>%{x}</b><br>Estado: %{fullData.name}<br>"
            "Proyectos: %{y}<br>Participación: %{customdata[0]:.1f}%<extra></extra>"
        )
    )
    totales_y = datos.groupby("Departamento", observed=True)["Proyectos"].sum()
    for depto in top_deptos:
        if depto not in totales_y.index:
            continue
        mask = presup_depto["Departamento"] == depto
        if region is not None:
            mask = mask & (presup_depto["Region"] == region)
        pct_pais = presup_depto.loc[mask, "Pct_Pais"].iloc[0] if mask.any() else 0
        fig.add_annotation(
            x=depto, y=totales_y[depto],
            text=f"<b>Alerta retraso</b><br>{pct_ret.get(depto, 0):.1f}% retrasados<br>{pct_pais:.2f}% presup.",
            showarrow=True, arrowhead=2, arrowcolor=COLOR_ALERTA, ay=-40,
            font=dict(size=11, color=COLOR_NAVY),
            bgcolor="rgba(255,255,255,0.95)", bordercolor=COLOR_ALERTA, borderwidth=1.5,
        )

    ticktext = [f"<b>{d}</b>" if d in top_deptos else d for d in orden_x]
    fig.update_xaxes(tickmode="array", tickvals=orden_x, ticktext=ticktext, tickangle=-35)
    fig.update_layout(height=450, legend_title="Estado")
    return fig


def fig_sector_umbral(
    df: pd.DataFrame,
    *,
    umbral_presup: float,
    umbral_retraso: float,
    etiqueta_presup: str,
    titulo: str,
) -> go.Figure:
    from data_loader import tabla_categoria

    cat = tabla_categoria(df, etiqueta_presup)
    if cat.empty:
        fig = go.Figure()
        fig.update_layout(title="Sin datos para el filtro aplicado", height=400)
        return fig

    orden_cat = sorted(cat["Categoria"].unique())
    cat_plot = cat.melt(
        id_vars=["Categoria"],
        value_vars=[etiqueta_presup, "Pct_Retrasados"],
        var_name="Metrica",
        value_name="Porcentaje",
    )
    cat_plot["Metrica"] = cat_plot["Metrica"].map(
        {etiqueta_presup: "% presupuesto", "Pct_Retrasados": "% retrasados"}
    )

    presupuesto_alto = set(cat.loc[cat[etiqueta_presup] >= umbral_presup, "Categoria"])
    retraso_alto = set(cat.loc[cat["Pct_Retrasados"] >= umbral_retraso, "Categoria"])

    fig = px.bar(
        cat_plot,
        x="Categoria",
        y="Porcentaje",
        color="Metrica",
        barmode="group",
        text=cat_plot["Porcentaje"].round(1),
        title=titulo,
        color_discrete_map={"% presupuesto": COLOR_METRICA["% presupuesto nacional"], "% retrasados": COLOR_ALERTA},
        category_orders={"Categoria": orden_cat},
    )
    for trace in fig.data:
        if "presupuesto" in trace.name:
            activo, gris = COLOR_DESTACADO, GRAY_PRESUP
            trace.marker.color = [
                activo if c in presupuesto_alto else gris for c in trace.x
            ]
        else:
            activo, gris = COLOR_ALERTA, GRAY_RETASO
            trace.marker.color = [
                activo if c in retraso_alto else gris for c in trace.x
            ]
    fig.update_traces(texttemplate="%{text:.1f}%", textposition="outside", cliponaxis=False)
    fig.update_layout(height=460, yaxis_title="Porcentaje (%)")
    return fig


def fig_scatter_regional_filtro(
    resumen_reg: pd.DataFrame,
    *,
    umbral_benef: float | None = None,
) -> plt.Figure:
    plot_region = resumen_reg.copy()
    if plot_region.empty:
        fig, ax = plt.subplots(figsize=(8, 4))
        ax.text(0.5, 0.5, "Sin datos", ha="center", va="center")
        return fig

    mediana = plot_region["Presupuesto_Millones_USD"].median()
    alto = plot_region[plot_region["Presupuesto_Millones_USD"] >= mediana]
    if alto.empty:
        alto = plot_region
    critica = alto.sort_values("Beneficiarios_por_Millon_USD").iloc[0]
    nombre_crit = critica["Region"]

    if umbral_benef is not None:
        bajo_cob = plot_region["Beneficiarios_por_Millon_USD"] < umbral_benef
        colores = [
            COLOR_ALERTA if (r == nombre_crit or row_bajo) else COLOR_NEUTRO
            for r, row_bajo in zip(plot_region["Region"], bajo_cob)
        ]
    else:
        colores = [COLOR_ALERTA if r == nombre_crit else COLOR_NEUTRO for r in plot_region["Region"]]

    fig, ax = plt.subplots(figsize=(11, 6), facecolor=COLOR_FONDO)
    ax.scatter(
        plot_region["Presupuesto_Millones_USD"],
        plot_region["Beneficiarios_por_Millon_USD"],
        s=[420 if r == nombre_crit else 200 for r in plot_region["Region"]],
        c=colores, edgecolor="white", linewidth=1.5, alpha=0.9,
    )
    for _, row in plot_region.iterrows():
        ax.annotate(row["Region"], (row["Presupuesto_Millones_USD"], row["Beneficiarios_por_Millon_USD"]),
                    xytext=(8, 6), textcoords="offset points", fontsize=10)
    if umbral_benef is not None:
        ax.axhline(umbral_benef, color=COLOR_DESTACADO, linestyle="--", linewidth=1.2,
                   label=f"Umbral cobertura {umbral_benef:,.0f} benef./M USD")
        ax.legend(loc="lower right", fontsize=9)
    ax.set_title(f"Cobertura regional — alerta: {nombre_crit}", loc="left", fontweight="bold")
    ax.set_xlabel("Presupuesto (millones USD)")
    ax.set_ylabel("Beneficiarios por millón USD")
    ax.grid(color=COLOR_NEUTRO_2, alpha=0.5)
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    return fig


def fig_scatter_departamental_filtro(
    resumen_dep: pd.DataFrame,
    *,
    umbral_presup: float,
    umbral_retraso: float,
) -> plt.Figure:
    plot = resumen_dep.copy()
    if plot.empty:
        fig, ax = plt.subplots(figsize=(8, 4))
        ax.text(0.5, 0.5, "Sin datos", ha="center", va="center")
        return fig

    if "Segmento_Retraso" not in plot.columns:
        plot["Segmento_Retraso"] = segmento_pct_retrasados(plot["Pct_Retrasados"])

    fig, ax = plt.subplots(figsize=(11, 6.5), facecolor=COLOR_FONDO)
    for seg in ORDEN_SEGMENTO_RETRASO:
        sub = plot[plot["Segmento_Retraso"] == seg]
        if sub.empty:
            continue
        ax.scatter(
            sub["Pct_Pais"], sub["Beneficiarios_por_Millon_USD"],
            c=COLOR_SEGMENTO_RETRASO[seg], s=sub["Proyectos"] * 2.8 + 35,
            alpha=0.85, edgecolors="white", linewidth=0.6, label=seg,
        )

    alerta = plot[
        (plot["Pct_Pais"] >= umbral_presup) | (plot["Pct_Retrasados"] >= umbral_retraso)
    ]
    for _, row in alerta.iterrows():
        ax.scatter(row["Pct_Pais"], row["Beneficiarios_por_Millon_USD"],
                   s=row["Proyectos"] * 2.8 + 90, facecolors="none",
                   edgecolors=COLOR_ALERTA, linewidth=2.2, zorder=5)
        ax.annotate(row["Departamento"], (row["Pct_Pais"], row["Beneficiarios_por_Millon_USD"]),
                    xytext=(6, 4), textcoords="offset points", fontsize=9,
                    fontweight="bold", color=COLOR_ALERTA)

    ax.axvline(umbral_presup, color=COLOR_DESTACADO, linestyle="--", linewidth=1,
               label=f"Umbral presup. {umbral_presup:.1f} %")
    ax.axhline(0, color="none")
    ax.legend(title="Retrasos / umbrales", loc="upper right", fontsize=8)
    ax.set_title("Cobertura departamental (borde rojo = supera umbrales)", loc="left", fontweight="bold")
    ax.set_xlabel("% presupuesto nacional")
    ax.set_ylabel("Beneficiarios por millón USD")
    ax.xaxis.set_major_formatter(mtick.StrMethodFormatter("{x:,.1f}"))
    ax.yaxis.set_major_formatter(mtick.StrMethodFormatter("{x:,.0f}"))
    ax.grid(color=COLOR_NEUTRO_2, alpha=0.5)
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    return fig


def fig_acumulado_filtro(acum: pd.DataFrame, deptos_destacar: set[str], titulo: str) -> go.Figure:
    fig = go.Figure()
    if acum.empty:
        fig.update_layout(title="Sin datos para el filtro aplicado", height=400)
        return fig

    deptos = sorted(acum["Departamento"].unique())
    for depto in deptos:
        sub = acum[acum["Departamento"] == depto].sort_values("Fecha")
        dest = depto in deptos_destacar
        fig.add_trace(
            go.Scatter(
                x=sub["Fecha"], y=sub["Acumulado"], mode="lines+markers", name=depto,
                line=dict(color=COLOR_ALERTA if dest else COLOR_NEUTRO, width=3 if dest else 1),
                marker=dict(size=7 if dest else 3),
                opacity=1.0 if dest else 0.35,
                showlegend=dest,
            )
        )
    fig.update_layout(title=titulo, height=420, xaxis_title="Mes", yaxis_title="Proyectos acumulados")
    return fig
