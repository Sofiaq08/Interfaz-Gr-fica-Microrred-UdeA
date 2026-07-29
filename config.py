# =============================================================================
# config.py — Configuración centralizada de la app
#
# Cambia solo este archivo cuando cambien las credenciales o el entorno.
# NUNCA subas este archivo a GitHub con credenciales reales.
# =============================================================================

# ── InfluxDB — Mediciones (lectura) ──────────────────────────────────────────
INFLUX_URL         = "https://us-east-1-1.aws.cloud2.influxdata.com"   # cambiar a URL de la nube cuando esté listo
INFLUX_TOKEN       = "ogJtAMxVe9SO75JNiIEdLhoy7UKM0DyH7ZD-O5Q-Xyg3xjY8jY2L_Cpm6hvreBsomzvOz3FPX9qg09PD3QQQmg=="  
INFLUX_ORG         = "colombia"                    # cambiar a "colombia" cuando sea la nube
INFLUX_BUCKET_DATA = "microgrid"               # cambiar a "microgrid" cuando sea la nube
MEASUREMENT_DATA   = "prueba"            # cambiar a nombre real cuando el profesor confirme

# ── InfluxDB — Control (lectura y escritura) ──────────────────────────────────
INFLUX_BUCKET_CTRL = "microgrid"                 # cambiar a bucket de control de la nube
MEASUREMENT_CTRL   = "prueba"

# ── App ───────────────────────────────────────────────────────────────────────
INTERVALO_REFRESCO = 5000    # milisegundos entre refrescos del diagrama
DEBUG              = True    # cambiar a False en producción