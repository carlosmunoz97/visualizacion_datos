"""Figuras del informe (Plotly y Matplotlib)."""

from __future__ import annotations

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from matplotlib.patches import Patch

from data_loader import segmento_pct_retrasados

from config import (
    CATEGORIA_DESTACADA_G1,
    CATEGORIA_DESTACADA_G2,
    COLOR_ALERTA,
    COLOR_DESTACADO,
    COLOR_DEPARTAMENTO_CRITICO,
    COLOR_ESTADO,
    COLOR_FONDO,
    COLOR_METRICA,
    COLOR_REGION,
    COLOR_NAVY,
    COLOR_NEUTRO,
    COLOR_NEUTRO_2,
    COLOR_TEXTO,
    COLOR_TEXTO_SEC,
    COLOR_SEGMENTO_RETRASO,
    CRITICOS,
    GRAY_ESTADO,
    GRAY_PRESUP,
    GRAY_RETASO,
    ORDEN_ESTADO_A,
    ORDEN_REGION,
    ORDEN_SEGMENTO_RETRASO,
)


def limpiar_ejes(ax, quitar_left: bool = False) -> None:
    for spine in ["top", "right"]:
        ax.spines[spine].set_visible(False)
    if quitar_left:
        ax.spines["left"].set_visible(False)
    ax.set_axisbelow(True)


def fig_acumulado_proyectos_region(acum: pd.DataFrame):
    fig = px.line(
        acum,
        x="Fecha",
        y="Acumulado",
        color="Region",
        markers=True,
        custom_data=["Nuevos"],
        title="Crecimiento acumulado de proyectos por región",
        labels={"Fecha": "Mes de inicio", "Acumulado": "Proyectos acumulados"},
        color_discrete_map=COLOR_REGION,
        category_orders={"Region": ORDEN_REGION},
    )
    fig.update_traces(
        line=dict(width=2.5),
        marker=dict(size=7),
        hovertemplate=(
            "<b>%{fullData.name}</b><br>"
            "Mes: %{x|%b %Y}<br>"
            "Nuevos en el mes: %{customdata[0]}<br>"
            "Acumulado: %{y}<extra></extra>"
        ),
    )
    fig.update_layout(
        height=460,
        xaxis_title="Fecha de inicio del proyecto",
        yaxis_title="Proyectos acumulados",
        legend_title="Región",
        hovermode="x unified",
    )
    return fig


def fig_acumulado_proyectos_departamento(acum: pd.DataFrame):
    fig = go.Figure()
    deptos = list(acum["Departamento"].cat.categories)
    otros = [d for d in deptos if d not in CRITICOS]
    orden_trazas = otros + [d for d in CRITICOS if d in deptos]

    for depto in orden_trazas:
        sub = acum[acum["Departamento"] == depto].sort_values("Fecha")
        critico = depto in CRITICOS
        color = COLOR_DEPARTAMENTO_CRITICO.get(depto, COLOR_NEUTRO)
        fig.add_trace(
            go.Scatter(
                x=sub["Fecha"],
                y=sub["Acumulado"],
                mode="lines+markers",
                name=depto,
                line=dict(
                    color=color,
                    width=3.2 if critico else 1.2,
                ),
                marker=dict(size=8 if critico else 4),
                opacity=1.0 if critico else 0.35,
                customdata=sub["Nuevos"],
                hovertemplate=(
                    "<b>%{fullData.name}</b><br>"
                    "Mes: %{x|%b %Y}<br>"
                    "Nuevos en el mes: %{customdata}<br>"
                    "Acumulado: %{y}<extra></extra>"
                ),
                showlegend=critico,
            )
        )

    fig.update_layout(
        title="Crecimiento acumulado de proyectos por departamento",
        height=500,
        xaxis_title="Fecha de inicio del proyecto",
        yaxis_title="Proyectos acumulados",
        legend_title="Deptos críticos",
        hovermode="x unified",
    )
    return fig


