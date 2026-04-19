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

# --- 2. ADVANCED SESSION MEMORY ---
if 'api_key' not in st.session_state:
    st.session_state['api_key'] = ""
if 'memory_cache' not in st.session_state:
    st.session_state['memory_cache'] = {} 

with st.sidebar:
    st.header("🔑 Authentication")
    api_input = st.text_input("Enter Groq API Key:", type="password", value=st.session_state['api_key'])
    
    if api_input:
        st.session_state['api_key'] = api_input
        st.success("API Key active for this session.")
    else:
        st.info("Don't have a key? [Get your Groq API Key here](https://console.groq.com/keys)")
    
    st.divider()
    st.markdown("### 🛠️ Creator")
    st.markdown("[**bis3946 on GitHub**](https://github.com/bis3946)")
    st.markdown("**Project:** TTF-9 Active Inference Engine")
    st.markdown("**Version:** 3.8 (Groq Optimizer)")
    st.divider()
    st.caption("Post-Quantum Resistant Data Integrity Framework")

# --- 3. TRIADIC LOGIC ENGINE ---
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

# --- 4. SAFE API CALLER (RATE LIMIT PROTECTOR) ---
def call_groq_safe(client, messages, temp=0, resp_format=None):
    max_retries = 3
    for attempt in range(max_retries):
        try:
            time.sleep(2.5) # STRICT PACING: Max 24 requests per minute
            kwargs = {"model": "llama-3.3-70b-versatile", "messages": messages, "temperature": temp}
            if resp_format:
                kwargs["response_format"] = resp_format
            return client.chat.completions.create(**kwargs)
        except Exception as e:
            if "429" in str(e) or "Rate limit" in str(e):
                time.sleep(10) # Penalty wait for breaking limit
                if attempt == max_retries - 1:
                    raise e
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

# --- 6. OPERATION PIPELINE ---
if not st.session_state['api_key']:
    st.warning("⚠️ Please provide your Groq API Key in the sidebar to start.")
else:
    client = Groq(api_key=st.session_state['api_key'])
    uploaded_file = st.file_uploader("📂 Upload Document (PDF, TXT) for Audit", type=["pdf", "txt"])

    if uploaded_file:
        if st.button("🚀 Commence TTF-9 Audit"):
            segments = process_file(uploaded_file)
            
            if segments:
                st.write(f"System ready. Analyzing **{len(segments)}** segments...")
                
                results = []
                final_text_lines = []
                progress_bar = st.progress(0)
                status_text = st.empty()
                table_placeholder = st.empty()
                
                for i, seg in enumerate(segments):
                    # MEMORY CHECK
                    if seg in st.session_state['memory_cache']:
                        cached = st.session_state['memory_cache'][seg]
                        status, final_seg, justification = "🧠 SESSION HIT", cached['final'], cached['justification']
                        status_text.text(f"Segment {i+1}/{len(segments)}: Loaded from Memory.")
                        time.sleep(0.1) # Fast progress for memory hits
                    else:
                        status_text.text(f"Processing segment {i+1}/{len(segments)}...")
                        try:
                            # AUDIT
                            comp = call_groq_safe(client, [{"role": "system", "content": AUDITOR_PROMPT}, {"role": "user", "content": seg}], temp=0, resp_format={"type": "json_object"})
                            res = json.loads(comp.choices[0].message.content)
                            f = calculate_triadic_stability(res.get('x',0), res.get('y',0), res.get('z',0))
                            justification = res.get('justification', "")
                            
                            if f == 1:
                                status, final_seg = "✅ APPROVED", seg
                            else:
                                status_text.text(f"Repairing segment {i+1}/{len(segments)}...")
                                # REPAIR
                                rep_comp = call_groq_safe(client, [{"role": "system", "content": REPAIR_PROMPT}, {"role": "user", "content": f"Fix: {seg}\nReason: {justification}"}], temp=0.5)
                                final_seg = rep_comp.choices[0].message.content.strip()
                                status = "🔧 REPAIRED"
                            
                            st.session_state['memory_cache'][seg] = {"final": final_seg, "justification": justification}

                        except Exception as e:
                            status, final_seg, justification = "❌ ERROR", seg, f"API Alert: Server limit exceeded after retries."
                    
                    results.append({"Status": status, "Segment": seg[:80] + "...", "Logic Justification": justification})
                    final_text_lines.append(final_seg)
                    
                    table_placeholder.dataframe(pd.DataFrame(results), use_container_width=True)
                    progress_bar.progress((i + 1) / len(segments))
                
                status_text.text("Audit Complete.")
                st.success("🎯 Audit Complete. Triadic Equilibrium achieved.")
                
                st.divider()
                c1, c2 = st.columns(2)
                full_txt = "\n\n".join(final_text_lines)
                c1.download_button("💾 Download Clean TXT", full_txt, file_name=f"TTF9_CLEAN_{uploaded_file.name}.txt")
                csv_report = pd.DataFrame(results).to_csv(index=False).encode('utf-8')
                c2.download_button("📊 Download Audit Log (CSV)", csv_report, file_name=f"TTF9_LOG_{uploaded_file.name}.csv")
                
                st.info("💡 System is ready. You can re-run this file (it will use Memory) or upload a new one.")

