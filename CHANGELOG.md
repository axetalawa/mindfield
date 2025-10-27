# CHANGELOG.md — Commit Story of MindField  
### Cognitive Geometry, Embedding Atlases & the Bridge Query System  
*Mute Logic Lab — Salvador, Bahia (2025)*  

> *Before understanding could be measured,  
> it had to learn how to take shape.*

## Phase I — Corpus Genesis (March–April 2025)

**Objective:**  
Transform notebooks, codices, and essays into a structured, machine-legible corpus.  
This marked the birth of *Cognitive Geometry* as a computational experiment — the attempt to make thought itself spatial.

**Key work**
- Authored **`1_md_to_jsonl.py`** for converting Markdown archives into structured `.jsonl` objects with `title`, `section`, and `body` fields.  
- Defined preliminary schema for *MindField Document Object (MDO)*.  
- Created initial test corpus from Lab notebooks (*Integrity Geometry*, *Interactional Topology*, *Cognitive Atlas*).  
- Implemented basic text cleaning, tokenization, and title inference.

**Artifacts**
- `1_md_to_jsonl.py`
- `/corpus/*.md`
- `/data/mindfield_raw.jsonl`

**Decisions**
- Retain paragraph structure; reject sentence-level fragmentation.  
- Treat each file as a *semantic cell*, not as linear text.  
- Begin mapping knowledge as geometry, not hierarchy.

---

## Phase II — Local Embedding Architecture (April–May 2025)

**Objective:**  
Build a local semantic field from the corpus — enabling proximity search and visual clustering without external dependencies.

**Key work**
- Implemented **`2_embed_local.py`** using **sentence-transformers** + **ChromaDB**.  
- Stored embeddings as persistent vectors in `/chroma_index`.  
- Introduced concept of **Integrity Geometry** — the shape of coherence within a corpus.  
- Added metadata fields: embedding norm, cluster ID, document origin.

**Artifacts**
- `2_embed_local.py`
- `/chroma_index/`
- `/data/embeddings_local.json`

**Decisions**
- Prefer local embeddings for transparency and reproducibility.  
- No API calls — full autonomy even offline.  
- Begin developing *resonance metrics* based on cosine similarity.

---

## Phase III — Dual Geometry Bridge (May–June 2025)

**Objective:**  
Create a **dual geometry** system linking local embeddings (Integrity Geometry) with global embeddings (Interactional Topology).

**Key work**
- Authored **`3_make_abstracts_dual_geometry.py`** and **`4_embed_openai_abstracts.py`**.  
- Integrated **OpenAI text-embedding-3-small** and **bge-large-en-v1.5** for global context.  
- Created **bridge matrices** aligning local and external semantic coordinates.  
- Developed *resonance*, *novelty*, and *cross-coherence* metrics.  

**Artifacts**
- `3_make_abstracts_dual_geometry.py`
- `4_embed_openai_abstracts.py`
- `/data/dual_geometry.json`

**Decisions**
- Global embeddings extend the field; local embeddings preserve integrity.  
- Geometry is bidirectional: corpus ↔ world.  
- Establish the **Bridge Query Protocol** (BQP) — a semantic handshake between geometries.

---

## Phase IV — Bridge Query System (June–July 2025)

**Objective:**  
Operationalize the bridge into a live querying environment.

**Key work**
- Authored **`bridge_query.py`** for running real-time semantic resonance queries.  
- Implemented **`server.py`** (Flask) exposing `/query`, `/bridge`, and `/compasses` endpoints.  
- Created response schema with **Orientation** and **Texture** layers:
  ```json
  {
    "orientation": [{ "title": "...", "x": 0.12, "y": 0.34 }],
    "texture": [{ "excerpt": "...", "x": -0.28, "y": 0.56 }]
  }
````

* Integrated JSON streaming for dynamic front-end rendering.

**Artifacts**

* `server.py`
* `bridge_query.py`
* `5_sanity_query_compasses.py`

**Decisions**

* Serve results in dual-layer format: structural (orientation) and affective (texture).
* Maintain consistent interface regardless of corpus size.
* Treat every query as a *compass bearing* in the atlas.

---

## Phase V — Constellation Interface (August–September 2025)

**Objective:**
Visualize the bridge output as constellations of thought — geometry rendered in browser.

**Key work**

* Authored **`mindfield.js`** and **`index.html`** for live visualization.
* Implemented canvas rendering of **Orientation (gold)** and **Texture (cyan)** nodes.
* Added interactive hover details, link lines, and gradual fading.
* Enabled dual modes:

  * **Constellation Mode** — 2D geometric visualization.
  * **Textual Bridge Mode** — symbolic narration (🧭, 🌿, →).

**Artifacts**

* `index.html`
* `mindfield.js`

**Decisions**

* Use pure JS + Canvas for minimal dependencies.
* Favor atmospheric subtlety over analytical exactness.
* Each frame should *breathe*, not compute.

---

## Phase VI — Cognitive Narration & Deployment (October 2025)

**Objective:**
Integrate text and geometry into a single interpretive system — the *MindField Atlas*.

**Key work**

* Authored **glyphic narration layer** in `bridge_query.py`.
* Added **auto-storytelling**: each query produces both data and prose.
* Deployed to **Railway** and local Vercel static environments.
* Authored `README.md` and `CHANGELOG.md`.
* Conducted sanity tests with “Integrity Geometry”, “Ritual Machines”, and “Bahian Cognition” corpora.

**Artifacts**

* `README.md`
* `CHANGELOG.md`
* `/deploy/railway.toml`

**Decisions**

* Documentation is itself a form of geometry.
* The atlas is not closed — every corpus added reshapes its topology.
* Treat the final build as **v1.0 of the Cognitive Bridge Framework**.

---

## Forward Trajectory

* [ ] Integrate **WebGL UMAP projection** for real-time embedding constellations.
* [ ] Add **recursive querying** — feedback between queries and prior fields.
* [ ] Implement **Corpus Dashboard** for visual inspection of embedding clusters.
* [ ] Expand beyond English to **Portuguese and Yoruba corpora**.
* [ ] Release **MindField Atlas (v2.0)** with open-source dataset and visualization API.

---

## ✴︎ Coda

> *A field is not a map.
> It is the hum of adjacency —
> the quiet recognition between ideas.*

---

**Authored by:** [Javed Saunja Jaghai](https://javedjaghai.com)
**Lab:** Mute Logic Lab — Salvador, Bahia (2025)
**License:** MIT

---
