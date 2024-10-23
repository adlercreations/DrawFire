import os
from flask import Flask, request, jsonify, make_response
from flask_cors import CORS
import openai
import cloudinary
import cloudinary.uploader
import cv2
import numpy as np
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__, static_folder='static', static_url_path='/static')
CORS(app, resources={r"/*": {"origins": "http://localhost:3000"}})

cloudinary.config( 
    cloud_name=os.getenv('CLOUDINARY_CLOUD_NAME'),
    api_key=os.getenv('CLOUDINARY_API_KEY'),
    api_secret=os.getenv('CLOUDINARY_API_SECRET')
)
if not os.getenv('CLOUDINARY_CLOUD_NAME') or not os.getenv('CLOUDINARY_API_KEY') or not os.getenv('CLOUDINARY_API_SECRET'):
    raise ValueError('Cloudinary configuration is missing or incomplete')



# optimize_url, _ = cloudinary_url("shoes", fetch_format="auto", quality="auto")
# print(optimize_url)


# auto_crop_url, _ = cloudinary_url("shoes", width=500, height=500, crop="auto", gravity="auto")
# print(auto_crop_url)

openai.api_key = os.getenv("OPENAI_API_KEY")

images = []  # Store uploaded images in memory (or database in the future)


def analyze_drawing(image_path):
    """Analyze the drawing using OpenCV to generate metadata."""
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


@app.route('/upload', methods=['POST'])
def upload_image():
    """Upload the image to Cloudinary and store its URL."""
    if 'image' not in request.files:
        return make_response(jsonify({"error": "No image file provided"}), 400)

    file = request.files['image']
    upload_result = cloudinary.uploader.upload(file)
    image_url = upload_result['secure_url']
    images.append({'url': image_url})

    return jsonify({'message': 'Image uploaded successfully!', 'url': image_url}), 200


@app.route('/improve', methods=['POST'])
def improve_image():
    """Generate suggestions using OpenAI based on the drawing description and metadata."""
    data = request.json
    image_url = data.get('image_url')
    drawing_description = data.get('description')

    # Download the image from Cloudinary and analyze it
    image_path = f'static/temp_image.jpg'
    os.system(f'wget -O {image_path} {image_url}')
    metadata = analyze_drawing(image_path)

    # Generate suggestions from OpenAI
    prompt = (
        f"My drawing: {drawing_description}. "
        f"It has {metadata['contour_count']} primary shapes and the style is {metadata['drawing_style']}. "
        "How can I improve it?"
    )

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an expert artist and illustrator."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=150
        )
        suggestions = response.choices[0].message['content']
        return jsonify({"suggestion": suggestions}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/submitted', methods=['GET'])
def get_images():
    """Return all uploaded images."""
    return jsonify(images), 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)


# from flask import Flask, request, jsonify, make_response
# from flask_cors import CORS

# app = Flask(__name__, static_folder='static', static_url_path='/static')

# # Allow requests from localhost:3000
# CORS(app, resources={r"/*": {"origins": "http://localhost:3000"}})

# images = []

# @app.before_request
# def log_request_info():
#     print(f"Method: {request.method}, Path: {request.path}")
#     print(f"Headers: {request.headers}")
#     print(f"Data: {request.data}")

# @app.route('/upload', methods=['POST', 'OPTIONS'])
# def upload_image():
#     if request.method == 'OPTIONS':
#         response = make_response()
#         response.headers['Access-Control-Allow-Origin'] = 'http://localhost:3000'
#         response.headers['Access-Control-Allow-Methods'] = 'POST, OPTIONS'
#         response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
#         return response

#     if 'image' not in request.files:
#         return make_response(jsonify({"error": "No image file provided"}), 400)

#     file = request.files['image']
#     url = f"http://localhost:8000/static/{file.filename}"
#     file.save(f"static/{file.filename}")
#     images.append({'url': url})

#     response = make_response(jsonify({'message': 'Image uploaded successfully!'}))
#     response.headers['Access-Control-Allow-Origin'] = 'http://localhost:3000'
#     return response

# @app.route('/submitted', methods=['GET'])
# def get_images():
#     response = make_response(jsonify(images))
#     response.headers['Access-Control-Allow-Origin'] = 'http://localhost:3000'
#     return response

# if __name__ == '__main__':
#     # Ensure Flask runs on all network interfaces (0.0.0.0) and port 5000
#     app.run(host='0.0.0.0', port=8000, debug=True)

