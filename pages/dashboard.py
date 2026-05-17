import streamlit as st
import pandas as pd
from database import AziendeManager, ContattiManager, CandidatureManager

# -------------------------------------------------------------------
# Avanza stati automatici
# -------------------------------------------------------------------
if "stati_avanzati" not in st.session_state:
    risultati = CandidatureManager.avanza_stati()
    st.session_state["stati_avanzati"] = risultati
    totale = sum(risultati.values())
    if totale > 0:
        st.toast(
            f"🔄 {totale} candidature aggiornate automaticamente", icon="✅")

# -------------------------------------------------------------------
# Dati
# -------------------------------------------------------------------
candidature = CandidatureManager.read_all()
aziende = AziendeManager.read_all()
contatti = ContattiManager.read_all()

df = pd.DataFrame([dict(r) for r in candidature]
                  ) if candidature else pd.DataFrame()

# -------------------------------------------------------------------
# Header
# -------------------------------------------------------------------
st.markdown("## 📊 Dashboard")
st.caption("Panoramica delle tue candidature in corso")
st.divider()


# -------------------------------------------------------------------
# Metriche principali
# -------------------------------------------------------------------
col1, col2, col3, col4, col5 = st.columns(5)

totale_cand = len(df)
attive = len(df[df['stato'].isin(
    ["inviata", "ricevuta", "pending", "sollecito"])]) if not df.empty else 0
solleciti = len(df[df["stato"] == "sollecito"]) if not df.empty else 0
rifiutate = len(df[df["stato"] == "rifiutata"]) if not df.empty else 0
tot_aziende = len(aziende)

col1.metric("Candidature totali",  totale_cand)
col2.metric("Ancora attive",       attive)
col3.metric("Da sollecitare",      solleciti,
            delta=None if solleciti == 0 else f"⚠️ {solleciti}")
col4.metric("Rifiutate",           rifiutate)
col5.metric("Aziende tracciate",   tot_aziende)

st.divider()
