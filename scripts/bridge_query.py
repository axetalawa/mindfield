# scripts/bridge_query.py
import os, chromadb
from openai import OpenAI
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv
from pathlib import Path  # <-- 1. IMPORT PATHLIB

# ---------------------------------------------------------
#  Environment setup
# ---------------------------------------------------------
load_dotenv()

# --- 2. DYNAMICALLY RESOLVE PATHS ---
# Get the directory of this script (scripts/)
# Get its parent (the project root, 'mindfield/')
ROOT_DIR = Path(__file__).resolve().parent.parent 

# Build absolute paths from the project root
DB_ORIENT_PATH = str(ROOT_DIR / "data/vectors/abstracts_v2")   # <-- 3. FIXED
DB_FIELD_PATH  = str(ROOT_DIR / "data/vectors/local")          # <-- 4. FIXED
# ----------------------------------------

COLL_ORIENT = "mindfield_compasses_large_v2"
COLL_FIELD  = "mindfield_fragments"

EMB_MODEL_OPENAI = os.getenv("OPENAI_EMBED_MODEL", "text-embedding-3-large")
API_KEY           = os.getenv("OPENAI_API_KEY")
LOCAL_MODEL_NAME  = "BAAI/bge-large-en-v1.5"
TOP_K = 5


# ---------------------------------------------------------
#  Bridge Function
# ---------------------------------------------------------
def query_bridge(query: str) -> dict:
    """Bridge across dual embedding spaces (OpenAI + Local)."""
    if not API_KEY:
        raise RuntimeError("Missing OPENAI_API_KEY")

    # --- orientation (OpenAI) client ---
    openai_client = OpenAI(api_key=API_KEY)
    db_o = chromadb.PersistentClient(path=DB_ORIENT_PATH)
    try:
        coll_o = db_o.get_collection(COLL_ORIENT)
    except Exception:
        print(f"⚠️  Orientation collection '{COLL_ORIENT}' not found. Creating a new one for fallback.")
        coll_o = db_o.create_collection(COLL_ORIENT)

    # --- texture (local) client ---
    local_model = SentenceTransformer(LOCAL_MODEL_NAME)
    db_f = chromadb.PersistentClient(path=DB_FIELD_PATH)
    try:
        coll_f = db_f.get_collection(COLL_FIELD)
    except Exception:
        # This warning should no longer appear after the fix
        print(f"⚠️  Texture collection '{COLL_FIELD}' not found. Creating a new one for fallback.")
        coll_f = db_f.create_collection(COLL_FIELD)

    # --- embed query for both hemispheres ---
    q_vec_o = openai_client.embeddings.create(
        model=EMB_MODEL_OPENAI, input=query
    ).data[0].embedding

    q_vec_f = local_model.encode(query, normalize_embeddings=True).tolist()

    # ---------------------------------------------------------
    #  Orientation layer (OpenAI embeddings)
    # ---------------------------------------------------------
    results_o = coll_o.query(
        query_embeddings=[q_vec_o],
        n_results=TOP_K,
        include=["metadatas"]
    )
    metadatas_o = results_o.get("metadatas", [])
    if len(metadatas_o) == 1 and isinstance(metadatas_o[0], list):
        metadatas_o = metadatas_o[0]

    orientation_items = []
    for m in metadatas_o:
        if not isinstance(m, dict):
            continue
        orientation_items.append({
            "codex_id": m.get("codex_id"),
            "node_label": m.get("node_label"),
            "field_label": m.get("field_label"),
            "geometry_pair": m.get("geometry_pair"),
            "source": m.get("source"),
            "id": m.get("id")
        })

    # ---------------------------------------------------------
    #  Texture layer (Local embeddings + paragraphs)
    # ---------------------------------------------------------
    results_f = coll_f.query(
        query_embeddings=[q_vec_f],
        n_results=TOP_K,
        include=["metadatas", "documents"] # 'documents' will now be populated
    )

    # Normalize nested vs flat lists
    metadatas_f = results_f.get("metadatas", [])
    documents_f = results_f.get("documents", [])

    if len(metadatas_f) == 1 and isinstance(metadatas_f[0], list):
        metadatas_f = metadatas_f[0]
    if len(documents_f) == 1 and isinstance(documents_f[0], list):
        documents_f = documents_f[0]

    texture_items = []
    for i, meta in enumerate(metadatas_f):
        doc_text = ""
        if i < len(documents_f) and documents_f[i]:
            doc_text = documents_f[i]
        else:
            print(f"⚠️ Missing text for item {i}: {meta.get('title')}")
        meta["document"] = doc_text
        texture_items.append(meta)

    # ---------------------------------------------------------
    #  Return dual hemisphere results
    # ---------------------------------------------------------
    return {
        "orientation": orientation_items,
        "texture": texture_items,
        "query": query
    }


# ---------------------------------------------------------
#  CLI test
# ---------------------------------------------------------
if __name__ == "__main__":
    q = input("Query the archive: ").strip()
    result = query_bridge(q)
    print("\n✅ bridge complete")
    print("🧭  Orientation layer — dual-geometry compasses:")
    for o in result["orientation"]:
        print(f"  • {o.get('codex_id')} — {o.get('node_label')} ↔ {o.get('field_label')}  ({o.get('source')}) [{o.get('geometry_pair')}]")

    print("\n🌿  Texture layer — paragraph fragments:")
    for t in result["texture"]:
        snippet = t.get("document", "").strip().replace("\n", " ")
        if len(snippet) > 200:
            snippet = snippet[:197] + "..."
        print(f"  • {t.get('codex_id')} — {t.get('title')}  [segment {t.get('segment')}]")
        print(f"    → {snippet}")

    print("\n✅  bridge complete — two hemispheres queried in native geometry.")