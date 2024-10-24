import os
from flask import Flask, request, jsonify, make_response
from flask_cors import CORS
from openai import OpenAI
import cloudinary
import cloudinary.uploader
import cv2
import numpy as np
from dotenv import load_dotenv
import requests

# Load environment variables from .env
load_dotenv()

# Initialize Flask app
app = Flask(__name__, static_folder='static', static_url_path='/static')
CORS(app, resources={r"/*": {"origins": "http://localhost:3000"}})

# Configure Cloudinary
cloudinary.config(
    cloud_name=os.getenv('CLOUDINARY_CLOUD_NAME'),
    api_key=os.getenv('CLOUDINARY_API_KEY'),
    api_secret=os.getenv('CLOUDINARY_API_SECRET')
)

# Ensure Cloudinary configuration is present
if not all([os.getenv('CLOUDINARY_CLOUD_NAME'),
            os.getenv('CLOUDINARY_API_KEY'),
            os.getenv('CLOUDINARY_API_SECRET')]):
    raise ValueError("Cloudinary configuration is missing or incomplete.")

# # Configure OpenAI API
# openai.api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY"),
)

print(f"OpenAI API Key: {os.getenv('OPENAI_API_KEY')}")

# Store uploaded images in memory
images = []

def analyze_drawing(image_path):
    """Analyze the drawing using OpenCV to generate metadata."""
    try:
        image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
        edges = cv2.Canny(image, threshold1=30, threshold2=100)
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        contour_count = len(contours)
        non_zero_pixels = np.count_nonzero(edges)
        line_coverage = non_zero_pixels / edges.size

        return {
            "contour_count": contour_count,
            "line_coverage": round(line_coverage, 2),
            "drawing_style": "detailed" if line_coverage > 0.1 else "minimalistic"
        }
    except Exception as e:
        raise RuntimeError(f"Error during image analysis: {str(e)}")

@app.route('/upload', methods=['POST'])
def upload_image():
    """Upload the image to Cloudinary and store its URL."""
    if 'image' not in request.files:
        return make_response(jsonify({"error": "No image file provided"}), 400)

    file = request.files['image']
    try:
        upload_result = cloudinary.uploader.upload(file)
        image_url = upload_result['secure_url']
        images.append({'url': image_url})

        return jsonify({'message': 'Image uploaded successfully!', 'url': image_url}), 200
    except Exception as e:
        return jsonify({"error": f"Failed to upload image: {str(e)}"}), 500

@app.route('/submitted', methods=['GET'])
def get_images():
    """Return all submitted images."""
    return jsonify(images), 200

@app.route('/improve', methods=['POST'])
def improve_image():
    """Download the image, process it with OpenCV, and generate suggestions using OpenAI."""
    data = request.json
    image_url = data.get('image_url')

    print(f"Received image_url: {image_url}")

    # Download the image from Cloudinary
    image_path = 'static/temp_image.jpg'
    try:
        response = requests.get(image_url)
        response.raise_for_status()  # Raise an error for failed HTTP requests
        with open(image_path, 'wb') as f:
            f.write(response.content)
        print(f"Image downloaded successfully to {image_path}")
    except Exception as e:
        print(f"Failed to download image: {e}")
        return jsonify({"error": f"Failed to download image: {str(e)}"}), 500

    # Analyze the image using OpenCV
    try:
        metadata = analyze_drawing(image_path)
        print(f"Image analysis metadata: {metadata}")
    except RuntimeError as e:
        print(f"Image analysis failed: {e}")
        return jsonify({"error": str(e)}), 500

    # Create a prompt for OpenAI based on the image metadata
    prompt = (
        f"The drawing has {metadata['contour_count']} primary shapes and "
        f"the style is {metadata['drawing_style']}. How can I improve it?"
    )
    print(f"Generated prompt for OpenAI: {prompt}")

    # Generate suggestions using OpenAI API
    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an expert artist and illustrator."
                                              "Most of the images will be half done comic book pages."
                                              "Suggest improvements for anatomy, composition, lighting, "
                                              "camera angles, storytelling principles and design principles."},
                {"role": "user", "content": prompt}
            ],
        )
        print(f"OpenAI API response: {response}")
        suggestions = response.choices[0].message.content
        return jsonify({"suggestion": suggestions}), 200
    # except OpenAIError as e:
    #     print(f"OpenAI API error: {e}")
    #     return jsonify({"error": f"OpenAI API error: {str(e)}"}), 500
    except Exception as e:
        print(f"Error generating suggestions: {e}")
        return jsonify({"error": f"Unexpected error: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)