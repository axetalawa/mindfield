from dotenv import load_dotenv
load_dotenv()

import chromadb
from openai import OpenAI
import os

DB_PATH   = "data/vectors/abstracts_v2"
COLL_NAME = "mindfield_compasses_large_v2"

def main():
    db = chromadb.PersistentClient(path=DB_PATH)
    coll = db.get_or_create_collection(COLL_NAME)

    q = input("Query the compasses: ").strip()
    if not q:
        return

    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    emb = client.embeddings.create(
        model=os.getenv("OPENAI_EMBED_MODEL", "text-embedding-3-large"),
        input=[q]
    )
    query_vec = emb.data[0].embedding

    res = coll.query(query_embeddings=[query_vec], n_results=5)
    print("\nDEBUG: raw result keys ->", res.keys())
    print("DEBUG: number of matches ->", len(res.get("ids", [[]])[0]))

    ids = (res.get("ids") or [[]])[0]
    metas = (res.get("metadatas") or [[]])[0]

    if not ids:
        print("⚠️ No matches found — check query string or embedding dimension.")
        return

    print("\nTop matches:")
    for _id, m in zip(ids, metas):
        print(f"- {_id} :: {m.get('codex_id')} | node {m.get('node_index')}:{m.get('node_label')}  ↔  field {m.get('field_index')}:{m.get('field_label')}")

if __name__ == "__main__":
    main()
