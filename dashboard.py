"""
Dashboard de indicadores económicos de México con datos de la API SIE de Banxico.
Materia: Herramientas de Visualización (IDIA221-4) - ED.03.03
Ejecutar con:  streamlit run dashboard.py
"""
from datetime import date, timedelta

import pandas as pd
import plotly.express as px
import requests
import streamlit as st

# ---------------------------------------------------------------
# 1. CONFIGURACIÓN DE LA PÁGINA
# ---------------------------------------------------------------
st.set_page_config(page_title="Dashboard Banxico", page_icon="💵", layout="wide")

# El token NO se escribe en el código: se lee de .streamlit/secrets.toml
TOKEN = st.secrets["BANXICO_TOKEN"]
BASE_URL = "https://www.banxico.org.mx/SieAPIRest/service/v1/series"

# Series del SIE que vamos a consultar (clave: nombre legible)
SERIES = {
    "SF43718": "Tipo de cambio FIX (MXN por USD)",
    "SF61745": "Tasa objetivo Banxico (%)",
    "SP1": "INPC (índice general)",
}


# ---------------------------------------------------------------
# 2. FUNCIÓN QUE CONSUME LA API
# ---------------------------------------------------------------
@st.cache_data(ttl=3600)  # guarda la respuesta 1 hora para no gastar peticiones
def obtener_series(claves, inicio, fin):
    """Pide varias series a Banxico y regresa un DataFrame: serie | fecha | valor."""
    url = f"{BASE_URL}/{','.join(claves)}/datos/{inicio}/{fin}"
    respuesta = requests.get(url, headers={"Bmx-Token": TOKEN}, timeout=30)
    respuesta.raise_for_status()  # si hay error (token malo, etc.) lanza excepción

    filas = []
    for serie in respuesta.json()["bmx"]["series"]:
        for dato in serie.get("datos", []):
            filas.append({"serie": serie["idSerie"], "fecha": dato["fecha"], "valor": dato["dato"]})

    df = pd.DataFrame(filas)
    # Banxico manda fechas como "dd/mm/aaaa" y valores como texto ("20.1234" o "N/E")
    df["fecha"] = pd.to_datetime(df["fecha"], format="%d/%m/%Y")
    df["valor"] = pd.to_numeric(df["valor"].str.replace(",", ""), errors="coerce")
    return df.dropna()


# ---------------------------------------------------------------
# 3. BARRA LATERAL (FILTROS)
# ---------------------------------------------------------------
st.sidebar.header("⚙️ Filtros")
hoy = date.today()
rango = st.sidebar.date_input(
    "Periodo a analizar",
    value=(hoy - timedelta(days=730), hoy),
    max_value=hoy,
)
ventana = st.sidebar.slider("Media móvil del tipo de cambio (días)", 5, 60, 20)
st.sidebar.caption("Fuente: Banco de México, Sistema de Información Económica (SIE).")

if not isinstance(rango, tuple) or len(rango) != 2:
    st.info("Selecciona la fecha de inicio y la de fin en la barra lateral.")
    st.stop()
inicio, fin = rango

# Pedimos 13 meses extra para poder calcular la inflación anual desde el inicio
inicio_api = inicio - timedelta(days=400)

try:
    datos = obtener_series(list(SERIES), inicio_api.isoformat(), fin.isoformat())
except Exception as e:
    st.error(f"No se pudo consultar la API de Banxico: {e}")
    st.stop()

# Separamos cada serie en su propio DataFrame
fix_todo = datos[datos["serie"] == "SF43718"].sort_values("fecha")
tasa_todo = datos[datos["serie"] == "SF61745"].sort_values("fecha")
inpc = datos[datos["serie"] == "SP1"].sort_values("fecha").copy()

# Transformación: inflación anual = cambio % del INPC contra 12 meses antes
inpc["inflacion_anual"] = inpc["valor"].pct_change(12) * 100

# Filtramos al periodo elegido por el usuario
en_rango = lambda df: df[(df["fecha"].dt.date >= inicio) & (df["fecha"].dt.date <= fin)].copy()
fix = en_rango(fix_todo)
tasa = en_rango(tasa_todo)
inflacion = en_rango(inpc).dropna(subset=["inflacion_anual"])

