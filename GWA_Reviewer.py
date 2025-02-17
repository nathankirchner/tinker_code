import os
import csv
import base64
import requests
from pathlib import Path

DEFAULT_IMAGE_DIR = os.path.join(os.getcwd(), "/IM_TEXT_DESCRIPTION")
DEFAULT_QUESTIONS_PATH = os.path.join(os.getcwd(), "questions_to_ask.txt")
OUTPUT_DIR = os.path.join(os.getcwd(), "OUTPUT")

def get_api_key():
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        api_key = input("Please enter your OpenAI API key: ")
    return api_key

def get_file_path(default_path, prompt_message):
    if os.path.exists(default_path):
        return default_path
    else:
        while True:
            user_path = input(f"{prompt_message}: ")
            if os.path.exists(user_path):
                return user_path
            print("Path not found. Please try again.")

def read_questions(questions_path):
    with open(questions_path, 'r') as file:
        return [line.strip() for line in file if line.strip()]

def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def analyze_image(image_path, questions, api_key):
    base64_image = encode_image(image_path)
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    payload = {
        "model": "gpt-4o-preview",
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "Please provide a detailed description of this image."},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                ]
            }
        ],
        "max_tokens": 500
    }
    
    # Get general description
    response = requests.post(
        "https://api.openai.com/v1/chat/completions",
        headers=headers,
        json=payload
    )
    
    if response.status_code != 200:
        raise Exception(f"API Error: {response.status_code} - {response.text}")
    
    response_data = response.json()
    if 'error' in response_data:
        raise Exception(f"API Error: {response_data['error']}")
        
    description = response_data['choices'][0]['message']['content']
    
    # Now get answers to specific questions
    answers = []
    for question in questions:
        payload["messages"][0]["content"][0]["text"] = question
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers,
            json=payload
        )
        
        if response.status_code != 200:
            raise Exception(f"API Error: {response.status_code} - {response.text}")
            
        response_data = response.json()
        if 'error' in response_data:
            raise Exception(f"API Error: {response_data['error']}")
            
        answers.append(response_data['choices'][0]['message']['content'])
    
    return description, answers

def main():
    # Create output directory if it doesn't exist
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # Get API key
    api_key = get_api_key()
    
    # Get paths
    image_dir = get_file_path(DEFAULT_IMAGE_DIR, "Enter the path to your images directory")
    questions_path = get_file_path(DEFAULT_QUESTIONS_PATH, "Enter the path to your questions file")
    
    # Read questions
    questions = read_questions(questions_path)
    
    # Prepare CSV files
    descriptions_file = os.path.join(OUTPUT_DIR, "images_descriptions.csv")
    responses_file = os.path.join(OUTPUT_DIR, "responses.csv")
    
    # Process images
    image_data = []
    for filename in os.listdir(image_dir):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
            print(f"Processing {filename}...")
            image_path = os.path.join(image_dir, filename)
            try:
                description, answers = analyze_image(image_path, questions, api_key)
                image_data.append({
                    'filename': filename,
                    'description': description,
                    'answers': answers
                })
            except Exception as e:
                print(f"Error processing {filename}: {str(e)}")
    
    # Save descriptions
    with open(descriptions_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Filename', 'Description'])
        for data in image_data:
            writer.writerow([data['filename'], data['description']])
    
    # Save responses
    with open(responses_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        header = ['Filename'] + [f'Q{i+1}' for i in range(len(questions))]
        writer.writerow(header)
        for data in image_data:
            writer.writerow([data['filename']] + data['answers'])
    
    print(f"\nAnalysis complete!")
    print(f"Descriptions saved to: {descriptions_file}")
    print(f"Responses saved to: {responses_file}")

if __name__ == "__main__":
    main()