def fig_treemap(treemap_df: pd.DataFrame):
    fig = px.treemap(
        treemap_df,
        path=["Pais", "Region", "Departamento"],
        values="Presupuesto_USD",
        color="Pct_Pais",
        color_continuous_scale=["#BFDBFE", "#60A5FA", "#2563EB", "#1E3A8A"],
        hover_data={
            "Presupuesto_USD": ":,.0f",
            "Pct_Pais": ":.2f",
            "Proyectos": True,
        },
        title="Distribución del presupuesto por región y departamento (Colombia)",
    )
    fig.update_layout(
        height=500,
        margin=dict(t=60, l=10, r=10, b=10),
        coloraxis_colorbar_title="% presupuesto nacional",
    )
    fig.update_traces(textinfo="label+percent root", textfont=dict(color="white", size=11))
    return fig


def fig_depto_region(
    datos: pd.DataFrame,
    orden_x: list,
    top_deptos: set,
    presupuesto_depto: pd.DataFrame,
    *,
    titulo: str,
    region: str | None = None,
):
    fig = px.bar(
        datos,
        x="Departamento",
        y="Proyectos",
        color="Estado",
        color_discrete_map=COLOR_ESTADO,
        barmode="stack",
        category_orders={"Estado": ORDEN_ESTADO_A},
        custom_data=["Pct"],
        title=titulo,
    )
    for trace in fig.data:
        estado = trace.name
        if estado == "Retrasado":
            trace.marker.color = COLOR_ALERTA
            trace.marker.line.color = "rgba(0,0,0,0)"
        else:
            trace.marker.color = GRAY_ESTADO.get(estado, "#9CA3AF")
            trace.marker.line.color = "rgba(0,0,0,0)"
    fig.update_traces(
        hovertemplate=(
            "<b>%{x}</b><br>Estado: %{fullData.name}<br>"
            "Proyectos: %{y}<br>Participación: %{customdata[0]:.1f}%<extra></extra>"
        )
    )
    totales = datos.groupby("Departamento", observed=True)["Proyectos"].sum()
    for depto in top_deptos:
        if depto not in totales.index:
            continue
        mask = presupuesto_depto["Departamento"] == depto
        if region is not None:
            mask = mask & (presupuesto_depto["Region"] == region)
        pct_pais = presupuesto_depto.loc[mask, "Pct_Pais"].iloc[0]
        fig.add_annotation(
            x=depto,
            y=totales[depto],
            text=f"<b>Presupuesto</b><br>{pct_pais:.2f}% del país",
            showarrow=True,
            arrowhead=2,
            arrowcolor=COLOR_NAVY,
            arrowwidth=1.5,
            ay=-42,
            font=dict(size=13, color=COLOR_NAVY, family="Arial Black, Arial, sans-serif"),
            bgcolor="rgba(255,255,255,0.95)",
            bordercolor=COLOR_DESTACADO,
            borderwidth=2,
            borderpad=6,
        )
    ticktext = [f"<b>{d}</b>" if d in top_deptos else d for d in orden_x]
    fig.update_xaxes(tickmode="array", tickvals=orden_x, ticktext=ticktext, tickangle=-35)
    fig.update_layout(
        height=450,
        xaxis_title="Departamento",
        yaxis_title="Número de proyectos",
        legend_title="Estado",
    )
    return fig


def fig_sector_nacional(cat_nacional: pd.DataFrame, orden_cat: list):
    cat_plot = cat_nacional.melt(
        id_vars=["Categoria"],
        value_vars=["Pct_Presup_Pais", "Pct_Retrasados"],
        var_name="Metrica",
        value_name="Porcentaje",
    )
    cat_plot["Metrica"] = cat_plot["Metrica"].map(
        {
            "Pct_Presup_Pais": "% presupuesto nacional",
            "Pct_Retrasados": "% proyectos retrasados",
        }
    )
    fig = px.bar(
        cat_plot,
        x="Categoria",
        y="Porcentaje",
        color="Metrica",
        barmode="group",
        text=cat_plot["Porcentaje"].round(1),
        title="Nacional: presupuesto y retrasos por categoría (Energía resaltada)",
        color_discrete_map=COLOR_METRICA,
        category_orders={"Categoria": orden_cat},
    )
    for trace in fig.data:
        if "presupuesto" in trace.name:
            color_activo, gray = COLOR_METRICA["% presupuesto nacional"], GRAY_PRESUP
        else:
            color_activo, gray = COLOR_METRICA["% proyectos retrasados"], GRAY_RETASO
        trace.marker.color = [
            color_activo if cat == CATEGORIA_DESTACADA_G1 else gray for cat in trace.x
        ]
    fig.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
    fig.update_layout(height=480, yaxis_title="Porcentaje (%)", legend_title="")
    cats = list(fig.data[0].x)
    fig.update_xaxes(
        tickmode="array",
        tickvals=cats,
        ticktext=[f"<b>{c}</b>" if c == CATEGORIA_DESTACADA_G1 else c for c in cats],
    )
    return fig


