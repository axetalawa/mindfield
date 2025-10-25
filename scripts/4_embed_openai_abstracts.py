# scripts/4_embed_openai_abstracts.py
import os, json, time, dotenv
import chromadb
from openai import OpenAI

# ---------- config ----------
dotenv.load_dotenv()
ABS_PATH   = "data/processed/abstracts.jsonl"
DB_PATH   = "data/vectors/abstracts_v2"
COLL_NAME = "mindfield_compasses_large_v2"
     # orientation layer
EMB_MODEL  = os.getenv("OPENAI_EMBED_MODEL", "text-embedding-3-large")
API_KEY    = os.getenv("OPENAI_API_KEY")

BATCH_SIZE = 64
# ----------------------------

def sanitize_meta(d: dict) -> dict:
    """Cast to legal Chroma metadata types and drop empties."""
    def cast(v):
        if v is None: return ""
        if isinstance(v, (bool, int, float, str)): return v
        return str(v)
    out = {k: cast(v) for k, v in d.items()}
    return {k: v for k, v in out.items() if v not in ["", "None", None]}

def embed_batch(client: OpenAI, texts: list[str]) -> list[list[float]]:
    r = client.embeddings.create(model=EMB_MODEL, input=texts)
    return [item.embedding for item in r.data]

def main():
    if not API_KEY:
        raise RuntimeError("OPENAI_API_KEY is missing in your .env")
    if not os.path.exists(ABS_PATH):
        raise FileNotFoundError(f"{ABS_PATH} not found. Run script 3 first.")

    os.makedirs(DB_PATH, exist_ok=True)
    client = OpenAI()

    print(f"\n🧭 Using OpenAI embedding model: {EMB_MODEL}")
    print("🗃️  Initializing Chroma collection (orientation layer)…")
    db = chromadb.PersistentClient(path=DB_PATH)
    coll = db.get_or_create_collection(COLL_NAME)

    ids, texts, metas = [], [], []
    total = 0
    t0 = time.time()

    # stream abstracts.jsonl and batch
    with open(ABS_PATH, "r", encoding="utf-8") as f:
        for i, line in enumerate(f, start=1):
            obj = json.loads(line)
            # required text field for embedding
            # prefer the fused 'summary' if present; otherwise combine node+field
            text = (
                obj.get("summary")
                or f"{obj.get('node_label','')} — {obj.get('node_summary','')} :: {obj.get('field_label','')} — {obj.get('field_paragraph','')}"
            ).strip()
            if not text:
                continue

            _id = obj.get("id") or f"{obj.get('codex_id','?')}::compass::{i}"
            meta = sanitize_meta({
                "codex_id":       obj.get("codex_id"),
                "node_index":     obj.get("node_index"),
                "node_label":     obj.get("node_label"),
                "field_index":    obj.get("field_index"),
                "field_label":    obj.get("field_label"),
                "geometry_pair":  obj.get("geometry_pair", "icosa↔dodeca"),
                "source":         obj.get("source"),
            })

            ids.append(_id)
            texts.append(text)
            metas.append(meta)

            if len(ids) >= BATCH_SIZE:
                embs = embed_batch(client, texts)
                coll.add(ids=ids, embeddings=embs, metadatas=metas)
                total += len(ids)
                print(f"   ↳ {total} compasses indexed…")
                ids, texts, metas = [], [], []

    # flush
    if ids:
        embs = embed_batch(client, texts)
        coll.add(ids=ids, embeddings=embs, metadatas=metas)
        total += len(ids)

    dt = time.time() - t0
    print(f"\n[OK] Indexed {total} dual-geometry compasses in {dt/60:.1f} min.")
    print(f"Collection: {COLL_NAME} → {DB_PATH}")

if __name__ == "__main__":
    main()
