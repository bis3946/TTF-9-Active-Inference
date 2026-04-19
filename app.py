import streamlit as st
import pandas as pd
from groq import Groq
import json
import io
import pdfplumber
import pytesseract
from pdf2image import convert_from_bytes
import time

# --- 1. CONFIGURATION ---
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
st.markdown("### NuN Nexus v4.9 Core | Autonomous Active Inference Engine")

# --- 2. AUTHENTICATION ---
if 'api_key' not in st.session_state:
    st.session_state['api_key'] = ""

with st.sidebar:
    st.header("🔑 Authentication")
    saved_key = st.text_input("Enter Groq API Key:", type="password", value=st.session_state['api_key'])
    
    if saved_key:
        st.session_state['api_key'] = saved_key
        st.success("API Key locked for this session.")
    
    st.divider()
    st.markdown("### 🛠️ Creator")
    st.markdown("[**bis3946 on GitHub**](https://github.com/bis3946)")
    st.markdown("**Role:** Root Authority")
    st.markdown("**Version:** 4.1 (Token Protector)")

# --- 3. TRIADIC LOGIC & PROMPTS ---
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

# --- 4. SAFE API CALLER (AUTO-RETRY) ---
def call_api_with_retry(client, messages, temp=0, resp_format=None, status_ui=None):
    max_retries = 3
    for attempt in range(max_retries):
        try:
            kwargs = {"model": "llama-3.3-70b-versatile", "messages": messages, "temperature": temp}
            if resp_format:
                kwargs["response_format"] = resp_format
            return client.chat.completions.create(**kwargs)
        except Exception as e:
            if "429" in str(e) or "rate limit" in str(e).lower():
                wait_time = 15 # Dajemo serveru 15 sekundi da obnovi tokene
                if status_ui:
                    status_ui.warning(f"⚠️ Token limit reached (429). Cooling down for {wait_time} seconds before retry...")
                time.sleep(wait_time)
                if attempt == max_retries - 1:
                    raise Exception("Max retries exceeded due to severe server limits.")
            else:
                raise e

# --- 5. ROBUST PARSER ---
def process_file(uploaded_file):
    uploaded_file.seek(0)
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

# --- 6. MAIN APPLICATION LOOP ---
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
                    status_text.info(f"Processing segment {i+1}/{len(segments)}...")
                    
                    try:
                        # Osnovna pauza od 4 sekunde (štedi tokene u startu)
                        time.sleep(4) 
                        
                        # AUDIT
                        comp = call_api_with_retry(client, [{"role": "system", "content": AUDITOR_PROMPT}, {"role": "user", "content": seg}], temp=0, resp_format={"type": "json_object"}, status_ui=status_text)
                        res = json.loads(comp.choices[0].message.content)
                        f = calculate_triadic_stability(res.get('x',0), res.get('y',0), res.get('z',0))
                        
                        if f == 1:
                            status, final_seg = "✅ APPROVED", seg
                        else:
                            status_text.info(f"Repairing segment {i+1}/{len(segments)}...")
                            time.sleep(2) # Mikro pauza prije popravka
                            
                            # REPAIR
                            rep_comp = call_api_with_retry(client, [{"role": "system", "content": REPAIR_PROMPT}, {"role": "user", "content": f"Fix: {seg}\nReason: {res['justification']}"}], temp=0.5, status_ui=status_text)
                            final_seg = rep_comp.choices[0].message.content.strip()
                            status = "🔧 REPAIRED"
                        
                        results.append({"Status": status, "Original": seg[:80] + "...", "Audit Justification": res.get('justification', "")})
                        final_text_lines.append(final_seg)
                        
                        # Live Update
                        table_placeholder.dataframe(pd.DataFrame(results), use_container_width=True)
                        progress_bar.progress((i + 1) / len(segments))
                        
                    except Exception as e:
                        results.append({"Status": "❌ ERROR", "Original": seg[:50] + "...", "Audit Justification": str(e)})
                        final_text_lines.append(seg)
                        table_placeholder.dataframe(pd.DataFrame(results), use_container_width=True)
                    
                status_text.success("🎯 Audit Complete. All processed segments achieved Triadic Equilibrium.")
                
                # EXPORT SECTION
                st.divider()
                c1, c2 = st.columns(2)
                
                full_txt = "\n\n".join(final_text_lines)
                c1.download_button("💾 Download Clean TXT", full_txt, file_name=f"TTF9_CLEAN_{uploaded_file.name}.txt")
                
                csv_report = pd.DataFrame(results).to_csv(index=False).encode('utf-8')
                c2.download_button("📊 Download Audit Log (CSV)", csv_report, file_name=f"TTF9_LOG_{uploaded_file.name}.csv")
            else:
                st.error("No valid text segments found in the document.")

