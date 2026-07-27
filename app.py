# =============================================================================
# app.py  —  HMI Microrred Sede Oriente UdeA
#
# Layout Dash con SVG en linea + botones transparentes sobre cada toggle.
# Callbacks:
#   1. toggle_contactor  — clic sobre un toggle → acciones.py → datos.py
#   2. actualizar_vista  — cada 3 s lee datos.py y repinta SVG + panel vars
#   3. aplicar_setpoint  — boton Aplicar → acciones.py → datos.py
#   4. toggle_isla       — boton Modo Isla → acciones.py → datos.py
# =============================================================================

import dash
from dash import dcc, html, Input, Output, State, callback, ctx, no_update
from dash.exceptions import PreventUpdate

import datos
import acciones
import svg_utils

# -----------------------------------------------------------------------------
app = dash.Dash(__name__, suppress_callback_exceptions=True)
app.title = "HMI — Microrred UdeA"
server = app.server   # para despliegue con gunicorn si se necesita

# IDs de todos los toggles — misma lista que svg_utils, centralizada aqui
TOGGLE_IDS = list(svg_utils._TOGGLE_IDS)

# Etiquetas legibles para el panel de log
TOGGLE_LABELS = {
    "toggle-operador-red":   "Operador de red",
    "toggle-fronius":        "Inversor Fronius",
    "toggle-carga-elec":     "Carga electrónica",
    "toggle-electrolizador": "Electrolizador H₂",
    "toggle-enphase":        "Microinv. Enphase",
    "toggle-gab-ilum":       "Gab. Iluminación",
    "toggle-piso1-ilum":     "Ilum. Piso 1",
    "toggle-piso2-ilum":     "Ilum. Piso 2",
    "toggle-piso3-ilum":     "Ilum. Piso 3",
    "toggle-gab-exp":        "Gab. Experimentales",
    "toggle-piso1-exp":      "Exp. Piso 1 [3 kW]",
    "toggle-piso2-exp":      "Exp. Piso 2 [6 kW]",
    "toggle-quattro-or":     "Quattro — Bus AC OR",
}

# =============================================================================
# ESTILOS BASE
# =============================================================================

C = {
    "bg":       "#0d0f1a",
    "surface":  "#141828",
    "border":   "#1e2436",
    "text":     "#e2e8f0",
    "muted":    "#475569",
    "label":    "#64748b",
    "green":    "#22c55e",
    "red":      "#ef4444",
    "blue":     "#3b82f6",
    "yellow":   "#f59e0b",
    "purple":   "#a78bfa",
    "cyan":     "#22d3ee",
}

def card(children, extra_style=None):
    style = {
        "backgroundColor": C["surface"],
        "border":          f"1px solid {C['border']}",
        "borderRadius":    "10px",
        "padding":         "18px 20px",
    }
    if extra_style:
        style.update(extra_style)
    return html.Div(children=children, style=style)

def etiqueta_seccion(texto):
    return html.P(texto, style={
        "margin":        "0 0 14px 0",
        "fontSize":      "10px",
        "letterSpacing": "2.5px",
        "color":         C["label"],
        "fontWeight":    "700",
        "textTransform": "uppercase",
    })


# =============================================================================
# BOTONES TRANSPARENTES SOBRE LOS TOGGLES
# Posiciones calculadas en % del viewBox 1900x850.
# El div contenedor tiene position:relative y paddingTop=44.7%
# (850/1900*100) para mantener el aspect ratio del SVG.
# =============================================================================