def fig_sector_criticos(cat_criticos: pd.DataFrame, orden_cat: list):
    cat_plot2 = cat_criticos.melt(
        id_vars=["Categoria"],
        value_vars=["Pct_Presup_Criticos", "Pct_Retrasados"],
        var_name="Metrica",
        value_name="Porcentaje",
    )
    cat_plot2["Metrica"] = cat_plot2["Metrica"].map(
        {
            "Pct_Presup_Criticos": "% presupuesto (deptos críticos)",
            "Pct_Retrasados": "% proyectos retrasados",
        }
    )
    fig = px.bar(
        cat_plot2,
        x="Categoria",
        y="Porcentaje",
        color="Metrica",
        barmode="group",
        text=cat_plot2["Porcentaje"].round(1),
        title="Deptos críticos (agregado): presupuesto y retrasos (Infraestructura resaltada)",
        color_discrete_map={
            "% presupuesto (deptos críticos)": "#2563EB",
            "% proyectos retrasados": "#DC2626",
        },
        category_orders={"Categoria": orden_cat},
    )
    for trace in fig.data:
        if "presupuesto" in trace.name:
            color_activo, gray = "#2563EB", GRAY_PRESUP
        else:
            color_activo, gray = "#DC2626", GRAY_RETASO
        trace.marker.color = [
            color_activo if cat == CATEGORIA_DESTACADA_G2 else gray for cat in trace.x
        ]
    fig.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
    fig.update_layout(height=480, yaxis_title="Porcentaje (%)", legend_title="")
    cats2 = list(fig.data[0].x)
    fig.update_xaxes(
        tickmode="array",
        tickvals=cats2,
        ticktext=[f"<b>{c}</b>" if c == CATEGORIA_DESTACADA_G2 else c for c in cats2],
    )
    return fig


def fig_sector_depto(cat_por_critico: pd.DataFrame, depto: str):
    t = cat_por_critico[cat_por_critico["Departamento"] == depto].copy()
    t["Pareja"] = t["Pct_Presup_Depto"] + t["Pct_Retrasados"]
    cat_destacada = t.loc[t["Pareja"].idxmax(), "Categoria"]
    orden_cats = t.sort_values("Pct_Retrasados", ascending=False)["Categoria"].tolist()
    cat_plot = t.melt(
        id_vars=["Categoria"],
        value_vars=["Pct_Presup_Depto", "Pct_Retrasados"],
        var_name="Metrica",
        value_name="Porcentaje",
    )
    cat_plot["Metrica"] = cat_plot["Metrica"].map(
        {
            "Pct_Presup_Depto": "% presupuesto del departamento",
            "Pct_Retrasados": "% proyectos retrasados",
        }
    )
    fig = px.bar(
        cat_plot,
        x="Categoria",
        y="Porcentaje",
        color="Metrica",
        barmode="group",
        text=cat_plot["Porcentaje"].round(1),
        title=(
            f"{depto}: presupuesto y retrasos por categoría "
            f"(resaltado: {cat_destacada}, mayor pareja presup. + % retrasos)"
        ),
        color_discrete_map={
            "% presupuesto del departamento": "#2563EB",
            "% proyectos retrasados": "#DC2626",
        },
        category_orders={"Categoria": orden_cats},
    )
    for trace in fig.data:
        if "presupuesto" in trace.name:
            color_activo, gray = "#2563EB", GRAY_PRESUP
        else:
            color_activo, gray = "#DC2626", GRAY_RETASO
        trace.marker.color = [
            color_activo if cat == cat_destacada else gray for cat in trace.x
        ]
    fig.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
    fig.update_layout(height=480, yaxis_title="Porcentaje (%)", legend_title="")
    cats = list(fig.data[0].x)
    fig.update_xaxes(
        tickmode="array",
        tickvals=cats,
        ticktext=[f"<b>{c}</b>" if c == cat_destacada else c for c in cats],
    )
    return fig


