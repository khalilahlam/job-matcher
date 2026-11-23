import html
import json
import tempfile
import time
from pathlib import Path

import streamlit as st

from cv_a_perfil import extraer_perfil
from estilos import aplicar_tema
from puntuar import puntuar_oferta

PERFIL_PATH = Path("perfil.json")
OFERTAS_PATH = Path("ofertas.json")
ESTADOS = ["Pendiente", "Preparada", "Enviada", "Descartada"]
MODALIDADES = ["Presencial", "Híbrido", "Remoto"]
CONTRATOS = ["Indefinido", "Temporal", "Prácticas", "Autónomo"]
SECCIONES = ["Ofertas", "Mi perfil", "Preferencias"]

st.set_page_config(
    page_title="JobMatcher",
    layout="wide",
    initial_sidebar_state="collapsed",
)


def esc(v) -> str:
    return html.escape(str(v))


def csv_lista(txt: str) -> list[str]:
    return [x.strip() for x in txt.split(",") if x.strip()]


def chips(items, fuerte: bool = False) -> str:
    if not items:
        return '<span class="sub">Sin datos</span>'
    cls = "pill pill-accent" if fuerte else "pill"
    return "".join(f'<span class="{cls}">{esc(x)}</span>' for x in items)


def fila_perfil(titulo: str, contenido: str) -> str:
    return (
        f'<div class="profile-row">'
        f'<div class="profile-k">{esc(titulo)}</div>'
        f"<div>{contenido}</div>"
        f"</div>"
    )


def req_label(texto: str) -> None:
    st.markdown(
        f'<div style="font-size:0.88rem;font-weight:600;margin-bottom:0.25rem;">{esc(texto)}<span class="req-star">*</span></div>',
        unsafe_allow_html=True,
    )


def cargar_json(ruta: Path, defecto):
    if ruta.exists():
        try:
            return json.loads(ruta.read_text(encoding="utf-8"))
        except Exception:
            pass
    return defecto


def guardar_json(ruta: Path, datos) -> None:
    ruta.write_text(json.dumps(datos, ensure_ascii=False, indent=2), encoding="utf-8")


# ------------------------------------------------------------------ Estado
if "perfil" not in st.session_state:
    p_ini = cargar_json(PERFIL_PATH, None)
    if p_ini:
        st.session_state["perfil"] = p_ini

if "ofertas" not in st.session_state:
    st.session_state["ofertas"] = cargar_json(OFERTAS_PATH, [])

if "cambiando_cv" not in st.session_state:
    st.session_state["cambiando_cv"] = False

if "seccion" not in st.session_state:
    st.session_state["seccion"] = "Ofertas"

aviso = st.session_state.pop("aviso", None)
if aviso:
    st.toast(aviso)

perfil = st.session_state.get("perfil")
ofertas = st.session_state["ofertas"]


# ------------------------------------------------------------------ Topbar
h1, h2 = st.columns([6, 1.4], vertical_alignment="center")
with h1:
    st.markdown(
        '<div class="top-shell"><div class="brand-box">'
        '<div class="brand-icon">JM</div>'
        '<div><div class="brand-name">JobMatcher</div>'
        '<div class="brand-tag">Revisa qué ofertas encajan de verdad con tu experiencia y tus condiciones</div></div>'
        "</div></div>",
        unsafe_allow_html=True,
    )
with h2:
    oscuro = st.toggle("Modo oscuro", value=False, key="tema_oscuro")

aplicar_tema(oscuro)


