"""
bridge_query.py
MindField dual-geometry query bridge
------------------------------------
Routes semantic queries through both hemispheres:
 - Orientation layer (theory compasses)
 - Texture layer (paragraph fragments)

Automatically connects to either:
  • Local persistent Chroma (development)
  • Chroma Cloud (production)

Controlled via .env:
  CHROMA_MODE = local | cloud
  CHROMA_API_KEY = <your cloud key>
  CHROMA_DB_NAME = <database name>
  CHROMA_TENANT  = <tenant name>
"""

import os
import chromadb
from chromadb import Client
from chromadb.config import Settings

from dotenv import load_dotenv
load_dotenv()

# ─────────────────────────────────────────────
# Chroma connection logic
# ─────────────────────────────────────────────
CHROMA_MODE = os.getenv("CHROMA_MODE", "local").lower()

def get_chroma_client():
    """Initialize Chroma in local or cloud mode."""
    if CHROMA_MODE == "cloud":
        print("☁️  Connecting to Chroma Cloud (v1.x client)...")
        return Client(
            api_key=os.getenv("CHROMA_API_KEY"),
            database=os.getenv("CHROMA_DB_NAME"),
            tenant=os.getenv("CHROMA_TENANT", "default_tenant"),
        )
    else:
        print("💾  Using local Chroma persistence...")
        vector_path = os.getenv("CHROMA_LOCAL_PATH", "data/vectors/local")
        return chromadb.PersistentClient(path=vector_path)

# ─────────────────────────────────────────────
# Query function
# ─────────────────────────────────────────────
def query_bridge(query_text: str):
    """
    Run a dual-geometry query against both vector collections.
    Returns a structured dict with 'orientation' and 'texture' results.
    """
    client = get_chroma_client()

    # Collections: orientation (theory compasses) + texture (paragraph fragments)
    orientation_collection_name = os.getenv(
        "CHROMA_COLLECTION_ORIENTATION", "mindfield_compasses_large_v2"
    )
    texture_collection_name = os.getenv(
        "CHROMA_COLLECTION_TEXTURE", "mindfield_fragments_v2"
    )

    try:
        orientation = client.get_collection(orientation_collection_name)
        texture = client.get_collection(texture_collection_name)
    except Exception as e:
        raise RuntimeError(f"Failed to load collections: {e}")

    # ── Orientation layer query ──
    orient_results = orientation.query(
        query_texts=[query_text],
        n_results=5,
    )

    orientation_hits = []
    if orient_results and "documents" in orient_results:
        for i in range(len(orient_results["ids"][0])):
            orientation_hits.append({
                "codex_id": orient_results["metadatas"][0][i].get("codex_id", ""),
                "node_label": orient_results["metadatas"][0][i].get("node_label", ""),
                "field_label": orient_results["metadatas"][0][i].get("field_label", ""),
                "source": orient_results["metadatas"][0][i].get("source", ""),
                "geometry_pair": orient_results["metadatas"][0][i].get("geometry_pair", ""),
            })

    # ── Texture layer query ──
    text_results = texture.query(
        query_texts=[query_text],
        n_results=5,
    )

    texture_hits = []
    if text_results and "documents" in text_results:
        for i in range(len(text_results["ids"][0])):
            texture_hits.append({
                "codex_id": text_results["metadatas"][0][i].get("codex_id", ""),
                "title": text_results["metadatas"][0][i].get("title", ""),
                "segment": text_results["metadatas"][0][i].get("segment", ""),
                "document": text_results["documents"][0][i],
            })

    return {
        "orientation": orientation_hits,
        "texture": texture_hits,
    }

# ─────────────────────────────────────────────
# Local test harness
# ─────────────────────────────────────────────
if __name__ == "__main__":
    print(f"Running bridge in {CHROMA_MODE.upper()} mode\n")
    q = input("Enter query: ").strip()
    if q:
        result = query_bridge(q)
        print(result)
