import os, re, json, hashlib, yaml

RAW_DIR = "data/raw_md"
OUT_PATH = "data/processed/archive.jsonl"

MD_RE_TITLE = re.compile(r'^\s*#\s+(.+)', re.MULTILINE)

def read_md_with_frontmatter(path):
    text = open(path, 'r', encoding='utf-8').read()
    meta = {}
    content = text
    if text.startswith('---'):
        parts = text.split('---', 2)
        if len(parts) >= 3:
            try:
                meta = yaml.safe_load(parts[1]) or {}
            except Exception:
                meta = {}
            content = parts[2].lstrip()
    return meta, content

def strip_markdown(md):
    md = re.sub(r'```.*?```', '', md, flags=re.S)
    md = re.sub(r'`[^`]+`', '', md)
    md = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', md)
    md = re.sub(r'^\s*#{1,6}\s*', '', md, flags=re.M)
    md = re.sub(r'[*_~>`#-]+', ' ', md)
    md = re.sub(r'\s+', ' ', md).strip()
    return md

def first_heading(md):
    m = MD_RE_TITLE.search(md)
    return m.group(1).strip() if m else None

def parse_codex_id(filename):
    """Extract category, index, and slug from filename"""
    base = os.path.splitext(os.path.basename(filename))[0]
    parts = base.split('_', 1)
    prefix = parts[0]  # e.g. FIELD.201
    slug = parts[1] if len(parts) > 1 else ""
    if '.' in prefix:
        category, num = prefix.split('.', 1)
    else:
        category, num = "UNCAT", "000"
    codex_id = f"{category}.{num}_{slug}"
    codex_title = slug.replace('_', ' ').title() or codex_id
    return codex_id, category, num, slug, codex_title

def make_id(codex_id, relpath, title, seg):
    base = f"{codex_id}/{relpath}/{title}/{seg}"
    return hashlib.sha1(base.encode('utf-8')).hexdigest()[:16]

def split_paragraphs(text, filename=None):
    import re, os

    # normalize endings
    text = text.replace('\r\n', '\n').replace('\r', '\n').strip()

    # combine consecutive short lines into paragraphs
    lines = text.split('\n')
    combined = []
    current = []
    for line in lines:
        if not line.strip():
            if current:
                combined.append(" ".join(current).strip())
                current = []
        else:
            current.append(line.strip())
    if current:
        combined.append(" ".join(current).strip())

    # now, further segment long combined paragraphs into sub-blocks by sentence clusters
    paras = []
    for c in combined:
        # split after periods that are followed by capital letters or new sentences
        splits = re.split(r'(?<=[.!?])\s+(?=[A-Z(“"])', c)
        # group every 3–4 sentences together to preserve flow
        buf, count = [], 0
        for s in splits:
            buf.append(s.strip())
            count += 1
            if count >= 3:
                paras.append(" ".join(buf))
                buf, count = [], 0
        if buf:
            paras.append(" ".join(buf))

    # filter and fallback
    paras = [p for p in paras if len(p) > 60]
    if not paras:
        paras = [text]

    file_label = os.path.basename(filename) if filename else "<text>"
    print(f"   ↳ {len(paras)} segmentos extraídos de {file_label}")
    return paras

def main():
    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    count = 0
    with open(OUT_PATH, 'w', encoding='utf-8') as out:
        for root, _, files in os.walk(RAW_DIR):
            for fn in sorted(files):
                if not fn.lower().endswith('.md'):
                    continue
                full = os.path.join(root, fn)
                rel = os.path.relpath(full, RAW_DIR)
                meta, md = read_md_with_frontmatter(full)
                codex_id, category, num, slug, codex_title = parse_codex_id(fn)
                title = meta.get('title') or first_heading(md) or codex_title
                tags = meta.get('tags') or meta.get('keywords') or []
                mood = meta.get('mood')
                voice = meta.get('voice')
                lang = meta.get('language')
                notes = meta.get('notes')
                plain = strip_markdown(md)

                paragraphs = split_paragraphs(plain, filename=fn)
                for seg, para in enumerate(paragraphs):
                    doc = {
                        "id": make_id(codex_id, rel, title, seg),
                        "codex_id": codex_id,
                        "category": category,
                        "index": num,
                        "slug": slug,
                        "codex_title": codex_title,
                        "title": title,
                        "segment": seg,
                        "content": para,
                        "epoch": "atemporal",
                        "tags": tags,
                        "mood": mood,
                        "voice": voice,
                        "language": lang,
                        "notes": notes
                    }
                    out.write(json.dumps(doc, ensure_ascii=False) + "\n")
                    count += 1
    print(f"[OK] Gerado {OUT_PATH} com {count} fragmentos atemporais.")

if __name__ == "__main__":
    main()
