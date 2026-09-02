"""
LinkedIn Impulsa · Gestión de Recompensa Total
Prototipo académico para el puesto de Ingeniero(a) de Confiabilidad de Sistemas.

Todos los montos y metas son supuestos académicos del equipo y NO son
objetivos internos ni precios oficiales de LinkedIn.
"""

import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="LinkedIn Impulsa",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ------------------------------------------------------------------ paleta

AZUL = "#0A66C2"
AZUL_OSC = "#004182"
VERDE = "#046A38"
AMBAR = "#8A5A00"
ROJO = "#A32F1F"
TINTA = "#111111"
GRIS = "#4A4A4A"
GRIS_CLARO = "#6B6B6B"
LINEA = "#D0CCC6"
LIENZO = "#F1EFEB"
BLANCO = "#FFFFFF"

SALARIO_MENSUAL = 75_000
SALARIO_ANUAL = SALARIO_MENSUAL * 12
TOPE_ANUAL = 0.03
BONO_MAX = SALARIO_ANUAL * TOPE_ANUAL / 4      # $6,750
COSTO_HORA = SALARIO_MENSUAL / 160             # $468.75
PILOTO = 20

NIVELES = [
    ("Excelencia", 950, 1000, VERDE),
    ("Liderazgo", 850, 949, AZUL),
    ("Consolidado", 700, 849, AZUL_OSC),
    ("Construcción", 500, 699, AMBAR),
    ("Inicio", 0, 499, GRIS_CLARO),
]

# ------------------------------------------------------------------ puntos


def pts_confiabilidad(v):
    if v >= 99.95:
        return 250, "≥ 99.95 %"
    if v >= 99.90:
        return 180, "99.90 – 99.949 %"
    if v >= 99.80:
        return 90, "99.80 – 99.899 %"
    return 0, "< 99.80 %"


def pts_recuperacion(v):
    if v < 60:
        return 180, "< 60 min"
    if v <= 120:
        return 120, "60 – 120 min"
    if v <= 240:
        return 60, "121 – 240 min"
    return 0, "> 240 min"


def pts_prevencion(v):
    if v >= 90:
        return 200, "≥ 90 %"
    if v >= 80:
        return 150, "80 – 89 %"
    if v >= 70:
        return 75, "70 – 79 %"
    return 0, "< 70 %"


def pts_automatizacion(v):
    if v >= 5:
        return 170, "≥ 5 h/mes"
    if v >= 3:
        return 120, "3 – 4.9 h/mes"
    if v >= 1:
        return 60, "1 – 2.9 h/mes"
    return 0, "< 1 h/mes"


def pts_cultura(v):
    return {2: (100, "2 acciones verificadas"), 1: (50, "1 acción verificada")}.get(
        v, (0, "Sin acciones")
    )


def pts_desarrollo(v):
    return {
        "Curso + aplicación real": (50, "Curso aplicado"),
        "Solo curso completado": (25, "Solo curso"),
        "Sin evidencia": (0, "Sin evidencia"),
    }[v]


def pts_bienestar(v):
    return {
        "Cumple el protocolo": (50, "Protocolo cumplido"),
        "Cumplimiento parcial": (25, "Parcial"),
        "No cumple": (0, "No cumple"),
    }[v]


INDICADORES = [
    dict(n=1, eje="Técnico", nombre="Confiabilidad del servicio", max=250,
         meta="Disponibilidad trimestral ≥ 99.95 %",
         validacion="Sistema de monitoreo del servicio",
         tramos="≥99.95 % → 250 · 99.90–99.949 → 180 · 99.80–99.899 → 90 · <99.80 → 0",
         key="disponibilidad", fn=pts_confiabilidad),
    dict(n=2, eje="Técnico", nombre="Recuperación ante fallas", max=180,
         meta="Mediana de recuperación menor a 60 minutos",
         validacion="Sistema de incidentes y despliegues",
         tramos="<60 min → 180 · 60–120 → 120 · 121–240 → 60 · >240 → 0",
         key="recuperacion", fn=pts_recuperacion),
    dict(n=3, eje="Técnico", nombre="Prevención de reincidencias", max=200,
         meta="Cerrar en fecha al menos el 90 % de las acciones preventivas",
         validacion="Otro ingeniero comprueba que la solución funciona",
         tramos="≥90 % → 200 · 80–89 → 150 · 70–79 → 75 · <70 → 0",
         key="prevencion", fn=pts_prevencion),
    dict(n=4, eje="Técnico", nombre="Automatización útil", max=170,
         meta="Ahorrar 5 o más horas mensuales de trabajo repetitivo",
         validacion="Evidencia del ahorro y automatización viva 30 días",
         tramos="≥5 h → 170 · 3–4.9 → 120 · 1–2.9 → 60 · <1 → 0",
         key="automatizacion", fn=pts_automatizacion),
    dict(n=5, eje="Humano", nombre="Impacto en cultura", max=100,
         meta="2 acciones verificadas alineadas a los valores",
         validacion="Líder y compañero confirman la evidencia",
         tramos="2 acciones → 100 · 1 acción → 50 · ninguna → 0",
         key="cultura", fn=pts_cultura),
    dict(n=6, eje="Humano", nombre="Desarrollo aplicado", max=50,
         meta="Curso o capacitación más su aplicación real",
         validacion="El líder valida el resultado aplicado",
         tramos="Curso aplicado → 50 · Solo curso → 25 · Sin evidencia → 0",
         key="desarrollo", fn=pts_desarrollo),
    dict(n=7, eje="Humano", nombre="Trabajo sostenible", max=50,
         meta="Cumplir el protocolo de guardia y cierre",
         validacion="Registro operativo. Nunca datos de salud",
         tramos="Cumple → 50 · Parcial → 25 · No cumple → 0",
         key="bienestar", fn=pts_bienestar),
]

