# Dashboard Banxico con Streamlit

ED.03.03 – Herramientas de Visualización (IDIA221-4)

Dashboard que consume la **API SIE de Banxico** y transforma sus datos en indicadores y gráficas interactivas:

- Tipo de cambio FIX (serie `SF43718`) con media móvil ajustable
- Tasa de interés objetivo (serie `SF61745`)
- Inflación anual calculada a partir del INPC (serie `SP1`)
- Promedio mensual del tipo de cambio
- Tabla de datos y descarga en CSV

## Cómo ejecutarlo

1. Instalar dependencias:
   ```
   pip install -r requirements.txt
   ```
2. Obtener un token en https://www.banxico.org.mx/SieAPIRest/service/v1/token
3. Crear el archivo `.streamlit/secrets.toml` con:
   ```
   BANXICO_TOKEN = "tu_token"
   ```
4. Ejecutar:
   ```
   streamlit run dashboard.py
   ```

## Evidencias

Las capturas o el video del funcionamiento están en la carpeta `evidencias/`.
