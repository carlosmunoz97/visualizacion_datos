from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATA_PATH = BASE_DIR / "dataset_evaluacion_unidad1.csv"

CRITICOS = ["Meta", "Magdalena", "Atlántico", "Bogotá D.C."]
ORDEN_ESTADO_A = ["Retrasado", "En Planeación", "En Ejecución", "Finalizado"]
ORDEN_REGION = ["Orinoquía", "Amazonía", "Pacífica", "Caribe", "Andina"]

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
