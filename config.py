# =============================================================================
# config.py — Configuración centralizada de la app
#
# Cambia solo este archivo cuando cambien las credenciales o el entorno.
# NUNCA subas este archivo a GitHub con credenciales reales.
# =============================================================================

# ── InfluxDB — Mediciones (lectura) ──────────────────────────────────────────
INFLUX_URL         = "https://us-east-1-1.aws.cloud2.influxdata.com"   # cambiar a URL de la nube cuando esté listo
INFLUX_TOKEN       = "3xJSNJ4AEKl2Y3AMcpJDKFzxoP44zrI5hC6YTZzRKBlxg428ujnIUWeqrMpOdsIexoFfBQL-EMm3kOBFg6V3Ig=="  
INFLUX_ORG         = "UdeA"                    # cambiar a "colombia" cuando sea la nube
INFLUX_BUCKET_DATA = "Microrred"               # cambiar a "microgrid" cuando sea la nube
MEASUREMENT_DATA   = "microgridDB1"            # cambiar a nombre real cuando el profesor confirme

# ── InfluxDB — Control (lectura y escritura) ──────────────────────────────────
INFLUX_BUCKET_CTRL = "Microrred"                 # cambiar a bucket de control de la nube
MEASUREMENT_CTRL   = "control"

# ── App ───────────────────────────────────────────────────────────────────────
INTERVALO_REFRESCO = 1000    # milisegundos entre refrescos del diagrama
DEBUG              = True    # cambiar a False en producción