def fig_scatter_regional(resumen_reg: pd.DataFrame) -> plt.Figure:
    plot_region = resumen_reg.copy()
    mediana_presupuesto = plot_region["Presupuesto_Millones_USD"].median()
    regiones_alto = plot_region[plot_region["Presupuesto_Millones_USD"] >= mediana_presupuesto]
    region_critica = regiones_alto.sort_values("Beneficiarios_por_Millon_USD").iloc[0]
    nombre_region_critica = region_critica["Region"]

    colores = [
        COLOR_ALERTA if r == nombre_region_critica else COLOR_NEUTRO
        for r in plot_region["Region"]
    ]
    tamanos = [420 if r == nombre_region_critica else 200 for r in plot_region["Region"]]

    x_min, x_max = plot_region["Presupuesto_Millones_USD"].min(), plot_region["Presupuesto_Millones_USD"].max()
    y_min, y_max = plot_region["Beneficiarios_por_Millon_USD"].min(), plot_region["Beneficiarios_por_Millon_USD"].max()
    x_rango, y_rango = x_max - x_min, y_max - y_min
    x_lim_inf = x_min - x_rango * 0.12
    x_lim_sup = x_max + x_rango * 0.25
    y_lim_inf = y_min - y_rango * 0.14
    y_lim_sup = y_max + y_rango * 0.20

    fig, ax = plt.subplots(figsize=(12.8, 6.8), facecolor=COLOR_FONDO)
    ax.set_facecolor(COLOR_FONDO)
    ax.set_xlim(x_lim_inf, x_lim_sup)
    ax.set_ylim(y_lim_inf, y_lim_sup)

    ax.scatter(
        plot_region["Presupuesto_Millones_USD"],
        plot_region["Beneficiarios_por_Millon_USD"],
        s=tamanos,
        c=colores,
        edgecolor="white",
        linewidth=1.5,
        alpha=0.9,
        zorder=3,
    )
    offsets = {
        "Caribe": (14, 8),
        "Amazonía": (14, 8),
        "Orinoquía": (-62, -18),
        "Pacífica": (12, 8),
        "Andina": (12, 8),
    }
    for _, row in plot_region.iterrows():
        region = row["Region"]
        es_critica = region == nombre_region_critica
        dx, dy = offsets.get(region, (12, 8))
        ax.annotate(
            region,
            xy=(row["Presupuesto_Millones_USD"], row["Beneficiarios_por_Millon_USD"]),
            xytext=(dx, dy),
            textcoords="offset points",
            fontsize=11.5 if es_critica else 10.5,
            color=COLOR_ALERTA if es_critica else COLOR_TEXTO_SEC,
            fontweight="bold" if es_critica else "normal",
            zorder=4,
        )

    ax.set_title(
        f"{nombre_region_critica}: alto presupuesto y menor cobertura relativa",
        loc="left",
        fontsize=16,
        fontweight="bold",
        color=COLOR_NAVY,
        pad=12,
    )
    ax.annotate(
        f"Alerta\nUSD {region_critica['Presupuesto_Millones_USD']:,.0f} M\n"
        f"{region_critica['Beneficiarios_por_Millon_USD']:,.0f} benef./M USD",
        xy=(region_critica["Presupuesto_Millones_USD"], region_critica["Beneficiarios_por_Millon_USD"]),
        xytext=(
            region_critica["Presupuesto_Millones_USD"] - x_rango * 0.32,
            region_critica["Beneficiarios_por_Millon_USD"] + y_rango * 0.20,
        ),
        arrowprops=dict(arrowstyle="-|>", color=COLOR_ALERTA, lw=2.0, connectionstyle="arc3,rad=0.1"),
        fontsize=10.5,
        color=COLOR_NAVY,
        bbox=dict(boxstyle="round,pad=0.4", fc="white", ec=COLOR_ALERTA, lw=1.2),
        zorder=5,
    )
    ax.set_xlabel("Presupuesto total asignado (millones de USD)", fontsize=11, color=COLOR_TEXTO)
    ax.set_ylabel("Beneficiarios por millón de USD", fontsize=11, color=COLOR_TEXTO)
    ax.xaxis.set_major_formatter(mtick.StrMethodFormatter("{x:,.0f}"))
    ax.yaxis.set_major_formatter(mtick.StrMethodFormatter("{x:,.0f}"))
    ax.grid(color=COLOR_NEUTRO_2, linewidth=0.6, alpha=0.5)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.legend(
        handles=[
            Patch(facecolor=COLOR_NEUTRO, edgecolor="white", label="Regiones"),
            Patch(facecolor=COLOR_ALERTA, edgecolor="white", label="Región crítica (cobertura)"),
        ],
        loc="lower right",
        fontsize=9,
        framealpha=0.85,
    )
    fig.tight_layout(pad=1.6)
    return fig


