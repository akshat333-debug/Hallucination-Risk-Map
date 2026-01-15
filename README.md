# 🧠 Hallucination Risk Map

A powerful RAG (Retrieval-Augmented Generation) system designed to detect, visualize, and auto-correct hallucinations in AI-generated text. It uses a **Hybrid Search** mechanism (Vector + Keyword) and a local **NLI (Natural Language Inference)** model to verify claims against a trusted knowledge base.

## 🚀 Features

*   **Hybrid Retrieval**: Combines Semantic Search (`all-mpnet-base-v2`) and Keyword Search (`BM25`) for high-recall context retrieval.
*   **Real-time Verification**: Checks every generated sentence against your document corpus effectively using a local DeBERTa model (`cross-encoder/nli-deberta-v3-base`).
*   **Visual Risk Assessment**:
    *   **Sunburst Charts**: Global view of text safety.
    *   **Radar Charts**: Detailed contradictory vs. entailment probability.
    *   **Claims Cards**: Color-coded (Green/Orange/Red) risk indicators.
*   **Dual Modes**:
    1.  **Ask & Verify**: Chat with your documents with instant fact-checking.
    2.  **Audit Mode**: Paste external text (e.g., from ChatGPT) to verify it against your trusted data.
*   **Auto-Correction**: Automatically rewrites hallucinated answers using only verified facts.

## 🛠️ Installation

1.  **Clone the Repository**
    ```bash
    git clone https://github.com/akshat333-debug/Hallucination-Risk-Map.git
    cd Hallucination-Risk-Map
    ```

2.  **Create a Virtual Environment**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3.  **Install Dependencies**
    ```bash
    pip install -r requirements.txt
    ```

## 🏃‍♂️ How to Run

1.  **(Optional) Configure API Key**
    *   To use Google Gemini for generation, create a `.streamlit/secrets.toml` file:
        ```toml
        GEMINI_API_KEY = "your_api_key_here"
        ```
    *   *Note: The project works in "Offline Mode" (using local heuristics) if no key is provided.*

2.  **Start the Application**
    ```bash
    streamlit run app.py
    ```
    The app will open in your browser at `http://localhost:8501`.

## 📖 Usage Guide & Controls

### 1. Knowledge Base (Setup)
*   Go to the **Knowledge Base** page from the sidebar menu.
*   **Upload File**: Upload a PDF or TXT file containing your "Ground Truth" data.
*   **Button: `⚡ Build Index`**:
    *   **What it does**: Chunks your document, generates vector embeddings, and builds the search index.
    *   **When to use**: You **must** click this once after uploading new data so the AI "learns" the content.

### 2. Dashboard (Analysis)
Navigate to the **Dashboard** page. You will see two tabs:

#### Mode 1: 💬 Ask & Verify
*   **Input**: Type a question about your documents.
*   **Button: `🚀 Run Analysis`**:
    *   **What it does**: Retrieves context, generates an answer, and runs the verification pipeline.
    *   **Result**: Displays the answer and a detailed Risk Report below.

#### Mode 2: 📋 Audit External Text
*   **Input**: Paste text from another source (ChatGPT, Claude, or a human draft).
*   **Button: `🕵️ Verify Pasted Text`**:
    *   **What it does**:Treats the pasted text as a set of claims and verifies each sentence against your local index.
    *   **Result**: Highlights which sentences are supported by your data and which are hallucinations.

### 3. Analyzing Results
*   **Risk Cards**:
    *   🟢 **Green**: Verified by evidence.
    *   🔴 **Red**: Contradicts evidence (Hallucination).
    *   🟠 **Orange**: Not enough evidence found.
*   **Button: `✨ Auto-Correct Hallucinations`**:
    *   **What it does**: appearing only when risks are detected, this triggers the LLM to rewrite the answer, strictly removing red/orange claims and keeping verified information.

### 4. Sidebar Options
*   **Toggle: `🔒 Use Local Model Only`**:
    *   **What it does**: Disables outgoing API calls to Gemini. Forces the system to use local logic for generation and verification.
    *   **When to use**: For privacy or offline usage.

## 📂 Project Structure

*   `app.py`: Main Streamlit application entry point.
*   `src/`: Core logic modules.
    *   `pipeline.py`: Orchestrates the retrieval and verification flow.
    *   `index_builder.py`: Handles PDF parsing and Faiss index creation.
    *   `nli_verifier.py`: Loads the local DeBERTa model for logic checking.
    *   `retriever.py`: Hybrid search (Vector + BM25) logic.
*   `corpus_data.json`: Sample data for testing.
*   `requirements.txt`: Python dependencies.

## 🧪 Accuracy Checks
You can run the included accuracy evaluation script to test the model's performance:
```bash
python run_accuracy_check.py
```
*Current Accuracy on Test Set: 100%*
