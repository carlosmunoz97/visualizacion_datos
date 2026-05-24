"""
Dashboard Streamlit — Portafolio de proyectos Colombia.
Ejecutar: streamlit run app.py
"""

from __future__ import annotations

import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

from charts import (
    fig_acumulado_proyectos_departamento,
    fig_depto_region,
    fig_presupuesto_departamentos_atencion,
    fig_scatter_departamental,
    fig_scatter_regional,
    fig_sector_criticos,
    fig_sector_depto,
    fig_sector_nacional,
    fig_treemap,
)
from config import CRITICOS, ORDEN_REGION
from data_loader import (
    acumulado_proyectos_por_departamento,
    build_analitico,
    conteo_depto_por_region,
    load_raw,
    metricas_clave,
    presupuesto_depto,
    resumen_departamentos,
    resumen_region,
    tablas_sector,
    top2_retraso_por_region,
    treemap_departamentos,
)


@st.cache_data
def cargar_datos():
    df = load_raw()
    analitico = build_analitico(df)
    orden_cat = sorted(analitico["Categoria"].unique())
    return {
        "df": analitico,
        "treemap": treemap_departamentos(analitico),
        "conteo_depto": conteo_depto_por_region(analitico),
        "presup_depto": presupuesto_depto(analitico),
        "top2": top2_retraso_por_region(analitico),
        "resumen_region": resumen_region(analitico),
        "resumen_depto": resumen_departamentos(analitico),
        "cat_nacional": (sector := tablas_sector(analitico))[0],
        "cat_criticos": sector[1],
        "cat_por_critico": sector[2],
        "orden_cat": orden_cat,
        "metricas": metricas_clave(analitico),
        "acum_depto": acumulado_proyectos_por_departamento(analitico),
    }


