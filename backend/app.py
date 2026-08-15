from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from urllib.parse import urlparse

app = Flask(__name__)
CORS(app)

@app.get("/health")
def health():
    return jsonify({"ok": True, "service": "video-downloader-api"})

@app.post("/download")
def download():
    data = request.get_json(silent=True) or {}
    url = (data.get("url") or "").strip()
    site = (data.get("site") or "").lower()

    if site not in {"instagram", "youtube"}:
        return jsonify({"error": "Unsupported site"}), 400

    host = urlparse(url).netloc.lower()
    if not host:
        return jsonify({"error": "Invalid URL"}), 400

    allowed = (
        ("instagram.com" in host or "youtube.com" in host or "youtu.be" in host)
    )
    if not allowed:
        return jsonify({"error": "Please provide an Instagram or YouTube URL"}), 400

    # Intentionally does not bypass platform protections or access controls.
    # Connect an authorized media-processing provider here.
    return jsonify({
        "message": "URL accepted. Connect an authorized media-processing provider to return the downloadable file."
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", "10000")))