DEFAULTS = {
    "disponibilidad": 99.93,
    "recuperacion": 45,
    "prevencion": 92,
    "automatizacion": 5.5,
    "cultura": 2,
    "desarrollo": "Curso + aplicación real",
    "bienestar": "Cumple el protocolo",
}
HISTORIAL = [("Q1 2026", 712), ("Q2 2026", 868)]

st.session_state.setdefault("nav", "Inicio")
for k, v in DEFAULTS.items():
    st.session_state.setdefault(k, v)


def calcular():
    filas, total = [], 0
    for ind in INDICADORES:
        p, etiqueta = ind["fn"](st.session_state[ind["key"]])
        total += p
        filas.append({**ind, "puntos": p, "tramo": etiqueta})
    return filas, total


def nivel_de(t):
    for nombre, lo, hi, color in NIVELES:
        if lo <= t <= hi:
            return nombre, color
    return "Inicio", GRIS_CLARO


def bono_de(t):
    if t >= 950:
        return BONO_MAX
    if t >= 850:
        return BONO_MAX * 0.75
    if t >= 700:
        return BONO_MAX * 0.50
    return 0.0


def mxn(v):
    return f"${v:,.2f}" if v % 1 else f"${v:,.0f}"


# ------------------------------------------------------------------ estilos
# Se fuerza el tema CLARO desde el código, sin depender de .streamlit/config.toml.
# Primero se neutraliza el tema de Streamlit; después van los estilos propios,
# para que ganen los empates de especificidad.

