import os
# --- STABILITY FLAGS ---
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
os.environ["TOKENIZERS_PARALLELISM"] = "false"
os.environ["OMP_NUM_THREADS"] = "1"

import streamlit as st
import sys
import streamlit.components.v1 as components
from streamlit_option_menu import option_menu

sys.path.append(os.getcwd())
st.set_page_config(page_title="Hallucination Risk Map", layout="wide", page_icon="🧠", initial_sidebar_state="expanded")

# --- CSS / THEME ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600&family=JetBrains+Mono:wght@400;700&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    .glass-card {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 15px;
    }
    .glow-green { border-left: 4px solid #00CC96; }
    .glow-red { border-left: 4px solid #EF553B; }
    .glow-orange { border-left: 4px solid #FFA15A; }
    div[data-testid="stMetricValue"] { font-size: 28px; color: #ffffff; }
    .stButton > button { background: linear-gradient(45deg, #636EFA, #00CC96); color: white; border: none; }
    #MainMenu {visibility: hidden;} footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

from src.visualizer import plot_radar_chart, plot_sunburst, create_interactive_network

def configure_api_key():
    if "GEMINI_API_KEY" in st.secrets: return st.secrets["GEMINI_API_KEY"]
    return None

@st.cache_resource
def get_pipeline():
    if not os.path.exists("vector_index.faiss"): return None
    from src.pipeline import RiskAnalysisPipeline
    return RiskAnalysisPipeline()

# --- SIDEBAR ---
api_key = configure_api_key()

with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2103/2103633.png", width=60)
    st.markdown("### **Risk Map AI**")
    
    # TOGGLE
    use_local = st.toggle("🔒 Use Local Model Only", value=False, help="Force offline generation & verification (No API usage)")
    
    if use_local:
        st.caption("Status: 🟡 Offline Mode (Local CPU)")
        active_key = None # Override key
    else:
        st.caption(f"Status: {'🟢 Online (API)' if api_key else '🟡 Offline Mode'}")
        active_key = api_key

    selected_page = option_menu(
        "Menu", ["Dashboard", "Knowledge Base", "Settings"], 
        icons=['speedometer2', 'database', 'gear'], menu_icon="cast", default_index=0,
        styles={"container": {"background-color": "transparent"}, "nav-link-selected": {"background-color": "#636EFA"}}
    )

# --- PAGE ROUTING ---

if selected_page == "Settings":
    st.header("⚙️ Configuration")
    st.text_input("Gemini API Key", value=api_key if api_key else "", type="password", disabled=True)
    if use_local:
        st.info("🔒 Local Mode is ON. API Key will be ignored.")

elif selected_page == "Knowledge Base":
    st.header("📚 Knowledge Base")
    uploaded_file = st.file_uploader("Upload Ground Truth (PDF/TXT)", type=["pdf", "txt"])
    if uploaded_file and st.button("⚡ Build Index", type="primary"):
        with st.spinner("Building Hybrid Index..."):
            from src.index_builder import process_uploaded_file
            count = process_uploaded_file(uploaded_file)
            st.success(f"Indexed {count} chunks!")
            st.cache_resource.clear()

elif selected_page == "Dashboard":
    st.markdown("<h1 style='text-align: center;'>🧠 Hallucination Risk Map</h1>", unsafe_allow_html=True)

    # --- TABS FOR MODE SELECTION ---
    mode_tab1, mode_tab2 = st.tabs(["💬 Ask & Verify", "📋 Audit External Text"])

    # === MODE 1: ASK & VERIFY (Standard RAG) ===
    with mode_tab1:
        if "generated_answer" not in st.session_state: st.session_state["generated_answer"] = ""
        
        question = st.text_input("", "What are the main risks?", placeholder="Ask your document...", key="q_input")
        
        if st.button("🚀 Run Analysis", use_container_width=True, key="run_btn"):
            pipeline = get_pipeline()
            if pipeline:
                msg = "🤖 Local LLM Thinking..." if use_local or not active_key else "☁️ Gemini Thinking..."
                with st.spinner(msg):
                    ctx = pipeline.retriever.retrieve(question)
                    from src.llm_client import generate_answer
                    st.session_state["generated_answer"] = generate_answer(question, ctx, active_key, force_local=use_local)
                    # Auto-trigger verification for generated answers
                    st.session_state['results'] = pipeline.process(question, st.session_state["generated_answer"], active_key)
            else:
                st.error("Build Index first!")

        if st.session_state["generated_answer"]:
            st.markdown("### 📝 Generated Answer")
            st.text_area("", st.session_state["generated_answer"], height=200, key="ans_display")

    # === MODE 2: AUDIT EXTERNAL TEXT (Manual Paste) ===
    with mode_tab2:
        st.info("Paste text from ChatGPT, Claude, or a human draft to verify it against your Knowledge Base.")
        
        col_q, col_txt = st.columns([1, 2])
        with col_q:
            audit_question = st.text_input("Context Question (Optional)", placeholder="What is this text about?", key="audit_q")
        with col_txt:
            audit_text = st.text_area("Paste Text to Verify", height=200, placeholder="Paste the AI response here...", key="audit_txt")
        
        if st.button("🕵️ Verify Pasted Text", type="primary", use_container_width=True):
            pipeline = get_pipeline()
            if pipeline and audit_text:
                with st.spinner("🧠 Auditing external text..."):
                    # Use the audit question if provided, else use the text itself as query context
                    query_context = audit_question if audit_question else audit_text[:100]
                    st.session_state['results'] = pipeline.process(query_context, audit_text, active_key)
                    # Clear generated answer so we focus on this result
                    st.session_state["generated_answer"] = "" 
            elif not pipeline:
                st.error("Index not ready.")
            elif not audit_text:
                st.warning("Please paste some text first.")

    # --- SHARED RESULTS DASHBOARD ---
    # This section appears regardless of which tab triggered the results
    if 'results' in st.session_state:
        res = st.session_state['results']
        st.divider()
        st.markdown("### 📊 Verification Report")
        
        # Sunburst Summary
        st.plotly_chart(plot_sunburst(res['claims']), use_container_width=True, key="sunburst_main")

        t1, t2, t3 = st.tabs(["🛡️ Risk Inspector", "🕸️ Graph", "✨ Auto-Fix"])
        
        with t1:
            for i, c in enumerate(res['claims']):
                risk = c['analysis']['color']
                st.markdown(f"""
                <div class="glass-card glow-{risk}">
                    <b>Claim {i+1}:</b> {c['analysis']['risk_label']}
                    <p>{c['claim_text']}</p>
                </div>""", unsafe_allow_html=True)
                with st.expander(f"Details for Claim {i+1}"):
                    st.plotly_chart(plot_radar_chart(c['analysis']), use_container_width=True, key=f"radar_{i}")
                    for ev in c['evidence']:
                        st.caption(f"Source: {ev['source']} ({ev['similarity']:.2f})")
                        st.text(ev['text'])

        with t2:
            path = create_interactive_network(res['claims'])
            if path:
                with open(path, 'r', encoding='utf-8') as f:
                    components.html(f.read(), height=600, scrolling=True)

        with t3:
            green_claims = [c['claim_text'] for c in res['claims'] if c['analysis']['color'] == 'green']
            
            # Prevent division by zero if no claims found
            total = len(res['claims'])
            score = int((len(green_claims)/total)*100) if total > 0 else 0
            
            st.metric("Factuality Score", f"{score}%")
            
            if score < 100 and total > 0:
                if st.button("✨ Auto-Correct Hallucinations"):
                    with st.spinner("Rewriting..."):
                        from src.llm_client import rewrite_verified_answer
                        # Use audit_question if available, otherwise generic prompt
                        q_context = audit_question if 'audit_question' in locals() and audit_question else "the user query"
                        
                        new_ans = rewrite_verified_answer(q_context, green_claims, active_key)
                        st.success("Fixed Answer Generated!")
                        st.markdown(f"<div class='glass-card glow-green'>{new_ans}</div>", unsafe_allow_html=True)
            elif total == 0:
                st.warning("No claims detected to fix.")
            else:
                st.success("Text is already 100% verified!")