from flask import Flask, Response
from flask_cors import CORS
import requests, gzip
from io import BytesIO

app = Flask(__name__)
CORS(app)  # ✅ This line enables CORS

@app.route("/epg.xml")
def serve_epg():
    try:
        r = requests.get("https://epgshare01.online/epgshare01/epg_ripper_US1.xml.gz", timeout=10)
        if r.status_code == 200:
            buf = BytesIO(r.content)
            xml = gzip.decompress(buf.read())
            return Response(xml, mimetype="application/xml")
    except Exception as e:
        return str(e), 500
    return "EPG not available", 503