st.markdown(
    f"""
<style>
  :root {{ color-scheme: light; }}

  /* ---- 1. neutralizar el tema oscuro de Streamlit ---- */
  html, body, .stApp,
  [data-testid="stAppViewContainer"],
  [data-testid="stBottomBlockContainer"] {{
      background: {LIENZO} !important;
  }}
  [data-testid="stHeader"] {{ background: transparent !important; }}
  .stApp, .stApp p, .stApp li, .stApp span, .stApp label,
  .stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp h5, .stApp h6 {{
      color: {TINTA};
  }}
  [data-testid="stMetricValue"],
  [data-testid="stMetricValue"] div {{ color: {TINTA} !important; }}
  [data-testid="stMetricLabel"],
  [data-testid="stMetricLabel"] p {{ color: {GRIS_CLARO} !important; }}
  [data-testid="stWidgetLabel"] p,
  [data-testid="stWidgetLabel"] label {{
      color: {TINTA} !important; font-weight: 600 !important; font-size: 15px !important;
  }}
  [data-testid="stCaptionContainer"],
  [data-testid="stCaptionContainer"] p {{ color: {GRIS_CLARO} !important; }}
  [data-testid="stThumbValue"] {{ color: {AZUL} !important; font-weight: 700 !important; }}
  [data-testid="stTickBarMin"], [data-testid="stTickBarMax"] {{ color: {GRIS_CLARO} !important; }}
  [role="radiogroup"] label p {{ color: {TINTA} !important; font-weight: 500 !important; }}
  /* menús desplegables (react-aria ComboBox) */
  [data-testid="stSelectbox"] .react-aria-ComboBox > div,
  [data-baseweb="select"] > div {{
      background-color: {BLANCO} !important;
      border: 1px solid {LINEA} !important;
      border-radius: 8px !important;
  }}
  [data-testid="stSelectbox"] input,
  [data-testid="stSelectbox"] button,
  [data-baseweb="select"] div, [data-baseweb="select"] input {{ color: {TINTA} !important; }}
  [data-testid="stSelectbox"] button svg {{ color: {GRIS} !important; fill: {GRIS} !important; }}
  .react-aria-Popover, .react-aria-ListBox,
  ul[data-baseweb="menu"], [data-baseweb="popover"] > div {{
      background-color: {BLANCO} !important; border: 1px solid {LINEA} !important;
  }}
  .react-aria-ListBoxItem, ul[data-baseweb="menu"] li {{
      color: {TINTA} !important; background-color: {BLANCO} !important;
  }}
  .react-aria-ListBoxItem[data-focused], .react-aria-ListBoxItem[data-hovered],
  ul[data-baseweb="menu"] li:hover {{ background-color: #E9F0F9 !important; }}

  /* el rojo por defecto de Streamlit -> azul LinkedIn */
  [data-testid="stSlider"] {{ filter: hue-rotate(212deg) saturate(1.2); }}

  /* menú lateral hecho con botones, no con radios */
  section[data-testid="stSidebar"] .stButton button {{
      width: 100% !important; justify-content: flex-start !important;
      background-color: {BLANCO} !important; border: 1px solid {LINEA} !important;
      border-radius: 8px !important; padding: 10px 15px !important;
      margin-bottom: 6px !important; font-weight: 600 !important;
  }}
  section[data-testid="stSidebar"] .stButton button p {{
      color: {TINTA} !important; font-size: 15px !important;
  }}
  section[data-testid="stSidebar"] .stButton button[kind="primary"] {{
      background-color: {AZUL} !important; border-color: {AZUL} !important;
  }}
  section[data-testid="stSidebar"] .stButton button[kind="primary"] p {{
      color: {BLANCO} !important;
  }}
  [data-testid="stExpander"] details {{
      background: {BLANCO} !important; border: 1px solid {LINEA} !important; border-radius: 10px;
  }}
  [data-testid="stExpander"] summary p {{ color: {TINTA} !important; font-weight: 600 !important; }}
  [data-testid="stAlertContainer"] p {{ color: {TINTA} !important; }}
  .stDownloadButton button {{
      background: {AZUL} !important; color: {BLANCO} !important; border: none !important;
      font-weight: 600 !important; border-radius: 999px !important; padding: 10px 22px !important;
  }}
  .stDownloadButton button p {{ color: {BLANCO} !important; }}
  section[data-testid="stSidebar"] {{ background: {BLANCO} !important; border-right: 1px solid {LINEA}; }}
  section[data-testid="stSidebar"] > div {{ background: {BLANCO} !important; }}
  hr {{ border-color: {LINEA} !important; }}

  /* ---- 2. tipografía general ---- */
  .block-container {{ padding-top: 2rem; max-width: 1150px; }}
  .stApp {{ font-size: 16px; }}
  .stApp h2 {{ font-size: 30px !important; letter-spacing: -.02em; margin-bottom: .2em; }}
  .stApp h3 {{ font-size: 23px !important; letter-spacing: -.01em; }}
  .stApp h4 {{ font-size: 19px !important; }}

  /* ---- 3. componentes propios ---- */
  .marca {{ display:flex; align-items:center; gap:12px; margin-bottom:2px; }}
  .marca .in {{ background:{AZUL}; color:#fff; font-weight:700; font-size:22px;
       width:40px; height:40px; border-radius:8px; display:flex;
       align-items:center; justify-content:center; }}
  .marca .nm {{ font-size:30px; font-weight:700; color:{TINTA}; letter-spacing:-.02em; }}

  .eyebrow {{ font-size:12px; letter-spacing:.16em; text-transform:uppercase;
       color:{AZUL}; font-weight:700; margin-bottom:8px; }}
  .lead {{ font-size:19px; color:{GRIS}; line-height:1.5; max-width:60ch; margin:6px 0 22px; }}

  .card {{ background:{BLANCO}; border:1px solid {LINEA}; border-radius:12px;
       padding:20px 22px; margin-bottom:14px; }}
  .card h4 {{ margin:0 0 8px 0; font-size:19px; color:{TINTA}; font-weight:700; }}
  .card p {{ margin:0; color:{GRIS}; font-size:16px; line-height:1.6; }}

  .ind {{ background:{BLANCO}; border:1px solid {LINEA};
       border-left:5px solid var(--c,{AZUL}); border-radius:12px;
       padding:18px 20px; margin-bottom:14px; height:100%; }}
  .ind .top {{ display:flex; justify-content:space-between; align-items:baseline; gap:12px; }}
  .ind .nom {{ font-weight:700; font-size:18px; color:{TINTA}; line-height:1.25; }}
  .ind .pmax {{ font-size:16px; font-weight:700; color:var(--c,{AZUL}); white-space:nowrap; }}
  .ind .lab {{ font-size:11px; letter-spacing:.14em; text-transform:uppercase;
       color:{GRIS_CLARO}; margin-top:14px; font-weight:700; }}
  .ind .val {{ font-size:16px; color:{TINTA}; line-height:1.5; margin-top:2px; }}
  .ind .tr {{ font-size:14px; color:{GRIS}; margin-top:14px; padding-top:12px;
       border-top:1px solid {LINEA}; }}

  .barra {{ height:12px; background:#E2DFDA; border-radius:99px; overflow:hidden; margin:8px 0 4px; }}
  .barra i {{ display:block; height:100%; border-radius:99px; }}

  .chip {{ display:inline-block; font-size:13px; letter-spacing:.06em; text-transform:uppercase;
       font-weight:700; padding:5px 13px; border-radius:99px; }}

  .fila {{ display:flex; justify-content:space-between; align-items:center; gap:14px;
       padding:13px 0; border-bottom:1px solid {LINEA}; }}
  .fila:last-child {{ border-bottom:none; }}
  .fila .iz {{ font-size:16px; color:{TINTA}; }}
  .fila .iz small {{ display:block; color:{GRIS_CLARO}; font-size:14px; margin-top:3px; }}
  .fila .de {{ font-weight:700; font-size:17px; white-space:nowrap; }}

  .aviso {{ background:#FFF6DF; border-left:5px solid {AMBAR}; border-radius:0 12px 12px 0;
       padding:16px 20px; font-size:16px; color:{TINTA}; line-height:1.6; margin:14px 0; }}
  .aviso b {{ color:{TINTA}; }}

  .paso {{ background:{BLANCO}; border:1px solid {LINEA}; border-radius:12px; padding:18px 12px;
       text-align:center; height:100%; }}
  .paso .n {{ width:34px; height:34px; border-radius:50%; background:{AZUL}; color:#fff;
       font-weight:700; font-size:16px; display:flex; align-items:center;
       justify-content:center; margin:0 auto 10px; }}
  .paso .t {{ font-weight:700; font-size:16px; color:{TINTA}; }}
  .paso .d {{ font-size:14px; color:{GRIS}; margin-top:5px; line-height:1.45; }}

  .nota {{ font-size:14px; color:{GRIS_CLARO}; }}
  .grande {{ font-size:46px; font-weight:700; line-height:1.05; letter-spacing:-.03em; }}
</style>
""",
    unsafe_allow_html=True,
)

