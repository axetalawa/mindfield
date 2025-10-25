import chromadb

DB_PATH = "data/vectors/local"
COLLECTION_NAME = "mindfield_fragments"

client = chromadb.PersistentClient(path=DB_PATH)
coll = client.get_collection(COLLECTION_NAME)

print(f"\n🔍 Checking first 5 entries in '{COLLECTION_NAME}' ...\n")

results = coll.get(limit=5)
docs = results.get("documents", [])
metas = results.get("metadatas", [])

for i, (doc, meta) in enumerate(zip(docs, metas), start=1):
    title = meta.get("title", "Unknown")
    codex = meta.get("codex_id", "")
    print(f"{i}. {codex} — {title}")
    if doc:
        print("   →", doc[:200].replace("\n", " ") + "...")
    else:
        print("   ⚠️  (no document text found)")
