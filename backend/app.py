from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import yt_dlp
import tempfile
import os
import glob

app = Flask(__name__)
CORS(app)

@app.get("/")
def home():
    return jsonify({
        "ok": True,
        "service": "video-downloader-api"
    })

@app.get("/health")
def health():
    return jsonify({
        "ok": True,
        "service": "video-downloader-api"
    })

@app.post("/download")
def download():
    data = request.get_json(silent=True) or {}

    url = (data.get("url") or "").strip()
    site = (data.get("site") or "").lower()

    if not url:
        return jsonify({"error": "URL डालें"}), 400

    if site not in ("youtube", "instagram"):
        return jsonify({"error": "Unsupported site"}), 400

    # केवल public URL स्वीकार करें
    if site == "youtube":
        allowed = (
            "youtube.com/" in url.lower()
            or "youtu.be/" in url.lower()
        )
    else:
        allowed = "instagram.com/" in url.lower()

    if not allowed:
        return jsonify({"error": "Invalid URL"}), 400

    temp_dir = tempfile.mkdtemp(prefix="video_")
    output = os.path.join(temp_dir, "video.%(ext)s")

    options = {
        "outtmpl": output,
        "format": "best[ext=mp4]/best",
        "noplaylist": True,
        "quiet": True,
        "no_warnings": True,
        "restrictfilenames": True,
    }

    try:
        with yt_dlp.YoutubeDL(options) as ydl:
            info = ydl.extract_info(url, download=True)

        files = glob.glob(os.path.join(temp_dir, "video.*"))

        if not files:
            return jsonify({
                "error": "Video file नहीं मिली"
            }), 500

        filename = os.path.basename(files[0])

        return send_file(
            files[0],
            as_attachment=True,
            download_name=filename,
            mimetype="video/mp4"
        )

    except Exception as e:
        return jsonify({
            "error": "Video process नहीं हो सका",
            "details": str(e)
        }), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "10000"))
    app.run(host="0.0.0.0", port=port)
