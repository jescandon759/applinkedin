"""
LinkedIn Impulsa · Gestión de Recompensa Total
Prototipo académico de app de recompensa total gamificada para el puesto de
Ingeniero(a) de Confiabilidad de Sistemas (Site Reliability Engineer).

Todos los montos y metas son supuestos académicos del equipo y NO son
objetivos internos ni precios oficiales de LinkedIn.
"""

import pandas as pd
import streamlit as st

# ---------------------------------------------------------------- configuración

st.set_page_config(
    page_title="LinkedIn Impulsa",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded",
)

AZUL = "#0A66C2"
AZUL_OSCURO = "#004182"
VERDE = "#01754F"
AMBAR = "#915907"
ROJO = "#B24020"
TINTA = "#191919"
GRIS = "#5E5E5E"
LINEA = "#D9D6D1"
LIENZO = "#F4F2EE"

# Supuestos académicos declarados en la presentación
SALARIO_MENSUAL = 75_000
SALARIO_ANUAL = SALARIO_MENSUAL * 12          # $900,000
TOPE_INCENTIVO_ANUAL = 0.03                   # 3 %
BONO_MAX_TRIMESTRE = SALARIO_ANUAL * TOPE_INCENTIVO_ANUAL / 4   # $6,750
COSTO_HORA = SALARIO_MENSUAL / 160            # $468.75
PILOTO_PERSONAS = 20

NIVELES = [
    ("Excelencia", 950, 1000, VERDE),
    ("Liderazgo", 850, 949, AZUL),
    ("Consolidado", 700, 849, AZUL_OSCURO),
    ("Construcción", 500, 699, AMBAR),
    ("Inicio", 0, 499, GRIS),
]

# ---------------------------------------------------------------- motor de puntos


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
        v, (0, "Sin acciones verificadas")
    )


def pts_desarrollo(v):
    return {
        "Curso + aplicación real": (50, "Curso aplicado"),
        "Solo curso completado": (25, "Solo curso"),
        "Sin evidencia": (0, "Sin evidencia"),
    }[v]


def pts_bienestar(v):
    return {
        "Cumple protocolo de guardia y cierre": (50, "Protocolo cumplido"),
        "Cumplimiento parcial": (25, "Cumplimiento parcial"),
        "No cumple": (0, "No cumple"),
    }[v]


INDICADORES = [
    {
        "n": 1,
        "eje": "Técnico",
        "nombre": "Confiabilidad del servicio",
        "max": 250,
        "meta": "Disponibilidad trimestral ≥ 99.95 %",
        "calculo": "Tiempo disponible ÷ tiempo total × 100",
        "validacion": "Sistema de monitoreo del servicio",
        "tramos": "≥99.95 % = 250 · 99.90–99.949 % = 180 · 99.80–99.899 % = 90 · <99.80 % = 0",
        "key": "disponibilidad",
        "fn": pts_confiabilidad,
        "fuente": "LinkedIn Engineering · confiabilidad",
    },
    {
        "n": 2,
        "eje": "Técnico",
        "nombre": "Recuperación ante fallas",
        "max": 180,
        "meta": "Mediana de recuperación < 60 minutos",
        "calculo": "Desde la degradación por despliegue hasta la restauración",
        "validacion": "Sistema de incidentes y despliegues",
        "tramos": "<60 min = 180 · 60–120 = 120 · 121–240 = 60 · >240 = 0",
        "key": "recuperacion",
        "fn": pts_recuperacion,
        "fuente": "DORA · tiempo de recuperación de despliegues fallidos",
    },
    {
        "n": 3,
        "eje": "Técnico",
        "nombre": "Prevención de reincidencias",
        "max": 200,
        "meta": "Cerrar ≥ 90 % de las acciones preventivas en fecha",
        "calculo": "Acciones cerradas en fecha ÷ acciones comprometidas",
        "validacion": "Otro ingeniero comprueba que la solución funciona",
        "tramos": "≥90 % = 200 · 80–89 % = 150 · 70–79 % = 75 · <70 % = 0",
        "key": "prevencion",
        "fn": pts_prevencion,
        "fuente": "Google SRE · postmortems sin culpa",
    },
    {
        "n": 4,
        "eje": "Técnico",
        "nombre": "Automatización útil",
        "max": 170,
        "meta": "Ahorrar ≥ 5 horas mensuales de trabajo repetitivo",
        "calculo": "Comparar tiempo antes vs. después y sostener 30 días",
        "validacion": "Evidencia del ahorro + automatización viva 30 días",
        "tramos": "≥5 h = 170 · 3–4.9 h = 120 · 1–2.9 h = 60 · <1 h = 0",
        "key": "automatizacion",
        "fn": pts_automatizacion,
        "fuente": "Google SRE · eliminación de trabajo operativo repetitivo",
    },
    {
        "n": 5,
        "eje": "Humano",
        "nombre": "Impacto en cultura",
        "max": 100,
        "meta": "2 acciones verificadas alineadas a los valores",
        "calculo": "Conteo de acciones con evidencia",
        "validacion": "Líder + compañero confirman la evidencia",
        "tramos": "2 acciones = 100 · 1 acción = 50 · 0 = 0",
        "key": "cultura",
        "fn": pts_cultura,
        "fuente": "LinkedIn Careers · Culture and Values",
    },
    {
        "n": 6,
        "eje": "Humano",
        "nombre": "Desarrollo aplicado",
        "max": 50,
        "meta": "Curso o capacitación + aplicación real",
        "calculo": "Evidencia del curso más el resultado aplicado",
        "validacion": "Líder valida el resultado aplicado",
        "tramos": "Curso aplicado = 50 · Solo curso = 25 · Sin evidencia = 0",
        "key": "desarrollo",
        "fn": pts_desarrollo,
        "fuente": "Modelo del equipo",
    },
    {
        "n": 7,
        "eje": "Humano",
        "nombre": "Trabajo sostenible",
        "max": 50,
        "meta": "Cumplir el protocolo de guardia y cierre",
        "calculo": "Registro operativo del turno de guardia",
        "validacion": "Registro operativo — nunca datos de salud",
        "tramos": "Cumple = 50 · Parcial = 25 · No cumple = 0",
        "key": "bienestar",
        "fn": pts_bienestar,
        "fuente": "Minimización de datos personales · LFPDPPP",
    },
]

