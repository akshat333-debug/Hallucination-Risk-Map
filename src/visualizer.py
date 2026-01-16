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

# --- 4. TRUST TIMELINE (Line Chart) ---
def plot_trust_timeline(claims):
    """
    Shows how factuality evolves as you read the text.
    """
    x = [f"Claim {i+1}" for i in range(len(claims))]
    y = [c['analysis']['score'] for c in claims]
    colors = [c['analysis']['color'] for c in claims]
    
    # Map colors to hex
    color_map = {"green": "#00CC96", "orange": "#FFA15A", "red": "#EF553B"}
    marker_colors = [color_map.get(c, "#d3d3d3") for c in colors]

    fig = go.Figure()

    # Line Trace
    fig.add_trace(go.Scatter(
        x=x, y=y,
        mode='lines+markers',
        line=dict(color='white', width=2, shape='spline'),
        marker=dict(size=12, color=marker_colors, line=dict(color='white', width=2)),
        name='Trust Score'
    ))

    # Add background zones
    fig.add_hrect(y0=0.8, y1=1.0, fillcolor="green", opacity=0.1, layer="below", line_width=0)
    fig.add_hrect(y0=0.4, y1=0.8, fillcolor="orange", opacity=0.1, layer="below", line_width=0)
    fig.add_hrect(y0=0.0, y1=0.4, fillcolor="red", opacity=0.1, layer="below", line_width=0)

    fig.update_layout(
        title="Evaluated Trust Flow",
        yaxis=dict(title="Trust Score", range=[0, 1.05], gridcolor='rgba(255,255,255,0.1)'),
        xaxis=dict(gridcolor='rgba(255,255,255,0.1)'),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="white"),
        margin=dict(l=20, r=20, t=40, b=20),
        showlegend=False
    )
    return fig

# --- 5. SOURCE ATTRIBUTION (Bar Chart) ---
def plot_source_attribution(claims):
    """
    Which files are we relying on?
    """
    source_counts = {}
    
    for c in claims:
        # Only count 'Supporting' evidence (similarity > 0.4 or entailed)
        for ev in c['evidence']:
            if ev['similarity'] > 0.4:
                # Clean filename: "report.pdf (Page 1)" -> "report.pdf"
                fname = ev['source'].split(" (Page")[0]
                source_counts[fname] = source_counts.get(fname, 0) + 1
    
    if not source_counts:
        return None

    sorted_src = sorted(source_counts.items(), key=lambda x: x[1], reverse=True)
    names = [x[0] for x in sorted_src]
    counts = [x[1] for x in sorted_src]

    fig = go.Figure(go.Bar(
        x=counts,
        y=names,
        orientation='h',
        marker=dict(color='#636EFA', line=dict(color='white', width=1))
    ))

    fig.update_layout(
        title="Evidence Source Attribution",
        xaxis=dict(title="Citations Count", gridcolor='rgba(255,255,255,0.1)'),
        yaxis=dict(autorange="reversed"), # Top source at top
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="white"),
        margin=dict(l=20, r=20, t=40, b=20)
    )
    return fig

# --- 6. EVIDENCE HEATMAP (Matrix) ---
def plot_heatmap(claims):
    """
    Shows the strength of top 3 evidence chunks for each claim.
    """
    claim_labels = [f"C{i+1}" for i in range(len(claims))]
    evidence_labels = ["Ev 1", "Ev 2", "Ev 3"] # Top 3
    
    z_data = []
    text_data = []
    
    for c in claims:
        # Get top 3 evidence scores (or 0 if missing)
        row_scores = []
        row_text = []
        for k in range(3):
            if k < len(c['evidence']):
                score = c['evidence'][k]['similarity']
                row_scores.append(score)
                row_text.append(f"{score:.2f}")
            else:
                row_scores.append(0.0)
                row_text.append("N/A")
        z_data.append(row_scores)
        text_data.append(row_text)
        
    # Transpose for easier plotting (Claims on Y axis usually better for long lists)
    # But here we'll keep Claims on X for timeline alignment
    
    fig = go.Figure(data=go.Heatmap(
        z=list(map(list, zip(*z_data))), # Transpose
        x=claim_labels,
        y=evidence_labels,
        colorscale='Viridis',
        text=list(map(list, zip(*text_data))), # Transpose text
        texttemplate="%{text}",
        showscale=True
    ))

    fig.update_layout(
        title="Evidence Strength Heatmap",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="white"),
        margin=dict(l=20, r=20, t=40, b=20)
    )
    return fig