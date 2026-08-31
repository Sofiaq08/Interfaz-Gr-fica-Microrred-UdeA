""""
FORMA DE GUARDAR DATOS EN INFLUXDB
measurement: microgridDB1
time: 2026-05-20 00:00:01
campos:
    CurrentBattery = -3.8
    PowerBattery = -189.0
    power_grid = 5.2
    ...
"""

import pandas as pd
from influxdb_client import InfluxDBClient, Point, WriteOptions
from influxdb_client.client.write_api import SYNCHRONOUS
from datetime import datetime

# ── Configuración InfluxDB ──────────────────────────────
INFLUX_URL   = "https://us-east-1-1.aws.cloud2.influxdata.com"
INFLUX_TOKEN = "3xJSNJ4AEKl2Y3AMcpJDKFzxoP44zrI5hC6YTZzRKBlxg428ujnIUWeqrMpOdsIexoFfBQL-EMm3kOBFg6V3Ig=="      # pega tu token aquí
INFLUX_ORG   = "UdeA"
INFLUX_BUCKET= "Microrred"

# ── Columnas a excluir ──────────────────────────────────
# Metadatos de InfluxDB que no son variables de medición
EXCLUIR = ['result', 'table', '_start', '_stop', '_measurement',
           'humidity', 'rollangle', 'tiltangle']

# ── Leer y preparar datos ───────────────────────────────
df = pd.read_csv('datos/2026_datos_05.csv')
df['_time'] = pd.to_datetime(df['_time'], format='mixed', utc=True)

# Filtrar últimos 30 días
from datetime import datetime, timezone, timedelta

# Desplazar las fechas al mes actual para que entren en el periodo de retención
fecha_max_original = df['_time'].max()
fecha_max_nueva = datetime.now(timezone.utc) - timedelta(days=1)
diferencia = fecha_max_nueva - fecha_max_original

# Aplicar el desplazamiento a todas las fechas
df['_time'] = df['_time'] + diferencia

# Tomar los últimos 25 días (para no acercarse al límite de 30)
fecha_corte = df['_time'].max() - pd.Timedelta(hours=1)
df = df[df['_time'] >= fecha_corte].copy()
print(f"Rango de fechas ajustado:")
print(f"  Inicio: {df['_time'].min()}")
print(f"  Fin:    {df['_time'].max()}")


# Eliminar columnas excluidas
df = df.drop(columns=[c for c in EXCLUIR if c in df.columns])

# Eliminar filas donde TODAS las variables son NaN
cols_datos = [c for c in df.columns if c != '_time']
df = df.dropna(subset=cols_datos, how='all')
print(f"Filas después de limpiar: {len(df):,}")

# ── Conectar a InfluxDB ─────────────────────────────────
print("Conectando a InfluxDB...")
client = InfluxDBClient(
    url=INFLUX_URL,
    token=INFLUX_TOKEN,
    org=INFLUX_ORG
)
write_api = client.write_api(write_options=SYNCHRONOUS)

# ── Cargar datos en lotes ───────────────────────────────
# Cargamos de 1000 en 1000 filas para no saturar la memoria
LOTE = 100
total = len(df)
cargadas = 0

print("Cargando datos...")
for i in range(0, total, LOTE):
    lote = df.iloc[i:i+LOTE]
    puntos = []

    for _, fila in lote.iterrows():
        punto = Point("microgridDB1").time(fila['_time'])

        # Agregar cada columna como campo
        for col in cols_datos:
            valor = fila[col]
            if pd.notna(valor):          # solo si tiene valor
                punto = punto.field(col, float(valor))

        puntos.append(punto)

    write_api.write(bucket=INFLUX_BUCKET, org=INFLUX_ORG, record=puntos)
    cargadas += len(lote)
    print(f"  {cargadas:,} / {total:,} filas cargadas ({round(cargadas/total*100)}%)")

client.close()
print("✓ Carga completada")