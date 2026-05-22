"""Carga y agregaciones del portafolio (misma lógica que el notebook)."""

from __future__ import annotations

import pandas as pd

from config import CRITICOS, DATA_PATH, ORDEN_ESTADO_A


def load_raw() -> pd.DataFrame:
    df = pd.read_csv(DATA_PATH)
    df["Fecha_Inicio"] = pd.to_datetime(df["Fecha_Inicio"], errors="coerce")
    df["Presupuesto_USD"] = pd.to_numeric(df["Presupuesto_USD"], errors="coerce")
    return df


def build_analitico(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["Presupuesto_Millones_USD"] = out["Presupuesto_USD"] / 1_000_000
    out["Beneficiarios_por_Millon_USD"] = (
        out["Poblacion_Beneficiada"] / out["Presupuesto_Millones_USD"].replace(0, pd.NA)
    )
    return out


def resumen_region(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df.assign(Impacto_Alto=lambda d: (d["Nivel_Impacto"] == "Alto").astype(int))
        .groupby("Region", as_index=False)
        .agg(
            Proyectos=("ID_Proyecto", "count"),
            Presupuesto_Total_USD=("Presupuesto_USD", "sum"),
            Poblacion_Beneficiada=("Poblacion_Beneficiada", "sum"),
        )
        .assign(
            Presupuesto_Millones_USD=lambda d: d["Presupuesto_Total_USD"] / 1_000_000,
        )
        .assign(
            Beneficiarios_por_Millon_USD=lambda d: (
                d["Poblacion_Beneficiada"] / d["Presupuesto_Millones_USD"]
            ),
        )
    )


def treemap_departamentos(df: pd.DataFrame) -> pd.DataFrame:
    t = (
        df.groupby(["Region", "Departamento"], as_index=False)
        .agg(
            Presupuesto_USD=("Presupuesto_USD", "sum"),
            Proyectos=("ID_Proyecto", "count"),
        )
    )
    t["Pais"] = "Colombia"
    total = t["Presupuesto_USD"].sum()
    t["Pct_Pais"] = 100 * t["Presupuesto_USD"] / total
    return t


def conteo_depto_por_region(df: pd.DataFrame) -> pd.DataFrame:
    c = (
        df.groupby(["Region", "Departamento", "Estado"], as_index=False)
        .size()
        .rename(columns={"size": "Proyectos"})
    )
    c["Estado"] = pd.Categorical(c["Estado"], categories=ORDEN_ESTADO_A, ordered=True)
    c["Pct"] = c.groupby(["Region", "Departamento"])["Proyectos"].transform(
        lambda s: 100 * s / s.sum()
    )
    return c


def presupuesto_depto(df: pd.DataFrame) -> pd.DataFrame:
    p = df.groupby(["Region", "Departamento"], as_index=False)["Presupuesto_USD"].sum()
    total = p["Presupuesto_USD"].sum()
    p["Pct_Pais"] = 100 * p["Presupuesto_USD"] / total
    return p


def top2_retraso_por_region(df: pd.DataFrame) -> dict[str, set[str]]:
    retraso = (
        df[df["Estado"] == "Retrasado"]
        .groupby(["Region", "Departamento"])
        .size()
        .reset_index(name="N_Retrasados")
    )
    totales = (
        df.groupby(["Region", "Departamento"])
        .size()
        .reset_index(name="N_Proyectos")
    )
    merged = totales.merge(retraso, on=["Region", "Departamento"], how="left")
    merged["N_Retrasados"] = merged["N_Retrasados"].fillna(0).astype(int)
    merged["Pct_Retrasado"] = 100 * merged["N_Retrasados"] / merged["N_Proyectos"]
    top2 = (
        merged.sort_values(
            ["Region", "Pct_Retrasado", "N_Retrasados"],
            ascending=[True, False, False],
        )
        .groupby("Region", as_index=False)
        .head(2)
    )
    return top2.groupby("Region")["Departamento"].apply(set).to_dict()


def tabla_categoria(df: pd.DataFrame, etiqueta_pct_presup: str) -> pd.DataFrame:
    agg = (
        df.groupby("Categoria", as_index=False)
        .agg(
            Presupuesto_USD=("Presupuesto_USD", "sum"),
            Proyectos=("ID_Proyecto", "count"),
        )
    )
    total_presup = agg["Presupuesto_USD"].sum()
    agg[etiqueta_pct_presup] = 100 * agg["Presupuesto_USD"] / total_presup
    retrasos = df[df["Estado"] == "Retrasado"].groupby("Categoria").size()
    agg["N_Retrasados"] = agg["Categoria"].map(retrasos).fillna(0).astype(int)
    agg["Pct_Retrasados"] = 100 * agg["N_Retrasados"] / agg["Proyectos"]
    return agg.sort_values("Presupuesto_USD", ascending=False)


def tablas_sector(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    cat_nacional = tabla_categoria(df, "Pct_Presup_Pais")
    cat_criticos = tabla_categoria(df[df["Departamento"].isin(CRITICOS)], "Pct_Presup_Criticos")
    filas = []
    for depto in CRITICOS:
        t = tabla_categoria(df[df["Departamento"] == depto], "Pct_Presup_Depto")
        t["Departamento"] = depto
        filas.append(t)
    cat_por_critico = pd.concat(filas, ignore_index=True)
    return cat_nacional, cat_criticos, cat_por_critico


def resumen_departamentos(df: pd.DataFrame) -> pd.DataFrame:
    r = (
        df.groupby(["Region", "Departamento"], as_index=False)
        .agg(
            Proyectos=("ID_Proyecto", "count"),
            Presupuesto_USD=("Presupuesto_USD", "sum"),
            Poblacion_Beneficiada=("Poblacion_Beneficiada", "sum"),
            Retrasados=("Estado", lambda s: (s == "Retrasado").sum()),
        )
    )
    total = r["Presupuesto_USD"].sum()
    r["Presupuesto_Millones_USD"] = r["Presupuesto_USD"] / 1_000_000
    r["Pct_Pais"] = 100 * r["Presupuesto_USD"] / total
    r["Pct_Retrasados"] = 100 * r["Retrasados"] / r["Proyectos"]
    r["Beneficiarios_por_Millon_USD"] = (
        r["Poblacion_Beneficiada"] / r["Presupuesto_Millones_USD"].replace(0, pd.NA)
    )
    return r


def metricas_clave(df: pd.DataFrame) -> dict:
    total_m = df["Presupuesto_USD"].sum() / 1_000_000
    pct_ret = 100 * (df["Estado"] == "Retrasado").mean()
    reg = resumen_region(df)
    caribe = reg.loc[reg["Region"] == "Caribe", "Beneficiarios_por_Millon_USD"].iloc[0]
    return {
        "n_proyectos": len(df),
        "presupuesto_m_usd": total_m,
        "pct_retrasados_nacional": pct_ret,
        "caribe_benef_m": caribe,
    }
