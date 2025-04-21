from flask import Flask, Response, request, make_response
import requests

app = Flask(__name__)

# Full original m3u8 URL
M3U8_SOURCE = "https://c58bx6vat7sxiexj.freshsoup.shop/v4/variant/VE1gTdz0mLzRnLv52bt9SMhFjdtM3ajFmc09iMkZ2YxQTM3Q2MyIWL3UGZi1iZkFDNtIDZjhTLhJGN0UTN1kzL.m3u8?md5=-h2MLUUDl0ZLq1zxWSAGtw&expires=1745208900&net=MjYwMDo0MDQxOjU0Mjk6MjkwMDo3NTA4OjI1MzM6MjIyZjo4YTc4"

# Headers to spoof source validation
COMMON_HEADERS = {
    "Referer": "https://ppv.wtf/",
    "Origin": "https://ppv.wtf",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36",
    "Accept": "*/*",
}

@app.route("/live.m3u8")
def proxy_m3u8():
    r = requests.get(M3U8_SOURCE, headers=COMMON_HEADERS)
    content = r.text
    base_url = M3U8_SOURCE.rsplit("/", 1)[0] + "/"

    # Rewrite key URI to go through this server
    content = content.replace('URI="/key/', f'URI="http://{request.host}/key/')

    # Rewrite .ts segments to go through this server
    lines = []
    for line in content.splitlines():
        if line.strip().endswith(".ts"):
            lines.append(f"/segment?url={line.strip()}")
        else:
            lines.append(line)

    resp = make_response("\n".join(lines))
    resp.headers["Content-Type"] = "application/vnd.apple.mpegurl"
    resp.headers["Access-Control-Allow-Origin"] = "*"
    return resp

@app.route("/segment")
def segment():
    ts_url = request.args.get("url")
    if ts_url.startswith("/"):
        ts_url = "https://ve16o29z6o6dszgkty9jni4ulo4ba76t.global.ssl.fastly.net" + ts_url
    r = requests.get(ts_url, headers=COMMON_HEADERS, stream=True)
    resp = Response(r.iter_content(chunk_size=1024), content_type="video/MP2T")
    resp.headers["Access-Control-Allow-Origin"] = "*"
    return resp

@app.route("/key/<uuid>/<key_id>")
def key(uuid, key_id):
    key_url = f"https://c58bx6vat7sxiexj.freshsoup.shop/key/{uuid}/{key_id}"
    r = requests.get(key_url, headers=COMMON_HEADERS)
    resp = make_response(r.content)
    resp.headers["Content-Type"] = "application/octet-stream"
    resp.headers["Access-Control-Allow-Origin"] = "*"
    return resp

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8072)

