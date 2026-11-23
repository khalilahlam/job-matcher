import streamlit as st

TEMAS = {
    "claro": {
        "bg": "#F4F5F7",
        "panel": "#FFFFFF",
        "panel_2": "#F8FAFC",
        "field": "#FFFFFF",
        "ink": "#18181B",
        "ink_2": "#52525B",
        "border": "#D4D4D8",
        "brand": "#0F766E",
        "brand_hover": "#115E59",
        "on_brand": "#FFFFFF",
        "soft": "#F0FDFA",
        "soft_border": "#99F6E4",
        "good": "#15803D",
        "warn": "#B45309",
        "bad": "#B91C1C",
    },
    "oscuro": {
        "bg": "#0D1015",
        "panel": "#151921",
        "panel_2": "#1C222D",
        "field": "#232A38",
        "ink": "#F4F4F5",
        "ink_2": "#A1A1AA",
        "border": "#2E3748",
        "brand": "#2DD4BF",
        "brand_hover": "#14B8A6",
        "on_brand": "#062825",
        "soft": "#132A29",
        "soft_border": "#1F4B47",
        "good": "#4ADE80",
        "warn": "#FBBF24",
        "bad": "#F87171",
    },
}

CSS_BASE = """
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&display=swap');

*, *::before, *::after {
    box-sizing: border-box;
}

@keyframes jmFadeUp {
    from {
        opacity: 0;
        transform: translateY(6px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

html, body, .stApp, button, input, textarea, select {
    font-family: 'DM Sans', system-ui, -apple-system, sans-serif !important;
}

.stApp {
    background-color: var(--bg) !important;
    color: var(--ink) !important;
    overflow-x: hidden;
    transition: background-color 0.22s ease, color 0.22s ease;
}

header[data-testid="stHeader"],
[data-testid="stSidebar"],
[data-testid="stSidebarCollapsedControl"],
[data-testid="collapsedControl"],
[data-testid="InputInstructions"] {
    display: none !important;
}

.block-container {
    max-width: 1180px !important;
    padding: 1rem 1.25rem 3.5rem !important;
    margin: 0 auto !important;
    animation: jmFadeUp 0.24s ease-out both;
}

/* Cabecera */
.top-shell {
    background: var(--panel);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 0.8rem 1.15rem;
    margin-bottom: 1rem;
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 1rem;
    min-width: 0;
    transition: background-color 0.22s ease, border-color 0.22s ease;
}

.brand-box {
    display: flex;
    align-items: center;
    gap: 0.7rem;
    min-width: 0;
}

.brand-icon {
    width: 34px;
    height: 34px;
    border-radius: 8px;
    background: var(--brand);
    color: var(--on_brand) !important;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 700;
    font-size: 0.9rem;
    flex-shrink: 0;
    transition: transform 0.2s ease, background-color 0.22s ease;
}

.top-shell:hover .brand-icon {
    transform: scale(1.03);
}

.brand-name {
    font-size: 1.1rem;
    font-weight: 700;
    color: var(--ink) !important;
    line-height: 1.2;
}

.brand-tag {
    font-size: 0.8rem;
    color: var(--ink_2) !important;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

/* Métricas */
.kpi-grid {
    display: grid;
    grid-template-columns: repeat(4, minmax(0, 1fr));
    gap: 0.75rem;
    margin-bottom: 1.1rem;
}

.kpi-card {
    background: var(--panel);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 0.85rem 1rem;
    min-width: 0;
    animation: jmFadeUp 0.26s ease-out both;
    transition: transform 0.18s ease, border-color 0.18s ease, background-color 0.22s ease;
}

.kpi-card:hover {
    transform: translateY(-2px);
    border-color: var(--brand);
}

.kpi-lbl {
    font-size: 0.74rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.04em;
    color: var(--ink_2) !important;
}

.kpi-val {
    font-size: 1.25rem;
    font-weight: 700;
    color: var(--ink) !important;
    margin-top: 0.2rem;
    line-height: 1.2;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}

.kpi-sub {
    font-size: 0.78rem;
    color: var(--ink_2) !important;
    margin-top: 0.2rem;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}

/* Tarjetas */
[data-testid="stVerticalBlockBorderWrapper"] {
    background-color: var(--panel) !important;
    border: 1px solid var(--border) !important;
    border-radius: 12px !important;
    animation: jmFadeUp 0.25s ease-out both;
    transition: border-color 0.18s ease, background-color 0.22s ease, box-shadow 0.18s ease;
}

[data-testid="stVerticalBlockBorderWrapper"]:hover {
    border-color: var(--border);
}

[data-testid="stForm"] {
    border: 0 !important;
    padding: 0 !important;
}

.stApp p, .stApp label, .stApp span, .stApp div, .stApp li {
    color: var(--ink);
}

.sub {
    color: var(--ink_2) !important;
    font-size: 0.9rem;
    line-height: 1.5;
}

.sec-h {
    font-size: 1.05rem;
    font-weight: 700;
    color: var(--ink) !important;
    margin: 0 0 0.25rem;
}

.req-star {
    color: var(--bad) !important;
    font-weight: 700;
    margin-left: 3px;
}

/* Chips */
.pill {
    display: inline-block;
    background: var(--soft);
    border: 1px solid var(--soft_border);
    color: var(--ink) !important;
    padding: 0.2rem 0.6rem;
    border-radius: 6px;
    font-size: 0.8rem;
    font-weight: 500;
    margin: 0 0.3rem 0.3rem 0;
    transition: transform 0.15s ease, border-color 0.15s ease;
}

.pill:hover {
    transform: translateY(-1px);
    border-color: var(--brand);
}

.pill-accent {
    border-color: var(--brand);
    font-weight: 600;
}

/* Filas perfil */
.profile-row {
    display: grid;
    grid-template-columns: 160px minmax(0, 1fr);
    gap: 0.85rem;
    padding: 0.75rem 0;
    border-top: 1px solid var(--border);
}

.profile-row:first-child {
    border-top: 0;
    padding-top: 0.1rem;
}

.profile-k {
    font-size: 0.86rem;
    font-weight: 600;
    color: var(--ink_2) !important;
}

/* Ofertas */
.offer-row {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    gap: 1.15rem;
}

.offer-h {
    font-size: 1.08rem;
    font-weight: 700;
    color: var(--ink) !important;
}

.offer-co {
    font-size: 0.88rem;
    font-weight: 600;
    color: var(--brand) !important;
    margin: 0.15rem 0 0.45rem;
}

.offer-sum {
    font-size: 0.9rem;
    color: var(--ink_2) !important;
    line-height: 1.5;
    max-width: 680px;
}

.score-tile {
    min-width: 84px;
    background: var(--panel_2);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 0.6rem 0.75rem;
    text-align: center;
    flex-shrink: 0;
    transition: transform 0.18s ease, border-color 0.18s ease;
}

.score-tile:hover {
    transform: translateY(-1px);
    border-color: var(--brand);
}

.score-n {
    font-size: 1.55rem;
    font-weight: 700;
    line-height: 1.1;
}

.score-d {
    font-size: 0.74rem;
    color: var(--ink_2) !important;
}

.c-good { color: var(--good) !important; }
.c-warn { color: var(--warn) !important; }
.c-bad { color: var(--bad) !important; }

.prog-track {
    height: 4px;
    background: var(--border);
    border-radius: 999px;
    margin-top: 0.45rem;
    overflow: hidden;
}

.prog-fill {
    height: 100%;
    border-radius: 999px;
    transition: width 0.45s cubic-bezier(0.22, 1, 0.36, 1);
}

.bg-good { background: var(--good); }
.bg-warn { background: var(--warn); }
.bg-bad { background: var(--bad); }

.flag-bad {
    margin-top: 0.55rem;
    padding: 0.35rem 0.65rem;
    border-radius: 6px;
    font-size: 0.82rem;
    font-weight: 600;
    color: var(--bad) !important;
    background: var(--panel_2);
    border: 1px solid var(--border);
    display: inline-block;
}

/* Inputs y textareas */
[data-baseweb="input"],
[data-baseweb="input"] > div,
[data-baseweb="base-input"],
[data-baseweb="textarea"],
[data-baseweb="textarea"] > div,
[data-testid="stNumberInputContainer"],
[data-testid="stNumberInput"] > div > div {
    background-color: var(--field) !important;
    color: var(--ink) !important;
    border-radius: 8px !important;
    transition: border-color 0.18s ease, box-shadow 0.18s ease, background-color 0.22s ease;
}

[data-baseweb="input"] > div,
[data-baseweb="textarea"] > div {
    border: 1px solid var(--border) !important;
}

[data-baseweb="input"] > div:focus-within,
[data-baseweb="textarea"] > div:focus-within {
    border-color: var(--brand) !important;
    box-shadow: 0 0 0 2px rgba(45, 212, 191, 0.16);
}

input,
textarea,
[data-baseweb="input"] input,
[data-baseweb="textarea"] textarea {
    background-color: var(--field) !important;
    color: var(--ink) !important;
    -webkit-text-fill-color: var(--ink) !important;
    caret-color: var(--ink) !important;
    font-size: 0.92rem !important;
}

input::placeholder,
textarea::placeholder {
    color: var(--ink_2) !important;
    -webkit-text-fill-color: var(--ink_2) !important;
    opacity: 0.85 !important;
}

[data-testid="stNumberInput"] button {
    background-color: var(--panel_2) !important;
    color: var(--ink) !important;
    transition: background-color 0.15s ease, color 0.15s ease;
}

[data-testid="stFileUploaderDropzone"] {
    background-color: var(--panel_2) !important;
    border: 1.5px dashed var(--border) !important;
    border-radius: 10px !important;
    transition: border-color 0.18s ease, background-color 0.18s ease;
}

[data-testid="stFileUploaderDropzone"]:hover {
    border-color: var(--brand) !important;
}

/* Botones */
.stButton > button,
.stFormSubmitButton > button,
.stDownloadButton > button {
    border-radius: 8px !important;
    font-weight: 600 !important;
    font-size: 0.88rem !important;
    background: var(--panel_2) !important;
    color: var(--ink) !important;
    -webkit-text-fill-color: var(--ink) !important;
    border: 1px solid var(--border) !important;
    white-space: nowrap !important;
    transition: transform 0.14s ease, background-color 0.18s ease, border-color 0.18s ease, color 0.18s ease !important;
}

.stButton > button:hover,
.stFormSubmitButton > button:hover,
.stDownloadButton > button:hover {
    transform: translateY(-1px);
    border-color: var(--brand) !important;
    color: var(--brand) !important;
    -webkit-text-fill-color: var(--brand) !important;
}

.stButton > button:active,
.stFormSubmitButton > button:active,
.stDownloadButton > button:active {
    transform: translateY(0);
}

button[kind="primary"],
button[data-testid="stBaseButton-primary"],
button[data-testid="stBaseButton-primaryFormSubmit"] {
    background: var(--brand) !important;
    border-color: var(--brand) !important;
    color: var(--on_brand) !important;
    -webkit-text-fill-color: var(--on_brand) !important;
}

button[kind="primary"] *,
button[data-testid="stBaseButton-primary"] *,
button[data-testid="stBaseButton-primaryFormSubmit"] * {
    color: var(--on_brand) !important;
    -webkit-text-fill-color: var(--on_brand) !important;
}

button[kind="primary"]:hover,
button[data-testid="stBaseButton-primary"]:hover,
button[data-testid="stBaseButton-primaryFormSubmit"]:hover {
    background: var(--brand_hover) !important;
    border-color: var(--brand_hover) !important;
}

.hero-heading {
    font-size: 1.85rem;
    font-weight: 700;
    letter-spacing: -0.02em;
    line-height: 1.2;
    color: var(--ink) !important;
    margin-bottom: 0.5rem;
}

@media (prefers-reduced-motion: reduce) {
    *, *::before, *::after {
        animation: none !important;
        transition: none !important;
    }
}

@media (max-width: 960px) {
    .kpi-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
}

@media (max-width: 640px) {
    .block-container { padding: 0.75rem 0.85rem 3.5rem !important; }
    .kpi-grid { grid-template-columns: 1fr; }
    .profile-row { grid-template-columns: 1fr; gap: 0.25rem; }
    .offer-row { flex-direction: column; }
    .score-tile { width: 100%; text-align: left; }
    .brand-tag { display: none; }
}
"""


def aplicar_tema(oscuro: bool) -> None:
    t = TEMAS["oscuro" if oscuro else "claro"]
    vars_css = (
        ":root{color-scheme:"
        + ("dark" if oscuro else "light")
        + ";"
        + "".join(f"--{k}:{v};" for k, v in t.items())
        + "}"
    )
    st.markdown(f"<style>{vars_css}{CSS_BASE}</style>", unsafe_allow_html=True)