# ------------------------------------------------------------------ Subir / Cambiar CV
if perfil is None or st.session_state["cambiando_cv"]:
    es_cambio = perfil is not None
    c_izq, c_der = st.columns([1.35, 1], gap="large")

    with c_izq:
        if es_cambio:
            if st.button("← Volver atrás", key="btn_volver_atras"):
                st.session_state["cambiando_cv"] = False
                st.rerun()
            st.write("")

        st.markdown(
            '<div class="hero-heading">'
            + ("Cambiar currículum" if es_cambio else "Sube tu CV y filtra ofertas sin perder el tiempo")
            + "</div>",
            unsafe_allow_html=True,
        )
        st.markdown(
            '<p class="sub">'
            + (
                "Carga un PDF nuevo para actualizar tu perfil. Si vuelves atrás, se queda tal como está."
                if es_cambio
                else "Carga tu CV en PDF, indica qué buscas y cuánto pides, y pega ofertas para ver si valen la pena."
            )
            + "</p>",
            unsafe_allow_html=True,
        )

        with st.container(border=True):
            req_label("Currículum (PDF)")
            archivo = st.file_uploader("PDF", type=["pdf"], label_visibility="collapsed")
            limpiar = False
            if es_cambio and ofertas:
                limpiar = st.checkbox("Borrar ofertas guardadas anteriormente", value=False, key="chk_limpiar")

            if st.button("Analizar currículum", type="primary", key="btn_analizar_cv"):
                if archivo is None:
                    st.error("Sube un archivo PDF primero.")
                else:
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                        tmp.write(archivo.getvalue())
                        ruta_pdf = tmp.name
                    try:
                        with st.spinner("Leyendo tu currículum..."):
                            perfil_nuevo = extraer_perfil(ruta_pdf)
                        if es_cambio and isinstance(perfil, dict):
                            for campo in (
                                "modalidad",
                                "contrato",
                                "sueldo_minimo_bruto_anual",
                                "sectores_si",
                                "sectores_no",
                                "no_negociables",
                                "preferencias_guardadas",
                            ):
                                if campo in perfil and campo not in perfil_nuevo:
                                    perfil_nuevo[campo] = perfil[campo]
                        st.session_state["perfil"] = perfil_nuevo
                        guardar_json(PERFIL_PATH, perfil_nuevo)
                        if limpiar:
                            st.session_state["ofertas"] = []
                            guardar_json(OFERTAS_PATH, [])
                        st.session_state["cambiando_cv"] = False
                        st.session_state["seccion"] = "Mi perfil" if es_cambio else "Ofertas"
                        st.session_state["aviso"] = "Currículum actualizado" if es_cambio else "Perfil listo"
                        st.rerun()
                    except Exception as e:
                        st.error(f"No se pudo leer el PDF: {e}")
                    finally:
                        Path(ruta_pdf).unlink(missing_ok=True)

    with c_der:
        with st.container(border=True):
            st.markdown('<div class="sec-h">En dos minutos</div>', unsafe_allow_html=True)
            st.markdown(
                """
                <p class="sub"><b>1. Tu CV:</b> sacamos experiencia, puestos que encajan, habilidades e idiomas.</p>
                <p class="sub"><b>2. Tus límites:</b> sueldo mínimo, modalidad, contrato y qué prefieres evitar.</p>
                <p class="sub"><b>3. Cada oferta:</b> ves una nota de 0 a 100, qué cumples y qué se queda corto.</p>
                """,
                unsafe_allow_html=True,
            )
    st.stop()


# ------------------------------------------------------------------ Workspace principal
puestos = perfil.get("puestos_objetivo") or []
fuertes = perfil.get("habilidades_fuertes") or []
medias = perfil.get("habilidades_medias") or []
idiomas = perfil.get("idiomas") or {}
estudios = perfil.get("estudios") or []
prefs_ok = bool(perfil.get("preferencias_guardadas"))

scores_num = []
for o in ofertas:
    try:
        scores_num.append(int(o.get("puntuacion") or 0))
    except Exception:
        scores_num.append(0)
media_encaje = f"{round(sum(scores_num) / len(scores_num))}/100" if scores_num else "—"

st.markdown(
    f'<div class="kpi-grid">'
    f'<div class="kpi-card"><div class="kpi-lbl">Candidato</div><div class="kpi-val">{esc(perfil.get("nombre") or "Candidato")}</div><div class="kpi-sub">{esc(perfil.get("ubicacion") or "Sin ciudad")} · {esc(perfil.get("experiencia_anios") or 0)} años</div></div>'
    f'<div class="kpi-card"><div class="kpi-lbl">Habilidades</div><div class="kpi-val">{len(fuertes) + len(medias)}</div><div class="kpi-sub">{len(fuertes)} clave · {len(medias)} extra</div></div>'
    f'<div class="kpi-card"><div class="kpi-lbl">Ofertas</div><div class="kpi-val">{len(ofertas)}</div><div class="kpi-sub">Media: {esc(media_encaje)}</div></div>'
    f'<div class="kpi-card"><div class="kpi-lbl">Condiciones</div><div class="kpi-val"><span class="{"c-good" if prefs_ok else "c-warn"}">{"Listas" if prefs_ok else "Sin guardar"}</span></div><div class="kpi-sub">Mín. {esc(perfil.get("sueldo_minimo_bruto_anual") or 18000)} € / año</div></div>'
    f"</div>",
    unsafe_allow_html=True,
)

