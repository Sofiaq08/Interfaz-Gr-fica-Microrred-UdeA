# =============================================================================
# datos.py  —  Capa de datos de la Microrred HMI
#
# FASE ACTUAL: datos en memoria (diccionarios Python).
# FASE SIGUIENTE: reemplazar el interior de cada función por queries/escrituras
#                 a InfluxDB. La firma de cada función NO cambia.
#
# Convención de estados de contactor:
#   True  → ISLANDED  (toggle verde  #22c55e)
#   False → CONNECTED (toggle rojo   #ef4444)
# =============================================================================

import random
from config import (
    INFLUX_URL, INFLUX_TOKEN, INFLUX_ORG,
    INFLUX_BUCKET_DATA, INFLUX_BUCKET_CTRL,
    MEASUREMENT_DATA, MEASUREMENT_CTRL
)
from datetime import datetime, timezone

# -----------------------------------------------------------------------------
# ESTADO INTERNO — nunca acceder directamente desde app.py o acciones.py.
# Usar siempre las funciones get_* / set_* de abajo.
# -----------------------------------------------------------------------------

_estados = {
    # ── Contactores (True = ISLANDED, False = CONNECTED) ─────────────────────
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

    # ── Variables de control (campos nuevos que se crearán en InfluxDB) ───────
    "setpoint_potencia_kw":  0.0,   # float  — potencia de referencia del inversor
}


# -----------------------------------------------------------------------------
# LECTURA DE ESTADOS
# -----------------------------------------------------------------------------

def get_estados() -> dict:
    """
    Lee el último estado de todos los contactores y variables de control
    desde el bucket Control de InfluxDB.
    """
    from influxdb_client import InfluxDBClient

    INFLUX_BUCKET = INFLUX_BUCKET_CTRL

    try:
        client = InfluxDBClient(
            url=INFLUX_URL,
            token=INFLUX_TOKEN,
            org=INFLUX_ORG
        )
        query_api = client.query_api()

        query = f'''
        from(bucket: "{INFLUX_BUCKET}")
          |> range(start: -30d)
          |> filter(fn: (r) => r._measurement == "{MEASUREMENT_CTRL}")
          |> last()
        '''

        resultado = query_api.query(query=query, org=INFLUX_ORG)
        client.close()

        # Partir del estado por defecto y sobreescribir con lo que viene de InfluxDB
        estados = dict(_estados)
        for tabla in resultado:
            for registro in tabla.records:
                campo = registro.get_field()
                valor = registro.get_value()
                if campo in estados:
                    # Convertir 0/1 a bool para los contactores
                    if campo.startswith("estado_") or campo == "modo_isla":
                        estados[campo] = bool(int(valor))
                    else:
                        estados[campo] = valor

        print("Estados leídos de InfluxDB:", estados)   #NUEVOOOO

        return estados

    except Exception as e:
        print(f"Error InfluxDB get_estados: {e}")
        print("Usando estados en memoria")   #NUEVOOO
        return dict(_estados)


def get_estado_contactor(nombre: str) -> bool:
    """
    Devuelve el estado de UN contactor específico.

    Args:
        nombre: clave tal como aparece en _estados,
                p. ej. "estado_operador_red".

    Raises:
        KeyError si el nombre no existe.
    """
    return _estados[nombre]


# -----------------------------------------------------------------------------
# LECTURA DE MEDICIONES
# -----------------------------------------------------------------------------

def get_mediciones() -> dict:
    """
    Devuelve las últimas mediciones del sistema desde InfluxDB.

    Nombres de campo: idénticos a las columnas del CSV de InfluxDB.
    """
    from influxdb_client import InfluxDBClient


    INFLUX_BUCKET = INFLUX_BUCKET_DATA

    CAMPOS = [
        "CurrentBattery", "PowerBattery", "SoCBattery", "VoltageBattery",
        "carga_total", "power_fronius", "power_grid", "power_quattro",
        "irradiance", "temperature", "EnergiaFroniusSc", "EnergiaIlumSc",
        "EnergiaMicrosSc", "PowerFroniusSc", "PowerIlumSc", "PowerMicrosSc",
        "Piso1", "Piso2", "Piso3", "isla", "EnergiaPM5500",
    ]

    # Construir el filtro de campos para la query Flux
    campos_flux = " or ".join([f'r._field == "{c}"' for c in CAMPOS])

    try:
        client = InfluxDBClient(
            url=INFLUX_URL,
            token=INFLUX_TOKEN,
            org=INFLUX_ORG
        )
        query_api = client.query_api()

        query = f'''
        from(bucket: "{INFLUX_BUCKET}")
          |> range(start: -60d)
          |> filter(fn: (r) => r._measurement == "{MEASUREMENT_DATA}")
          |> filter(fn: (r) => {campos_flux})
          |> last()
        '''

        resultado = query_api.query(query=query, org=INFLUX_ORG)
        client.close()

        mediciones = {"_time": datetime.now(timezone.utc)}
        for tabla in resultado:
            for registro in tabla.records:
                mediciones[registro.get_field()] = registro.get_value()

        return mediciones

    except Exception as e:
        print(f"Error InfluxDB get_mediciones: {e}")
        return {
            "_time":          datetime.now(timezone.utc),
            "CurrentBattery": 0, "PowerBattery":  0, "SoCBattery":    0,
            "VoltageBattery": 0, "carga_total":   0, "power_fronius": 0,
            "power_grid":     0, "power_quattro": 0, "irradiance":    0,
            "temperature":    0,
        }


