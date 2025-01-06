
import pytesseract
from PIL import Image
import openai

def getText() :
    return "Hello World! OpenAI Question Bank"


# Extract text from image using Tesseract
def extract_text_from_image(image_path):
    image = Image.open(image_path)
    text = pytesseract.image_to_string(image)
    return text

# Process text to extract questions using GPT API
def get_questions_from_text(text):
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


def process_file(file):
    print(f"Processing file: {file['name']} (ID: {file['id']})")