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
import tensorflow as tf
from torchvision import transforms
from PIL import Image
import torch
import torch.nn.functional as F
import torchvision.models as models

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

        # Detect edges and contours
        edges = cv2.Canny(image, threshold1=30, threshold2=100)
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        contour_count = len(contours)
        # Calculate line coverage (amount of non-white pixels)
        non_zero_pixels = np.count_nonzero(edges)
        line_coverage = non_zero_pixels / edges.size
        # Calculate line using Hough
        lines = cv2.HoughLines(edges, 1, np.pi / 180, threshold=150)
        line_count = len(lines) if lines is not None else 0
        # Detect corners using haerris
        corners = cv2.cornerHarris(edges, 2, 3, 0.04)
        corner_count = np.count_nonzero(corners > 0.01 * corners.max())
        # Calculate aspect ratio and bounding box
        x, y, w, h = cv2.boundingRect(edges)
        aspect_ratio = round(w / h, 2)

        # TensorFlow analysis
        tf_analysis = tensorflow_image_analysis(image_path)

        # PyTorch analysis
        torch_analysis = pytorch_image_analysis(image_path)

        return {
            "contour_count": contour_count,
            "line_coverage": round(line_coverage, 2),
            "line_count": line_count,
            "corner_count": corner_count,
            "aspect_ratio": aspect_ratio,
            "drawing_style": "detailed" if line_coverage > 0.1 else "minimalistic",
            "tensorflow_analysis": tf_analysis,
            "pytorch_analysis": torch_analysis
        }
    except Exception as e:
        raise RuntimeError(f"Error during image analysis: {str(e)}")
    

def tensorflow_image_analysis(image_path):
    """Use TensorFlow to analyze the image and return top classification predictions."""
    try:
        # Load image and prepare it for the model
        image = tf.keras.preprocessing.image.load_img(image_path, target_size=(224, 224))
        input_arr = tf.keras.preprocessing.image.img_to_array(image)
        input_arr = np.array([input_arr])  # Convert single image to a batch.
        
        # Load a MobileNetV2 model pretrained on ImageNet
        model = tf.keras.applications.MobileNetV2(weights='imagenet')
        predictions = model.predict(input_arr)
        
        # Decode predictions to get top classes
        decoded_predictions = tf.keras.applications.mobilenet_v2.decode_predictions(predictions, top=3)
        
        # Extract labels and confidence scores
        return [{"label": label, "confidence": float(conf)} for (_, label, conf) in decoded_predictions[0]]
    except Exception as e:
        print(f"Error during TensorFlow analysis: {str(e)}")
        return []

def pytorch_image_analysis(image_path):
    """Use PyTorch to analyze the image and return feature vector."""
    try:
        # Load image and apply transforms
        image = Image.open(image_path).convert('RGB')
        transform = transforms.Compose([
            transforms.Resize(256),
            transforms.CenterCrop(224),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
        ])
        image = transform(image).unsqueeze(0)  # Add batch dimension
        
        # Load a pretrained ResNet model
        model = models.resnet50(pretrained=True)
        model.eval()  # Set model to evaluation mode
        with torch.no_grad():
            features = model(image)
        
        # Convert tensor to list for easy JSON serialization
        return features.squeeze().tolist()
    except Exception as e:
        print(f"Error during PyTorch analysis: {str(e)}")
        return []
    
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
    initial_prompt = data.get('initial_prompt', '')

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
    # prompt = (
    #     f"This is an unfinished drawing with the following details:\n"
    #     f"- Contour count: {metadata['contour_count']}\n"
    #     f"- Line coverage: {metadata['line_coverage']}\n"
    #     f"- Aspect ratio: {metadata['aspect_ratio']}\n"
    #     f"- Style: {metadata['drawing_style']}\n"
    #     f"- TensorFlow Analysis (Top 3 labels): {metadata['tensorflow_analysis']}\n"
    #     f"- PyTorch Feature Vector (first 10 elements): {metadata['pytorch_analysis'][:10]}\n"
    #     "Provide feedback on:\n"
    #     "1. Improving composition and element placement.\n"
    #     "2. Refining the character's anatomy and poses.\n"
    #     "3. Suggestions for enhancing storytelling through design elements.\n"
    #     "4. Recommendations for lighting, shading, and future details.\n"
    # )

    # print(f"Generated prompt for OpenAI: {prompt}")

    # # Generate suggestions using OpenAI API
    # try:
    #     response = client.chat.completions.create(
    #         model="gpt-4",
    #         messages=[
    #             {
    #                 "role": "system",
    #                 "content": (
    #                     "You are an expert artist and illustrator. You will receive technical metadata "
    #                     "about the drawings, and based on that, you should provide specific feedback "
    #                     "to improve composition, lighting, anatomy, and storytelling. Avoid generic responses."
    #                 ),
    #             },
    #             {"role": "user", "content": prompt}
    #         ]
    #     )
    #     print(f"OpenAI API response: {response}")
    #     suggestions = response.choices[0].message.content
    #     return jsonify({"suggestion": suggestions}), 200
    # # except OpenAIError as e:
    # #     print(f"OpenAI API error: {e}")
    # #     return jsonify({"error": f"OpenAI API error: {str(e)}"}), 500
    # except Exception as e:
    #     print(f"Error generating suggestions: {e}")
    #     return jsonify({"error": f"Unexpected error: {str(e)}"}), 500

    # Adjusted prompt construction
    # 
    
    prompt = (
        f"User's Description of the Comic Page: {initial_prompt}\n\n"
        f"Technical Analysis of the Drawing:\n"
        f"- Contour count: {metadata['contour_count']}\n"
        f"- Line coverage: {metadata['line_coverage']}\n"
        f"- Aspect ratio: {metadata['aspect_ratio']}\n"
        f"- Style: {metadata['drawing_style']}\n"
        f"- TensorFlow Analysis (Top 3 labels): {metadata['tensorflow_analysis']}\n"
        f"- PyTorch Feature Vector (summary): {metadata['pytorch_analysis'][:10]}\n\n"
        "Please provide specific and creative feedback on the following aspects:\n"
        "1. Enhancing composition and panel layout for storytelling impact.\n"
        "2. Improving the anatomy and expressiveness of the characters, focusing on anthropomorphic details.\n"
        "3. Suggestions for refining storytelling elements that match the user description.\n"
        "4. Advice on adding shading, lighting, and final touches to bring depth to the artwork.\n"
    )

    # Prompt OpenAI with a focus on comic art feedback
    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are an expert comic book artist and illustrator. Use the provided technical data and user description "
                        "to give creative, specific feedback on composition, character anatomy, storytelling. Provide targeted feedback on composition, character anatomy, storytelling, and finishing touches. "
                        "Focus on enhancing the comic's storyteelling anf visual impact."
                    ),
                },
                {"role": "user", "content": prompt}
            ]
        )
        print(f"OpenAI API response: {response}")
        suggestions = response.choices[0].message.content
        return jsonify({"suggestion": suggestions}), 200
    except Exception as e:
        print(f"Error generating suggestions: {e}")
        return jsonify({"error": f"Unexpected error: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)  