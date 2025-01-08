
from openai import OpenAI
import base64

from firebase_functions.params import IntParam, StringParam


from questions import QuestionList


OPENAI_API_KEY = StringParam("OPENAI_API_KEY")

def getText() :
    return "Hello World! OpenAI Question Bank"

    
# Function to encode the image
def encode_image(file_bytes):
    return base64.b64encode(file_bytes).decode("utf-8")
    
# Process text to extract questions using GPT API
def get_questions_from_image(file_bytes):
    # Getting the base64 string
    base64_image = encode_image(file_bytes)
    
    client = OpenAI(api_key=OPENAI_API_KEY.value)
    try:
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
        parsed_response = response.choices[0].message.parsed
        questions = parsed_response.questions
        
        return questions
    except Exception as e:
        print(f"Error with OpenAI API: {e}")
        return []


def process_file(file, file_bytes):
    print(f"Processing file: {file['name']} (ID: {file['id']})")
    
    #image file downloaded with fileid as name of the file
    questions = get_questions_from_image(file_bytes)
    
    return questions