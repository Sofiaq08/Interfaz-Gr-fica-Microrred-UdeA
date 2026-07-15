# =============================================================================
# acciones.py  —  Funciones de control de la Microrred HMI
#
# Cada acción tiene su propia función con nombre legible.
# Internamente todas llaman a set_contactor() de datos.py.
#
# Cuando se agreguen nuevas acciones (alarmas, modos especiales, etc.)
# se añaden aquí sin tocar app.py ni datos.py.
# =============================================================================

import datos


# -----------------------------------------------------------------------------
# FUNCIÓN GENÉRICA INTERNA
# No llamar directamente desde app.py — usar las funciones nombradas abajo.
# -----------------------------------------------------------------------------

def _set_contactor(nombre: str, estado: bool) -> None:
    """Escribe el estado de un contactor a través de la capa de datos."""
    datos.set_contactor(nombre, estado)


# -----------------------------------------------------------------------------
# OPERADOR DE RED
# -----------------------------------------------------------------------------

def abrir_operador_red() -> None:
    """Abre el contactor del Operador de Red → estado ISLANDED (True)."""
    _set_contactor("estado_operador_red", True)


def cerrar_operador_red() -> None:
    """Cierra el contactor del Operador de Red → estado CONNECTED (False)."""
    _set_contactor("estado_operador_red", False)


# -----------------------------------------------------------------------------
# INVERSOR FRONIUS
# -----------------------------------------------------------------------------

def abrir_fronius() -> None:
    """Abre el contactor del Inversor Fronius → estado ISLANDED (True)."""
    _set_contactor("estado_fronius", True)


def cerrar_fronius() -> None:
    """Cierra el contactor del Inversor Fronius → estado CONNECTED (False)."""
    _set_contactor("estado_fronius", False)


# -----------------------------------------------------------------------------
# CARGA ELECTRÓNICA PROGRAMABLE
# -----------------------------------------------------------------------------

def abrir_carga_elec() -> None:
    """Abre el contactor de la Carga Electrónica → estado ISLANDED (True)."""
    _set_contactor("estado_carga_elec", True)


def cerrar_carga_elec() -> None:
    """Cierra el contactor de la Carga Electrónica → estado CONNECTED (False)."""
    _set_contactor("estado_carga_elec", False)


# -----------------------------------------------------------------------------
# ELECTROLIZADOR DE HIDRÓGENO
# -----------------------------------------------------------------------------

def abrir_electrolizador() -> None:
    """Abre el contactor del Electrolizador → estado ISLANDED (True)."""
    _set_contactor("estado_electrolizador", True)


def cerrar_electrolizador() -> None:
    """Cierra el contactor del Electrolizador → estado CONNECTED (False)."""
    _set_contactor("estado_electrolizador", False)


# -----------------------------------------------------------------------------
# MICROINVERSORES ENPHASE
# -----------------------------------------------------------------------------

def abrir_enphase() -> None:
    """Abre el contactor de los Microinversores Enphase → ISLANDED (True)."""
    _set_contactor("estado_enphase", True)


def cerrar_enphase() -> None:
    """Cierra el contactor de los Microinversores Enphase → CONNECTED (False)."""
    _set_contactor("estado_enphase", False)


# -----------------------------------------------------------------------------
# GABINETE DE ILUMINACIÓN
# -----------------------------------------------------------------------------

def abrir_gab_ilum() -> None:
    """Abre el contactor del Gabinete de Iluminación → ISLANDED (True)."""
    _set_contactor("estado_gab_ilum", True)


def cerrar_gab_ilum() -> None:
    """Cierra el contactor del Gabinete de Iluminación → CONNECTED (False)."""
    _set_contactor("estado_gab_ilum", False)


# -----------------------------------------------------------------------------
# GABINETE ILUMINACIÓN — PISO 1
# -----------------------------------------------------------------------------

def abrir_piso1_ilum() -> None:
    """Abre el contactor de Iluminación Piso 1 → ISLANDED (True)."""
    _set_contactor("estado_piso1_ilum", True)


def cerrar_piso1_ilum() -> None:
    """Cierra el contactor de Iluminación Piso 1 → CONNECTED (False)."""
    _set_contactor("estado_piso1_ilum", False)


# -----------------------------------------------------------------------------
# GABINETE ILUMINACIÓN — PISO 2
# -----------------------------------------------------------------------------

def abrir_piso2_ilum() -> None:
    """Abre el contactor de Iluminación Piso 2 → ISLANDED (True)."""
    _set_contactor("estado_piso2_ilum", True)


def cerrar_piso2_ilum() -> None:
    """Cierra el contactor de Iluminación Piso 2 → CONNECTED (False)."""
    _set_contactor("estado_piso2_ilum", False)


