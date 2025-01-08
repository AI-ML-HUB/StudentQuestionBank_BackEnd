from flask import Flask, request, jsonify
from openai import OpenAI
import os
from dotenv import load_dotenv
import base64
import os
import traceback

from pydantic import BaseModel


# Load environment variables from .env file
load_dotenv()

class Question(BaseModel):
    question_statement : str
    options : list[str]
    
    
class QuestionList(BaseModel):
    questions : list[Question]

# Get OpenAI API key from environment
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def get_question():
    try:
        
        # Getting the base64 string
        base64_image = encode_image('1x7A4hzlAVkMuJsfPJ62TQfiwQbCWQoHf')
        # Query OpenAI API
        response = client.beta.chat.completions.parse(
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
                                "detail": "high"
                            },
                        },
                    ],
                }
            ],
            response_format=QuestionList
        )

        # Extract the answer
        parsed_response = response.choices[0].message.parsed
        questions = parsed_response.questions
        print(f"Type of questions : {type(questions)}")

        return questions

    except Exception as e:
        return ''.join(traceback.format_exception(None, e, e.__traceback__))

# Function to encode the image
def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")
# Run the server
if __name__ == '__main__':
    print(get_question())
