"""Pestaña de dashboard interactivo con filtros globales y umbrales configurables."""

from __future__ import annotations

import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

from config import ORDEN_ESTADO_A, ORDEN_REGION
from dashboard_charts import (
    fig_acumulado_filtro,
    fig_ejecucion_umbral,
    fig_presupuesto_atencion_umbral,
    fig_scatter_departamental_filtro,
    fig_scatter_regional_filtro,
    fig_sector_umbral,
)
from data_loader import (
    acumulado_proyectos_por_departamento,
    conteo_depto_por_region,
    presupuesto_depto,
    resumen_departamentos,
    resumen_region,
    treemap_departamentos,
)


def _filtrar_proyectos(
    df: pd.DataFrame,
    *,
    region: str,
    departamento: str,
    categorias: list[str],
    estados: list[str],
    impactos: list[str],
) -> pd.DataFrame:
    out = df.copy()
    if departamento != "Todos":
        out = out[out["Departamento"] == departamento]
    elif region != "Todas":
        out = out[out["Region"] == region]
    if categorias:
        out = out[out["Categoria"].isin(categorias)]
    if estados:
        out = out[out["Estado"].isin(estados)]
    if impactos:
        out = out[out["Nivel_Impacto"].isin(impactos)]
    return out


def _deptos_en_scope(df_full: pd.DataFrame, region: str, departamento: str) -> list[str]:
    if departamento != "Todos":
        return [departamento]
    if region != "Todas":
        return sorted(df_full.loc[df_full["Region"] == region, "Departamento"].unique())
    return sorted(df_full["Departamento"].unique())


def _etiqueta_filtro(region: str, departamento: str) -> str:
    if departamento != "Todos":
        reg = region if region != "Todas" else "—"
        return f"Departamento: **{departamento}** (región {reg})"
    if region != "Todas":
        return f"Región: **{region}**"
    return "Ámbito: **Nacional**"


