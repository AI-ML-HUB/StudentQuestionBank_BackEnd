
import pytesseract
from PIL import Image
from openai import OpenAI
import base64

from firebase_functions.params import IntParam, StringParam


OPENAI_API_KEY = StringParam("OPENAI_API_KEY")

def getText() :
    return "Hello World! OpenAI Question Bank"


# Extract text from image using Tesseract
def extract_text_from_image(image_path):
    image = Image.open(image_path)
    text = pytesseract.image_to_string(image)
    return text

# Process text to extract questions using GPT API
def get_questions_from_text(text):
    
    client = OpenAI(api_key=OPENAI_API_KEY)
    prompt = f"Extract and format questions from the following text:\n\n{text}\n\nReturn only the questions, one per line."
    try:
        response = openai.Completion.create(
            model="text-davinci-003",
            prompt=prompt,
            max_tokens=500
        )
        questions = response.choices[0].text.strip().split("\n")
        return [q.strip() for q in questions if q.strip()]
    except Exception as e:
        print(f"Error with OpenAI API: {e}")
        return []
    
# Function to encode the image
def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")
    
# Process text to extract questions using GPT API
def get_questions_from_image(image_path):
    # Getting the base64 string
    base64_image = encode_image(image_path)
    
    client = OpenAI(api_key=OPENAI_API_KEY)
    try:
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
                            "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"},
                        },
                    ],
                }
            ],
        )
        questions = response.choices[0].text.strip().split("\n")
        return [q.strip() for q in questions if q.strip()]
    except Exception as e:
        print(f"Error with OpenAI API: {e}")
        return []


def process_file(file):
    print(f"Processing file: {file['name']} (ID: {file['id']})")
    
    #image file downloaded with fileid as name of the file
    questions = get_questions_from_image(file['id'])
    
    print(questions)