DEFAULTS = {
    "disponibilidad": 99.93,
    "recuperacion": 45,
    "prevencion": 92,
    "automatizacion": 5.5,
    "cultura": 2,
    "desarrollo": "Curso + aplicación real",
    "bienestar": "Cumple protocolo de guardia y cierre",
}

HISTORIAL = [("Q1 2026", 712), ("Q2 2026", 868)]

for k, v in DEFAULTS.items():
    st.session_state.setdefault(k, v)


def calcular():
    """Devuelve (filas, total) con el puntaje vigente del trimestre."""
    filas = []
    total = 0
    for ind in INDICADORES:
        p, etiqueta = ind["fn"](st.session_state[ind["key"]])
        total += p
        filas.append({**ind, "puntos": p, "tramo": etiqueta})
    return filas, total


def nivel_de(total):
    for nombre, low, high, color in NIVELES:
        if low <= total <= high:
            return nombre, low, high, color
    return NIVELES[-1][0], 0, 499, GRIS


def bono_de(total):
    if total >= 950:
        return BONO_MAX_TRIMESTRE
    if total >= 850:
        return BONO_MAX_TRIMESTRE * 0.75
    if total >= 700:
        return BONO_MAX_TRIMESTRE * 0.50
    return 0.0


def mxn(v):
    return f"${v:,.2f}" if v % 1 else f"${v:,.0f}"


# ---------------------------------------------------------------- estilos

