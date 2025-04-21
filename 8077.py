from flask import Flask, redirect, request
import requests
import urllib.parse

app = Flask(__name__)

@app.route('/<server>/<channel>/<mac>')
def redirect_to_stream(server, channel, mac):
    # Ensure mac is URL-encoded
    mac_encoded = urllib.parse.quote(mac)

    # Construct the target URL with user-provided parameters
    TARGET_URL = f"http://{server}/server/load.php?type=itv&action=create_link&cmd=ffmpeg%20http%3A%2F%2Flocalhost%2Fch%2F{channel}_&mac={mac_encoded}&stb_lang=en&timezone=America%2FNew_York"
    
    # Print the target URL for debugging
    print(f"Target URL: {TARGET_URL}")

    # Add headers to the GET request
    headers = {
        'User-Agent': 'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    }

    # Fetch the response from the target URL with headers
    response = requests.get(TARGET_URL, headers=headers)
    
    if response.status_code == 200:
        try:
            data = response.json()  # Try to parse JSON response
        except ValueError:
            return f"Error: Failed to parse JSON response. Content: {response.text}", 500
        
        if 'js' in data and 'cmd' in data['js']:
            # Extract the URL portion after 'ffmpeg '
            stream_url = data['js']['cmd'].split('ffmpeg ')[1]
            return redirect(stream_url, code=302)
        else:
            return "Error: 'cmd' not found in the response.", 500
    else:
        return f"Error: Failed to fetch data from the target URL. Status code: {response.status_code}", 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8077)
