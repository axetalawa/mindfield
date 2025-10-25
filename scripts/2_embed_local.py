# scripts/2_embed_local.py
import os, time, json, chromadb
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv

load_dotenv()

# ── ENV CONFIG ─────────────────────────────────────────────────────────────
CHROMA_MODE       = os.getenv("CHROMA_MODE", "local")
CHROMA_URL        = os.getenv("CHROMA_URL", "https://api.trychroma.com")
CHROMA_API_KEY    = os.getenv("CHROMA_API_KEY")
CHROMA_DB_NAME    = os.getenv("CHROMA_DB_NAME", "mindfield")
CHROMA_TENANT     = os.getenv("CHROMA_TENANT", "default_tenant") # <-- ADDED
COLLECTION_NAME   = "mindfield_fragments"
DATA_PATH         = "data/processed/archive.jsonl"
LOCAL_VECTOR_PATH = "data/vectors/local"
MODEL_NAME        = "BAAI/bge-large-en-v1.5"

# ── CLIENT SETUP ───────────────────────────────────────────────────────────
def get_chroma_client():
    """Return local or cloud Chroma client (v1.2+)."""
    if CHROMA_MODE == "cloud":
        print("☁️  Connecting to Chroma Cloud (v1.2+ API)...")
        # --- UPDATED ---
        return chromadb.HttpClient(
            host=CHROMA_URL,
            headers={"X-Chroma-Token": CHROMA_API_KEY},
            database=CHROMA_DB_NAME,
            tenant=CHROMA_TENANT
        )
        # ---------------
    else:
        print("💽  Using local Chroma storage...")
        return chromadb.PersistentClient(path=LOCAL_VECTOR_PATH)

# ── MAIN INGESTION ─────────────────────────────────────────────────────────
def main():
    start = time.time()
    model = SentenceTransformer(MODEL_NAME)
    db = get_chroma_client()

    try:
        coll = db.get_collection(COLLECTION_NAME)
    except Exception:
        print(f"🗃️  Creating new collection: {COLLECTION_NAME}")
        coll = db.create_collection(COLLECTION_NAME)

    print(f"🧭 carregando modelo {MODEL_NAME} ...")
    with open(DATA_PATH, "r") as f:
        docs = [json.loads(line) for line in f]

    ids, texts, metas = [], [], []
    for i, d in enumerate(docs):
        ids.append(d["id"])
        texts.append(d["content"])
        metas.append({
            "title": d.get("title"),
            "codex_id": d.get("codex_id"),
            "segment": d.get("segment"),
            "category": d.get("category"),
            "slug": d.get("slug"),
        })
        if (i + 1) % 64 == 0:
            embs = model.encode(texts, normalize_embeddings=True).tolist()
            coll.add(ids=ids, embeddings=embs, metadatas=metas, documents=texts)
            print(f"   ↳ {i+1} fragmentos indexados...")
            ids, texts, metas = [], [], []

    if texts:
        embs = model.encode(texts, normalize_embeddings=True).tolist()
        coll.add(ids=ids, embeddings=embs, metadatas=metas, documents=texts)

    print(f"\n[OK] Indexados {len(docs)} fragmentos em {round((time.time()-start)/60,1)} min.")
    if CHROMA_MODE == "local":
        print(f"Base vetorial salva em {LOCAL_VECTOR_PATH}")
    else:
        print(f"☁️  Upload concluído na base '{CHROMA_DB_NAME}'.")

if __name__ == "__main__":
    main()