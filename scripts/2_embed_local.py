# scripts/2_embed_local.py
import os, json, time
import chromadb
from sentence_transformers import SentenceTransformer

# Caminhos
ARCHIVE_PATH = "data/processed/archive.jsonl"
DB_PATH = "data/vectors/local"
COLLECTION_NAME = "mindfield_fragments"

# Modelo de embeddings
MODEL_NAME = "BAAI/bge-large-en-v1.5"  # ou 'BAAI/bge-base-en-v1.5' se quiser mais leve

def main():
    if not os.path.exists(ARCHIVE_PATH):
        raise FileNotFoundError(f"Arquivo {ARCHIVE_PATH} não encontrado.")
    os.makedirs(DB_PATH, exist_ok=True)

    print(f"\n🧭 carregando modelo {MODEL_NAME} ...")
    model = SentenceTransformer(MODEL_NAME)
    model.max_seq_length = 8192

    print("🗃️  inicializando base vetorial ...")
    client = chromadb.PersistentClient(path=DB_PATH)
    coll = client.get_or_create_collection(COLLECTION_NAME)

    ids, embeddings, metadatas, texts = [], [], [], []
    total = 0
    t0 = time.time()

    with open(ARCHIVE_PATH, "r", encoding="utf-8") as f:
        for i, line in enumerate(f, start=1):
            doc = json.loads(line)
            text = doc.get("content", "").strip()
            if not text:
                continue

            emb = model.encode(text, normalize_embeddings=True)
            ids.append(doc["id"])
            embeddings.append(emb.tolist())
            texts.append(text)

            meta = {
                "codex_id": str(doc.get("codex_id", "")),
                "category": str(doc.get("category", "")),
                "index": str(doc.get("index", "")),
                "slug": str(doc.get("slug", "")),
                "codex_title": str(doc.get("codex_title", "")),
                "segment": int(doc.get("segment", 0)),
                "title": str(doc.get("title", "")),
                "epoch": str(doc.get("epoch", "")),
                "voice": str(doc.get("voice", "")),
                "mood": str(doc.get("mood", "")),
            }
            meta = {k: v for k, v in meta.items() if v not in ["", "None", None]}
            metadatas.append(meta)

            if len(ids) >= 64:
                coll.add(
                    ids=ids,
                    embeddings=embeddings,
                    metadatas=metadatas,
                    documents=texts
                )
                total += len(ids)
                print(f"   ↳ {total} fragmentos indexados...")
                ids, embeddings, metadatas, texts = [], [], [], []

    # flush final
    if ids:
        coll.add(
            ids=ids,
            embeddings=embeddings,
            metadatas=metadatas,
            documents=texts
        )
        total += len(ids)

    dt = time.time() - t0
    print(f"\n[OK] Indexados {total} fragmentos em {dt/60:.1f} min.")
    print(f"Base vetorial salva em {DB_PATH}")

if __name__ == "__main__":
    main()
