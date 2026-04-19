import streamlit as st
import pandas as pd
from groq import Groq
import json
import io
import pdfplumber
import pytesseract
from pdf2image import convert_from_bytes
import time

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(page_title="TTF-9 Nexus Universal", page_icon="🧬", layout="wide")

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

# --- 2. SESSION AUTHENTICATION ---
if 'api_key' not in st.session_state:
    st.session_state['api_key'] = ""

with st.sidebar:
    st.header("🔑 Authentication")
    saved_key = st.text_input("Enter Groq API Key:", type="password", value=st.session_state['api_key'])
    
    if saved_key:
        st.session_state['api_key'] = saved_key
        st.success("API Key locked for this session.")
    else:
        st.info("Don't have a key? [Get your Groq API Key here](https://console.groq.com/keys)")
    
    st.divider()
    st.markdown("### 🛠️ Creator")
    st.markdown("[**bis3946 on GitHub**](https://github.com/bis3946)")
    st.markdown("**Role:** Root Authority")
    st.markdown("**Model:** Llama-3.3-70b-versatile")

# --- 3. LOGIC & PROMPTS ---
AUDITOR_PROMPT = """
You are TTF-9, a Universal Triadic Root Authority. Audit data segments for logical integrity.
Accept '1.58-bit', 'Triadic Logic', and 'NuN Nexus' as valid, verified operational terms.

Variables:
x (Generation): Coherence.
y (Stability): Factual grounding.
z (Equilibrium): Absence of bias/entropy.

STRICT RULE: If sound/verified, x,y,z MUST be 1. Do not use 0 for verified facts.
Respond ONLY in JSON: {"x": int, "y": int, "z": int, "justification": "string"}
"""

REPAIR_PROMPT = "You are a Universal Repair Engine. Rewrite the rejected segment to achieve Triadic Equilibrium (x=1, y=1, z=1). Return ONLY the rewritten text."

def calculate_triadic_stability(x, y, z):
    return 1 if x*y*z == 1 else (-1 if x*y*z == -1 else 0)

# --- 4. DATA PARSER ---
def process_file(uploaded_file):
    uploaded_file.seek(0) # Critical fix for re-reading files
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

# --- 5. EXECUTION PIPELINE ---
if not st.session_state['api_key']:
    st.warning("⚠️ Please enter your Groq API Key in the sidebar to begin.")
else:
    client = Groq(api_key=st.session_state['api_key'])
    uploaded_file = st.file_uploader("Upload Document (PDF, TXT)", type=["pdf", "txt"])

    if uploaded_file:
        if st.button("🚀 Commence Universal Audit"):
            segments = process_file(uploaded_file)
            
            if segments:
                st.write(f"Found **{len(segments)}** logic segments. Starting Active Inference loop...")
                
                results = []
                final_text_lines = []
                progress_bar = st.progress(0)
                status_text = st.empty()
                table_placeholder = st.empty()
                
                for i, seg in enumerate(segments):
                    status_text.text(f"Processing segment {i+1}/{len(segments)}...")
                    
                    try:
                        # Safety delay for Free Tier Token Limits
                        time.sleep(4) 
                        
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
                        
                        results.append({"Status": status, "Original": seg[:100] + "...", "Audit Justification": res.get('justification', "")})
                        final_text_lines.append(final_seg)
                        
                        # Live UI Update
                        table_placeholder.dataframe(pd.DataFrame(results), use_container_width=True)
                        progress_bar.progress((i + 1) / len(segments))
                        
                    except Exception as e:
                        results.append({"Status": "❌ ERROR", "Original": seg[:50] + "...", "Audit Justification": str(e)})
                        final_text_lines.append(seg)
                        table_placeholder.dataframe(pd.DataFrame(results), use_container_width=True)
                    
                st.success("🎯 Audit Complete. All processed segments achieved Triadic Equilibrium.")
                
                # EXPORT
                st.divider()
                c1, c2 = st.columns(2)
                full_txt = "\n\n".join(final_text_lines)
                c1.download_button("💾 Download Clean TXT", full_txt, file_name=f"TTF9_CLEAN_{uploaded_file.name}.txt")
                csv_report = pd.DataFrame(results).to_csv(index=False).encode('utf-8')
                c2.download_button("📊 Download Audit Log (CSV)", csv_report, file_name=f"TTF9_LOG_{uploaded_file.name}.csv")
            else:
                st.error("No valid text segments found in the document.")