TOGGLE_POSITIONS = {
    "toggle-operador-red":   {"left": "3.739%",  "top": "62.142%"},
    "toggle-fronius":        {"left": "14.216%", "top": "61.996%"},
    "toggle-carga-elec":     {"left": "42.109%", "top": "54.243%"},
    "toggle-electrolizador": {"left": "51.917%", "top": "54.129%"},
    "toggle-enphase":        {"left": "57.494%", "top": "35.314%"},
    "toggle-gab-ilum":       {"left": "64.654%", "top": "53.85%"},
    "toggle-piso1-ilum":     {"left": "67.18%",  "top": "61.968%"},
    "toggle-piso2-ilum":     {"left": "67.18%",  "top": "69.615%"},
    "toggle-piso3-ilum":     {"left": "67.18%",  "top": "77.262%"},
    "toggle-gab-exp":        {"left": "81.374%", "top": "54.022%"},
    "toggle-piso1-exp":      {"left": "83.901%", "top": "62.14%"},
    "toggle-piso2-exp":      {"left": "83.901%", "top": "69.787%"},
    "toggle-quattro-or":     {"left": "27.165%", "top": "55.717%"},
}


def botones_overlay():
    """Genera los 12 botones transparentes posicionados sobre los toggles."""
    botones = []
    for tid in TOGGLE_IDS:
        pos = TOGGLE_POSITIONS[tid]
        botones.append(
            html.Button(
                id=f"btn-{tid}",
                n_clicks=0,
                title=TOGGLE_LABELS.get(tid, tid),   # tooltip al pasar el mouse
                style={
                    "position":        "absolute",
                    "left":            pos["left"],
                    "top":             pos["top"],
                    "width":           "3.79%",        # 72/1900
                    "height":          "2.59%",        # 22/850
                    "background":      "transparent",
                    "border":          "none",
                    "cursor":          "pointer",
                    "padding":         "0",
                    "zIndex":          "10",
                    # Anillo de foco visible para accesibilidad
                    "outline":         "none",
                },
            )
        )
    return botones


# =============================================================================
# LAYOUT
# =============================================================================

