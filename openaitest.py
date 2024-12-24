from flask import Flask, request, jsonify
from openai import OpenAI
import os
from dotenv import load_dotenv


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

        # Query OpenAI API
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": f"Explain step-by-step how to solve this question: {question}"}],
            max_tokens=500,
            temperature=0.7
            )

        # Extract the answer
        answer = response.choices[0].message.content

        return jsonify({"question": question, "answer": answer}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Run the server
if __name__ == '__main__':
    app.run(debug=True)
