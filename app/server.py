from flask import Flask, request, jsonify, send_from_directory
import sys
from pathlib import Path

# --- Path setup ---
BASE_DIR = Path(__file__).resolve().parent
SCRIPTS_PATH = BASE_DIR.parent / "scripts"
STATIC_PATH = BASE_DIR / "static"

sys.path.append(str(SCRIPTS_PATH))
from bridge_query import query_bridge  # import your bridge

# --- Flask app setup ---
app = Flask(
    __name__,
    static_folder=str(STATIC_PATH),
    static_url_path="",  # <-- this line fixes the 404s
)

@app.route("/")
def index():
    """Serve MindField Atlas interface."""
    return send_from_directory(STATIC_PATH, "index.html")


@app.route("/query", methods=["POST"])
def query():
    """Bridge front-end query to the dual-geometry engine"""
    data = request.get_json(force=True)
    q = data.get("query", "").strip()
    if not q:
        return jsonify({"error": "empty query"}), 400

    try:
        result = query_bridge(q)
        lines = ["✅ bridge complete"]

        # --- Orientation layer ---
        if "orientation" in result:
            lines.append("\n🧭  Orientation layer — dual-geometry compasses:")
            for o in result["orientation"]:
                codex = o.get("codex_id", "N/A")
                node = o.get("node_label", "Unknown")
                field = o.get("field_label", "")
                src = o.get("source", "")
                geom = o.get("geometry_pair", "")
                lines.append(
                    f"  • {codex} — {node} ↔ {field}  ({src}) [{geom}]"
                )

        # --- Texture layer ---
        if "texture" in result:
            lines.append("\n🌿  Texture layer — paragraph fragments:")
            for t in result["texture"]:
                codex = t.get("codex_id", "N/A")
                title = t.get("title", "Unknown")
                segment = t.get("segment", "")
                # ↓ now we also show the first ~180 chars of the actual text
                text = t.get("document", "").strip()
                if text:
                    preview = text.replace("\n", " ")[:180] + "..."
                else:
                    preview = "(no text)"
                lines.append(f"  • {codex} — {title}  [segment {segment}]")
                lines.append(f"    → {preview}")

        lines.append("\n✅  bridge complete — two hemispheres queried in native geometry.")
        return jsonify({"output": "\n".join(lines)})

    except Exception as e:
        print("Bridge error:", e)
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    # Forces Flask to resolve absolute path for static assets
    app.run(host="127.0.0.1", port=5050, debug=True)
