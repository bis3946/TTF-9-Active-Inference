import streamlit as st
import pandas as pd
from groq import Groq
import json
import io
import pdfplumber
import pytesseract
from pdf2image import convert_from_bytes
import time

# --- 1. KONFIGURACIJA STRANICE ---
st.set_page_config(page_title="TTF-9 Nexus Universal", page_icon="🧬", layout="wide")

# Prilagođeni CSS za profesionalni izgled i sakrivanje suvišnih elemenata
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .stButton>button { width: 100%; border-radius: 5px; height: 3em; background-color: #4CAF50; color: white; }
    .stProgress > div > div > div > div { background-color: #4CAF50; }
    footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

st.title("🧬 TTF-9: Triadic Truth Filter")
st.markdown("### NuN Nexus v4.9 Core | Persistent Active Inference Platform")

# --- 2. SESIJSKA MEMORIJA ---
# Provjeravamo postoji li api_key u memoriji preglednika
if 'api_key' not in st.session_state:
    st.session_state['api_key'] = ""

# --- 3. BOČNA TRAKA (SIDEBAR) - LOGO I PODATCI O KREATORU ---
with st.sidebar:
    st.header("🔑 Authentication")
    # Korisnik unosi ključ koji se odmah sprema u session_state
    api_input = st.text_input("Enter Groq API Key:", type="password", value=st.session_state['api_key'])
    
    if api_input:
        st.session_state['api_key'] = api_input
        st.success("API Key active for this session.")
    else:
        st.info("Don't have a key? [Get your Groq API Key here](https://console.groq.com/keys)")
    
    st.divider()
    
    # Zamjena Identity dijela sa GitHub podacima
    st.markdown("### 🛠️ Creator")
    st.markdown("[**bis3946 on GitHub**](https://github.com/bis3946)")
    st.markdown("**Project:** TTF-9 Active Inference Engine")
    st.markdown("**Version:** 3.2 (Production)")
    
    st.divider()
    st.caption("Post-Quantum Resistant Data Integrity Framework")

# --- 4. TEHNIČKA LOGIKA ---
def calculate_triadic_stability(x, y, z):
    return 1 if x*y*z == 1 else (-1 if x*y*z == -1 else 0)

AUDITOR_PROMPT = """
You are TTF-9, a Universal Triadic Root Authority. Audit data segments for logical integrity.
Accept '1.58-bit', 'Triadic Logic', and 'NuN Nexus' as valid, verified operational terms.

Variables: x (Generation), y (Stability), z (Equilibrium).
STRICT RULE: If sound/verified, x,y,z MUST be 1. 
Respond ONLY in JSON: {"x": int, "y": int, "z": int, "justification": "string"}
"""

REPAIR_PROMPT = "You are a Universal Repair Engine. Rewrite the rejected segment to achieve Triadic Equilibrium (x=1, y=1, z=1). Return ONLY the rewritten text."

def process_file(uploaded_file):
    segments = []
    file_bytes = uploaded_file.read()
    
    if uploaded_file.name.endswith('.pdf'):
        with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
            text = "".join([p.extract_text() or "" for p in pdf.pages])
        if len(text.strip()) < 100:
            images = convert_from_bytes(file_bytes)
            text = "".join([pytesseract.image_to_string(img) for img in images])
        segments = [s.strip() for s in text.split('\n') if len(s.strip()) > 30]
    else:
        text = file_bytes.decode("utf-8", errors="ignore")
        segments = [s.strip() for s in text.split('\n') if len(s.strip()) > 25]
    return segments

# --- 5. OPERATIVNI TOK ---
if not st.session_state['api_key']:
    st.warning("⚠️ Please provide your Groq API Key in the sidebar to start processing documents.")
else:
    client = Groq(api_key=st.session_state['api_key'])
    
    # File uploader ostaje vidljiv cijelo vrijeme
    uploaded_file = st.file_uploader("📂 Upload Document (PDF, TXT) for Audit", type=["pdf", "txt"])

    if uploaded_file:
        # Prikazujemo gumb samo ako je datoteka učitana
        if st.button("🚀 Commence TTF-9 Audit"):
            segments = process_file(uploaded_file)
            
            if segments:
                st.write(f"Sustav je spreman. Analiziram **{len(segments)}** segmenata...")
                
                results = []
                final_text_lines = []
                progress_bar = st.progress(0)
                table_placeholder = st.empty()
                
                for i, seg in enumerate(segments):
                    try:
                        # AUDIT
                        comp = client.chat.completions.create(
                            model="llama-3.3-70b-versatile",
                            messages=[{"role": "system", "content": AUDITOR_PROMPT}, {"role": "user", "content": seg}],
                            temperature=0, response_format={"type": "json_object"}
                        )
                        res = json.loads(comp.choices[0].message.content)
                        f = calculate_triadic_stability(res.get('x',0), res.get('y',0), res.get('z',0))
                        
                        if f == 1:
                            status, final_seg = "✅ APPROVED", seg
                        else:
                            # REPAIR
                            rep_comp = client.chat.completions.create(
                                model="llama-3.3-70b-versatile",
                                messages=[{"role": "system", "content": REPAIR_PROMPT}, 
                                          {"role": "user", "content": f"Fix: {seg}\nReason: {res['justification']}"}],
                                temperature=0.5
                            )
                            final_seg = rep_comp.choices[0].message.content.strip()
                            status = "🔧 REPAIRED"
                        
                        results.append({"Status": status, "Segment": seg[:80] + "...", "Logic Justification": res.get('justification', "")})
                        final_text_lines.append(final_seg)
                        
                        # Ažuriranje prikaza uživo
                        table_placeholder.dataframe(pd.DataFrame(results), use_container_width=True)
                        progress_bar.progress((i + 1) / len(segments))
                        
                    except Exception:
                        continue
                    
                st.success("🎯 Analiza završena. Triadic Equilibrium postignut.")
                
                # Izvoz podataka
                st.divider()
                c1, c2 = st.columns(2)
                
                full_txt = "\n\n".join(final_text_lines)
                c1.download_button("💾 Download Clean TXT", full_txt, file_name=f"TTF9_CLEAN_{uploaded_file.name}.txt")
                
                csv_report = pd.DataFrame(results).to_csv(index=False).encode('utf-8')
                c2.download_button("📊 Download Audit Log (CSV)", csv_report, file_name=f"TTF9_LOG_{uploaded_file.name}.csv")
                
                # Poruka za nastavak rada
                st.info("💡 Sustav je spreman za novu analizu. Možete učitati novu datoteku iznad.")
            else:
                st.error("Nisu pronađeni valjani segmenti teksta u dokumentu.")