# ------------------------------------------------------------------ sidebar

with st.sidebar:
    st.markdown(
        '<div class="marca"><div class="in">in</div><div class="nm">Impulsa</div></div>'
        f'<div class="nota" style="margin-bottom:14px">Gestión de Recompensa Total</div>',
        unsafe_allow_html=True,
    )
    for _p in ["Inicio", "Retos", "Progreso", "Recompensas", "Carrera", "Perfil"]:
        if st.button(
            _p,
            key=f"nav_{_p}",
            type="primary" if st.session_state["nav"] == _p else "secondary",
            use_container_width=True,
        ):
            st.session_state["nav"] = _p
            st.rerun()
    pantalla = st.session_state["nav"]
    st.divider()
    _, t_ = calcular()
    n_, c_ = nivel_de(t_)
    st.markdown(
        f'<div class="nota">Trimestre en curso</div>'
        f'<div style="font-size:40px;font-weight:700;color:{TINTA};line-height:1.05">{t_}'
        f'<span style="font-size:17px;color:{GRIS_CLARO};font-weight:400"> / 1,000</span></div>'
        f'<div style="margin:8px 0 16px"><span class="chip" style="background:{c_}1A;color:{c_}">{n_}</span></div>'
        f'<div class="nota">Incentivo proyectado</div>'
        f'<div style="font-size:26px;font-weight:700;color:{VERDE}">{mxn(bono_de(t_))}</div>',
        unsafe_allow_html=True,
    )
    st.divider()
    st.caption(
        "Prototipo académico. Metas y montos son supuestos del equipo, "
        "no datos oficiales de LinkedIn."
    )

filas, total = calcular()
nivel, nivel_color = nivel_de(total)

# ------------------------------------------------------------------ INICIO

if pantalla == "Inicio":
    st.markdown(
        '<div class="marca"><div class="in">in</div>'
        '<div class="nm">LinkedIn Impulsa</div></div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<p class="lead">Convertimos resultados verificables en reconocimiento, '
        "recompensas y crecimiento profesional, para el puesto de "
        "<b>Ingeniero(a) de Confiabilidad de Sistemas</b>.</p>",
        unsafe_allow_html=True,
    )

    c = st.columns(4)
    for col, (lab, val) in zip(
        c,
        [("Duración del ciclo", "90 días"), ("Puntos por trimestre", "1,000"),
         ("Incentivo máximo", mxn(BONO_MAX)), ("Personas en el piloto", str(PILOTO))],
    ):
        col.markdown(
            f'<div class="card" style="text-align:center;margin-bottom:0">'
            f'<div class="nota">{lab}</div>'
            f'<div class="grande" style="color:{AZUL};margin-top:4px">{val}</div></div>',
            unsafe_allow_html=True,
        )

    st.markdown(
        '<div class="aviso"><b>Retos → Evidencia → Recompensa → Carrera.</b><br>'
        "No se premia “hacer más”. Se premia cumplir un estándar verificable, "
        "sostenible y con evidencia.</div>",
        unsafe_allow_html=True,
    )

    st.markdown("### Cómo funciona")
    pasos = [
        ("Meta", "Qué lograr y antes de cuándo"),
        ("Evidencia", "Dato automático o prueba"),
        ("Validación", "Sistema, líder o compañero"),
        ("Puntos", "Valor según el resultado"),
        ("Recompensa", "Dinero, tiempo o aprendizaje"),
        ("Carrera", "Historial y revisión"),
    ]
    cols = st.columns(6)
    for i, (col, (t, d)) in enumerate(zip(cols, pasos), 1):
        col.markdown(
            f'<div class="paso"><div class="n">{i}</div>'
            f'<div class="t">{t}</div><div class="d">{d}</div></div>',
            unsafe_allow_html=True,
        )

    st.markdown("### El puesto elegido")
    st.markdown(
        f'<div class="card" style="border-left:5px solid {AZUL}">'
        "<h4>Ingeniero(a) de confiabilidad de sistemas</h4>"
        "<p>Mantiene la plataforma disponible, confiable, monitoreada y automatizada. "
        "LinkedIn describe el rol como <i>mission-critical</i>.<br><br>"
        "<b>Por qué lo elegimos:</b> cada reto puede tener una meta numérica, una fecha, "
        "una fuente de datos y una validación. No dependemos de opiniones vagas ni de "
        "encuestas de popularidad.</p></div>",
        unsafe_allow_html=True,
    )

    st.info("Abre **Progreso** en el menú de la izquierda para simular un trimestre completo.", icon="💡")