def render_dashboard_interactivo(df_full: pd.DataFrame) -> None:
    st.header("Dashboard interactivo")
    st.markdown(
        """
Explora el portafolio con **filtros globales** que aplican a todas las gráficas.
Ajusta **umbrales** para controlar qué departamentos o categorías se resaltan.
        """
    )

    with st.expander("Filtros territoriales y de proyecto", expanded=True):
        c1, c2, c3 = st.columns(3)
        with c1:
            region = st.selectbox(
                "Región",
                ["Todas", *ORDEN_REGION],
                key="dash_region",
            )
        deptos_disponibles = sorted(
            df_full.loc[df_full["Region"] == region, "Departamento"].unique()
            if region != "Todas"
            else df_full["Departamento"].unique()
        )
        with c2:
            departamento = st.selectbox(
                "Departamento",
                ["Todos", *deptos_disponibles],
                key="dash_depto",
            )
        if departamento != "Todos":
            region_efectiva = df_full.loc[
                df_full["Departamento"] == departamento, "Region"
            ].iloc[0]
            if region != "Todas" and region != region_efectiva:
                st.warning(
                    f"El departamento **{departamento}** pertenece a **{region_efectiva}**. "
                    "Se usará el departamento seleccionado."
                )
            region = region_efectiva

        categorias_all = sorted(df_full["Categoria"].unique())
        estados_all = list(ORDEN_ESTADO_A)
        impactos_all = sorted(df_full["Nivel_Impacto"].unique())
        with c3:
            categorias = st.multiselect(
                "Categoría",
                categorias_all,
                default=categorias_all,
                key="dash_cat",
            )
        c4, c5 = st.columns(2)
        with c4:
            estados = st.multiselect(
                "Estado del proyecto",
                estados_all,
                default=estados_all,
                key="dash_estado",
            )
        with c5:
            impactos = st.multiselect(
                "Nivel de impacto",
                impactos_all,
                default=impactos_all,
                key="dash_impacto",
            )

    with st.expander("Umbrales de resaltado", expanded=True):
        u1, u2, u3 = st.columns(3)
        with u1:
            umbral_presup = st.slider(
                "% presupuesto para resaltar",
                min_value=1.0,
                max_value=100.0,
                value=5.0,
                step=0.5,
                key="dash_umbral_presup",
            )
        with u2:
            umbral_retraso = st.slider(
                "% retrasos para alerta",
                min_value=1.0,
                max_value=100.0,
                value=22.0,
                step=1.0,
                key="dash_umbral_retraso",
            )
        with u3:
            umbral_benef = st.slider(
                "Umbral cobertura (benef./M USD)",
                min_value=6000,
                max_value=10000,
                value=8000,
                step=250,
                key="dash_umbral_benef",
            )

    df = _filtrar_proyectos(
        df_full,
        region=region,
        departamento=departamento,
        categorias=categorias,
        estados=estados,
        impactos=impactos,
    )

    st.info(_etiqueta_filtro(region, departamento))

    if df.empty:
        st.warning("No hay proyectos con la combinación de filtros seleccionada.")
        return

    n_proj = len(df)
    presup_m = df["Presupuesto_USD"].sum() / 1_000_000
    pct_ret = 100 * (df["Estado"] == "Retrasado").mean()
    benef_m = (
        df["Poblacion_Beneficiada"].sum()
        / max(presup_m, 1e-9)
    )
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Proyectos (filtro)", f"{n_proj:,}")
    k2.metric("Presupuesto (filtro)", f"USD {presup_m:,.1f} M")
    k3.metric("% retrasados (filtro)", f"{pct_ret:.1f} %")
    k4.metric("Benef./M USD (filtro)", f"{benef_m:,.0f}")

    presup_full = presupuesto_depto(df_full)

    conteo = conteo_depto_por_region(df)
    res_reg = resumen_region(df)
    res_dep = resumen_departamentos(df)
    acum = acumulado_proyectos_por_departamento(df)

    deptos_scope = _deptos_en_scope(df_full, region, departamento)
    deptos_alerta = set(
        res_dep.loc[
            (res_dep["Pct_Pais"] >= umbral_presup)
            | (res_dep["Pct_Retrasados"] >= umbral_retraso),
            "Departamento",
        ]
    )

    tab_p, tab_e, tab_s, tab_c, tab_t = st.tabs(
        ["Presupuesto", "Ejecución", "Sector", "Cobertura", "Tendencia"]
    )

    with tab_p:
        st.plotly_chart(
            fig_presupuesto_atencion_umbral(
                treemap_departamentos(df),
                umbral_pct=umbral_presup,
                titulo=f"Presupuesto — {_etiqueta_filtro(region, departamento).replace('**', '')}",
            ),
            use_container_width=True,
        )
        st.caption(
            f"Barras en **rojo**: departamentos con % presupuesto ≥ {umbral_presup:.1f} %. "
            "La línea punteada marca el umbral seleccionado."
        )

    with tab_e:
        if departamento != "Todos":
            datos_e = conteo.copy()
            orden_x = [departamento]
        else:
            datos_e = conteo.copy()
            orden_x = (
                presup_full[presup_full["Departamento"].isin(deptos_scope)]
                .sort_values("Pct_Pais", ascending=False)["Departamento"]
                .tolist()
            )
        datos_e = datos_e[datos_e["Departamento"].isin(orden_x)]
        datos_e["Departamento"] = pd.Categorical(
            datos_e["Departamento"], categories=orden_x, ordered=True
        )
        datos_e = datos_e.sort_values(["Departamento", "Estado"])
        region_ej = region if region != "Todas" else None
        st.plotly_chart(
            fig_ejecucion_umbral(
                datos_e,
                orden_x,
                presup_full,
                umbral_retraso=umbral_retraso,
                titulo=f"Proyectos por estado — {_etiqueta_filtro(region, departamento).replace('**', '')}",
                region=region_ej,
            ),
            use_container_width=True,
        )

    with tab_s:
        if departamento != "Todos":
            titulo_sector = f"Sector — {departamento}"
        elif region != "Todas":
            titulo_sector = f"Sector — {region}"
        else:
            titulo_sector = "Sector — subconjunto filtrado"
        st.plotly_chart(
            fig_sector_umbral(
                df,
                umbral_presup=umbral_presup,
                umbral_retraso=umbral_retraso,
                etiqueta_presup="Pct_Presup_Filtro",
                titulo=titulo_sector,
            ),
            use_container_width=True,
        )
        st.caption(
            f"**Azul:** categorías con % presupuesto ≥ {umbral_presup:.1f} %. "
            f"**Rojo:** categorías con % retrasados ≥ {umbral_retraso:.1f} %."
        )

    with tab_c:
        if len(res_reg) > 1:
            fig_r = fig_scatter_regional_filtro(res_reg, umbral_benef=umbral_benef)
            st.pyplot(fig_r)
            plt.close(fig_r)
        else:
            st.caption("Vista regional no aplica con un solo punto en el filtro.")
        if len(res_dep) > 0:
            fig_d = fig_scatter_departamental_filtro(
                res_dep,
                umbral_presup=umbral_presup,
                umbral_retraso=umbral_retraso,
            )
            st.pyplot(fig_d)
            plt.close(fig_d)

    with tab_t:
        acum_f = acum[acum["Departamento"].isin(deptos_scope)]
        st.plotly_chart(
            fig_acumulado_filtro(
                acum_f,
                deptos_alerta,
                titulo=f"Acumulado de proyectos — {_etiqueta_filtro(region, departamento).replace('**', '')}",
            ),
            use_container_width=True,
        )
        if deptos_alerta:
            st.caption(
                "Destacados en rojo (superan umbrales): "
                + ", ".join(sorted(deptos_alerta))
            )
