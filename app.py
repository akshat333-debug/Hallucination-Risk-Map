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

@st.cache_resource
def get_pipeline():
    if not os.path.exists("vector_index.faiss"): return None
    from src.pipeline import RiskAnalysisPipeline
    return RiskAnalysisPipeline()

# --- SIDEBAR ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2103/2103633.png", width=60)
    st.markdown("### **Risk Map AI**")
    st.caption("Status: 🟢 Offline Mode (Local)")
    
    selected_page = option_menu(
        "Menu", ["Dashboard", "Knowledge Base", "Settings"], 
        icons=['speedometer2', 'database', 'gear'], menu_icon="cast", default_index=0,
        styles={"container": {"background-color": "transparent"}, "nav-link-selected": {"background-color": "#636EFA"}}
    )

# --- PAGE ROUTING ---

if selected_page == "Settings":
    st.header("⚙️ Configuration")
    st.info("System is running in pure Offline Mode. No API keys required.")
    st.text("Embeddings: all-mpnet-base-v2")
    st.text("Verifier: cross-encoder/nli-deberta-v3-base")

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
    mode_tab1, mode_tab2 = st.tabs(["🔎 Search & Verify", "📋 Audit External Text"])

    # === MODE 1: SEARCH & VERIFY (Extractive RAG) ===
    with mode_tab1:
        if "generated_answer" not in st.session_state: st.session_state["generated_answer"] = ""
        
        question = st.text_input("", "What is the capital of France?", placeholder="Ask your document...", key="q_input")
        
        if st.button("🚀 Run Search", use_container_width=True, key="run_btn"):
            pipeline = get_pipeline()
            if pipeline:
                with st.spinner("🔍 Searching Local Knowledge Base..."):
                    # 1. Retrieve
                    ctx = pipeline.retriever.retrieve(question, k=3)
                    
                    if ctx:
                        # 2. Extractive "Generation" (Take top result)
                        # We use the top result as the "Answer" to verify and display
                        top_answer = ctx[0]['text']
                        if len(ctx) > 1: top_answer += " " + ctx[1]['text']
                        
                        st.session_state["generated_answer"] = top_answer
                        
                        # 3. Verify
                        st.session_state['results'] = pipeline.process(question, st.session_state["generated_answer"])
                    else:
                        st.warning("No relevant information found in Knowledge Base.")
                        st.session_state["generated_answer"] = ""
            else:
                st.error("Build Index first!")

        if st.session_state["generated_answer"]:
            st.markdown("### 📝 Retrieved Answer")
            st.info(st.session_state["generated_answer"])

    # === MODE 2: AUDIT EXTERNAL TEXT (Manual Paste) ===
    with mode_tab2:
        st.info("Paste text to verify it against your Knowledge Base.")
        
        col_q, col_txt = st.columns([1, 2])
        with col_q:
            audit_question = st.text_input("Context Question (Optional)", placeholder="What is this text about?", key="audit_q")
        with col_txt:
            audit_text = st.text_area("Paste Text to Verify", height=200, placeholder="Paste the AI response here...", key="audit_txt")
        
        if st.button("🕵️ Verify Pasted Text", type="primary", use_container_width=True):
            pipeline = get_pipeline()
            if pipeline and audit_text:
                with st.spinner("🧠 Auditing external text..."):
                    query_context = audit_question if audit_question else audit_text[:100]
                    st.session_state['results'] = pipeline.process(query_context, audit_text)
                    st.session_state["generated_answer"] = "" 
            elif not pipeline:
                st.error("Index not ready.")
            elif not audit_text:
                st.warning("Please paste some text first.")

    # --- SHARED RESULTS DASHBOARD ---
    if 'results' in st.session_state:
        res = st.session_state['results']
        st.divider()
        st.markdown("### 📊 Verification Report")
        
        st.plotly_chart(plot_sunburst(res['claims']), use_container_width=True, key="sunburst_main")

        t1, t2, t3 = st.tabs(["🛡️ Risk Inspector", "🕸️ Graph", "✨ Clean Up"])
        
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
            total = len(res['claims'])
            score = int((len(green_claims)/total)*100) if total > 0 else 0
            
            st.metric("Factuality Score", f"{score}%")
            
            if score < 100 and total > 0:
                # Local "Auto-Correct" -> Just show verified sentences
                st.markdown("### 🧼 Verified Content Only")
                clean_text = " ".join(green_claims) if green_claims else "No verified content available."
                st.markdown(f"<div class='glass-card glow-green'>{clean_text}</div>", unsafe_allow_html=True)
            elif total == 0:
                st.warning("No claims detected.")
            else:
                st.success("Text is already 100% verified!")