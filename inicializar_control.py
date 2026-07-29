# =============================================================================
# inicializar_control.py
#
# Escribe el estado inicial de todos los contactores y variables de control
# en el bucket "Control" de InfluxDB.
#
# Corre este script UNA SOLA VEZ para inicializar el bucket.
# Después la app web será la que escriba los cambios.
# =============================================================================

from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS
from datetime import datetime, timezone

INFLUX_URL    = "https://us-east-1-1.aws.cloud2.influxdata.com"
INFLUX_TOKEN  = "ogJtAMxVe9SO75JNiIEdLhoy7UKM0DyH7ZD-O5Q-Xyg3xjY8jY2L_Cpm6hvreBsomzvOz3FPX9qg09PD3QQQmg=="
INFLUX_ORG    = "colombia"
INFLUX_BUCKET = "microgrid"

# Estado inicial de los 13 contactores + 2 variables de control
ESTADO_INICIAL = {
    # Contactores (True = ISLANDED, False = CONNECTED)
    "estado_operador_red":   True,
    "estado_fronius":        False,
    "estado_carga_elec":     False,
    "estado_electrolizador": True,
    "estado_enphase":        True,
    "estado_gab_ilum":       False,
    "piso1P":     True,
    "piso2P":     True,
    "piso3P":     True,
    "estado_gab_exp":        False,
    "estado_piso1_exp":      True,
    "estado_piso2_exp":      True,
    "islaP":     True,

    # Variables de control
    "setpoint_potencia_kw":  0.0,
    "modo_isla":             False,
}

print("Conectando a InfluxDB...")
client = InfluxDBClient(
    url=INFLUX_URL,
    token=INFLUX_TOKEN,
    org=INFLUX_ORG
)
write_api = client.write_api(write_options=SYNCHRONOUS)

# Crear un punto con todos los estados
punto = Point("control").time(datetime.now(timezone.utc))

for campo, valor in ESTADO_INICIAL.items():
    # InfluxDB guarda bool como 0/1 para facilitar las queries
    if isinstance(valor, bool):
        punto = punto.field(campo, int(valor))
    else:
        punto = punto.field(campo, float(valor))

write_api.write(bucket=INFLUX_BUCKET, org=INFLUX_ORG, record=punto)
client.close()

print("✓ Estado inicial escrito en bucket Control")
print()
print("Campos escritos:")
for campo, valor in ESTADO_INICIAL.items():
    print(f"  {campo:<28} = {valor}")