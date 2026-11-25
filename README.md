# ED.03.03 – Evidencia de Desempeño: Dashboard en Streamlit

**Matrícula:** 124050194
**Materia:** Manejo Masivo de Datos (Big Data)

## Descripción

Este proyecto toma la API desarrollada en el examen del segundo parcial (repositorio `examen-p2-124050194`) y transforma sus resultados en un **dashboard interactivo hecho con Streamlit**.

La API expone los resultados del pipeline contenerizado (Docker + Hadoop MapReduce + base de datos), que responde a la pregunta:

> **¿Cuántas unidades se vendieron por método de pago y día de la semana?**

El dashboard consume esos datos desde la API y los muestra en tablas, gráficas y filtros.

## Arquitectura

```
Dataset (CSV) → Hadoop MapReduce → Base de datos → API → Dashboard Streamlit
```

## Funcionalidades del dashboard

- Consulta de datos en tiempo real desde la API
- Tabla con unidades vendidas por método de pago y día de la semana
- Gráfica de barras por método de pago
- Gráfica por día de la semana
- Filtros por método de pago y día
- Indicadores (KPIs): total de unidades, método más usado, día con más ventas

## Tecnologías

- Python 3
- Streamlit
- Pandas
- Requests
- Docker / Docker Compose
- Hadoop 3.3.6 (MapReduce)

## Estructura del repositorio

```
├── app.py               # Dashboard en Streamlit
├── requirements.txt     # Dependencias de Python
├── evidencias/          # Capturas y videos del funcionamiento
└── README.md
```

## Cómo ejecutarlo

1. Levantar la API del examen (desde el repo `examen-p2-124050194`):

   ```bash
   docker compose up -d
   ```

2. Instalar dependencias del dashboard:

   ```bash
   pip install -r requirements.txt
   ```

3. Ejecutar el dashboard:

   ```bash
   streamlit run app.py
   ```

4. Abrir en el navegador: `http://localhost:8501`

## Evidencias

Las capturas y videos del funcionamiento están en la carpeta [`evidencias/`](evidencias/).

| Evidencia | Descripción |
|---|---|
| `evidencias/01_api.png` | API funcionando y respondiendo datos |
| `evidencias/02_dashboard.png` | Vista general del dashboard |
| `evidencias/03_filtros.png` | Uso de filtros |
| `evidencias/demo.mp4` | Video del funcionamiento completo |

## Autor

Matrícula 124050194