app.layout = html.Div(
    style={
        "fontFamily":      "'Segoe UI', system-ui, sans-serif",
        "backgroundColor": C["bg"],
        "minHeight":       "100vh",
        "color":           C["text"],
        "padding":         "20px 24px",
        "boxSizing":       "border-box",
    },
    children=[

        # ── Encabezado ───────────────────────────────────────────────────────
        html.Div(
            style={
                "display":       "flex",
                "alignItems":    "center",
                "gap":           "12px",
                "marginBottom":  "20px",
                "paddingBottom": "16px",
                "borderBottom":  f"1px solid {C['border']}",
            },
            children=[
                html.Span("⚡", style={"fontSize": "24px"}),
                html.Div([
                    html.H1("HMI — Microrred Sede Oriente",
                            style={"margin": "0", "fontSize": "18px",
                                   "fontWeight": "700", "color": C["text"]}),
                    html.P("Universidad de Antioquia · El Carmen de Viboral",
                           style={"margin": "0", "fontSize": "11px",
                                  "color": C["label"]}),
                ]),
                html.Div(
                    style={"marginLeft": "auto", "display": "flex",
                           "alignItems": "center", "gap": "8px"},
                    children=[
                        html.Span(id="indicador-isla",
                                  style={"fontSize": "11px",
                                         "fontWeight": "700",
                                         "letterSpacing": "1px",
                                         "color": C["muted"]}),
                        html.Span("●", style={"color": C["green"],
                                              "fontSize": "10px"}),
                        html.Span("EN VIVO",
                                  style={"fontSize": "10px",
                                         "color":    C["green"],
                                         "fontWeight": "700",
                                         "letterSpacing": "2px"}),
                    ],
                ),
            ],
        ),

        # ── Diagrama — ancho completo ────────────────────────────────────────
        html.Div(
            style={"display": "flex", "flexDirection": "column", "gap": "16px"},
            children=[

                # ── Diagrama ocupa todo el ancho ─────────────────────────────
                html.Div(
                    style={"width": "100%"},
                    children=[
                        card([
                            etiqueta_seccion("Diagrama unifilar"),

                            # Contenedor con aspect-ratio 1900:850
                            html.Div(
                                style={
                                    "position":    "relative",
                                    "width":       "100%",
                                    "paddingTop":  "44.74%",   # 850/1900*100
                                    "overflow":    "hidden",
                                    "borderRadius":"6px",
                                    "backgroundColor": "#1a1d2e",
                                },
                                children=[
                                    # SVG en linea — se actualiza en el callback
                                    html.Div(
                                        id="svg-container",
                                        style={
                                            "position": "absolute",
                                            "top": "0", "left": "0",
                                            "width": "100%", "height": "100%",
                                        },
                                    ),
                                    # Capa de botones transparentes
                                    html.Div(
                                        children=botones_overlay(),
                                        style={
                                            "position": "absolute",
                                            "top": "0", "left": "0",
                                            "width": "100%", "height": "100%",
                                        },
                                        id="overlay-botones",
                                    ),
                                ],
                            ),

                            # Leyenda
                            html.Div(
                                style={"display": "flex", "gap": "20px",
                                       "marginTop": "12px", "flexWrap": "wrap"},
                                children=[
                                    html.Span([
                                        html.Span("■ ", style={"color": C["green"]}),
                                        html.Span("ISLANDED",
                                                  style={"fontSize": "11px",
                                                         "color": C["label"]}),
                                    ]),
                                    html.Span([
                                        html.Span("■ ", style={"color": C["red"]}),
                                        html.Span("CONNECTED",
                                                  style={"fontSize": "11px",
                                                         "color": C["label"]}),
                                    ]),
                                    html.Span(
                                        "Haz clic sobre cualquier toggle para cambiar su estado",
                                        style={"fontSize": "11px",
                                               "color": C["muted"],
                                               "marginLeft": "auto"}
                                    ),
                                ],
                            ),
                        ]),
                    ],
                ),

                # ── Panel inferior: variables + control en fila ───────────────
                html.Div(
                    style={
                        "display":   "flex",
                        "gap":       "16px",
                        "flexWrap":  "wrap",
                    },
                    children=[

                        # ── Variables en tiempo real ─────────────────────────
                        card([
                            etiqueta_seccion("Variables en tiempo real"),
                            html.Div(id="panel-variables"),
                        ], extra_style={"flex": "2", "minWidth": "320px"}),

                        # ── Setpoint de potencia ─────────────────────────────
                        card([
                            etiqueta_seccion("Setpoint de potencia"),
                            html.Label("Referencia de potencia [kW]",
                                       style={"fontSize": "11px",
                                              "color":    C["label"],
                                              "display":  "block",
                                              "marginBottom": "8px"}),
                            html.Div(
                                style={"display": "flex", "gap": "8px"},
                                children=[
                                    dcc.Input(
                                        id="input-setpoint",
                                        type="number",
                                        placeholder="0 – 15",
                                        min=0, max=15, step=0.5,
                                        debounce=False,
                                        style={
                                            "flex":            "1",
                                            "padding":         "8px 10px",
                                            "borderRadius":    "7px",
                                            "border":          f"1px solid {C['border']}",
                                            "backgroundColor": C["bg"],
                                            "color":           C["text"],
                                            "fontSize":        "13px",
                                        },
                                    ),
                                    html.Button(
                                        "Aplicar",
                                        id="btn-setpoint",
                                        n_clicks=0,
                                        style={
                                            "padding":         "8px 14px",
                                            "borderRadius":    "7px",
                                            "border":          "none",
                                            "backgroundColor": C["blue"],
                                            "color":           "white",
                                            "cursor":          "pointer",
                                            "fontWeight":      "700",
                                            "fontSize":        "12px",
                                        },
                                    ),
                                ],
                            ),
                            html.Div(id="msg-setpoint",
                                     style={"marginTop": "8px",
                                            "fontSize":  "12px",
                                            "color":     C["green"],
                                            "minHeight": "18px"}),
                        ]),

                        # ── Log de acciones ──────────────────────────────────
                        card([
                            etiqueta_seccion("Últimas acciones"),
                            html.Div(id="log-acciones",
                                     style={"fontSize":  "11px",
                                            "color":     C["label"],
                                            "lineHeight":"1.7"}),
                        ], extra_style={"flex": "1", "minWidth": "220px"}),

                    ],
                ),
            ],
        ),

        # ── Componentes no visuales ──────────────────────────────────────────
        dcc.Interval(id="intervalo", interval=5000, n_intervals=0),

        # Store para el log de las ultimas N acciones
        dcc.Store(id="store-log", data=[]),

        # Store para forzar refresco inmediato tras un clic
        dcc.Store(id="store-trigger", data=0),
    ],
)


