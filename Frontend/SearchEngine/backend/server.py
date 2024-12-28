from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)
CORS(app)  # Enable CORS

# Function to scrape the thumbnail image
def scrape_thumbnail_image(url):
    try:
        # Fetch the HTML content from the URL
        response = requests.get(url)
        response.raise_for_status()  # Raise an HTTPError for bad responses

        # Load the HTML content into BeautifulSoup
        soup = BeautifulSoup(response.text, 'html.parser')

        # Extract the image URL from the meta tag with property "og:image"
        image_url = soup.find('meta', property='og:image')
        if image_url:
            return image_url['content']
        return 'https://via.placeholder.com/200'  # Fallback placeholder
    except Exception as e:
        print(f"Error fetching the image from {url}: {e}")
        return 'https://via.placeholder.com/200'  # Return placeholder in case of error

# Test route
@app.route('/', methods=['GET'])
def test_route():
    return "Reached"

# Endpoint to scrape images for a list of URLs
@app.route('/scrape-images', methods=['POST'])
def scrape_images():
    data = request.get_json()
    urls = data.get('urls')
    print(f"POST /scrape-images reached with URLs: {urls}")

    if not urls or not isinstance(urls, list):
        return jsonify({'error': 'URLs are required and should be an array.'}), 400

    try:
        image_urls = []
        for url in urls:
            image_url = scrape_thumbnail_image(url)
            image_urls.append({'url': url, 'image': image_url})

        # Respond with the scraped images
        return jsonify({'imageUrls': image_urls})
    except Exception as e:
        print(f"Error scraping images: {e}")
        return jsonify({'error': 'Failed to scrape images'}), 500

if __name__ == '__main__':
    port = 5001
    app.run(host='localhost', port=port, debug=True)
