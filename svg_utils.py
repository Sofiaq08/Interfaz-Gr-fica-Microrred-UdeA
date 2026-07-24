# =============================================================================
# svg_utils.py  —  Utilidades para manipular el SVG del diagrama unifilar
#
# Tres helpers de bajo nivel (reemplazar_texto, cambiar_fill, cambiar_stroke)
# más la función de alto nivel construir_svg() que los orquesta.
#
# app.py solo llama a construir_svg(); los tres helpers son internos.
# =============================================================================

import re

# -----------------------------------------------------------------------------
# Leer el SVG base UNA SOLA VEZ al importar el módulo.
# Cada llamada a construir_svg() parte de esta cadena sin modificar.
# -----------------------------------------------------------------------------

with open("diagrama.svg", "r", encoding="utf-8") as _f:
    _SVG_BASE = _f.read()


# =============================================================================
# HELPERS DE BAJO NIVEL
# =============================================================================

def reemplazar_texto(svg: str, elem_id: str, nuevo_texto: str) -> str:
    """
    Reemplaza el contenido del primer <tspan> dentro del elemento
    <text id="elem_id">.

    Ejemplo:
        reemplazar_texto(svg, "lbl-power-grid", "P: 5.32 kW")

    Nota: usa funcion como reemplazo (no string) para evitar que re.sub
    interprete caracteres del texto como referencias de grupo.
    """
    patron = rf'(id="{elem_id}"[^>]*>\s*<tspan[^>]*>)[^<]*(</tspan>)'

    def _reemplazar(m):
        return m.group(1) + nuevo_texto + m.group(2)

    return re.sub(patron, _reemplazar, svg, flags=re.DOTALL)


def cambiar_fill(svg: str, elem_id: str, nuevo_color: str) -> str:
    """
    Cambia el atributo fill="..." del tag con ese id.

    El SVG del proyecto usa atributos directos (fill="#22c55e"), no
    notacion CSS inline (fill:#22c55e), por eso el regex busca fill="...".

    Usado para colorear los toggles:
        verde #22c55e -> ISLANDED
        rojo  #ef4444 -> CONNECTED
    """
    def _reemplazar(match):
        tag = match.group(0)
        return re.sub(r'fill="#[0-9a-fA-F]{3,6}"', f'fill="{nuevo_color}"', tag, count=1)

    patron = rf'<[^>]*\bid="{elem_id}"[^>]*>'
    return re.sub(patron, _reemplazar, svg)


def cambiar_stroke(svg: str, elem_id: str, nuevo_color: str) -> str:
    """
    Cambia el atributo stroke="..." del tag con ese id.

    Mismo criterio que cambiar_fill: atributos SVG directos, no CSS inline.
    """
    def _reemplazar(match):
        tag = match.group(0)
        return re.sub(r'stroke="#[0-9a-fA-F]{3,6}"', f'stroke="{nuevo_color}"', tag, count=1)

    patron = rf'<[^>]*\bid="{elem_id}"[^>]*>'
    return re.sub(patron, _reemplazar, svg)


# =============================================================================
# FUNCION PRINCIPAL
# =============================================================================

# Colores de toggle
_COLOR_ISLANDED  = "#22c55e"   # verde
_COLOR_CONNECTED = "#ef4444"   # rojo

# Mapa toggle-id SVG -> clave en el dict de estados
_TOGGLE_IDS = [
    "toggle-operador-red",
    "toggle-fronius",
    "toggle-carga-elec",
    "toggle-electrolizador",
    "toggle-enphase",
    "toggle-gab-ilum",
    "toggle-piso1-ilum",
    "toggle-piso2-ilum",
    "toggle-piso3-ilum",
    "toggle-gab-exp",
    "toggle-piso1-exp",
    "toggle-piso2-exp",
    "toggle-quattro-or",
]

# Mapa toggle-id -> clave de estado (mismo que TOGGLE_A_ESTADO en datos.py,
# duplicado aqui para que svg_utils no dependa de datos directamente)
_TOGGLE_A_ESTADO = {
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


def construir_svg(estados: dict, mediciones: dict) -> str:
    """
    Genera el SVG completo con los valores actuales del sistema.

    Toma el SVG base (leido al importar el modulo) y aplica:
      1. Color de cada toggle segun su estado (ISLANDED/CONNECTED).
      2. Etiquetas de medicion con los valores del dict de mediciones.

    Args:
        estados:    resultado de datos.get_estados()
        mediciones: resultado de datos.get_mediciones()

    Returns:
        String con el SVG listo para incrustar en html.Div.

    Notas para agregar mas variables al SVG en el futuro:
        - Agregar el id al elemento <text> en diagrama.svg.
        - Agregar una linea reemplazar_texto() en la seccion de mediciones.
        - No tocar nada mas.
    """
    svg = _SVG_BASE  # siempre parte del SVG original sin modificar

    # -- 1. Colorear los 12 toggles ------------------------------------------
    for toggle_id in _TOGGLE_IDS:
        clave  = _TOGGLE_A_ESTADO[toggle_id]
        estado = estados.get(clave, False)
        color  = _COLOR_ISLANDED if estado else _COLOR_CONNECTED
        svg    = cambiar_fill(svg, toggle_id, color)

    # -- 2. Etiquetas de medicion --------------------------------------------
    # Cada reemplazar_texto busca el <text id="..."> en el SVG y pone el valor.
    # Si el id no existe en el SVG actual, la funcion no hace nada (safe).
    #
    # Fase actual: los ids de texto de medicion aun NO estan en diagrama.svg.
    # Se anadiran cuando se disene la zona de lecturas del SVG.
    # Las lineas ya estan preparadas aqui para ese momento.

    pg   = mediciones.get("power_grid",    0)
    pf   = mediciones.get("power_fronius", 0)
    pq   = mediciones.get("power_quattro", 0)
    soc  = mediciones.get("SoCBattery",    0)
    vbat = mediciones.get("VoltageBattery",0)
    ibat = mediciones.get("CurrentBattery",0)
    ct   = mediciones.get("carga_total",   0)
    irr  = mediciones.get("irradiance",    0)
    temp = mediciones.get("temperature",   0)

    # Potencias principales
    svg = reemplazar_texto(svg, "lbl-power-grid",    f"P red: {pg:+.2f} kW")
    svg = reemplazar_texto(svg, "lbl-power-fronius", f"P Fronius: {pf:.2f} kW")
    svg = reemplazar_texto(svg, "lbl-power-quattro", f"P Quattro: {int(pq)} W")
    svg = reemplazar_texto(svg, "lbl-carga-total",   f"Carga: {ct:.2f} kW")

    # Bateria
    svg = reemplazar_texto(svg, "lbl-soc-battery",     f"SoC: {int(soc)} %")
    svg = reemplazar_texto(svg, "lbl-voltage-battery", f"V bat: {vbat:.1f} V")
    svg = reemplazar_texto(svg, "lbl-current-battery", f"I bat: {ibat:+.1f} A")

    # Meteorologia
    svg = reemplazar_texto(svg, "lbl-irradiance",  f"Irr: {irr:.0f} W/m2")
    svg = reemplazar_texto(svg, "lbl-temperature", f"T: {temp:.1f} C")

    # Variables de control
    svg = reemplazar_texto(svg, "lbl-setpoint",  f"{estados.get('setpoint_potencia_kw', 0):.1f} kW")
    svg = reemplazar_texto(svg, "lbl-modo-isla", "ISLA" if estados.get("modo_isla") else "RED")

    return svg