def main():
    st.set_page_config(
        page_title="Portafolio de proyectos — Colombia",
        page_icon="📊",
        layout="wide",
    )

    data = cargar_datos()
    m = data["metricas"]

    st.sidebar.title("Portafolio Colombia")
    st.sidebar.metric("Proyectos", f"{m['n_proyectos']:,}")
    st.sidebar.metric("Presupuesto", f"USD {m['presupuesto_m_usd']:,.1f} M")
    st.sidebar.metric("% retrasados (país)", f"{m['pct_retrasados_nacional']:.1f} %")
    st.sidebar.metric("Caribe (benef./M USD)", f"{m['caribe_benef_m']:,.0f}")

    seccion = st.sidebar.radio(
        "Navegación",
        [
            "1. Presupuesto",
            "2. Ejecución por departamento",
            "3. Sector (críticos)",
            "4. Cobertura",
            "5. Conclusiones",
        ],
    )

    st.title("Informe ejecutivo — Visualización del portafolio")

    if seccion.startswith("1"):
        st.header("¿Dónde está el presupuesto?")
    
        st.markdown(
            """
    **Pregunta:** ¿Qué departamentos concentran mayor participación del presupuesto nacional?
    
    **Lectura esperada:** La primera visualización conserva todos los departamentos y guía la atención mediante ordenamiento y contraste tonal.  
    El treemap se mantiene como vista complementaria para observar la composición regional y departamental del presupuesto.
            """
        )
    
        tab1, tab2 = st.tabs(
            [
                "Recorrido visual por departamento",
                "Composición territorial del presupuesto",
            ]
        )
    
        with tab1:
            st.plotly_chart(
                fig_presupuesto_departamentos_atencion(data["treemap"]),
                use_container_width=True,
            )
    
            st.caption(
                "Orden lógico: región → departamentos ordenados por participación presupuestal descendente. "
                "Los tonos más oscuros indican mayor peso presupuestal dentro de cada región."
            )
    
        with tab2:
            st.plotly_chart(
                fig_treemap(data["treemap"]),
                use_container_width=True,
            )
    
            st.caption(
                "El treemap permite observar la composición del presupuesto por región y departamento. "
                "El tamaño representa presupuesto asignado y el color representa participación en el presupuesto nacional."
            )
    
        st.info(
            "La barra jerárquica se usa para controlar el recorrido visual del espectador. "
            "El treemap queda como apoyo exploratorio para ver composición y proporciones territoriales."
        )

    elif seccion.startswith("2"):
        st.header("¿Dónde falla la ejecución por departamento?")
        st.markdown(
            """
        **Pregunta:** ¿Qué departamentos concentran mayor participación del presupuesto nacional?
        
        **Lectura esperada:** La visualización conserva todos los departamentos, pero ordena la lectura por región y por peso presupuestal descendente. Los tonos más oscuros dirigen la atención hacia los departamentos líderes dentro de cada región.
            """
        )
        region_sel = st.selectbox("Región", ORDEN_REGION)
        datos = data["conteo_depto"][data["conteo_depto"]["Region"] == region_sel].copy()
        orden_x = (
            data["presup_depto"][data["presup_depto"]["Region"] == region_sel]
            .sort_values("Pct_Pais", ascending=False)["Departamento"]
            .tolist()
        )
        datos["Departamento"] = pd.Categorical(
            datos["Departamento"], categories=orden_x, ordered=True
        )
        datos = datos.sort_values(["Departamento", "Estado"])
        top_deptos = data["top2"].get(region_sel, set())
        st.plotly_chart(
            fig_depto_region(
                datos,
                orden_x,
                top_deptos,
                data["presup_depto"],
                titulo=f"Proyectos por estado — {region_sel}",
                region=region_sel,
            ),
            use_container_width=True,
        )
        if top_deptos:
            st.caption(f"Destacados en {region_sel}: **{', '.join(sorted(top_deptos))}**")

        st.subheader("Departamentos críticos")
        st.markdown(
            f"""
Vista agregada de los cuatro departamentos priorizados: **{", ".join(CRITICOS)}**.
            """
        )
        datos_crit = data["conteo_depto"][
            data["conteo_depto"]["Departamento"].isin(CRITICOS)
        ].copy()
        orden_crit = (
            data["presup_depto"][data["presup_depto"]["Departamento"].isin(CRITICOS)]
            .sort_values("Pct_Pais", ascending=False)["Departamento"]
            .tolist()
        )
        datos_crit["Departamento"] = pd.Categorical(
            datos_crit["Departamento"], categories=orden_crit, ordered=True
        )
        datos_crit = datos_crit.sort_values(["Departamento", "Estado"])
        st.plotly_chart(
            fig_depto_region(
                datos_crit,
                orden_crit,
                set(CRITICOS),
                data["presup_depto"],
                titulo="Proyectos por estado — departamentos críticos",
            ),
            use_container_width=True,
        )
        st.caption(
            f"Etiquetas de presupuesto en: **{', '.join(CRITICOS)}**. "
            "Retrasados en rojo; demás estados en gris."
        )

        st.subheader("Crecimiento acumulado de proyectos")
        st.markdown(
            """
Serie mensual acumulada por departamento (fecha de inicio). Los **cuatro críticos** resaltados
a color; el resto en gris claro.
            """
        )
        st.plotly_chart(
            fig_acumulado_proyectos_departamento(data["acum_depto"]),
            use_container_width=True,
        )
        tot_crit = (
            data["acum_depto"][data["acum_depto"]["Es_Critico"]]
            .sort_values("Fecha")
            .groupby("Departamento", observed=True)["Acumulado"]
            .last()
        )
        st.caption(
            "Críticos al cierre del periodo: "
            + " · ".join(f"**{d}** {int(tot_crit[d])}" for d in tot_crit.index)
        )

    elif seccion.startswith("3"):
        st.header("¿En qué sectores se concentra el gasto y el retraso?")
        st.markdown(
            f"""
**Departamentos críticos:** {", ".join(CRITICOS)} — elegidos por peso presupuestario y % de retrasos
(véase sección de ejecución). **Energía** se resalta a nivel nacional; **Infraestructura** en el bloque crítico.
            """
        )
        st.subheader("Nacional")
        st.plotly_chart(
            fig_sector_nacional(data["cat_nacional"], data["orden_cat"]),
            use_container_width=True,
        )
        st.subheader("Críticos agregados")
        st.plotly_chart(
            fig_sector_criticos(data["cat_criticos"], data["orden_cat"]),
            use_container_width=True,
        )
        st.subheader("Detalle por departamento crítico")
        depto_sel = st.selectbox("Departamento crítico", CRITICOS)
        st.plotly_chart(
            fig_sector_depto(data["cat_por_critico"], depto_sel),
            use_container_width=True,
        )

    elif seccion.startswith("4"):
        st.header("¿El gasto se traduce en cobertura?")
        st.markdown(
            """
**Pregunta regional:** ¿Qué región combina alto presupuesto con baja cobertura (beneficiarios por millón USD)?

**Pregunta departamental:** ¿Dónde hay mucho presupuesto, poca cobertura y muchos retrasos?
            """
        )
        st.subheader("Cobertura por región")
        fig_reg = fig_scatter_regional(data["resumen_region"])
        st.pyplot(fig_reg)
        plt.close(fig_reg)

        st.subheader("Cobertura por departamento")
        fig_dep = fig_scatter_departamental(data["resumen_depto"])
        st.pyplot(fig_dep)
        plt.close(fig_dep)
        st.caption(
            "Borde rojo: Meta, Magdalena, Atlántico, Bogotá D.C. "
            "Color = nivel de retrasos (Bajo / Medio / Alto por terciles del % retrasado)."
        )

    else:
        st.header("Conclusiones y recomendaciones")
        st.markdown(
            f"""
### Contexto
Portafolio de **{m['n_proyectos']:,} proyectos** y **USD {m['presupuesto_m_usd']:,.1f} millones**.
**{m['pct_retrasados_nacional']:.1f} %** de proyectos retrasados a nivel país.

### Hallazgo integrado
- **Presupuesto:** diversificado por región; foco en **Meta** y en **Magdalena / Atlántico** (Caribe).
- **Ejecución:** retrasos elevados en departamentos destacados por región (p. ej. Magdalena ~29 %, Bogotá ~29 %).
- **Sector:** **Infraestructura** concentra el peor ratio retraso/presupuesto en críticos; **Energía** alerta nacional.
- **Cobertura:** **Caribe** con ~**{m['caribe_benef_m']:,.0f}** beneficiarios/M USD (menor entre regiones con alto gasto).

### Recomendaciones
1. **Caribe** — revisión integrada Magdalena y Atlántico (retrasos + cobertura regional).
2. **Meta** — seguimiento por mayor peso presupuestario (~8,5 % nacional) y cobertura bajo mediana.
3. **Bogotá D.C.** — auditoría de Infraestructura y cobertura (~6.747 benef./M USD).
4. **Sector** — priorizar **Infraestructura** en el bloque crítico; Energía como política nacional.
5. Decidir con **presupuesto + retrasos + benef./M USD** conjuntos, no solo por región.
            """
        )


if __name__ == "__main__":
    main()