# ------------------------------------------------------------------ RETOS

elif pantalla == "Retos":
    st.markdown('<div class="eyebrow">02 · Retos</div>', unsafe_allow_html=True)
    st.markdown("## Siete indicadores, mil puntos")
    st.markdown(
        '<p class="lead">Cada reto tiene una meta numérica, una fuente de datos y '
        "quién lo valida. Las metas son propuestas del equipo, no objetivos internos "
        "de LinkedIn.</p>",
        unsafe_allow_html=True,
    )

    st.markdown("### Indicadores técnicos · 800 puntos")
    tec = [i for i in INDICADORES if i["eje"] == "Técnico"]
    for par in (tec[:2], tec[2:]):
        cols = st.columns(2)
        for col, ind in zip(cols, par):
            col.markdown(
                f'<div class="ind" style="--c:{AZUL}">'
                f'<div class="top"><span class="nom">{ind["n"]}. {ind["nombre"]}</span>'
                f'<span class="pmax">{ind["max"]} pts</span></div>'
                f'<div class="lab">Meta</div><div class="val">{ind["meta"]}</div>'
                f'<div class="lab">Quién lo valida</div><div class="val">{ind["validacion"]}</div>'
                f'<div class="tr">{ind["tramos"]}</div></div>',
                unsafe_allow_html=True,
            )

    st.markdown("### Indicadores humanos · 200 puntos")
    cols = st.columns(3)
    for col, ind in zip(cols, [i for i in INDICADORES if i["eje"] == "Humano"]):
        col.markdown(
            f'<div class="ind" style="--c:{VERDE}">'
            f'<div class="top"><span class="nom">{ind["n"]}. {ind["nombre"]}</span>'
            f'<span class="pmax">{ind["max"]}</span></div>'
            f'<div class="lab">Meta</div><div class="val">{ind["meta"]}</div>'
            f'<div class="lab">Quién lo valida</div><div class="val">{ind["validacion"]}</div>'
            f'<div class="tr">{ind["tramos"]}</div></div>',
            unsafe_allow_html=True,
        )

    st.markdown("### Reglas contra la manipulación")
    a, b = st.columns(2)
    a.markdown(
        '<div class="card"><h4>Lo que el sistema NO premia</h4><p>'
        "Cero incidentes.<br>Cantidad de despliegues.<br>"
        "Popularidad o reacciones.<br>Datos que la persona se autoreporta.</p></div>",
        unsafe_allow_html=True,
    )
    b.markdown(
        f'<div class="card" style="background:#E9F0F9"><h4>Por qué</h4><p>'
        "Premiar “cero incidentes” enseña a ocultar errores. Premiar despliegues "
        "enseña a hacer cambios inútiles. Premiar popularidad convierte el "
        "reconocimiento en un concurso de amigos.</p></div>",
        unsafe_allow_html=True,
    )

# ------------------------------------------------------------------ PROGRESO

