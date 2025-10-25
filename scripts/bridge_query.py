# scripts/bridge_query.py
import os, chromadb
from openai import OpenAI
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv

load_dotenv()

# --- Paths and models ---
DB_ORIENT_PATH = "data/vectors/abstracts_v2"   # 3072-D OpenAI layer (orientation)
DB_FIELD_PATH  = "data/vectors/local"          # 1024-D local layer (texture)

COLL_ORIENT = "mindfield_compasses_large_v2"
COLL_FIELD  = "mindfield_fragments"

EMB_MODEL_OPENAI = os.getenv("OPENAI_EMBED_MODEL", "text-embedding-3-large")
API_KEY           = os.getenv("OPENAI_API_KEY")
LOCAL_MODEL_NAME  = "BAAI/bge-large-en-v1.5"

TOP_K = 5

# --- Cloud / local Chroma setup ---
CHROMA_MODE     = os.getenv("CHROMA_MODE", "local")  # "local" or "cloud"

# --- Mode selection ---
CHROMA_MODE = os.getenv("CHROMA_MODE", "local")

# --- Visual confirmation in console ---
mode_icon = "💽" if CHROMA_MODE == "local" else "☁️"
print(f"{mode_icon}  Running in {CHROMA_MODE.upper()} mode")

CHROMA_URL      = os.getenv("CHROMA_URL", "https://api.trychroma.com")
CHROMA_API_KEY  = os.getenv("CHROMA_API_KEY")
CHROMA_DB_NAME  = os.getenv("CHROMA_DB_NAME", "mindfield")


def get_chroma_collections():
    """Return orientation + texture collections for the active mode."""
    if CHROMA_MODE == "cloud":
        print(f"☁️  Connecting to Chroma Cloud ({CHROMA_DB_NAME})...")
        client = chromadb.HttpClient(
            host=CHROMA_URL,
            api_key=CHROMA_API_KEY,
            database=CHROMA_DB_NAME
        )
        coll_o = client.get_or_create_collection(COLL_ORIENT)
        coll_f = client.get_or_create_collection(COLL_FIELD)
    else:
        print("💽  Using local Chroma stores...")
        db_o = chromadb.PersistentClient(path=DB_ORIENT_PATH)
        coll_o = db_o.get_collection(COLL_ORIENT)
        db_f = chromadb.PersistentClient(path=DB_FIELD_PATH)
        coll_f = db_f.get_collection(COLL_FIELD)
    return coll_o, coll_f


# --- Main bridge function ---
def query_bridge(query: str) -> dict:
    """Bridge across dual embedding spaces (OpenAI + Local)."""
    if not API_KEY:
        raise RuntimeError("Missing OPENAI_API_KEY")

    # Initialize embedding engines
    openai_client = OpenAI(api_key=API_KEY)
    local_model = SentenceTransformer(LOCAL_MODEL_NAME)

    # Get appropriate Chroma collections
    coll_o, coll_f = get_chroma_collections()

    # --- Embed query for both hemispheres ---
    q_vec_o = openai_client.embeddings.create(
        model=EMB_MODEL_OPENAI, input=query
    ).data[0].embedding

    q_vec_f = local_model.encode(query, normalize_embeddings=True).tolist()

    # --- Query both hemispheres ---
    orient_results = coll_o.query(query_embeddings=[q_vec_o], n_results=TOP_K)
    texture_results = coll_f.query(query_embeddings=[q_vec_f], n_results=TOP_K)

    # --- Reformat results ---
    orientation = []
    texture = []

    # Orientation layer
    for ids, meta in zip(orient_results["ids"][0], orient_results["metadatas"][0]):
        orientation.append({
            "codex_id": meta.get("codex_id"),
            "node_label": meta.get("node_label"),
            "field_label": meta.get("field_label"),
            "source": meta.get("source"),
            "geometry_pair": meta.get("geometry_pair"),
        })

    # Texture layer
    for ids, meta, doc in zip(
        texture_results["ids"][0],
        texture_results["metadatas"][0],
        texture_results["documents"][0],
    ):
        texture.append({
            "codex_id": meta.get("codex_id"),
            "title": meta.get("title"),
            "segment": meta.get("segment"),
            "document": doc,
        })

    print("✅ bridge complete")
    return {"orientation": orientation, "texture": texture}