# =============================================================================
# HELPERS DE UI
# =============================================================================

def _fila_variable(titulo, valor_str, color):
    return html.Div(
        style={
            "display":        "flex",
            "justifyContent": "space-between",
            "alignItems":     "center",
            "padding":        "7px 10px",
            "backgroundColor": C["bg"],
            "borderRadius":   "6px",
            "marginBottom":   "6px",
            "borderLeft":     f"3px solid {color}",
        },
        children=[
            html.Span(titulo,    style={"fontSize": "11px", "color": C["label"]}),
            html.Span(valor_str, style={"fontSize": "13px", "fontWeight": "700",
                                        "color": color}),
        ],
    )


def _panel_variables(med, estados):
    pg   = med.get("power_grid",     0)
    pf   = med.get("power_fronius",  0)
    pq   = med.get("power_quattro",  0)
    soc  = med.get("SoCBattery",     0)
    vbat = med.get("VoltageBattery", 0)
    ibat = med.get("CurrentBattery", 0)
    ct   = med.get("carga_total",    0)
    irr  = med.get("irradiance",     0)
    temp = med.get("temperature",    0)
    sp   = estados.get("setpoint_potencia_kw", 0)

    # Color de power_grid: verde si importa (>0), amarillo si exporta (<0)
    color_grid = C["green"] if pg >= 0 else C["yellow"]

    return html.Div([
        _fila_variable("P red (OR)",     f"{pg:+.2f} kW",   color_grid),
        _fila_variable("P Fronius",      f"{pf:.2f} kW",    C["blue"]),
        _fila_variable("P Quattro",      f"{int(pq)} W",    C["cyan"]),
        _fila_variable("Carga total",    f"{ct:.2f} kW",    C["red"]),
        _fila_variable("SoC batería",    f"{int(soc)} %",   C["green"]),
        _fila_variable("V batería",      f"{vbat:.1f} V",   C["cyan"]),
        _fila_variable("I batería",      f"{ibat:+.1f} A",  C["yellow"]),
        _fila_variable("Irradiancia",    f"{irr:.0f} W/m²", C["yellow"]),
        _fila_variable("Temperatura",    f"{temp:.1f} °C",  C["purple"]),
        _fila_variable("Setpoint",       f"{sp:.1f} kW",    C["blue"]),
    ])


# =============================================================================
# CALLBACK 1 — Toggle de contactor
# Un solo callback recibe los n_clicks de los 12 botones.
# ctx.triggered_id identifica cuál botón disparó.
# =============================================================================

@callback(
    Output("store-trigger", "data"),
    Output("store-log",     "data"),
    [Input(f"btn-{tid}", "n_clicks") for tid in TOGGLE_IDS],
    State("store-log", "data"),
    prevent_initial_call=True,
)
def cb_toggle_contactor(*args):
    # Los ultimos dos argumentos son el State y el trigger actual
    # args = (n_clicks_0, ..., n_clicks_11, log_actual)
    log_actual = args[-1]
    triggered  = ctx.triggered_id

    if triggered is None:
        raise PreventUpdate

    # Extraer el toggle-id del id del boton (btn-toggle-xxx -> toggle-xxx)
    toggle_id = triggered[len("btn-"):]   # quita el prefijo "btn-"

    if toggle_id not in svg_utils._TOGGLE_IDS:
        raise PreventUpdate

    # Llamar a acciones.py — actualiza datos.py
    nuevo_estado = acciones.toggle_contactor(toggle_id)
    etiqueta     = TOGGLE_LABELS.get(toggle_id, toggle_id)
    estado_txt   = "ISLANDED" if nuevo_estado else "CONNECTED"

    # Actualizar log (maximo 6 entradas)
    from datetime import datetime
    hora = datetime.now().strftime("%H:%M:%S")
    entrada = f"[{hora}] {etiqueta} → {estado_txt}"
    nuevo_log = ([entrada] + log_actual)[:6]

    # Incrementar trigger para forzar refresco inmediato del diagrama
    trigger_val = args[0] if args[0] is not None else 0   # cualquier valor nuevo

    return trigger_val, nuevo_log


