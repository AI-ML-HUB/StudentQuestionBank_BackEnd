from flask import Flask, request, jsonify
from openai import OpenAI
import os
from dotenv import load_dotenv
import base64


# Load environment variables from .env file
load_dotenv()


client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
import os

# Get OpenAI API key from environment

# Initialize Flask app
app = Flask(__name__)

@app.route('/')
def home():
    return "Hello, Google Cloud Workstation!"

# Route to handle question solving
@app.route('/solve-question', methods=['POST'])
def solve_question():
    try:
        # Get the question from the request
        data = request.json
        question = data.get('question')

        if not question:
            return jsonify({"error": "Question is required"}), 400

        # Getting the base64 string
        base64_image = encode_image('1x7A4hzlAVkMuJsfPJ62TQfiwQbCWQoHf')
        # Query OpenAI API
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "Extract and format questions from the image",
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}",                                
                                "detail": "low"
                            },
                        },
                    ],
                }
            ],
        )

        # Extract the answer
        answer = response.choices[0].message.content

        return jsonify({"question": question, "answer": answer}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Function to encode the image
def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")
# Run the server
if __name__ == '__main__':
    app.run(debug=True)
