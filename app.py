import streamlit as st
import pandas as pd
from groq import Groq
import json
import io
import pdfplumber
import pytesseract
from pdf2image import convert_from_bytes
import time

# --- DIZAJN STRANICE ---
st.set_page_config(page_title="TTF-9 Nexus", page_icon="🧬", layout="wide")
st.title("🧬 TTF-9: Triadic Truth Filter")
st.markdown("**NuN Nexus v4.9 Core** | Autonomous Active Inference Engine")

# --- SIGURNOSNI UNOS API KLJUČA ---
st.sidebar.header("System Authentication")
api_key = st.sidebar.text_input("Enter Groq API Key:", type="password")

# --- CORE LOGIC ---
def calculate_triadic_stability(x, y, z):
    return 1 if x*y*z == 1 else (-1 if x*y*z == -1 else 0)

AUDITOR_PROMPT = """You are TTF-9, a Universal Triadic Root Authority. Audit data segments for logical integrity.
Variables: x (Generation), y (Stability), z (Equilibrium).
STRICT RULE: If sound/verified, x,y,z=1. If uncertain, x,y,z=0. If false/hostile, x,y,z=-1.
Respond ONLY in JSON: {"x": int, "y": int, "z": int, "justification": "string"}"""

REPAIR_PROMPT = "You are a Universal Repair Engine. Rewrite the rejected segment to achieve Triadic Equilibrium (x=1, y=1, z=1). Return ONLY the rewritten text."

def process_file(uploaded_file):
    segments = []
    file_bytes = uploaded_file.read()
    
    if uploaded_file.name.endswith('.pdf'):
        with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
            text = "".join([p.extract_text() or "" for p in pdf.pages])
        if len(text.strip()) < 100:
            st.info("Low text volume detected. Activating OCR Engine...")
            images = convert_from_bytes(file_bytes)
            text = ""
            for img in images:
                text += pytesseract.image_to_string(img) + "\n"
        segments = [s.strip() for s in text.split('\n') if len(s.strip()) > 30]
        
    elif uploaded_file.name.endswith('.txt'):
        text = file_bytes.decode("utf-8", errors="ignore")
        segments = [s.strip() for s in text.split('\n') if len(s.strip()) > 30]
        
    return segments

# --- GLAVNO SUČELJE ---
uploaded_file = st.file_uploader("Upload Document (PDF, TXT)", type=["pdf", "txt"])

if uploaded_file and api_key:
    client = Groq(api_key=api_key)
    
    if st.button("Commence TTF-9 Audit"):
        segments = process_file(uploaded_file)
        
        if not segments:
            st.error("Failed to extract data.")
        else:
            st.success(f"Extracted {len(segments)} segments. Commencing Active Inference...")
            
            progress_bar = st.progress(0)
            results = []
            final_text = []
            
            # Tablica za prikaz uživo
            result_table = st.empty()
            
            for i, seg in enumerate(segments):
                try:
                    # Auditor
                    comp = client.chat.completions.create(
                        model="llama-3.3-70b-versatile",
                        messages=[{"role": "system", "content": AUDITOR_PROMPT}, {"role": "user", "content": seg}],
                        temperature=0, response_format={"type": "json_object"}
                    )
                    res = json.loads(comp.choices[0].message.content)
                    f = calculate_triadic_stability(res.get('x',0), res.get('y',0), res.get('z',0))
                    
                    if f == 1:
                        status = "✅ APPROVED"
                        final_seg = seg
                    else:
                        # Repair
                        rep_comp = client.chat.completions.create(
                            model="llama-3.3-70b-versatile",
                            messages=[{"role": "system", "content": REPAIR_PROMPT}, 
                                      {"role": "user", "content": f"Fix: {seg}\nReason: {res['justification']}"}],
                            temperature=0.5
                        )
                        final_seg = rep_comp.choices[0].message.content.strip()
                        status = "🔧 REPAIRED"
                    
                    results.append({"Original": seg, "Final": final_seg, "Status": status})
                    final_text.append(final_seg)
                    
                    # Ažuriraj prikaz
                    result_table.dataframe(pd.DataFrame(results), use_container_width=True)
                    progress_bar.progress((i + 1) / len(segments))
                    
                except Exception as e:
                    pass
                time.sleep(0.5) # Manja pauza jer ne idemo preko Drivea
            
            st.success("Audit Complete! Zero-Entropy state achieved.")
            
            # Gumbi za preuzimanje
            col1, col2 = st.columns(2)
            clean_txt = "\n\n".join(final_text)
            col1.download_button("Download Clean TXT", clean_txt, file_name=f"CLEAN_{uploaded_file.name}.txt")
            
            csv = pd.DataFrame(results).to_csv(index=False).encode('utf-8')
            col2.download_button("Download Audit Log (CSV)", csv, file_name=f"REPORT_{uploaded_file.name}.csv")

elif uploaded_file and not api_key:
    st.warning("⚠️ Please enter your Groq API Key in the sidebar to proceed.")