nav_cols = st.columns([1, 1, 1, 1.15], gap="small")
for idx, sec in enumerate(SECCIONES):
    es_activa = st.session_state["seccion"] == sec
    if nav_cols[idx].button(
        sec,
        key=f"nav_btn_{idx}",
        type="primary" if es_activa else "secondary",
        use_container_width=True,
    ):
        st.session_state["seccion"] = sec
        st.rerun()

if nav_cols[3].button("Cambiar CV", key="nav_btn_cv", use_container_width=True):
    st.session_state["cambiando_cv"] = True
    st.rerun()

st.write("")
seccion_actual = st.session_state["seccion"]


# ------------------------------------------------------------------ OFERTAS
if seccion_actual == "Ofertas":
    with st.container(border=True):
        st.markdown('<div class="sec-h">Revisar una oferta</div>', unsafe_allow_html=True)
        st.markdown(
            '<p class="sub">Pega aquí la oferta completa para ver cómo encaja contigo.</p>',
            unsafe_allow_html=True,
        )
        if not prefs_ok:
            st.warning("Todavía no has guardado tus condiciones laborales. Puedes analizar ofertas igual, aunque no se aplicarán tus filtros.")

        with st.form("form_oferta_nueva", clear_on_submit=True):
            req_label("Texto de la oferta")
            texto_of = st.text_area(
                "Texto de la oferta",
                height=160,
                placeholder="Copia y pega aquí la descripción del puesto, requisitos, salario o modalidad...",
                label_visibility="collapsed",
            )
            url_of = st.text_input("Enlace (opcional)", placeholder="https://...")
            enviar_of = st.form_submit_button("Analizar oferta", type="primary")

        if enviar_of:
            txt = texto_of.strip()
            if not txt:
                st.error("Falta el texto de la oferta.")
            elif len(txt) < 80:
                st.error("El texto es muy corto. Pega la descripción completa (al menos 80 caracteres).")
            else:
                try:
                    with st.spinner("Analizando oferta..."):
                        res = puntuar_oferta(perfil, txt)
                    res.update(
                        id=int(time.time() * 1000),
                        url=url_of.strip(),
                        estado="Pendiente",
                        texto=txt,
                    )
                    ofertas.insert(0, res)
                    guardar_json(OFERTAS_PATH, ofertas)
                    st.session_state["aviso"] = "Oferta guardada"
                    st.rerun()
                except Exception as err:
                    st.error(f"No se pudo analizar la oferta: {err}")

    st.write("")

    if not ofertas:
        with st.container(border=True):
            st.markdown('<div class="sec-h">Todavía no has guardado ninguna oferta</div>', unsafe_allow_html=True)
            st.markdown(
                '<p class="sub">Cuando pegues una arriba, aquí verás tu puntuación, qué cumples y qué te falta.</p>',
                unsafe_allow_html=True,
            )
    else:
        f_a, f_b, f_c = st.columns([1.4, 1.4, 1.2], vertical_alignment="center")
        filtro_est = f_a.selectbox("Estado", ["Todos"] + ESTADOS, key="f_est_v3")
        orden_est = f_b.selectbox("Ordenar", ["Mayor encaje", "Más recientes"], key="f_ord_v3")
        ocultar_d = f_c.checkbox("Ocultar descartadas", value=False, key="f_desc_v3")

        def get_pts(item) -> int:
            try:
                return int(item.get("puntuacion") or 0)
            except Exception:
                return 0

        lista_of = ofertas[:]
        if filtro_est != "Todos":
            lista_of = [x for x in lista_of if x.get("estado", "Pendiente") == filtro_est]
        if ocultar_d:
            lista_of = [x for x in lista_of if not x.get("descartada")]

        if orden_est == "Mayor encaje":
            lista_of.sort(key=get_pts, reverse=True)
        else:
            lista_of.sort(key=lambda x: x.get("id", 0), reverse=True)

        st.markdown(f'<div class="sec-h">Ofertas ({len(lista_of)} de {len(ofertas)})</div>', unsafe_allow_html=True)

        for item in lista_of:
            pts = max(0, min(100, get_pts(item)))
            iid = item["id"]
            if pts >= 75:
                c_txt, c_bg = "c-good", "bg-good"
            elif pts >= 50:
                c_txt, c_bg = "c-warn", "bg-warn"
            else:
                c_txt, c_bg = "c-bad", "bg-bad"

            with st.container(border=True):
                motivo_html = (
                    f'<div class="flag-bad">Descartada: {esc(item.get("motivo_descarte") or "no encaja con tus condiciones")}</div>'
                    if item.get("descartada")
                    else ""
                )
                st.markdown(
                    f'<div class="offer-row">'
                    f'<div><div class="offer-h">{esc(item.get("titulo") or "Puesto sin título")}</div>'
                    f'<div class="offer-co">{esc(item.get("empresa") or "Empresa sin indicar")}</div>'
                    f'<div class="offer-sum">{esc(item.get("resumen") or "")}</div>{motivo_html}</div>'
                    f'<div class="score-tile">'
                    f'<div class="score-n {c_txt}">{pts}</div>'
                    f'<div class="score-d">de 100</div>'
                    f'<div class="prog-track"><div class="prog-fill {c_bg}" style="width:{pts}%"></div></div>'
                    f"</div></div>",
                    unsafe_allow_html=True,
                )

                with st.expander("Ver detalle"):
                    col_cum, col_fal = st.columns(2)
                    cum_li = "".join(f"<li>{esc(x)}</li>" for x in item.get("cumple", [])) or "<li>Nada destacado</li>"
                    fal_li = "".join(f"<li>{esc(x)}</li>" for x in item.get("faltan", [])) or "<li>Nada relevante</li>"
                    col_cum.markdown(f"**Cumples**<ul class='sub'>{cum_li}</ul>", unsafe_allow_html=True)
                    col_fal.markdown(f"**Te falta**<ul class='sub'>{fal_li}</ul>", unsafe_allow_html=True)
                    if item.get("no_indicado"):
                        st.markdown("**No se especifica en la oferta**")
                        st.markdown(chips(item["no_indicado"]), unsafe_allow_html=True)
                    if item.get("url"):
                        st.markdown(f'[Ver oferta original]({esc(item["url"])})')

                c_s1, c_s2, _ = st.columns([1.4, 1, 3], vertical_alignment="center")
                est_act = item.get("estado", "Pendiente")
                idx_s = ESTADOS.index(est_act) if est_act in ESTADOS else 0
                est_nuevo = c_s1.selectbox(
                    "Estado",
                    ESTADOS,
                    index=idx_s,
                    key=f"sel_est_v3_{iid}",
                    label_visibility="collapsed",
                )
                if est_nuevo != est_act:
                    item["estado"] = est_nuevo
                    guardar_json(OFERTAS_PATH, ofertas)

                if c_s2.button("Eliminar", key=f"btn_del_v3_{iid}"):
                    st.session_state["ofertas"] = [x for x in ofertas if x["id"] != iid]
                    guardar_json(OFERTAS_PATH, st.session_state["ofertas"])
                    st.rerun()


