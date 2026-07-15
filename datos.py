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
    "estado_piso1_ilum":     True,
    "estado_piso2_ilum":     True,
    "estado_piso3_ilum":     True,
    "estado_gab_exp":        False,
    "estado_piso1_exp":      True,
    "estado_piso2_exp":      True,
    "estado_quattro_or":     True,

    # ── Variables de control (campos nuevos que se crearán en InfluxDB) ───────
    "setpoint_potencia_kw":  0.0,   # float  — potencia de referencia del inversor
    "modo_isla":             False,  # bool   — True = sistema en modo isla
}


# -----------------------------------------------------------------------------
# LECTURA DE ESTADOS
# -----------------------------------------------------------------------------

def get_estados() -> dict:
    """
    Devuelve una copia del estado actual de todos los contactores
    y las variables de control.

    Retorna:
        dict con las mismas claves que _estados.

    Cuando se conecte InfluxDB:
        Reemplazar el return por una query Flux al bucket de control
        que lea el último punto de cada campo estado_* y las variables nuevas.
    """
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
    Devuelve las últimas mediciones del sistema.

    Nombres de campo: idénticos a las columnas del CSV de InfluxDB para
    que el cambio futuro sea un simple swap de esta función.

    Retorna dict con:
        _time             — timestamp de la medición (datetime UTC)
        CurrentBattery    — corriente de batería [A]
        PowerBattery      — potencia de batería [W]
        SoCBattery        — estado de carga batería [%]  0-100
        VoltageBattery    — tensión de batería [V]
        carga_total       — potencia total de carga [kW]
        humidity          — humedad relativa [%]
        irradiance        — irradiancia solar [W/m²]
        power_fronius     — potencia activa inversor Fronius [kW]
        power_grid        — potencia activa operador de red [kW]
        power_quattro     — potencia activa inversores Quattro [W]
        rollangle         — ángulo roll del panel [°]
        temperature       — temperatura ambiente [°C]
        tiltangle         — ángulo tilt del panel [°]

    Cuando se conecte InfluxDB:
        Reemplazar todo el cuerpo por una query Flux que traiga
        el último punto de _measurement con todos estos campos.
    """
    return {
        "_time":          datetime.now(timezone.utc),

        # ── Batería ──────────────────────────────────────────────────────────
        "CurrentBattery":  round(random.uniform(-50.0,  50.0),  1),   # A  (neg = carga)
        "PowerBattery":    round(random.uniform(-2400,  2400),  0),   # W
        "SoCBattery":      round(random.uniform(20,     95),    0),   # %
        "VoltageBattery":  round(random.uniform(46.0,   54.0),  2),   # V

        # ── Potencias ─────────────────────────────────────────────────────────
        "carga_total":     round(random.uniform(1.0,    9.0),   2),   # kW
        "power_fronius":   round(random.uniform(0.0,    10.0),  2),   # kW
        "power_grid":      round(random.uniform(-5.0,   15.0),  2),   # kW (neg = exporta)
        "power_quattro":   round(random.uniform(0,      15000), 0),   # W

        # ── Meteorología y panel solar ────────────────────────────────────────
        "humidity":        round(random.uniform(40.0,   90.0),  1),   # %
        "irradiance":      round(random.uniform(0.0,    1000.0),1),   # W/m²
        "temperature":     round(random.uniform(15.0,   35.0),  1),   # °C
        "rollangle":       round(random.uniform(-2.0,   2.0),   2),   # °
        "tiltangle":       round(random.uniform(10.0,   30.0),  1),   # °
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
    Cambia el estado de un contactor.

    Args:
        nombre: clave del contactor en _estados,
                p. ej. "estado_operador_red".
        estado: True = ISLANDED, False = CONNECTED.

    Raises:
        KeyError  si el nombre no existe en _estados.
        TypeError si estado no es bool.

    Cuando se conecte InfluxDB:
        Reemplazar el cuerpo por una escritura al bucket de control:
            punto = Point("control")
                      .field(nombre, estado)
                      .time(datetime.now(timezone.utc))
            write_api.write(bucket=BUCKET_CONTROL, record=punto)
    """
    if nombre not in _estados:
        raise KeyError(f"Contactor desconocido: '{nombre}'. "
                       f"Claves válidas: {list(_estados.keys())}")
    if not isinstance(estado, bool):
        raise TypeError(f"estado debe ser bool, recibido: {type(estado)}")

    _estados[nombre] = estado
    _guardar_estados()   


def set_setpoint(valor: float) -> None:
    """
    Actualiza el setpoint de potencia del inversor.

    Args:
        valor: potencia de referencia en kW. Rango esperado 0–15 kW.

    Raises:
        ValueError si valor está fuera del rango 0–15.

    Cuando se conecte InfluxDB:
        Escribir campo "setpoint_potencia_kw" en bucket de control.
    """
    if not (0.0 <= valor <= 15.0):
        raise ValueError(f"Setpoint fuera de rango [0, 15] kW: {valor}")

    _estados["setpoint_potencia_kw"] = float(valor)
    _guardar_estados()


def set_modo_isla(activo: bool) -> None:
    """
    Activa o desactiva el modo isla del sistema.

    Args:
        activo: True = modo isla activado, False = modo conectado a red.

    Cuando se conecte InfluxDB:
        Escribir campo "modo_isla" en bucket de control.
    """
    if not isinstance(activo, bool):
        raise TypeError(f"activo debe ser bool, recibido: {type(activo)}")

    _estados["modo_isla"] = activo
    _guardar_estados()   


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
    "toggle-piso1-ilum":     "estado_piso1_ilum",
    "toggle-piso2-ilum":     "estado_piso2_ilum",
    "toggle-piso3-ilum":     "estado_piso3_ilum",
    "toggle-gab-exp":        "estado_gab_exp",
    "toggle-piso1-exp":      "estado_piso1_exp",
    "toggle-piso2-exp":      "estado_piso2_exp",
    "toggle-quattro-or":     "estado_quattro_or",
}
