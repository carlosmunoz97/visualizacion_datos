<p align="center">
  <img src="https://latimpacto.org/wp-content/uploads/2023/11/Eafit.png" width="40%">
</p>

## Integrantes

- Juan Camilo Cataño Zuleta
- Juan Manuel Agudelo Olarte
- Carlos José Muñoz Cabrera 
- Miguel Roldan Yepes
  
# Visualización del portafolio de proyectos en Colombia

## 1. Descripción general

El análisis se documenta en dos notebooks:

| Archivo | Uso |
|---------|-----|
| **`taller 2/Visualizacion_datos_entrega.ipynb`** | Entrega del taller 2: EDA iterativo → hallazgo → visualizaciones aclaratorias → puente al dashboard |
| `Visualizacion_datos_P.ipynb` | Notebook histórico de trabajo y experimentación (raíz del repo) |

El objetivo principal es construir visualizaciones claras, justificadas y orientadas a la toma de decisiones, aplicando principios de ingeniería de la atención, reducción de ruido visual, ordenamiento lógico de los datos y uso selectivo del color.

El análisis se complementa con un **dashboard web interactivo** en Streamlit (`app.py`), donde las mismas visualizaciones están organizadas en secciones ejecutivas.

---

## 2. Objetivo del notebook

Diseñar y justificar visualizaciones que permitan responder preguntas clave del portafolio:

1. ¿Dónde se concentra el presupuesto nacional?
2. ¿Qué departamentos presentan mayores niveles de retraso?
3. ¿Qué categorías concentran simultáneamente presupuesto y retrasos?
4. ¿El gasto asignado se traduce en cobertura poblacional?
5. ¿Qué regiones o departamentos deben priorizarse para seguimiento?

---

## 3. Datos utilizados

El notebook utiliza una base de datos de proyectos con variables como:

- `ID_Proyecto`
- `Region`
- `Departamento`
- `Categoria`
- `Estado`
- `Presupuesto_USD`
- `Poblacion_Beneficiada`
- `Fecha_Inicio`
- `Nivel_Impacto`

A partir de estas variables se construyen indicadores derivados:

- presupuesto total por región y departamento;
- porcentaje del presupuesto nacional;
- número total de proyectos;
- número y porcentaje de proyectos retrasados;
- población beneficiada;
- beneficiarios por millón de USD;
- segmentos de retraso: bajo, medio y alto.

---

## 4. Estructura del análisis

El notebook está organizado en las siguientes etapas:

### 4.1. Carga y preparación de datos

Se cargan los datos originales y se convierten variables relevantes a formatos adecuados, por ejemplo:

- fechas;
- valores numéricos de presupuesto;
- indicadores derivados de eficiencia y cobertura.

### 4.2. Análisis del presupuesto

Se analiza la distribución del presupuesto nacional por región y departamento.

Las visualizaciones principales son:

- treemap de distribución territorial del presupuesto;
- gráfico de barras jerárquico por departamento, ordenado por región y porcentaje de presupuesto nacional.

En el gráfico jerárquico se muestran todos los departamentos, pero se utiliza una escala de grises para controlar la atención visual. Los departamentos con mayor participación presupuestal dentro de cada región aparecen con mayor contraste.

### 4.3. Ejecución por departamento

Se evalúa la distribución de proyectos por estado:

- en planeación;
- en ejecución;
- retrasado;
- finalizado.

La visualización utiliza color rojo únicamente para los proyectos retrasados. Los demás estados se presentan en escala de grises para reducir ruido visual y reforzar la lectura del problema de ejecución.

### 4.4. Análisis sectorial

Se comparan dos métricas por categoría:

- porcentaje del presupuesto;
- porcentaje de proyectos retrasados.

Se desarrollan dos niveles de análisis:

1. Nivel nacional, con énfasis en la categoría `Energía`.
2. Departamentos críticos, con énfasis en la categoría `Infraestructura`.

El color se usa de forma selectiva para resaltar la categoría estratégica, mientras que las demás categorías se mantienen en tonos neutros.

### 4.5. Cobertura regional y departamental

Se analiza si el presupuesto asignado se traduce en cobertura poblacional, usando el indicador:

`Beneficiarios por millón de USD`

Se construyen gráficos de dispersión para comparar:

- presupuesto asignado;
- cobertura relativa;
- retrasos;
- departamentos críticos.

---
