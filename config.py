from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATA_PATH = BASE_DIR / "dataset_evaluacion_unidad1.csv"

CRITICOS = ["Meta", "Magdalena", "Atlántico", "Bogotá D.C."]
ORDEN_ESTADO_A = ["Retrasado", "En Planeación", "En Ejecución", "Finalizado"]
ORDEN_REGION = ["Orinoquía", "Amazonía", "Pacífica", "Caribe", "Andina"]

COLOR_REGION = {
    "Orinoquía": "#2563EB",
    "Amazonía": "#16A34A",
    "Pacífica": "#7C3AED",
    "Caribe": "#DC2626",
    "Andina": "#D97706",
}

COLOR_DEPARTAMENTO_CRITICO = {
    "Meta": "#2563EB",
    "Magdalena": "#DC2626",
    "Atlántico": "#7C3AED",
    "Bogotá D.C.": "#D97706",
}

COLOR_DESTACADO = "#2563EB"
COLOR_NAVY = "#0F172A"
COLOR_ALERTA = "#DC2626"
COLOR_NEUTRO = "#CBD5E1"
COLOR_NEUTRO_2 = "#E5E7EB"
COLOR_TEXTO = "#2B2B2B"
COLOR_TEXTO_SEC = "#666666"
COLOR_FONDO = "white"

COLOR_ESTADO = {
    "En Planeación": "#CBD5E1",
    "En Ejecución": "#2563EB",
    "Retrasado": "#DC2626",
    "Finalizado": "#64748B",
}

GRAY_ESTADO = {
    "En Planeación": "#E5E7EB",
    "En Ejecución": "#9CA3AF",
    "Retrasado": "#6B7280",
    "Finalizado": "#4B5563",
}

GRAY_PRESUP = "#E5E7EB"
GRAY_RETASO = "#9CA3AF"
COLOR_METRICA = {
    "% presupuesto nacional": "#2563EB",
    "% proyectos retrasados": "#DC2626",
}

CATEGORIA_DESTACADA_G1 = "Energía"
CATEGORIA_DESTACADA_G2 = "Infraestructura"

ORDEN_SEGMENTO_RETRASO = ["Bajo", "Medio", "Alto"]
COLOR_SEGMENTO_RETRASO = {
    "Bajo": "#16A34A",
    "Medio": "#D97706",
    "Alto": "#DC2626",
}

COLOR_TEXTO_OSCURO = "#0F172A"
COLOR_TEXTO_MEDIO = "#64748B"
COLOR_EJE = "#94A3B8"
COLOR_GRID = "#EEF2F6"

COLOR_GRIS_1 = "#374151"
COLOR_GRIS_2 = "#6B7280"
COLOR_GRIS_3 = "#9CA3AF"
COLOR_GRIS_BASE = "#E5E7EB"
