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
INFLUX_URL   = "http://localhost:8086"
INFLUX_TOKEN = "BAYhSxshHUM6sHDULAWHrW_v5XHova6DYE2xik4bcFJHUU9_o61t5vOQdywKs56PVo1C5V5VOBD4CAOa8FYFTA=="      # pega tu token aquí
INFLUX_ORG   = "Universidad de Antioquia"
INFLUX_BUCKET= "Microrred"

# ── Columnas a excluir ──────────────────────────────────
# Metadatos de InfluxDB que no son variables de medición
EXCLUIR = ['result', 'table', '_start', '_stop', '_measurement',
           'humidity', 'rollangle', 'tiltangle']

# ── Leer y preparar datos ───────────────────────────────
df = pd.read_csv('datos/2026_datos_05.csv')
df['_time'] = pd.to_datetime(df['_time'], format='mixed', utc=True)

# Filtrar últimos 30 días
#fecha_corte = df['_time'].max() - pd.Timedelta(days=30)
#df = df[df['_time'] >= fecha_corte].copy()
#print(f"Filas a cargar: {len(df):,}")

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
LOTE = 1000
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