# ------------------------------------------------------------------ MI PERFIL
elif seccion_actual == "Mi perfil":
    p_col1, p_col2 = st.columns([1.2, 1], gap="large")

    with p_col1:
        with st.container(border=True):
            st.markdown('<div class="sec-h">Tu perfil</div>', unsafe_allow_html=True)
            if perfil.get("resumen"):
                st.markdown(f'<p class="sub">{esc(perfil["resumen"])}</p>', unsafe_allow_html=True)
            st.markdown(
                "".join([
                    fila_perfil("Puestos objetivo", chips(puestos, fuerte=True)),
                    fila_perfil("Habilidades clave", chips(fuertes)),
                    fila_perfil("Otras habilidades", chips(medias)),
                    fila_perfil("Idiomas", chips([f"{k}: {v}" for k, v in idiomas.items()])),
                    fila_perfil(
                        "Estudios",
                        "<br>".join(esc(e) for e in estudios) if estudios else '<span class="sub">Sin datos</span>',
                    ),
                ]),
                unsafe_allow_html=True,
            )

    with p_col2:
        with st.container(border=True):
            st.markdown('<div class="sec-h">Ajustar datos</div>', unsafe_allow_html=True)
            st.markdown('<p class="sub">Los campos con <span class="req-star">*</span> son obligatorios.</p>', unsafe_allow_html=True)

            with st.form("form_perfil_v3"):
                req_label("Nombre")
                v_nombre = st.text_input("Nombre", value=perfil.get("nombre", ""), label_visibility="collapsed")

                req_label("Ciudad")
                v_ubic = st.text_input("Ciudad", value=perfil.get("ubicacion", ""), label_visibility="collapsed")

                v_exp = st.number_input(
                    "Años de experiencia",
                    min_value=0.0,
                    max_value=50.0,
                    value=float(perfil.get("experiencia_anios") or 0.0),
                    step=0.5,
                )

                req_label("Puestos objetivo (separados por comas)")
                v_puestos = st.text_input(
                    "Puestos objetivo",
                    value=", ".join(puestos),
                    placeholder="Ej. Analista de datos, Desarrollador Python",
                    label_visibility="collapsed",
                )

                v_fuertes = st.text_area("Habilidades clave (separadas por comas)", value=", ".join(fuertes), height=85)
                v_medias = st.text_area("Otras habilidades (separadas por comas)", value=", ".join(medias), height=85)

                if st.form_submit_button("Guardar cambios", type="primary"):
                    errores = []
                    if not v_nombre.strip():
                        errores.append("Escribe tu nombre.")
                    if not v_ubic.strip():
                        errores.append("Escribe tu ciudad.")
                    if not csv_lista(v_puestos):
                        errores.append("Indica al menos un puesto objetivo.")

                    if errores:
                        for err in errores:
                            st.error(err)
                    else:
                        perfil.update(
                            nombre=v_nombre.strip(),
                            ubicacion=v_ubic.strip(),
                            experiencia_anios=v_exp,
                            puestos_objetivo=csv_lista(v_puestos),
                            habilidades_fuertes=csv_lista(v_fuertes),
                            habilidades_medias=csv_lista(v_medias),
                        )
                        st.session_state["perfil"] = perfil
                        guardar_json(PERFIL_PATH, perfil)
                        st.session_state["aviso"] = "Perfil actualizado"
                        st.rerun()


