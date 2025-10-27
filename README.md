---
# 🜂 MindField Atlas  
### Cognitive Geometry, Semantic Embeddings, and the Bridge Query System  
*Mute Logic Lab — Salvador, Bahia (2025)*

> *Every field of thought has a topology.  
> MindField lets you see it.*

---

## ✴ Overview

**MindField** is a hybrid research and visualization framework for exploring **semantic space as geometry**.  
It builds a cognitive atlas from text corpora — embedding documents, deriving relational topology, and visualizing queries as constellations of thought.

At its core, MindField implements a *Bridge Query System* that joins **local embeddings** (offline, Chroma-based) with **OpenAI semantic models** (online) to form a *dual geometry*: one native to the user’s corpus, the other to the wider linguistic field.

The interface (`index.html`) allows you to query both, rendering textual or visual responses in the browser.

---

## System Architecture

MindField operates across three layers:

### 1. Data Layer — *Corpus to Embeddings*
Scripts in the numbered pipeline (`1_` → `5_`) convert raw text archives into a structured, queryable semantic field.

| Script | Function |
|--------|-----------|
| `1_md_to_jsonl.py` | Converts Markdown notebooks into `.jsonl` documents with title, section, and body fields. |
| `2_embed_local.py` | Embeds documents locally using `sentence-transformers` and stores them in ChromaDB. |
| `3_make_abstracts_dual_geometry.py` | Builds a “dual geometry” index: local embeddings ↔ OpenAI embeddings. |
| `4_embed_openai_abstracts.py` | Uses `text-embedding-3-small` or `bge-large-en-v1.5` for high-dimensional global embeddings. |
| `5_sanity_query_compasses.py` | Validates embedding coherence; produces compass maps for internal evaluation. |

This pipeline produces an **embeddings vault**, which the live Flask app queries.

---

### 2. Bridge Layer — *Semantic Dual Geometry*

**`bridge_query.py`** implements the “Bridge”:
- Accepts a natural language query.
- Retrieves nearest neighbors from both local and global embeddings.
- Computes resonance (cosine similarity), novelty, and coherence across layers.
- Returns structured JSON:
  ```json
  {
    "orientation": [{ "x": 0.12, "y": 0.34, "title": "Integrity Geometry" }],
    "texture": [{ "x": -0.28, "y": 0.56, "excerpt": "Recursive structures of meaning..." }]
  }
````

* Optionally streams a *textual bridge summary* (with 🧭 and 🌿 glyph layers) for non-visual environments.

**`server.py`** hosts the Flask API routes:

* `/query` — run dual-geometry queries and return JSON for visualization.
* `/bridge` — return the textual explanation of the semantic resonance field.
* `/compasses` — optional diagnostic output from `5_sanity_query_compasses.py`.

---

### 3. Interface Layer — *Visualization & Interaction*

**`index.html`** and **`mindfield.js`** provide two synchronized views:

| Mode                    | Description                                                                                          |
| ----------------------- | ---------------------------------------------------------------------------------------------------- |
| **Constellation Mode**  | Renders orientation (gold) and texture (cyan) points in the 2D canvas, connected by resonance lines. |
| **Textual Bridge Mode** | Displays formatted glyphic output (🧭, 🌿, →) for semantic narration.                                |
| **Query Flow**          | The user types a phrase → Flask Bridge → JSON response → Browser render.                             |

Interactions:

* Press **Enter** or click **Query** to execute.
* Responsive canvas auto-resizes with the window.
* Results are drawn dynamically without reloading.

---

## Local Setup

### 1. Clone and Install

```bash
git clone https://github.com/<username>/mindfield.git
cd mindfield
pip install -r requirements.txt
```

### 2. Prepare Environment

```bash
export OPENAI_API_KEY="your-openai-key"
export CHROMA_MODE="local"     # or "cloud"
```

### 3. Build Embedding Vault

Run the full pipeline (or any subset):

```bash
python 1_md_to_jsonl.py
python 2_embed_local.py
python 3_make_abstracts_dual_geometry.py
python 4_embed_openai_abstracts.py
python 5_sanity_query_compasses.py
```

### 4. Start the Bridge Server

```bash
python server.py
```

### 5. Open the Interface

Visit
👉 `http://127.0.0.1:5001`
and type a query (e.g. “integrity geometry”, “cognitive recursion”, “Bahian epistemology”).

---

## Core Dependencies

From `requirements.txt`:

* **LLM + Embedding Stack** — `openai`, `sentence-transformers`, `chromadb`, `numpy`
* **Web Frameworks** — `flask`, `gunicorn`, optional `fastapi`, `uvicorn`
* **Visualization + Analysis** — `plotly`, `umap-learn`, `scikit-learn`
* **Utilities** — `python-dotenv`, `requests`, `tqdm`, `PyYAML`

All packages are Python ≥ 3.10 compatible.

---

## Conceptual Schema

MindField formalizes three types of cognitive geometry:

| Domain                     | Description                                                                                |
| -------------------------- | ------------------------------------------------------------------------------------------ |
| **Integrity Geometry**     | The local corpus — meaning held in relation to itself.                                     |
| **Interactional Topology** | The bridge — resonance between systems (local ↔ global).                                   |
| **Cognitive Geometry**     | The field — the resulting relational map that can be visualized, queried, and interpreted. |

Queries are not mere searches; they are *coordinate lookups* in a multidimensional semantic terrain.

---

## Visualization Mechanics

Each query produces two vectors of points:

* **Orientation Nodes (gold):** represent semantic poles or attractors — structural coherence.
* **Texture Nodes (cyan):** represent lexical resonance — emotional and stylistic grain.

The **canvas renderer** (`mindfield.js`) maps these onto the screen with gentle transparency and blurred glow.
If no coordinates are returned, the system falls back to **textual narration** using structured glyphs:

```
• Orientation: Integrity Geometry
• Texture: Recursive Lexicon
• Local resonance high (0.82)
    → “Geometries of thought align with integrity fields…”
```

---

## Deployment

### Railway (recommended)

```toml
[build]
builder = "NIXPACKS"
[deploy]
startCommand = "python server.py"
```

### Vercel / Static

Front-end (`index.html`, `mindfield.js`) can be served independently;
Bridge can be hosted separately and queried via `/query` endpoint.

---

## Forward Trajectory

* [ ] Add **WebGL-based embedding projection** for 3D constellations.
* [ ] Integrate **UMAP reduction + Plotly** for multi-session exploration.
* [ ] Add **Corpus Dashboard** to view node metadata and embedding stats.
* [ ] Implement **recursive querying** (queries that feed back into themselves).
* [ ] Publish public dataset *MindField: The Cognitive Geometry Atlas (v1.0)*.

---

## ✴︎ Coda

> *The bridge hums between two geometries —
> one of memory, one of language.
> Each query is a compass point in the atlas of mind.*

**Author:** [Javed Saunja Jaghai](https://javedjaghai.com)
**Lab:** Mute Logic Lab — Salvador, Bahia (2025)
**License:** MIT
---