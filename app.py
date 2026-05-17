import streamlit as st

st.set_page_config(
    page_title="CareerFlow",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded",
)

# CSS
st.markdown("""<style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display&family=DM+Sans:wght@300;400;500;600&display=swap');

    html, body, [class*="css"] {
        font-family: 'DM Sans', sans-serif;
    }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background: #0f1117;
        border-right: 1px solid #1e2130;
    }
    [data-testid="stSidebar"] * {
        color: #e0e0e0 !important;
    }

    /* Sidebar content: layout colonna con branding sempre in cima */
    [data-testid="stSidebar"] > div:first-child {
        display: flex;
        flex-direction: column;
    }

    /* Il blocco nav (stSidebarNav) va dopo il branding */
    [data-testid="stSidebarNav"] {
        order: 2;
    }

    /* Il div col branding (primo elemento stBlock) va sopra */
    [data-testid="stSidebar"] .stMarkdown:first-of-type {
        order: 1;
    }

    /* Nav links attivi */
    [data-testid="stSidebarNavLink"][aria-current="page"] {
        background: #1e2130 !important;
        border-left: 3px solid #4f8ef7 !important;
        border-radius: 0 8px 8px 0;
    }

    /* Titolo sidebar */
    .sidebar-title {
        font-family: 'DM Serif Display', serif;
        font-size: 1.6rem;
        color: #4f8ef7 !important;
        padding: 1.2rem 1rem 0.5rem;
        letter-spacing: -0.5px;
    }
    .sidebar-sub {
        font-size: 0.72rem;
        color: #555 !important;
        padding: 0 1rem 1.5rem;
        text-transform: uppercase;
        letter-spacing: 1.5px;
    }

    /* Metriche */
    [data-testid="metric-container"] {
        background: #1a1d27;
        border: 1px solid #1e2130;
        border-radius: 12px;
        padding: 1rem 1.2rem;
    }
    [data-testid="metric-container"] label {
        font-size: 0.75rem !important;
        text-transform: uppercase;
        letter-spacing: 1px;
        color: #666 !important;
    }

    /* Bottoni primari */
    .stButton > button[kind="primary"] {
        background: #4f8ef7;
        border: none;
        border-radius: 8px;
        font-weight: 600;
        letter-spacing: 0.3px;
    }
    .stButton > button[kind="primary"]:hover {
        background: #3a7de0;
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(79,142,247,0.3);
    }

    /* Dataframe */
    [data-testid="stDataFrame"] {
        border: 1px solid #1e2130;
        border-radius: 10px;
        overflow: hidden;
    }

    /* Badge stato */
    .stato-badge {
        display: inline-block;
        padding: 2px 10px;
        border-radius: 20px;
        font-size: 0.72rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.8px;
    }
    .stato-inviata    { background: #1e3a5f; color: #7cb9ff; }
    .stato-ricevuta   { background: #1a3a2a; color: #5dba7d; }
    .stato-pending    { background: #3a2e10; color: #f0b429; }
    .stato-sollecito  { background: #3a1a10; color: #f87c52; }
    .stato-rifiutata  { background: #2a1a1a; color: #e05c5c; }
</style>""", unsafe_allow_html=True)

pages = {
    "Panoramica": [
        st.Page("pages/dashboard.py", title="Dashboard", icon="📊"),
    ],
    "Gestione": [
        st.Page("pages/candidature.py", title="Candidature", icon="📨"),
        st.Page("pages/aziende.py",     title="Aziende",     icon="🏢"),
        st.Page("pages/contatti.py",    title="Contatti",    icon="👤"),
    ],
}
pg = st.navigation(pages)


st.sidebar.markdown(
    '<div class="sidebar-title">🎯 CareerFlow</div>'
    '<div class="sidebar-sub">Job Application Tracker</div>'
    "<hr>",
    unsafe_allow_html=True,
)

pg.run()