elif pantalla == "Progreso":
    st.markdown('<div class="eyebrow">03 · Progreso</div>', unsafe_allow_html=True)
    st.markdown("## Simulador del trimestre")
    st.markdown(
        '<p class="lead">Mueve los datos del trimestre y observa cómo cambian los '
        "puntos, el nivel y el incentivo.</p>",
        unsafe_allow_html=True,
    )

    r1, r2, r3 = st.columns(3)
    r1.markdown(
        f'<div class="card" style="text-align:center;margin-bottom:0">'
        f'<div class="nota">Puntos del trimestre</div>'
        f'<div class="grande" style="color:{TINTA}">{total}'
        f'<span style="font-size:20px;color:{GRIS_CLARO};font-weight:400"> / 1,000</span></div></div>',
        unsafe_allow_html=True,
    )
    r2.markdown(
        f'<div class="card" style="text-align:center;margin-bottom:0">'
        f'<div class="nota">Nivel alcanzado</div>'
        f'<div class="grande" style="color:{nivel_color};font-size:38px">{nivel}</div></div>',
        unsafe_allow_html=True,
    )
    r3.markdown(
        f'<div class="card" style="text-align:center;margin-bottom:0">'
        f'<div class="nota">Incentivo del trimestre</div>'
        f'<div class="grande" style="color:{VERDE}">{mxn(bono_de(total))}</div></div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        f'<div class="barra" style="height:16px;margin-top:18px">'
        f'<i style="width:{total/10:.1f}%;background:{nivel_color}"></i></div>'
        f'<div style="display:flex;justify-content:space-between;font-size:13px;color:{GRIS_CLARO}">'
        "<span>0</span><span>500</span><span>700</span><span>850</span><span>950</span>"
        "<span>1,000</span></div>",
        unsafe_allow_html=True,
    )

    falta = next((lo for _, lo, _, _ in reversed(NIVELES) if lo > total), None)
    if falta:
        sig = next(n for n, lo, _, _ in NIVELES if lo == falta)
        st.markdown(
            f'<div class="aviso">Faltan <b>{falta - total} puntos</b> para llegar al '
            f"nivel <b>{sig}</b>.</div>",
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            '<div class="aviso">Nivel máximo alcanzado en este trimestre.</div>',
            unsafe_allow_html=True,
        )

    izq, der = st.columns([1, 1])

    with izq:
        st.markdown("### Datos del trimestre")
        st.slider("1 · Disponibilidad del servicio (%)", 99.50, 100.00,
                  key="disponibilidad", step=0.01, format="%.2f")
        st.slider("2 · Mediana de recuperación (minutos)", 0, 400,
                  key="recuperacion", step=5)
        st.slider("3 · Acciones preventivas cerradas en fecha (%)", 0, 100,
                  key="prevencion", step=1)
        st.slider("4 · Horas al mes ahorradas por automatización", 0.0, 12.0,
                  key="automatizacion", step=0.5)
        st.selectbox("5 · Acciones de cultura verificadas", [2, 1, 0], key="cultura",
                     format_func=lambda v: {2: "2 acciones verificadas",
                                            1: "1 acción verificada",
                                            0: "Sin acciones"}[v])
        st.selectbox("6 · Desarrollo aplicado",
                     ["Curso + aplicación real", "Solo curso completado", "Sin evidencia"],
                     key="desarrollo")
        st.selectbox("7 · Trabajo sostenible",
                     ["Cumple el protocolo", "Cumplimiento parcial", "No cumple"],
                     key="bienestar")

    with der:
        st.markdown("### Puntos por indicador")
        html = ['<div class="card">']
        for f in filas:
            pct = f["puntos"] / f["max"] * 100
            color = VERDE if pct == 100 else (AZUL if pct >= 50 else (AMBAR if pct > 0 else ROJO))
            html.append(
                f'<div class="fila" style="border-bottom:none;padding-bottom:4px">'
                f'<div class="iz"><b>{f["n"]}. {f["nombre"]}</b>'
                f'<small>{f["tramo"]}</small></div>'
                f'<div class="de" style="color:{color}">{f["puntos"]} / {f["max"]}</div></div>'
                f'<div class="barra" style="height:8px;margin:0 0 14px">'
                f'<i style="width:{pct:.0f}%;background:{color}"></i></div>'
            )
        html.append("</div>")
        st.markdown("".join(html), unsafe_allow_html=True)

        evidencia = pd.DataFrame(
            [{"Indicador": f'{f["n"]}. {f["nombre"]}', "Eje": f["eje"],
              "Dato": st.session_state[f["key"]], "Tramo": f["tramo"],
              "Puntos": f["puntos"], "Máximo": f["max"],
              "Validación": f["validacion"]} for f in filas]
        )
        st.download_button(
            "Descargar evidencia del trimestre",
            evidencia.to_csv(index=False).encode("utf-8-sig"),
            file_name="linkedin_impulsa_evidencia.csv",
            mime="text/csv",
        )

# ------------------------------------------------------------------ RECOMPENSAS