st.markdown(
    f"""
<style>
  .stApp {{ background:{LIENZO}; }}
  .block-container {{ padding-top:2.2rem; max-width:1180px; }}
  h1,h2,h3,h4 {{ color:{TINTA}; letter-spacing:-.01em; }}

  .marca {{ display:flex; align-items:center; gap:10px; margin-bottom:4px; }}
  .marca .in {{ background:{AZUL}; color:#fff; font-weight:700; font-size:19px;
                width:34px; height:34px; border-radius:6px; display:flex;
                align-items:center; justify-content:center; }}
  .marca .nm {{ font-size:24px; font-weight:700; color:{TINTA}; }}

  .eyebrow {{ font-size:11px; letter-spacing:.14em; text-transform:uppercase;
              color:{AZUL}; font-weight:700; margin-bottom:6px; }}

  .card {{ background:#fff; border:1px solid {LINEA}; border-radius:8px;
           padding:18px 20px; margin-bottom:12px; }}
  .card h4 {{ margin:0 0 6px 0; font-size:16px; }}
  .card p {{ margin:0; color:{GRIS}; font-size:14px; line-height:1.55; }}

  .ind {{ background:#fff; border:1px solid {LINEA}; border-left:4px solid var(--c,{AZUL});
          border-radius:8px; padding:16px 18px; margin-bottom:12px; height:100%; }}
  .ind .top {{ display:flex; justify-content:space-between; align-items:baseline; gap:10px; }}
  .ind .nom {{ font-weight:700; font-size:15px; color:{TINTA}; }}
  .ind .pmax {{ font-size:13px; font-weight:700; color:var(--c,{AZUL}); white-space:nowrap; }}
  .ind .lab {{ font-size:10px; letter-spacing:.12em; text-transform:uppercase;
               color:{GRIS}; margin-top:11px; font-weight:600; }}
  .ind .val {{ font-size:13.5px; color:{TINTA}; line-height:1.5; }}
  .ind .tr {{ font-size:12px; color:{GRIS}; margin-top:12px; padding-top:10px;
              border-top:1px solid {LINEA}; }}
  .ind .fu {{ font-size:11px; color:#8A8A8A; margin-top:8px; font-style:italic; }}

  .barra {{ height:10px; background:#E6E4E0; border-radius:99px; overflow:hidden; margin:6px 0 2px; }}
  .barra i {{ display:block; height:100%; border-radius:99px; }}

  .chip {{ display:inline-block; font-size:11px; letter-spacing:.06em; text-transform:uppercase;
           font-weight:700; padding:3px 9px; border-radius:99px; }}

  .fila {{ display:flex; justify-content:space-between; align-items:center; gap:12px;
           padding:11px 0; border-bottom:1px solid {LINEA}; }}
  .fila:last-child {{ border-bottom:none; }}
  .fila .iz {{ font-size:14px; color:{TINTA}; }}
  .fila .iz small {{ display:block; color:{GRIS}; font-size:12px; margin-top:2px; }}
  .fila .de {{ font-weight:700; font-size:14px; white-space:nowrap; }}

  .aviso {{ background:#FFF8E6; border-left:4px solid {AMBAR}; border-radius:0 8px 8px 0;
            padding:13px 16px; font-size:13.5px; color:{TINTA}; line-height:1.55; margin:10px 0; }}
  .nota {{ font-size:12px; color:{GRIS}; font-style:italic; }}

  .paso {{ background:#fff; border:1px solid {LINEA}; border-radius:8px; padding:14px;
           text-align:center; height:100%; }}
  .paso .n {{ width:26px; height:26px; border-radius:50%; background:{AZUL}; color:#fff;
              font-weight:700; font-size:13px; display:flex; align-items:center;
              justify-content:center; margin:0 auto 8px; }}
  .paso .t {{ font-weight:700; font-size:14px; }}
  .paso .d {{ font-size:12px; color:{GRIS}; margin-top:4px; line-height:1.45; }}

  section[data-testid="stSidebar"] {{ background:#fff; border-right:1px solid {LINEA}; }}
</style>
""",
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------- barra lateral

with st.sidebar:
    st.markdown(
        f'<div class="marca"><div class="in">in</div><div class="nm">Impulsa</div></div>'
        f'<div class="nota">Gestión de Recompensa Total</div>',
        unsafe_allow_html=True,
    )
    st.divider()
    pantalla = st.radio(
        "Navegación",
        ["Inicio", "Retos", "Progreso", "Recompensas", "Carrera", "Perfil"],
        key="nav",
        label_visibility="collapsed",
    )
    st.divider()
    _, total_actual = calcular()
    nombre_nivel, _, _, color_nivel = nivel_de(total_actual)
    st.markdown(
        f'<div class="nota">Trimestre en curso</div>'
        f'<div style="font-size:26px;font-weight:700;color:{TINTA};line-height:1.1">'
        f"{total_actual} <span style='font-size:14px;color:{GRIS};font-weight:400'>/ 1,000</span></div>"
        f'<div style="margin-top:6px"><span class="chip" style="background:{color_nivel}1A;color:{color_nivel}">'
        f"{nombre_nivel}</span></div>"
        f'<div style="margin-top:10px;font-size:13px;color:{GRIS}">Incentivo proyectado</div>'
        f'<div style="font-size:19px;font-weight:700;color:{VERDE}">{mxn(bono_de(total_actual))}</div>',
        unsafe_allow_html=True,
    )
    st.divider()
    st.caption(
        "Prototipo académico. Metas, salarios y montos son supuestos del equipo, "
        "no objetivos internos ni precios oficiales de LinkedIn."
    )

filas, total = calcular()
nivel, nivel_low, nivel_high, nivel_color = nivel_de(total)

# ---------------------------------------------------------------- 01 · INICIO

if pantalla == "Inicio":
    st.markdown(
        f'<div class="marca"><div class="in">in</div>'
        f'<div class="nm">LinkedIn Impulsa</div></div>',
        unsafe_allow_html=True,
    )
    st.markdown("### Gestión de Recompensa Total")
    st.markdown(
        f'<p style="color:{GRIS};font-size:16px;max-width:70ch;margin-top:-6px">'
        "Convertir resultados verificables en reconocimiento, recompensas y "
        "crecimiento profesional, para el puesto de Ingeniero(a) de Confiabilidad "
        "de Sistemas.</p>",
        unsafe_allow_html=True,
    )

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Ciclo", "90 días")
    c2.metric("Puntos por trimestre", "1,000")
    c3.metric("Incentivo máximo", mxn(BONO_MAX_TRIMESTRE))
    c4.metric("Piloto", f"{PILOTO_PERSONAS} personas")

    st.markdown(
        '<div class="aviso"><b>Retos → Evidencia → Recompensa → Carrera.</b> '
        "No se premia “hacer más”: se premia cumplir un estándar verificable, "
        "sostenible y con evidencia.</div>",
        unsafe_allow_html=True,
    )

    st.markdown("#### El puesto crítico")
    a, b = st.columns([1, 1.6])
    with a:
        st.markdown(
            f'<div class="card" style="border-left:4px solid {AZUL}">'
            f'<div class="eyebrow">Puesto elegido</div>'
            f'<h4>Ingeniero(a) de confiabilidad de sistemas</h4>'
            "<p>Mantiene la plataforma disponible, confiable, monitoreada, "
            "automatizada y preparada para escalar. LinkedIn describe el rol "
            "como <i>mission-critical</i>.</p></div>",
            unsafe_allow_html=True,
        )
    with b:
        st.markdown(
            '<div class="card"><h4>¿Por qué facilita el proyecto?</h4>'
            "<p>Porque cada reto puede tener una meta numérica, una fecha, una "
            "fuente de datos y una validación. No dependemos de opiniones vagas "
            "ni de encuestas de popularidad.</p></div>",
            unsafe_allow_html=True,
        )

    cols = st.columns(4)
    pilares = [
        ("Resultados", "Disponibilidad · Recuperación · Prevención"),
        ("Mejora", "Automatización · Aprendizaje · Calidad"),
        ("Cultura", "Colaboración · Confianza · Enfoque en miembros"),
        ("Carrera", "Evidencia histórica · Mentoría · Revisión de desarrollo"),
    ]
    for col, (t, d) in zip(cols, pilares):
        col.markdown(
            f'<div class="paso"><div class="t">{t}</div><div class="d">{d}</div></div>',
            unsafe_allow_html=True,
        )

    st.markdown("#### El modelo, en seis pasos")
    pasos = [
        ("Meta concreta", "Qué debe lograr y antes de cuándo"),
        ("Evidencia", "Dato automático o prueba verificable"),
        ("Validación", "Sistema, líder o compañero"),
        ("Puntos", "Valor asignado según el resultado"),
        ("Recompensa", "Dinero, tiempo o aprendizaje"),
        ("Carrera", "Historial y revisión de desarrollo"),
    ]
    cols = st.columns(6)
    for i, (col, (t, d)) in enumerate(zip(cols, pasos), 1):
        col.markdown(
            f'<div class="paso"><div class="n">{i}</div>'
            f'<div class="t">{t}</div><div class="d">{d}</div></div>',
            unsafe_allow_html=True,
        )

    st.info(
        "Ve a **Progreso** para simular un trimestre: cambia los indicadores y "
        "observa cómo se recalculan los puntos, el nivel y el incentivo.",
        icon="💡",
    )

# ---------------------------------------------------------------- 02 · RETOS

elif pantalla == "Retos":
    st.markdown('<div class="eyebrow">02 · Retos del trimestre</div>', unsafe_allow_html=True)
    st.markdown("### Siete indicadores, mil puntos, cero ambigüedad")
    st.markdown(
        f'<p class="nota">Las metas son propuestas académicas del equipo; no '
        "afirmamos que sean objetivos internos de LinkedIn.</p>",
        unsafe_allow_html=True,
    )

    st.markdown("#### Indicadores técnicos · 800 puntos")
    tecnicos = [i for i in INDICADORES if i["eje"] == "Técnico"]
    for pareja in (tecnicos[:2], tecnicos[2:]):
        cols = st.columns(2)
        for col, ind in zip(cols, pareja):
            col.markdown(
                f'<div class="ind" style="--c:{AZUL}">'
                f'<div class="top"><span class="nom">{ind["n"]}. {ind["nombre"]}</span>'
                f'<span class="pmax">{ind["max"]} pts</span></div>'
                f'<div class="lab">Meta</div><div class="val">{ind["meta"]}</div>'
                f'<div class="lab">Cómo se calcula</div><div class="val">{ind["calculo"]}</div>'
                f'<div class="lab">Validación</div><div class="val">{ind["validacion"]}</div>'
                f'<div class="tr">{ind["tramos"]}</div>'
                f'<div class="fu">Fuente: {ind["fuente"]}</div></div>',
                unsafe_allow_html=True,
            )

    st.markdown("#### Indicadores humanos · 200 puntos")
    cols = st.columns(3)
    for col, ind in zip(cols, [i for i in INDICADORES if i["eje"] == "Humano"]):
        col.markdown(
            f'<div class="ind" style="--c:{VERDE}">'
            f'<div class="top"><span class="nom">{ind["n"]}. {ind["nombre"]}</span>'
            f'<span class="pmax">{ind["max"]} pts</span></div>'
            f'<div class="lab">Meta</div><div class="val">{ind["meta"]}</div>'
            f'<div class="lab">Validación</div><div class="val">{ind["validacion"]}</div>'
            f'<div class="tr">{ind["tramos"]}</div>'
            f'<div class="fu">Fuente: {ind["fuente"]}</div></div>',
            unsafe_allow_html=True,
        )

    st.markdown("#### Reglas de integridad")
    a, b = st.columns([1.3, 1])
    a.markdown(
        '<div class="card"><h4>Lo que el sistema NO premia</h4><p>'
        "• Los datos técnicos son automáticos, no autoreportados.<br>"
        "• No hay puntos por “cero incidentes”.<br>"
        "• No hay puntos por cantidad de despliegues.<br>"
        "• No hay ranking por popularidad ni por reacciones.</p></div>",
        unsafe_allow_html=True,
    )
    b.markdown(
        '<div class="card" style="background:#EEF3FA"><h4>¿Por qué?</h4><p>'
        "Porque premiar “cero incidentes” enseña a ocultar errores, premiar "
        "despliegues enseña a hacer cambios inútiles, y premiar popularidad "
        "convierte el reconocimiento en un concurso de amigos.</p></div>",
        unsafe_allow_html=True,
    )

# ---------------------------------------------------------------- 03 · PROGRESO

elif pantalla == "Progreso":
    st.markdown('<div class="eyebrow">03 · Progreso del trimestre</div>', unsafe_allow_html=True)
    st.markdown("### Simulador del ciclo de 90 días")
    st.markdown(
        f'<p class="nota">Ajusta cada indicador con los datos del trimestre. '
        "Los puntos, el nivel y el incentivo se recalculan al instante.</p>",
        unsafe_allow_html=True,
    )

    izq, der = st.columns([1, 1.25])

    with izq:
        st.markdown("##### Datos del trimestre")
        st.slider("1 · Disponibilidad del servicio (%)", 99.50, 100.00,
                  key="disponibilidad", step=0.01, format="%.2f")
        st.slider("2 · Mediana de recuperación (minutos)", 0, 400,
                  key="recuperacion", step=5)
        st.slider("3 · Acciones preventivas cerradas en fecha (%)", 0, 100,
                  key="prevencion", step=1)
        st.slider("4 · Horas mensuales ahorradas por automatización", 0.0, 12.0,
                  key="automatizacion", step=0.5)
        st.radio("5 · Acciones de cultura verificadas", [0, 1, 2],
                 key="cultura", horizontal=True)
        st.selectbox("6 · Desarrollo aplicado",
                     ["Curso + aplicación real", "Solo curso completado", "Sin evidencia"],
                     key="desarrollo")
        st.selectbox("7 · Trabajo sostenible",
                     ["Cumple protocolo de guardia y cierre", "Cumplimiento parcial", "No cumple"],
                     key="bienestar")

    with der:
        st.markdown("##### Resultado")
        m1, m2, m3 = st.columns(3)
        m1.metric("Puntos del trimestre", f"{total:,} / 1,000")
        m2.metric("Nivel", nivel)
        m3.metric("Incentivo", mxn(bono_de(total)))

        st.markdown(
            f'<div class="barra"><i style="width:{total/10:.1f}%;background:{nivel_color}"></i></div>'
            f'<div style="display:flex;justify-content:space-between;font-size:11px;color:{GRIS}">'
            f"<span>0</span><span>500</span><span>700</span><span>850</span><span>950</span><span>1,000</span></div>",
            unsafe_allow_html=True,
        )

        siguiente = next((n for n, lo, hi, _ in reversed(NIVELES) if lo > total), None)
        if siguiente:
            lo = next(lo for n, lo, hi, _ in NIVELES if n == siguiente)
            st.markdown(
                f'<div class="aviso">Faltan <b>{lo - total} puntos</b> para alcanzar '
                f"el nivel <b>{siguiente}</b>.</div>",
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                '<div class="aviso">Nivel máximo alcanzado en este trimestre.</div>',
                unsafe_allow_html=True,
            )

        st.markdown("##### Desglose por indicador")
        html = ['<div class="card">']
        for f in filas:
            pct = f["puntos"] / f["max"] * 100
            color = VERDE if pct == 100 else (AZUL if pct >= 50 else (AMBAR if pct > 0 else ROJO))
            html.append(
                f'<div class="fila"><div class="iz">{f["n"]}. {f["nombre"]}'
                f'<small>{f["tramo"]}</small></div>'
                f'<div class="de" style="color:{color}">{f["puntos"]} / {f["max"]}</div></div>'
                f'<div class="barra" style="height:5px;margin:-4px 0 6px">'
                f'<i style="width:{pct:.0f}%;background:{color}"></i></div>'
            )
        html.append("</div>")
        st.markdown("".join(html), unsafe_allow_html=True)

    evidencia = pd.DataFrame(
        [
            {
                "Indicador": f'{f["n"]}. {f["nombre"]}',
                "Eje": f["eje"],
                "Dato del trimestre": st.session_state[f["key"]],
                "Tramo alcanzado": f["tramo"],
                "Puntos": f["puntos"],
                "Máximo": f["max"],
                "Validación": f["validacion"],
            }
            for f in filas
        ]
    )
    st.download_button(
        "Descargar evidencia del trimestre (CSV)",
        evidencia.to_csv(index=False).encode("utf-8-sig"),
        file_name="linkedin_impulsa_evidencia.csv",
        mime="text/csv",
    )

# ---------------------------------------------------------------- 04 · RECOMPENSAS

elif pantalla == "Recompensas":
    st.markdown('<div class="eyebrow">04 · Recompensa total</div>', unsafe_allow_html=True)
    st.markdown("### Dinero, tiempo, aprendizaje, carrera y propósito")
    st.markdown(
        f'<p class="nota">La persona elige la categoría que más valora. Evitamos '
        "asumir que una generación “prefiere” lo mismo que otra.</p>",
        unsafe_allow_html=True,
    )

    izq, der = st.columns([1, 1.1])

    with izq:
        st.markdown("#### Incentivo financiero")
        st.markdown(
            f'<div class="card" style="border-left:4px solid {VERDE}">'
            f'<div class="eyebrow">Tu incentivo con {total} puntos</div>'
            f'<div style="font-size:38px;font-weight:700;color:{VERDE};line-height:1.1">'
            f"{mxn(bono_de(total))}</div>"
            f'<p style="margin-top:6px">Máximo por trimestre: {mxn(BONO_MAX_TRIMESTRE)}</p></div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            f'<div class="card"><h4>Base del cálculo</h4><p>'
            f"Salario de referencia {mxn(SALARIO_MENSUAL)} × 12 = {mxn(SALARIO_ANUAL)} anuales.<br>"
            f"Tope de incentivos 3 % anual = {mxn(SALARIO_ANUAL * TOPE_INCENTIVO_ANUAL)} "
            f"÷ 4 trimestres = <b>{mxn(BONO_MAX_TRIMESTRE)}</b>.</p></div>",
            unsafe_allow_html=True,
        )
        escala = [
            ("950 – 1,000", "Excelencia", BONO_MAX_TRIMESTRE),
            ("850 – 949", "Liderazgo", BONO_MAX_TRIMESTRE * 0.75),
            ("700 – 849", "Consolidado", BONO_MAX_TRIMESTRE * 0.50),
            ("0 – 699", "Sin incentivo financiero", 0.0),
        ]
        html = ['<div class="card"><h4>Escala de pago</h4>']
        for rango, nom, monto in escala:
            activo = bono_de(total) == monto and monto > 0
            peso = "700" if activo else "400"
            fondo = f"background:{AZUL}0F;border-radius:6px;padding:8px 10px;" if activo else ""
            html.append(
                f'<div class="fila" style="{fondo}"><div class="iz" style="font-weight:{peso}">'
                f"{rango}<small>{nom}</small></div>"
                f'<div class="de" style="color:{VERDE if monto else GRIS}">{mxn(monto)}</div></div>'
            )
        html.append("</div>")
        st.markdown("".join(html), unsafe_allow_html=True)

    with der:
        st.markdown("#### Recompensas no financieras")
        no_fin = [
            ("Tiempo", "Día de bienestar", "$2,500*", "Un día pagado adicional al calendario de ley."),
            ("Aprendizaje", "Certificación técnica", "hasta $4,000", "Certificación pagada del área de confiabilidad."),
            ("Carrera", "Mentoría + proyecto", "$1,875*", "4 horas de mentoría más un proyecto de mayor alcance."),
            ("Reconocimiento", "Insignia + mensaje del líder", "$0 incremental", "Insignia verificable en el historial y reconocimiento público."),
            ("Propósito", "Acción social o de equipo", "según catálogo", "Horas de voluntariado o proyecto de impacto elegido por la persona."),
        ]
        for i, (cat, nombre, costo, desc) in enumerate(no_fin, 1):
            st.markdown(
                f'<div class="ind" style="--c:{AZUL_OSCURO}">'
                f'<div class="top"><span class="nom">{i}. {nombre}</span>'
                f'<span class="pmax">{costo}</span></div>'
                f'<div class="lab">{cat}</div><div class="val">{desc}</div></div>',
                unsafe_allow_html=True,
            )
        st.markdown(
            '<p class="nota">* Costo académico de oportunidad calculado con el salario '
            "de referencia; no es un precio oficial de LinkedIn.</p>",
            unsafe_allow_html=True,
        )

    st.markdown(
        '<div class="aviso"><b>Los incentivos económicos pasan por nómina.</b> '
        "Toda gratificación entregada por el trabajo integra el salario conforme al "
        "artículo 84 de la Ley Federal del Trabajo, y se somete a revisión fiscal y "
        "laboral antes de pagarse.</div>",
        unsafe_allow_html=True,
    )

# ---------------------------------------------------------------- 05 · CARRERA

elif pantalla == "Carrera":
    st.markdown('<div class="eyebrow">05 · Horizonte de recompensa</div>', unsafe_allow_html=True)
    st.markdown("### El premio crece con la consistencia, no con un solo trimestre")

    historial = HISTORIAL + [("Q3 2026 (en curso)", total)]
    promedio = sum(p for _, p in historial) / len(historial)

    c1, c2, c3 = st.columns(3)
    c1.metric("Trimestres registrados", len(historial))
    c2.metric("Promedio del año", f"{promedio:,.0f}")
    c3.metric("Mejor trimestre", f"{max(p for _, p in historial):,}")

    html = ['<div class="card"><h4>Historial de puntos</h4>']
    for etiqueta, p in historial:
        n, _, _, c = nivel_de(p)
        html.append(
            f'<div class="fila"><div class="iz">{etiqueta}<small>{n}</small></div>'
            f'<div class="de" style="color:{c}">{p:,} pts</div></div>'
            f'<div class="barra" style="height:6px;margin:-4px 0 8px">'
            f'<i style="width:{p/10:.0f}%;background:{c}"></i></div>'
        )
    html.append("</div>")
    st.markdown("".join(html), unsafe_allow_html=True)

    horizontes = [
        ("0 – 3 meses", "Recompensa trimestral",
         ["≥ 700 puntos", "Bono o beneficio elegido", "Reconocimiento inmediato"],
         total >= 700),
        ("3 – 6 meses", "Ruta de crecimiento",
         ["≥ 850 en dos trimestres", "Mentoría + certificación", "Proyecto de mayor responsabilidad"],
         sum(1 for _, p in historial if p >= 850) >= 2),
        ("6 – 12 meses", "Revisión de desarrollo",
         ["Promedio anual ≥ 850", "Revisión formal de preparación", "≥ 950 + impacto = nominación"],
         promedio >= 850),
    ]
    cols = st.columns(3)
    for col, (plazo, titulo, puntos, activo) in zip(cols, horizontes):
        estado = (
            f'<span class="chip" style="background:{VERDE}1A;color:{VERDE}">Desbloqueado</span>'
            if activo
            else f'<span class="chip" style="background:#EDEBE7;color:{GRIS}">Pendiente</span>'
        )
        col.markdown(
            f'<div class="ind" style="--c:{VERDE if activo else LINEA}">'
            f'<div class="top"><span class="nom">{titulo}</span>{estado}</div>'
            f'<div class="lab">{plazo}</div>'
            f'<div class="val">' + "<br>".join(f"• {p}" for p in puntos) + "</div></div>",
            unsafe_allow_html=True,
        )

    st.markdown(
        '<div class="aviso"><b>La promoción no es automática.</b> La app solo activa '
        "una revisión formal de desarrollo. La decisión depende de competencias, "
        "alcance del rol, vacantes disponibles y criterios internos de la empresa. "
        "Los puntos desbloquean evidencia, no puestos.</div>",
        unsafe_allow_html=True,
    )

# ---------------------------------------------------------------- 06 · PERFIL

elif pantalla == "Perfil":
    st.markdown('<div class="eyebrow">06 · Perfil y reglas del programa</div>', unsafe_allow_html=True)
    st.markdown("### Claro para la persona, seguro para la empresa")

    izq, der = st.columns([1, 1.3])
    with izq:
        st.markdown(
            f'<div class="card">'
            f'<div style="display:flex;gap:12px;align-items:center">'
            f'<div style="width:52px;height:52px;border-radius:50%;background:{AZUL};'
            f"color:#fff;display:flex;align-items:center;justify-content:center;"
            f'font-weight:700;font-size:18px">AM</div>'
            f'<div><div style="font-weight:700;font-size:16px">Alex Morales</div>'
            f'<div style="color:{GRIS};font-size:13px">Ingeniero(a) de confiabilidad '
            f"de sistemas</div></div></div>"
            f'<div class="fila" style="margin-top:14px"><div class="iz">Ciclo actual</div>'
            f'<div class="de">Q3 2026 · 90 días</div></div>'
            f'<div class="fila"><div class="iz">Puntos del trimestre</div>'
            f'<div class="de" style="color:{nivel_color}">{total:,} / 1,000</div></div>'
            f'<div class="fila"><div class="iz">Nivel</div><div class="de">{nivel}</div></div>'
            f'<div class="fila"><div class="iz">Incentivo proyectado</div>'
            f'<div class="de" style="color:{VERDE}">{mxn(bono_de(total))}</div></div>'
            f"</div>",
            unsafe_allow_html=True,
        )

    with der:
        controles = [
            ("Datos", "Privacidad desde el diseño",
             "Solo datos laborales necesarios: monitoreo, incidentes, despliegues y "
             "registros operativos. Aviso de privacidad y acceso limitado. Nunca sueño, "
             "estrés, biometría ni información de salud."),
            ("Nómina", "Bonos formalizados",
             "Los incentivos económicos pasan por nómina y por revisión fiscal y laboral. "
             "Integran el salario conforme al artículo 84 de la LFT."),
            ("Equidad", "Sin concurso de popularidad",
             "No se premian reacciones, volumen de despliegues ni “cero incidentes”. "
             "Todo dato técnico proviene de un sistema, no de un autorreporte."),
            ("Escala", "Replicable a otros puestos",
             "Cambian las metas y el valor de los puntos; se conserva la estructura: "
             "meta, evidencia, validación, puntos, recompensa y carrera."),
        ]
        for et, tit, txt in controles:
            st.markdown(
                f'<div class="ind" style="--c:{AZUL}">'
                f'<div class="lab" style="margin-top:0">{et}</div>'
                f'<div class="nom">{tit}</div>'
                f'<div class="val" style="margin-top:5px">{txt}</div></div>',
                unsafe_allow_html=True,
            )

    with st.expander("Fuentes y supuestos del modelo"):
        st.markdown(
            """
| # | Fuente | Para qué se usó |
|---|---|---|
| 1 | LinkedIn Engineering · Site Reliability Engineering | Criticidad del rol, disponibilidad, automatización y escala |
| 2 | LinkedIn Careers · Culture and Values | Valores del eje de cultura |
| 3 | DORA · métricas de desempeño | Tiempo de recuperación de despliegues fallidos |
| 4 | Google SRE | Objetivos de confiabilidad, postmortems sin culpa, trabajo repetitivo |
| 5 | Gallup | Costo de reemplazo de 0.5 a 2 veces el salario anual |
| 6 | Cámara de Diputados | LFT art. 84 y Ley Federal de Protección de Datos Personales |

**Supuestos académicos del caso:** salario de referencia $75,000 mensuales ·
piloto de 20 personas · incentivo máximo 3 % anual · 70 % de pago esperado ·
costos de implementación y mantenimiento estimados. Ninguno es un dato interno
de LinkedIn.
            """
        )

    st.caption(
        "LinkedIn Impulsa es un prototipo académico. No está afiliado a LinkedIn "
        "Corporation ni representa sus políticas, metas o compensaciones reales."
    )
