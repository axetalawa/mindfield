import os, json, re

RAW_JSON_DIR = "data/raw_geometry_json"
OUT_PATH = "data/processed/abstracts.jsonl"

def clean(text):
    if not text:
        return ""
    return re.sub(r"\s+", " ", text).strip()

def fuse_summary(node_label, node_summary, field_label, field_paragraph):
    """create a compact, reflective synthesis"""
    base = (
        f"When the node '{node_label}' meets the field '{field_label}', "
        f"language curves as {node_summary.lower()} "
        f"and resonates through {field_paragraph.lower()}."
    )
    return re.sub(r"\s+", " ", base).strip()

def main():
    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    count = 0

    with open(OUT_PATH, "w", encoding="utf-8") as out:
        for fn in sorted(os.listdir(RAW_JSON_DIR)):
            if not fn.endswith(".json"):
                continue

            full = os.path.join(RAW_JSON_DIR, fn)
            data = json.load(open(full, "r", encoding="utf-8"))
            meta = data.get("metadata", {})
            codex_id = meta.get("id") or fn.split(".json")[0]
            title = meta.get("title", codex_id)

            nodes = data.get("ICOSA_MESH", {}).get("nodes", [])
            fields = data.get("DODECA_FIELD", {}).get("pentagonal_fields", [])
            if not nodes or not fields:
                continue

            for i, node in enumerate(nodes):
                node_label = clean(node.get("label") or f"Node {i+1}")
                node_summary = clean(node.get("summary") or node.get("reflection") or "")
                field = fields[i % len(fields)]
                field_label = clean(field.get("label") or f"Field {i%len(fields)+1}")
                field_paragraph = clean(field.get("paragraph", ""))

                synthesis = fuse_summary(node_label, node_summary, field_label, field_paragraph)

                doc = {
                    "codex_id": codex_id,
                    "node_index": i + 1,
                    "node_label": node_label,
                    "node_summary": node_summary,
                    "field_index": (i % len(fields)) + 1,
                    "field_label": field_label,
                    "field_paragraph": field_paragraph,
                    "summary": synthesis,
                    "geometry_pair": "icosa↔dodeca",
                    "source": title
                }
                out.write(json.dumps(doc, ensure_ascii=False) + "\n")
                count += 1

    print(f"[OK] Generated {count} dual-geometry compasses in {OUT_PATH}")

if __name__ == "__main__":
    main()
