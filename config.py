# =============================================================================
# config.py — Configuración centralizada de la app
#
# Cambia solo este archivo cuando cambien las credenciales o el entorno.
# NUNCA subas este archivo a GitHub con credenciales reales.
# =============================================================================

# ── InfluxDB — Mediciones (lectura) ──────────────────────────────────────────
INFLUX_URL         = "http://localhost:8086"   # cambiar a URL de la nube cuando esté listo
INFLUX_TOKEN       = "BAYhSxshHUM6sHDULAWHrW_v5XHova6DYE2xik4bcFJHUU9_o61t5vOQdywKs56PVo1C5V5VOBD4CAOa8FYFTA=="
INFLUX_ORG         = "Universidad de Antioquia"                    # cambiar a "colombia" cuando sea la nube
INFLUX_BUCKET_DATA = "Microrred"               # cambiar a "microgrid" cuando sea la nube
MEASUREMENT_DATA   = "microgridDB1"            # cambiar a nombre real cuando el profesor confirme

# ── InfluxDB — Control (lectura y escritura) ──────────────────────────────────
INFLUX_BUCKET_CTRL = "Control"                 # cambiar a bucket de control de la nube
MEASUREMENT_CTRL   = "control"

# ── App ───────────────────────────────────────────────────────────────────────
INTERVALO_REFRESCO = 3000    # milisegundos entre refrescos del diagrama
DEBUG              = True    # cambiar a False en producción