# -----------------------------------------------------------------------------
# GABINETE ILUMINACIÓN — PISO 3
# -----------------------------------------------------------------------------

def abrir_piso3_ilum() -> None:
    """Abre el contactor de Iluminación Piso 3 → ISLANDED (True)."""
    _set_contactor("estado_piso3_ilum", True)


def cerrar_piso3_ilum() -> None:
    """Cierra el contactor de Iluminación Piso 3 → CONNECTED (False)."""
    _set_contactor("estado_piso3_ilum", False)


# -----------------------------------------------------------------------------
# GABINETE DE CARGAS EXPERIMENTALES
# -----------------------------------------------------------------------------

def abrir_gab_exp() -> None:
    """Abre el contactor del Gabinete de Cargas Experimentales → ISLANDED (True)."""
    _set_contactor("estado_gab_exp", True)


def cerrar_gab_exp() -> None:
    """Cierra el contactor del Gabinete de Cargas Experimentales → CONNECTED (False)."""
    _set_contactor("estado_gab_exp", False)


# -----------------------------------------------------------------------------
# GABINETE EXPERIMENTALES — PISO 1 (3 kW)
# -----------------------------------------------------------------------------

def abrir_piso1_exp() -> None:
    """Abre el contactor de Experimentales Piso 1 [3 kW] → ISLANDED (True)."""
    _set_contactor("estado_piso1_exp", True)


def cerrar_piso1_exp() -> None:
    """Cierra el contactor de Experimentales Piso 1 [3 kW] → CONNECTED (False)."""
    _set_contactor("estado_piso1_exp", False)

# -----------------------------------------------------------------------------
# QUATTRO — conexión con Bus AC Operador de Red
# -----------------------------------------------------------------------------

def abrir_quattro_or() -> None:
    """Abre el contactor Quattro-OR → estado ISLANDED (True)."""
    _set_contactor("estado_quattro_or", True)


def cerrar_quattro_or() -> None:
    """Cierra el contactor Quattro-OR → estado CONNECTED (False)."""
    _set_contactor("estado_quattro_or", False)

# -----------------------------------------------------------------------------
# GABINETE EXPERIMENTALES — PISO 2 (6 kW)
# -----------------------------------------------------------------------------

def abrir_piso2_exp() -> None:
    """Abre el contactor de Experimentales Piso 2 [6 kW] → ISLANDED (True)."""
    _set_contactor("estado_piso2_exp", True)


def cerrar_piso2_exp() -> None:
    """Cierra el contactor de Experimentales Piso 2 [6 kW] → CONNECTED (False)."""
    _set_contactor("estado_piso2_exp", False)


# -----------------------------------------------------------------------------
# TOGGLE GENÉRICO — usado por los callbacks de app.py
#
# Recibe el toggle-id del SVG, consulta el estado actual y lo invierte.
# Así el callback solo necesita saber el id del botón, no el estado previo.
# -----------------------------------------------------------------------------

def toggle_contactor(toggle_id: str) -> bool:
    """
    Invierte el estado del contactor asociado al toggle-id del SVG.

    Args:
        toggle_id: id del elemento SVG, p. ej. "toggle-fronius".

    Returns:
        El nuevo estado (bool) tras el toggle.

    Raises:
        KeyError si toggle_id no existe en TOGGLE_A_ESTADO.
    """
    clave = datos.TOGGLE_A_ESTADO[toggle_id]
    estado_actual = datos.get_estado_contactor(clave)
    nuevo_estado = not estado_actual
    datos.set_contactor(clave, nuevo_estado)
    return nuevo_estado


# -----------------------------------------------------------------------------
# SETPOINT DE POTENCIA
# -----------------------------------------------------------------------------

def aplicar_setpoint(valor: float) -> str:
    """
    Envía un nuevo setpoint de potencia al inversor.

    Args:
        valor: potencia de referencia en kW (rango 0–15).

    Returns:
        Mensaje de confirmación para mostrar en la UI.
    """
    datos.set_setpoint(float(valor))
    return f"✓ Setpoint de {valor} kW aplicado."


# -----------------------------------------------------------------------------
# MODO ISLA
# -----------------------------------------------------------------------------

def activar_modo_isla() -> str:
    """Activa el modo isla (desconecta la microrred de la red pública)."""
    datos.set_modo_isla(True)
    return "✓ Modo isla ACTIVADO."


def desactivar_modo_isla() -> str:
    """Desactiva el modo isla (reconecta la microrred a la red pública)."""
    datos.set_modo_isla(False)
    return "✓ Modo isla DESACTIVADO."


def toggle_modo_isla() -> str:
    """Invierte el modo isla. Retorna mensaje de confirmación."""
    estado_actual = datos.get_estados()["modo_isla"]
    if estado_actual:
        return desactivar_modo_isla()
    else:
        return activar_modo_isla()