# ------------------------------------------------------------------ PREFERENCIAS
elif seccion_actual == "Preferencias":
    with st.container(border=True):
        st.markdown('<div class="sec-h">Tus condiciones</div>', unsafe_allow_html=True)
        st.markdown(
            '<p class="sub">Los campos con <span class="req-star">*</span> son obligatorios.</p>',
            unsafe_allow_html=True,
        )

        with st.form("form_prefs_v3"):
            col_1, col_2 = st.columns(2, gap="large")

            with col_1:
                req_label("Modalidad")
                mods_prev = set(perfil.get("modalidad") or ["Híbrido", "Remoto"])
                mods_elegidas = []
                mc1, mc2, mc3 = st.columns(3)
                for col_m, m_op in zip((mc1, mc2, mc3), MODALIDADES):
                    if col_m.checkbox(m_op, value=(m_op in mods_prev), key=f"m_v3_{m_op}"):
                        mods_elegidas.append(m_op)

                st.write("")
                req_label("Contrato")
                conts_prev = set(perfil.get("contrato") or ["Indefinido", "Temporal"])
                conts_elegidos = []
                cc1, cc2 = st.columns(2)
                for i_c, c_op in enumerate(CONTRATOS):
                    destino = cc1 if i_c % 2 == 0 else cc2
                    if destino.checkbox(c_op, value=(c_op in conts_prev), key=f"c_v3_{c_op}"):
                        conts_elegidos.append(c_op)

                st.write("")
                sueldo_min = st.number_input(
                    "Sueldo mínimo bruto anual (€)",
                    min_value=0,
                    max_value=300000,
                    value=int(perfil.get("sueldo_minimo_bruto_anual") or 18000),
                    step=1000,
                )

            with col_2:
                s_si = st.text_input(
                    "Sectores que te interesan (separados por comas)",
                    value=", ".join(perfil.get("sectores_si") or []),
                    placeholder="Ej. Tecnología, Salud, Finanzas",
                )
                s_no = st.text_input(
                    "Sectores que evitas (separados por comas)",
                    value=", ".join(perfil.get("sectores_no") or []),
                    placeholder="Ej. Call center, Comercial a comisión",
                )
                no_neg = st.text_input(
                    "Condiciones que no aceptas (separadas por comas)",
                    value=", ".join(perfil.get("no_negociables") or []),
                    placeholder="Ej. Turnos de noche, Viajes frecuentes",
                )

            st.write("")
            if st.form_submit_button("Guardar condiciones", type="primary"):
                err_prefs = []
                if not mods_elegidas:
                    err_prefs.append("Elige al menos una modalidad.")
                if not conts_elegidos:
                    err_prefs.append("Elige al menos un tipo de contrato.")

                if err_prefs:
                    for e in err_prefs:
                        st.error(e)
                else:
                    perfil.update(
                        modalidad=mods_elegidas,
                        contrato=conts_elegidos,
                        sueldo_minimo_bruto_anual=int(sueldo_min),
                        sectores_si=csv_lista(s_si),
                        sectores_no=csv_lista(s_no),
                        no_negociables=csv_lista(no_neg),
                        preferencias_guardadas=True,
                    )
                    st.session_state["perfil"] = perfil
                    guardar_json(PERFIL_PATH, perfil)
                    st.session_state["aviso"] = "Condiciones guardadas"
                    st.rerun()