# =============================================================================
# CALLBACK 2 — Refresco de vista cada 3 s (o inmediato tras un clic)
# =============================================================================

@callback(
    Output("svg-container",    "children"),
    Output("panel-variables",  "children"),
    Output("indicador-isla",   "children"),
    Output("log-acciones",     "children"),
    Input("intervalo",         "n_intervals"),
    Input("store-trigger",     "data"),
    State("store-log",         "data"),
)
def cb_actualizar_vista(n_intervals, trigger, log):
    estados    = datos.get_estados()
    mediciones = datos.get_mediciones()

    # ── SVG actualizado ──────────────────────────────────────────────────────
    svg_str = svg_utils.construir_svg(estados, mediciones)
    # Envolver SVG en HTML minimo para el iframe
    iframe_doc = f"""<!DOCTYPE html>
<html><head><meta charset="utf-8"/>
<style>* {{margin:0;padding:0;box-sizing:border-box;}} body {{background:#1a1d2e;overflow:hidden;}} svg {{width:100%;height:100%;display:block;}}</style>
</head><body>{svg_str}</body></html>"""
    estilo_iframe = {
        "width":    "100%",
        "height":   "100%",
        "border":   "none",
        "position": "absolute",
        "top":      "0",
        "left":     "0",
    }
    svg_div = html.Iframe(srcDoc=iframe_doc, style=estilo_iframe)

    # ── Panel de variables ───────────────────────────────────────────────────
    panel = _panel_variables(mediciones, estados)

    # ── Boton modo isla ──────────────────────────────────────────────────────
    modo_isla = estados.get("modo_isla", False)
    if modo_isla:
        btn_txt   = "Desactivar modo isla"
        btn_color = C["yellow"]
        ind_txt   = "⚡ MODO ISLA"
    else:
        btn_txt   = "Activar modo isla"
        btn_color = C["muted"]
        ind_txt   = ""

    btn_style = {
        "width":         "100%",
        "padding":       "9px",
        "borderRadius":  "7px",
        "border":        "none",
        "cursor":        "pointer",
        "fontWeight":    "700",
        "fontSize":      "12px",
        "letterSpacing": "0.5px",
        "backgroundColor": btn_color,
        "color":         C["text"],
        "transition":    "background-color 0.2s",
    }

    # ── Log de acciones ──────────────────────────────────────────────────────
    if log:
        log_div = html.Div([html.P(entrada, style={"margin": "2px 0"})
                            for entrada in log])
    else:
        log_div = html.P("Sin acciones recientes.",
                         style={"margin": "0", "fontStyle": "italic"})

    return svg_div, panel, ind_txt, log_div


# =============================================================================
# CALLBACK 3 — Setpoint de potencia
# =============================================================================

@callback(
    Output("msg-setpoint", "children"),
    Input("btn-setpoint",  "n_clicks"),
    State("input-setpoint","value"),
    prevent_initial_call=True,
)
def cb_setpoint(n_clicks, valor):
    if valor is None:
        return "⚠ Ingresa un valor entre 0 y 15 kW."
    try:
        msg = acciones.aplicar_setpoint(float(valor))
        return msg
    except ValueError as e:
        return f"⚠ {e}"


# ENTRAR EN LOCAL===============================
#if __name__ == "__main__":
#    app.run(debug=True)

# ENTRAR CON EL CELULAR=============================================================
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8050)