if fix.empty:
    st.warning("No hay datos en ese periodo. Prueba con otras fechas.")
    st.stop()

# ---------------------------------------------------------------
# 4. ENCABEZADO Y KPIs
# ---------------------------------------------------------------
st.title("💵 Indicadores económicos de México")
st.markdown(f"Datos en vivo de la **API SIE de Banxico** · del **{inicio:%d/%m/%Y}** al **{fin:%d/%m/%Y}**")

k1, k2, k3, k4 = st.columns(4)
fix_ultimo, fix_inicial = fix["valor"].iloc[-1], fix["valor"].iloc[0]
k1.metric(
    "Tipo de cambio FIX",
    f"${fix_ultimo:,.4f}",
    f"{fix_ultimo - fix_inicial:+.4f} en el periodo",
    delta_color="inverse",  # que suba el dólar se marca en rojo
)
k2.metric("Máximo del periodo", f"${fix['valor'].max():,.4f}", fix.loc[fix['valor'].idxmax(), 'fecha'].strftime('%d/%m/%Y'), delta_color="off")
if not tasa.empty:
    k3.metric("Tasa objetivo", f"{tasa['valor'].iloc[-1]:.2f} %",
              f"{tasa['valor'].iloc[-1] - tasa['valor'].iloc[0]:+.2f} pts", delta_color="off")
if not inflacion.empty:
    k4.metric("Inflación anual (último mes)", f"{inflacion['inflacion_anual'].iloc[-1]:.2f} %",
              inflacion["fecha"].iloc[-1].strftime("%b %Y"), delta_color="off")

st.divider()

# ---------------------------------------------------------------
# 5. GRÁFICAS
# ---------------------------------------------------------------
# Gráfica 1: tipo de cambio + media móvil
fix["media_movil"] = fix["valor"].rolling(ventana).mean()
graf1 = px.line(
    fix, x="fecha", y=["valor", "media_movil"],
    labels={"value": "MXN por USD", "fecha": "Fecha", "variable": ""},
    title=f"Tipo de cambio FIX y media móvil de {ventana} días",
)
graf1.for_each_trace(lambda t: t.update(name={"valor": "FIX diario", "media_movil": f"Media móvil {ventana} d"}[t.name]))
st.plotly_chart(graf1, use_container_width=True)

col_izq, col_der = st.columns(2)

# Gráfica 2: tasa objetivo (escalonada, porque cambia solo en decisiones de política)
with col_izq:
    if not tasa.empty:
        graf2 = px.line(tasa, x="fecha", y="valor", line_shape="hv",
                        labels={"valor": "Tasa (%)", "fecha": "Fecha"},
                        title="Tasa de interés objetivo de Banxico")
        st.plotly_chart(graf2, use_container_width=True)

# Gráfica 3: inflación anual mensual
with col_der:
    if not inflacion.empty:
        graf3 = px.bar(inflacion, x="fecha", y="inflacion_anual",
                       labels={"inflacion_anual": "Inflación anual (%)", "fecha": "Mes"},
                       title="Inflación anual (calculada con el INPC)")
        graf3.add_hline(y=3, line_dash="dash", annotation_text="Meta Banxico 3 %")
        st.plotly_chart(graf3, use_container_width=True)

# Gráfica 4: promedio mensual del tipo de cambio
fix_mensual = fix.set_index("fecha")["valor"].resample("MS").mean().reset_index()
graf4 = px.bar(fix_mensual, x="fecha", y="valor",
               labels={"valor": "Promedio MXN por USD", "fecha": "Mes"},
               title="Promedio mensual del tipo de cambio")
graf4.update_yaxes(range=[fix_mensual["valor"].min() * 0.97, fix_mensual["valor"].max() * 1.02])
st.plotly_chart(graf4, use_container_width=True)

# ---------------------------------------------------------------
# 6. TABLA Y DESCARGA
# ---------------------------------------------------------------
st.subheader("📋 Datos consultados")
tabla = en_rango(datos)
tabla["serie"] = tabla["serie"].map(SERIES)
tabla = tabla.sort_values(["serie", "fecha"], ascending=[True, False])
st.dataframe(tabla, use_container_width=True, hide_index=True)
st.download_button("⬇️ Descargar CSV", tabla.to_csv(index=False).encode("utf-8"),
                   "datos_banxico.csv", "text/csv")
