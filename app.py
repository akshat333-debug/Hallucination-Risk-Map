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
def get_pipeline_v3():
    if not os.path.exists("vector_index.faiss"): return None
    from src.pipeline import RiskAnalysisPipeline
    return RiskAnalysisPipeline()

# --- SIDEBAR ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2103/2103633.png", width=60)
    st.markdown("### **Risk Map AI**")

    
    selected_page = option_menu(
        "Menu", ["Dashboard", "Knowledge Base"], 
        icons=['speedometer2', 'database'], menu_icon="cast", default_index=0,
        styles={"container": {"background-color": "transparent"}, "nav-link-selected": {"background-color": "#636EFA"}}
    )
    

    with st.expander("⚙️ Advanced Settings"):
        st.caption("Adjust Verification Sensitivity")
        
        sim_val = st.slider(
            "Similarity Match", 
            min_value=0.4, max_value=0.9, value=0.6, step=0.05,
            help="Higher = Requires exact wording. Lower = Allows paraphrasing."
        )
        
        entail_val = st.slider(
            "Logic Match", 
            min_value=0.4, max_value=0.9, value=0.6, step=0.05,
            help="Higher = Requires strict logical proof. Lower = Allows 'likely' connections."
        )
        
        st.info(
            """
            **Recommended Values:**
            *   📄 **PDF / Summaries:** Sim 0.60 | Logic 0.60
            *   🧠 **General Facts:** Sim 0.75 | Logic 0.75
            *   🔬 **Critical Data:** Sim 0.85 | Logic 0.85
            
            *(Usually keep both values similar)*
            """
        )
        
        st.divider()
        st.caption("Verification Model")
        model_ui = st.radio(
            "Select AI Engine",
            ["⚡ Quick (Base)", "✨ Hyper-Efficient (Auto)"],
            help="Auto uses Base model + Symbolic Logic for math/units."
        )
        if "Quick" in model_ui: model_key = "base"
        else: model_key = "auto"
        
    thresholds = {
        "sim_threshold": sim_val,
        "entail_threshold": entail_val
    }

# --- PAGE ROUTING ---

if selected_page == "Knowledge Base":
    st.header("📚 Knowledge Base")
    
    # --- Display Current Index Content ---
    from src.index_builder import get_indexed_files, process_uploaded_file
    
    files = get_indexed_files()
    if files:
        st.subheader("✅ Currently Indexed Files")
        for f in files:
            st.markdown(f"- 📄 **{f}**")
        st.divider()
    else:
        st.warning("⚠️ Knowledge Base is Empty. Upload documents below.")

    if files and st.button("🗑️ Clear Knowledge Base"):
        import shutil
        if os.path.exists("vector_index.faiss"): os.remove("vector_index.faiss")
        if os.path.exists("corpus_metadata.pkl"): os.remove("corpus_metadata.pkl")
        if os.path.exists("bm25_index.pkl"): os.remove("bm25_index.pkl")
        st.success("Index cleared!")
        st.rerun()

    uploaded_file = st.file_uploader("Upload Ground Truth (PDF/TXT)", type=["pdf", "txt"])
    if uploaded_file and st.button("⚡ Build Index", type="primary"):
        with st.spinner("Building Hybrid Index..."):
            from src.index_builder import process_uploaded_file
            count = process_uploaded_file(uploaded_file)
            st.success(f"Indexed {count} chunks!")
            st.cache_resource.clear()

elif selected_page == "Dashboard":
    st.markdown("<h1 style='text-align: center;'>🧠 Hallucination Risk Map</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center;'>Paste any text (Article, LLM Response, Summary) to verify its claims against your verified Knowledge Base.</p>", unsafe_allow_html=True)
    
    # --- MAIN INPUT AREA ---
    col_q, col_txt = st.columns([1, 2])
    with col_q:
        st.info("💡 **Context Question (Optional)**\n\nHelps the AI understand what the text *should* be answering.")
        audit_question = st.text_input("Enter Question:", placeholder="What is this text about?", key="audit_q", label_visibility="collapsed")
    with col_txt:
        audit_text = st.text_area("Paste Text to Verify", height=200, placeholder="Paste the text you want to audit here...", key="audit_txt")
    
    if st.button("🕵️ Verify Pasted Text", type="primary", use_container_width=True):
        pipeline = get_pipeline_v3()
        if not audit_text:
            st.warning("Please paste some text first.")
        elif not pipeline:
            st.error("Index not ready. Go to 'Knowledge Base' to upload documents.")
        else:
            with st.spinner("🧠 Auditing external text..."):
                query_context = audit_question if audit_question else audit_text[:100]
                # Pass thresholds from sidebar
                results = pipeline.process(question=query_context, answer=audit_text, thresholds=thresholds, model_selection=model_key)
                st.session_state['results'] = results
                st.rerun()

    # --- SHARED RESULTS DASHBOARD ---
    if 'results' in st.session_state:
        res = st.session_state['results']
        st.divider()
        st.markdown("### 📊 Verification Report")
        
        st.plotly_chart(plot_sunburst(res['claims']), use_container_width=True, key="sunburst_main")

        t1, t2, t3 = st.tabs(["🛡️ Risk Inspector", "📈 Analytics & Graph", "✨ Clean Up"])
        
        with t1:
            for i, c in enumerate(res['claims']):
                risk = c['analysis']['color']
                st.markdown(f"""
                <div class="glass-card glow-{risk}">
                    <b>Claim {i+1}:</b> {c['analysis']['risk_label']}
                    <p>{c['claim_text']}</p>
                </div>""", unsafe_allow_html=True)
                with st.expander(f"Details for Claim {i+1}"):
                    c_chart, c_stats = st.columns([2, 1])
                    with c_chart:
                        st.plotly_chart(plot_radar_chart(c['analysis']), use_container_width=True, key=f"radar_{i}")
                    with c_stats:
                        st.markdown("#### Verification Status")
                        st.metric("Overall Score", f"{c['analysis']['score']:.2f}")
                        st.metric("Verdict", c['analysis']['risk_label'], delta_color="normal")
                        st.caption(f"Entailment: {c['analysis']['entailment_strength']:.2f}")
                        st.caption(f"Contradiction: {c['analysis']['contradiction_strength']:.2f}")
                    
                    st.divider()
                    st.markdown("#### Verified Evidence Sources")
                    for ev in c['evidence']:
                        st.caption(f"Source: {ev['source']} ({ev['similarity']:.2f})")
                        st.text(ev['text'])

                        st.text(ev['text'])

        with t2:
             # --- ANALYTICS DASHBOARD ---
             from src.visualizer import plot_trust_timeline, plot_source_attribution
             
             col_time, col_src = st.columns([2, 1])
             
             with col_time:
                 st.plotly_chart(plot_trust_timeline(res['claims']), use_container_width=True)
                 
             with col_src:
                 fig_src = plot_source_attribution(res['claims'])
                 if fig_src:
                     st.plotly_chart(fig_src, use_container_width=True)
                 else:
                     st.info("No sufficient evidence found for attribution.")

             # Heatmap Row
             from src.visualizer import plot_heatmap
             st.plotly_chart(plot_heatmap(res['claims']), use_container_width=True)

             st.divider()
             st.markdown("#### 🕸️ Interactive Graph")
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