def fig_scatter_departamental(resumen_dep: pd.DataFrame) -> plt.Figure:
    plot_depto = resumen_dep.copy()
    if "Segmento_Retraso" not in plot_depto.columns:
        plot_depto["Segmento_Retraso"] = segmento_pct_retrasados(
            plot_depto["Pct_Retrasados"]
        )

    fig, ax = plt.subplots(figsize=(12.5, 7.2), facecolor=COLOR_FONDO)
    ax.set_facecolor(COLOR_FONDO)

    for seg in ORDEN_SEGMENTO_RETRASO:
        sub = plot_depto[plot_depto["Segmento_Retraso"] == seg]
        if sub.empty:
            continue
        lo = sub["Pct_Retrasados"].min()
        hi = sub["Pct_Retrasados"].max()
        ax.scatter(
            sub["Pct_Pais"],
            sub["Beneficiarios_por_Millon_USD"],
            c=COLOR_SEGMENTO_RETRASO[seg],
            s=sub["Proyectos"] * 2.8 + 35,
            alpha=0.88,
            edgecolors="white",
            linewidth=0.7,
            zorder=3,
            label=f"{seg} ({lo:.1f}-{hi:.1f} %)",
        )

    for _, row in plot_depto.iterrows():
        if row["Departamento"] not in CRITICOS:
            continue
        ax.scatter(
            row["Pct_Pais"],
            row["Beneficiarios_por_Millon_USD"],
            s=row["Proyectos"] * 2.8 + 95,
            facecolors="none",
            edgecolors=COLOR_ALERTA,
            linewidth=2.4,
            zorder=5,
        )
        ax.annotate(
            row["Departamento"],
            (row["Pct_Pais"], row["Beneficiarios_por_Millon_USD"]),
            xytext=(7, 5),
            textcoords="offset points",
            fontsize=10,
            fontweight="bold",
            color=COLOR_ALERTA,
            zorder=6,
        )

    ax.legend(
        title="% proyectos retrasados",
        loc="upper right",
        frameon=True,
        fontsize=9,
        title_fontsize=9,
    )
    ax.set_title(
        "Departamentos: % presupuesto nacional vs cobertura (color = nivel de retrasos)",
        loc="left",
        fontsize=14.5,
        fontweight="bold",
        color=COLOR_NAVY,
        pad=10,
    )
    ax.set_xlabel("% presupuesto nacional", fontsize=10, color=COLOR_TEXTO)
    ax.set_ylabel("Beneficiarios por millón USD", fontsize=10, color=COLOR_TEXTO)
    ax.xaxis.set_major_formatter(mtick.StrMethodFormatter("{x:,.1f}"))
    ax.yaxis.set_major_formatter(mtick.StrMethodFormatter("{x:,.0f}"))
    ax.grid(color=COLOR_NEUTRO_2, linewidth=0.6, alpha=0.5)
    limpiar_ejes(ax)
    fig.tight_layout(pad=1.2)
    return fig