elif pantalla == "Recompensas":
    st.markdown('<div class="eyebrow">04 · Recompensa total</div>', unsafe_allow_html=True)
    st.markdown("## Dinero, tiempo, aprendizaje y carrera")
    st.markdown(
        '<p class="lead">La persona elige la categoría que más valora. No asumimos que '
        "una generación prefiere lo mismo que otra.</p>",
        unsafe_allow_html=True,
    )

    izq, der = st.columns([1, 1])

    with izq:
        st.markdown("### Incentivo financiero")
        st.markdown(
            f'<div class="card" style="border-left:5px solid {VERDE};text-align:center">'
            f'<div class="nota">Con tus {total} puntos de este trimestre</div>'
            f'<div class="grande" style="color:{VERDE};font-size:54px;margin:8px 0">'
            f"{mxn(bono_de(total))}</div>"
            f'<div class="nota">Máximo posible: {mxn(BONO_MAX)}</div></div>',
            unsafe_allow_html=True,
        )
        html = ['<div class="card"><h4>Escala de pago</h4>']
        for rango, nom, monto in [
            ("950 – 1,000", "Excelencia", BONO_MAX),
            ("850 – 949", "Liderazgo", BONO_MAX * 0.75),
            ("700 – 849", "Consolidado", BONO_MAX * 0.50),
            ("0 – 699", "Sin incentivo", 0.0),
        ]:
            activo = bono_de(total) == monto and monto > 0
            fondo = f"background:#E9F0F9;border-radius:8px;padding:12px 14px;" if activo else ""
            html.append(
                f'<div class="fila" style="{fondo}"><div class="iz">'
                f"<b>{rango}</b><small>{nom}</small></div>"
                f'<div class="de" style="color:{VERDE if monto else GRIS_CLARO}">{mxn(monto)}</div></div>'
            )
        html.append("</div>")
        st.markdown("".join(html), unsafe_allow_html=True)

        st.markdown(
            f'<div class="card"><h4>De dónde sale el máximo</h4><p>'
            f"Salario de referencia {mxn(SALARIO_MENSUAL)} al mes = {mxn(SALARIO_ANUAL)} al año.<br>"
            f"Tope de incentivos del 3 % anual = {mxn(SALARIO_ANUAL*TOPE_ANUAL)}.<br>"
            f"Entre 4 trimestres = <b>{mxn(BONO_MAX)}</b>.</p></div>",
            unsafe_allow_html=True,
        )

    with der:
        st.markdown("### Recompensas no financieras")
        for i, (cat, nombre, costo, desc) in enumerate(
            [
                ("Tiempo", "Día de bienestar", "$2,500*",
                 "Un día pagado, adicional a las vacaciones de ley."),
                ("Aprendizaje", "Certificación técnica", "hasta $4,000",
                 "Certificación pagada del área de confiabilidad."),
                ("Carrera", "Mentoría y proyecto", "$1,875*",
                 "Cuatro horas de mentoría más un proyecto de mayor alcance."),
                ("Reconocimiento", "Insignia y mensaje del líder", "$0 extra",
                 "Insignia verificable en el historial y reconocimiento público."),
                ("Propósito", "Acción social o de equipo", "según catálogo",
                 "Horas de voluntariado o un proyecto de impacto que la persona elige."),
            ],
            1,
        ):
            st.markdown(
                f'<div class="ind" style="--c:{AZUL_OSC}">'
                f'<div class="top"><span class="nom">{i}. {nombre}</span>'
                f'<span class="pmax">{costo}</span></div>'
                f'<div class="lab">{cat}</div><div class="val">{desc}</div></div>',
                unsafe_allow_html=True,
            )
        st.markdown(
            '<p class="nota">* Costo académico de oportunidad calculado con el salario '
            "de referencia. No es un precio oficial de LinkedIn.</p>",
            unsafe_allow_html=True,
        )

    st.markdown(
        '<div class="aviso"><b>Los incentivos económicos pasan por nómina.</b><br>'
        "Toda gratificación entregada por el trabajo integra el salario según el "
        "artículo 84 de la Ley Federal del Trabajo, y se revisa en materia fiscal y "
        "laboral antes de pagarse.</div>",
        unsafe_allow_html=True,
    )

# ------------------------------------------------------------------ CARRERA

elif pantalla == "Carrera":
    st.markdown('<div class="eyebrow">05 · Carrera</div>', unsafe_allow_html=True)
    st.markdown("## El premio crece con la consistencia")
    st.markdown(
        '<p class="lead">Un solo trimestre bueno da un bono. Varios trimestres buenos '
        "abren una revisión formal de desarrollo.</p>",
        unsafe_allow_html=True,
    )

    historial = HISTORIAL + [("Q3 2026 · en curso", total)]
    promedio = sum(p for _, p in historial) / len(historial)

    html = ['<div class="card"><h4>Historial de puntos</h4>']
    for etiqueta, p in historial:
        n, c = nivel_de(p)
        html.append(
            f'<div class="fila" style="border-bottom:none;padding-bottom:4px">'
            f'<div class="iz"><b>{etiqueta}</b><small>{n}</small></div>'
            f'<div class="de" style="color:{c}">{p:,} pts</div></div>'
            f'<div class="barra" style="height:10px;margin:0 0 16px">'
            f'<i style="width:{p/10:.0f}%;background:{c}"></i></div>'
        )
    html.append(
        f'<div class="fila"><div class="iz"><b>Promedio del año</b></div>'
        f'<div class="de" style="color:{AZUL}">{promedio:,.0f} pts</div></div></div>'
    )
    st.markdown("".join(html), unsafe_allow_html=True)

    st.markdown("### Qué desbloqueas y cuándo")
    cols = st.columns(3)
    horizontes = [
        ("0 – 3 meses", "Recompensa trimestral",
         ["Necesitas 700 puntos o más", "Bono o beneficio a elegir", "Reconocimiento inmediato"],
         total >= 700),
        ("3 – 6 meses", "Ruta de crecimiento",
         ["850 o más en dos trimestres", "Mentoría y certificación", "Proyecto de mayor responsabilidad"],
         sum(1 for _, p in historial if p >= 850) >= 2),
        ("6 – 12 meses", "Revisión de desarrollo",
         ["Promedio anual de 850 o más", "Revisión formal de preparación", "950 e impacto = nominación"],
         promedio >= 850),
    ]
    for col, (plazo, titulo, puntos, activo) in zip(cols, horizontes):
        estado = (
            f'<span class="chip" style="background:{VERDE}1A;color:{VERDE}">Desbloqueado</span>'
            if activo
            else f'<span class="chip" style="background:#E7E4DF;color:{GRIS}">Pendiente</span>'
        )
        col.markdown(
            f'<div class="ind" style="--c:{VERDE if activo else LINEA}">'
            f'<div class="top"><span class="nom">{titulo}</span></div>'
            f'<div style="margin:10px 0">{estado}</div>'
            f'<div class="lab">{plazo}</div>'
            f'<div class="val">' + "<br>".join(f"• {p}" for p in puntos) + "</div></div>",
            unsafe_allow_html=True,
        )

    st.markdown(
        '<div class="aviso"><b>La promoción no es automática.</b><br>'
        "La app solo activa una revisión formal de desarrollo. La decisión depende de "
        "competencias, alcance del puesto, vacantes y criterios internos de la empresa. "
        "Los puntos desbloquean evidencia, no puestos.</div>",
        unsafe_allow_html=True,
    )

