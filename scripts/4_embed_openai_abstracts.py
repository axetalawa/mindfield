# scripts/4_embed_openai_abstracts.py
import os, time, json, chromadb
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

# ── ENV CONFIG ─────────────────────────────────────────────────────────────
CHROMA_MODE       = os.getenv("CHROMA_MODE", "local")
CHROMA_URL        = os.getenv("CHROMA_URL", "https://api.trychroma.com")
CHROMA_API_KEY    = os.getenv("CHROMA_API_KEY")
CHROMA_DB_NAME    = os.getenv("CHROMA_DB_NAME", "mindfield")
CHROMA_TENANT     = os.getenv("CHROMA_TENANT", "default_tenant")
COLLECTION_NAME   = "mindfield_compasses_large_v2"
DATA_PATH         = "data/processed/abstracts.jsonl"
LOCAL_VECTOR_PATH = "data/vectors/abstracts_v2"
EMBED_MODEL       = os.getenv("OPENAI_EMBED_MODEL", "text-embedding-3-large")
API_KEY           = os.getenv("OPENAI_API_KEY")

# ── CLIENT SETUP ───────────────────────────────────────────────────────────
def get_chroma_client():
    """Return local or cloud Chroma client (v1.2+)."""
    if CHROMA_MODE == "cloud":
        print("☁️  Connecting to Chroma Cloud (v1.2+ API)...")
        return chromadb.HttpClient(
            host=CHROMA_URL,
            headers={"X-Chroma-Token": CHROMA_API_KEY},
            database=CHROMA_DB_NAME,
            tenant=CHROMA_TENANT
        )
    else:
        print("💽  Using local Chroma storage...")
        return chromadb.PersistentClient(path=LOCAL_VECTOR_PATH)

# ── MAIN INGESTION ─────────────────────────────────────────────────────────
def main():
    start = time.time()
    openai_client = OpenAI(api_key=API_KEY)
    db = get_chroma_client()

    try:
        coll = db.get_collection(COLLECTION_NAME)
    except Exception:
        print(f"🗃️  Creating new collection: {COLLECTION_NAME}")
        coll = db.create_collection(COLLECTION_NAME)

    print(f"🧭 Using OpenAI embedding model: {EMBED_MODEL}")
    with open(DATA_PATH, "r") as f:
        docs = [json.loads(line) for line in f]

    ids, texts, metas = [], [], []
    
    # --- MODIFIED LOOP ---
    for i, d in enumerate(docs):
        
        # 1. Create a unique ID since 'id' does not exist
        doc_id = f"{d.get('codex_id')}_{d.get('node_index')}_{d.get('field_index')}"
        
        # 2. Use the 'summary' field for text
        doc_text = d.get("summary")

        # 3. Safety check if 'summary' key is missing
        if not doc_text:
            print(f"⚠️  Skipping record {i}. Missing 'summary' field.")
            continue

        ids.append(doc_id)
        texts.append(doc_text)
        metas.append({
            "codex_id": d.get("codex_id"),
            "geometry_pair": d.get("geometry_pair"),
            "node_label": d.get("node_label"),
            "field_label": d.get("field_label"),
            "source": d.get("source"),
        })
        
        if (i + 1) % 64 == 0:
            resp = openai_client.embeddings.create(model=EMBED_MODEL, input=texts)
            embs = [e.embedding for e in resp.data]
            coll.add(ids=ids, embeddings=embs, metadatas=metas, documents=texts)
            print(f"   ↳ {i+1} compasses indexados...")
            ids, texts, metas = [], [], []

    if texts:
        resp = openai_client.embeddings.create(model=EMBED_MODEL, input=texts)
        embs = [e.embedding for e in resp.data]
        coll.add(ids=ids, embeddings=embs, metadatas=metas, documents=texts)

    print(f"\n[OK] Indexed {len(docs)} dual-geometry compasses in {round((time.time()-start)/60,1)} min.")
    if CHROMA_MODE == "local":
        print(f"Collection saved locally at {LOCAL_VECTOR_PATH}")
    else:
        print(f"☁️  Uploaded to Chroma Cloud database '{CHROMA_DB_NAME}'.")


if __name__ == "__main__":
    main()