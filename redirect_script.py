from flask import Flask, redirect
import requests
import re
import time
import threading
import os

app = Flask(__name__)
latest_m3u8_url = None

# Function to scrape the latest m3u8 URL
def scrape_m3u8_url():
    global latest_m3u8_url
    url = "https://la12hd.com/vivo/canal.php?stream=dsports&autoplay=1"
    headers = {
        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_5_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.1 Mobile/15E148 Safari/605.1.15/Clipbox+/2.2.8'
    }
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        html_content = response.text
        match = re.search(r"var playbackURL = '(.*?)';", html_content)
        if match:
            latest_m3u8_url = match.group(1)
            print(f"Updated m3u8 URL: {latest_m3u8_url}")
        else:
            print("Could not find m3u8 URL")
    except requests.RequestException as e:
        print(f"Error fetching webpage: {e}")

# Schedule scraping periodically (e.g., every hour)
def schedule_scraping():
    while True:
        scrape_m3u8_url()
        time.sleep(3600)  # Wait 1 hour

# Start the scraping in a background thread
threading.Thread(target=schedule_scraping, daemon=True).start()

# Define the redirect route
@app.route('/')
def redirect_to_stream():
    if latest_m3u8_url:
        return redirect(latest_m3u8_url, code=302)  # HTTP 302 redirect
    else:
        return "Stream URL not available", 503  # Service unavailable if no URL

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))  # Use Render's PORT env variable
    app.run(host='0.0.0.0', port=port)