# -----------------------------------------------------------------------------
# ESCRITURA DE ESTADOS
# -----------------------------------------------------------------------------

def _guardar_estados() -> None:
    """Escribe el estado actual en estados.json para debug."""
    import json
    from datetime import datetime
    datos_debug = {
        "ultima_actualizacion": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        **_estados
    }
    with open("estados.json", "w", encoding="utf-8") as f:
        json.dump(datos_debug, f, indent=2, default=str)

def set_contactor(nombre: str, estado: bool) -> None:
    """
    Escribe el nuevo estado de un contactor en el bucket Control de InfluxDB.
    """
    from influxdb_client import InfluxDBClient, Point
    from influxdb_client.client.write_api import SYNCHRONOUS
    
    if nombre not in _estados:
        raise KeyError(f"Contactor desconocido: '{nombre}'.")
    if not isinstance(estado, bool):
        raise TypeError(f"estado debe ser bool, recibido: {type(estado)}")


    INFLUX_BUCKET = INFLUX_BUCKET_CTRL

    try:
        client = InfluxDBClient(
            url=INFLUX_URL,
            token=INFLUX_TOKEN,
            org=INFLUX_ORG
        )
        write_api = client.write_api(write_options=SYNCHRONOUS)

        punto = Point(MEASUREMENT_CTRL) \
            .field(nombre, int(estado)) \
            .time(datetime.now(timezone.utc))

        write_api.write(bucket=INFLUX_BUCKET, org=INFLUX_ORG, record=punto)
        client.close()

        # Actualizar también en memoria para respuesta inmediata
        _estados[nombre] = estado
        _guardar_estados()

    except Exception as e:
        print(f"Error InfluxDB set_contactor: {e}")
        # Si falla InfluxDB, al menos actualiza en memoria
        _estados[nombre] = estado


def set_setpoint(valor: float) -> None:
    from influxdb_client import InfluxDBClient, Point
    from influxdb_client.client.write_api import SYNCHRONOUS

    if not (0.0 <= valor <= 15.0):
        raise ValueError(f"Setpoint fuera de rango [0, 15] kW: {valor}")


    INFLUX_BUCKET = INFLUX_BUCKET_CTRL

    try:
        client = InfluxDBClient(
            url=INFLUX_URL,
            token=INFLUX_TOKEN,
            org=INFLUX_ORG
        )
        write_api = client.write_api(write_options=SYNCHRONOUS)

        punto = Point(MEASUREMENT_CTRL) \
            .field("setpoint_potencia_kw", float(valor)) \
            .time(datetime.now(timezone.utc))

        write_api.write(bucket=INFLUX_BUCKET, org=INFLUX_ORG, record=punto)
        client.close()

        _estados["setpoint_potencia_kw"] = float(valor)
        _guardar_estados()

    except Exception as e:
        print(f"Error InfluxDB set_setpoint: {e}")
        _estados["setpoint_potencia_kw"] = float(valor)


def set_modo_isla(activo: bool) -> None:
    from influxdb_client import InfluxDBClient, Point
    from influxdb_client.client.write_api import SYNCHRONOUS

    if not isinstance(activo, bool):
        raise TypeError(f"activo debe ser bool, recibido: {type(activo)}")


    INFLUX_BUCKET = INFLUX_BUCKET_CTRL

    try:
        client = InfluxDBClient(
            url=INFLUX_URL,
            token=INFLUX_TOKEN,
            org=INFLUX_ORG
        )
        write_api = client.write_api(write_options=SYNCHRONOUS)

        punto = Point(MEASUREMENT_CTRL) \
            .field("modo_isla", int(activo)) \
            .time(datetime.now(timezone.utc))

        write_api.write(bucket=INFLUX_BUCKET, org=INFLUX_ORG, record=punto)
        client.close()

        _estados["modo_isla"] = activo
        _guardar_estados()

    except Exception as e:
        print(f"Error InfluxDB set_modo_isla: {e}")
        _estados["modo_isla"] = activo

# -----------------------------------------------------------------------------
# UTILIDAD — mapeo toggle-id → clave de estado
# Usado por acciones.py y los callbacks de app.py para no hardcodear strings.
# -----------------------------------------------------------------------------

TOGGLE_A_ESTADO = {
    "toggle-operador-red":   "estado_operador_red",
    "toggle-fronius":        "estado_fronius",
    "toggle-carga-elec":     "estado_carga_elec",
    "toggle-electrolizador": "estado_electrolizador",
    "toggle-enphase":        "estado_enphase",
    "toggle-gab-ilum":       "estado_gab_ilum",
    "toggle-piso1-ilum":     "piso1P",
    "toggle-piso2-ilum":     "piso2P",
    "toggle-piso3-ilum":     "piso3P",
    "toggle-gab-exp":        "estado_gab_exp",
    "toggle-piso1-exp":      "estado_piso1_exp",
    "toggle-piso2-exp":      "estado_piso2_exp",
    "toggle-quattro-or":     "islaP",
}
