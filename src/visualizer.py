import plotly.graph_objects as go
import plotly.express as px
import networkx as nx
from pyvis.network import Network
import tempfile
import os

# --- 1. THE TRUST RADAR (Spider Chart) ---
def plot_radar_chart(analysis):
    """
    Shows the 'DNA' of a specific claim's verification score.
    """
    categories = ['Entailment (Logic)', 'Contradiction (Risk)', 'Similarity (Vector)', 'Penalty (Entities)']
    
    # Extract values, defaulting to 0 if missing
    entail = analysis.get('entailment_strength', 0)
    contra = analysis.get('contradiction_strength', 0)
    # Recover similarity roughly from score if not stored explicitly
    # (Simplified for viz purposes)
    sim = analysis.get('score', 0) 
    penalty = analysis.get('penalty', 0)
    
    values = [entail, contra, sim, penalty]

    fig = go.Figure()

    fig.add_trace(go.Scatterpolar(
        r=values,
        theta=categories,
        fill='toself',
        name='Claim Metrics',
        line_color='#00CC96' if entail > contra else '#EF553B',
        mode='lines+markers+text',
        text=[f"{v:.2f}" for v in values],
        textposition="top center",
        textfont=dict(color="white", size=12, family="Arial Black"),
        marker=dict(size=8, color="white", line=dict(color="black", width=1))
    ))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 1],
                tickfont=dict(color="white", size=10),
                gridcolor="rgba(255, 255, 255, 0.2)",
                linecolor="rgba(255, 255, 255, 0.2)"
            ),
            angularaxis=dict(
                tickfont=dict(color="white", size=12),
                linecolor="rgba(255, 255, 255, 0.2)"
            ),
            bgcolor="rgba(0,0,0,0)"
        ),
        showlegend=False,
        margin=dict(l=40, r=40, t=40, b=40),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(size=14, color="white")
    )
    return fig

# --- 2. THE RISK SUNBURST (Donut Summary) ---
def plot_sunburst(claims):
    """
    Hierarchical view of the total answer.
    Inner Circle: Total Claims
    Outer Circle: Verified vs Unverified vs Contradicted
    """
    data = []
    
    for c in claims:
        label = c['analysis']['risk_label']
        data.append(dict(
            character="Answer",
            parent="",
            value=1
        ))
        data.append(dict(
            character=label,
            parent="Answer",
            value=1
        ))
        
    # Group by label
    counts = {}
    colors = {}
    
    for c in claims:
        lbl = c['analysis']['risk_label']
        counts[lbl] = counts.get(lbl, 0) + 1
        
        # Assign colors based on label
        if "Verified" in lbl or "True" in lbl:
            colors[lbl] = "#00CC96" # Green
        elif "Contradicted" in lbl:
            colors[lbl] = "#EF553B" # Red
        else:
            colors[lbl] = "#FFA15A" # Orange

    # Prepare Plotly Data
    labels = ["Total Answer"] + list(counts.keys())
    parents = [""] + ["Total Answer"] * len(counts)
    values = [len(claims)] + list(counts.values())
    marker_colors = ["#636EFA"] + [colors.get(k, "#d3d3d3") for k in counts.keys()]

    fig = go.Figure(go.Sunburst(
        labels=labels,
        parents=parents,
        values=values,
        branchvalues="total",
        marker=dict(colors=marker_colors)
    ))
    
    fig.update_layout(margin=dict(t=0, l=0, r=0, b=0), paper_bgcolor="rgba(0,0,0,0)")
    return fig

# --- 3. THE KNOWLEDGE NETWORK (Physics Graph) ---
def create_interactive_network(claims):
    """
    Creates a bouncing physics graph: Claims <-> Evidence
    """
    G = nx.Graph()
    
    for i, claim in enumerate(claims):
        claim_id = f"Claim {i+1}"
        risk = claim['analysis']['color']
        
        # Node Color based on risk
        c_color = "#00CC96" if risk == "green" else "#EF553B" if risk == "red" else "#FFA15A"
        
        # Add Claim Node
        G.add_node(claim_id, label=claim_id, title=claim['claim_text'], color=c_color, size=20, shape="dot")
        
        # Add Evidence Nodes & Edges
        for j, ev in enumerate(claim['evidence']):
            # Only graph high-relevance evidence to keep it clean
            if ev['similarity'] > 0.4 or ev['nli']['p_entailment'] > 0.5:
                ev_id = f"Src {i+1}-{j+1}"
                G.add_node(ev_id, label="Doc", title=ev['text'][:100]+"...", color="#636EFA", size=10, shape="square")
                
                # Edge weight based on trust score
                G.add_edge(claim_id, ev_id, weight=ev['similarity'])

    # Convert to PyVis
    nt = Network(height="500px", width="100%", bgcolor="#222222", font_color="white")
    nt.from_nx(G)
    
    # Physics Options (Make it bouncy but stable)
    nt.set_options("""
    var options = {
      "physics": {
        "barnesHut": {
          "gravitationalConstant": -2000,
          "centralGravity": 0.3,
          "springLength": 95
        },
        "minVelocity": 0.75
      }
    }
    """)
    
    # Save to temp file
    try:
        # Create a temporary file
        fd, path = tempfile.mkstemp(suffix=".html")
        with os.fdopen(fd, 'w') as tmp:
            nt.save_graph(path)
        return path
    except Exception as e:
        print(f"Graph error: {e}")
        return None