# ------------------------------------------------------------------ PERFIL

elif pantalla == "Perfil":
    st.markdown('<div class="eyebrow">06 · Perfil y reglas</div>', unsafe_allow_html=True)
    st.markdown("## Claro para la persona, seguro para la empresa")

    izq, der = st.columns([1, 1.2])
    with izq:
        st.markdown(
            f'<div class="card">'
            f'<div style="display:flex;gap:14px;align-items:center;margin-bottom:8px">'
            f'<div style="width:62px;height:62px;border-radius:50%;background:{AZUL};'
            f'color:#fff;display:flex;align-items:center;justify-content:center;'
            f'font-weight:700;font-size:22px">AM</div>'
            f'<div><div style="font-weight:700;font-size:20px;color:{TINTA}">Alex Morales</div>'
            f'<div style="color:{GRIS};font-size:15px">Ingeniero(a) de confiabilidad</div></div></div>'
            f'<div class="fila"><div class="iz">Ciclo actual</div>'
            f'<div class="de">Q3 2026 · 90 días</div></div>'
            f'<div class="fila"><div class="iz">Puntos</div>'
            f'<div class="de" style="color:{nivel_color}">{total:,} / 1,000</div></div>'
            f'<div class="fila"><div class="iz">Nivel</div>'
            f'<div class="de" style="color:{nivel_color}">{nivel}</div></div>'
            f'<div class="fila"><div class="iz">Incentivo proyectado</div>'
            f'<div class="de" style="color:{VERDE}">{mxn(bono_de(total))}</div></div>'
            f"</div>",
            unsafe_allow_html=True,
        )

    with der:
        for et, tit, txt in [
            ("Datos", "Privacidad desde el diseño",
             "Solo datos laborales: monitoreo, incidentes, despliegues y registros "
             "operativos. Nunca sueño, estrés, biometría ni información de salud."),
            ("Nómina", "Bonos formalizados",
             "Los incentivos pasan por nómina y por revisión fiscal y laboral. "
             "Integran el salario según el artículo 84 de la LFT."),
            ("Equidad", "Sin concurso de popularidad",
             "Todo dato técnico viene de un sistema, no de un autorreporte."),
            ("Escala", "Replicable a otros puestos",
             "Cambian las metas y los puntos; se conserva la estructura del modelo."),
        ]:
            st.markdown(
                f'<div class="ind" style="--c:{AZUL}">'
                f'<div class="lab" style="margin-top:0">{et}</div>'
                f'<div class="nom" style="margin-top:2px">{tit}</div>'
                f'<div class="val" style="margin-top:6px">{txt}</div></div>',
                unsafe_allow_html=True,
            )

    with st.expander("Fuentes y supuestos del modelo"):
        st.markdown(
            """
| Fuente | Para qué se usó |
|---|---|
| LinkedIn Engineering · Site Reliability Engineering | Criticidad del rol, disponibilidad y automatización |
| LinkedIn Careers · Culture and Values | Valores del eje de cultura |
| DORA · métricas de desempeño | Tiempo de recuperación de despliegues fallidos |
| Google SRE | Objetivos de confiabilidad, postmortems, trabajo repetitivo |
| Gallup | Costo de reemplazo de 0.5 a 2 veces el salario anual |
| Cámara de Diputados | LFT art. 84 y Ley Federal de Protección de Datos Personales |

**Supuestos del caso:** salario de referencia $75,000 al mes · piloto de 20 personas ·
incentivo máximo 3 % anual · 70 % de pago esperado. Ninguno es dato interno de LinkedIn.
            """
        )

    st.caption(
        "LinkedIn Impulsa es un prototipo académico. No está afiliado a LinkedIn "
        "Corporation ni representa sus políticas o compensaciones reales."
    )
