import openai
import pyautogui
import time
import os
from PIL import Image
import pytesseract
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from dotenv import load_dotenv
from google.cloud import vision
import io
from google.api_core.exceptions import GoogleAPIError

# Load environment variables from .env file
load_dotenv(".env")

# Get your OpenAI API key from environment variable
openai_api_key = os.getenv("OPENAI_API_KEY")

# Initialize OpenAI client
openai.api_key = openai_api_key

# Set the path to your Google Cloud service account JSON file
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "path_to_your_service_account_json_file"

# Initialize Google Vision client
vision_client = vision.ImageAnnotatorClient()

# Email configuration for Gmail
smtp_server = 'smtp.gmail.com'
smtp_port = 587
smtp_username = os.getenv("SMTP_USERNAME")
smtp_password = os.getenv("SMTP_PASSWORD")
from_email = os.getenv("FROM_EMAIL")
to_email = os.getenv("TO_EMAIL")

def take_screenshot(region=None):
    # Create a directory to save screenshots if it doesn't exist
    screenshot_dir = "screenshots"
    if not os.path.exists(screenshot_dir):
        os.makedirs(screenshot_dir)
    
    # Take a screenshot of the specified region
    screenshot = pyautogui.screenshot(region=region)
    
    # Save the screenshot with a timestamp
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    screenshot_path = os.path.join(screenshot_dir, f"screenshot_{timestamp}.png")
    screenshot.save(screenshot_path)
    
    return screenshot_path

def extract_text_from_image(image_path):
    image = Image.open(image_path)
    text = pytesseract.image_to_string(image)
    return text

def classify_question(text):
    if "multiple choice" in text.lower():
        return "multiple_choice"
    elif "drag and drop" in text.lower():
        return "drag_and_drop"
    elif "code" in text.lower() or "program" in text.lower():
        return "code_interpretation"
    elif "network" in text.lower() or "router" in text.lower() or "configuration" in text.lower():
        return "networking"
    elif "security" in text.lower() or "vulnerability" in text.lower() or "penetration" in text.lower():
        return "security"
    else:
        return "general"

def generate_prompt(text, question_type):
    if question_type == "multiple_choice":
        prompt = f"Provide the correct answer for the following multiple-choice question. Use only the given information.\n\n{text}"
    elif question_type == "drag_and_drop":
        prompt = f"Provide the correct arrangement for the following drag-and-drop question. Use only the given information.\n\n{text}"
    elif question_type == "code_interpretation":
        prompt = f"Provide the correct interpretation and output for the following code interpretation question. Use only the given information.\n\n{text}"
    elif question_type == "networking":
        prompt = f"Provide the correct configuration or answer for the following networking question. Use only the given information.\n\n{text}"
    elif question_type == "security":
        prompt = f"Provide the correct answer for the following security-related question. Use only the given information.\n\n{text}"
    else:
        prompt = f"Answer the following question appropriately. Use only the given information.\n\n{text}"
    return prompt

def send_text_to_chatgpt(text, question_type):
    prompt = generate_prompt(text, question_type)
    
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a knowledgeable assistant in IT, networking, security, and coding. Provide concise answers based solely on the provided information. Explain only if explicitly asked."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=1500,
        n=1,
        stop=None,
        temperature=0.7,
    )
    
    return response.choices[0].message['content'].strip()

def describe_image_with_vision_api(image_path):
    with io.open(image_path, 'rb') as image_file:
        content = image_file.read()
    image = vision.Image(content=content)
    response = vision_client.label_detection(image=image)
    labels = response.label_annotations
    
    description = 'Image Description:\n'
    description += '\n'.join([label.description for label in labels])
    
    return description

def send_email(subject, body, attachment_path):
    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = to_email
    msg['Subject'] = subject

    msg.attach(MIMEText(body, 'plain'))

    if attachment_path:
        with open(attachment_path, 'rb') as attachment:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(attachment.read())
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', f'attachment; filename= {os.path.basename(attachment_path)}')
            msg.attach(part)

    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()
        server.login(smtp_username, smtp_password)
        server.sendmail(from_email, to_email, msg.as_string())

if __name__ == "__main__":
    # Define the region to capture (left, top, width, height)
    # Adjust the coordinates and size as per your screen setup
    region = (0, 100, 1920, 880)  # Example: Adjust as needed

    screenshot_path = take_screenshot(region=region)
    print(f"Screenshot saved at {screenshot_path}")
    
    extracted_text = extract_text_from_image(screenshot_path)
    print(f"Extracted text: {extracted_text}")
    
    if extracted_text.strip():
        question_type = classify_question(extracted_text)
        try:
            chatgpt_response = send_text_to_chatgpt(extracted_text, question_type)
            print(f"ChatGPT Response: {chatgpt_response}")
            
            email_subject = "ChatGPT Processed Screenshot"
            email_body = f"ChatGPT Response:\n{chatgpt_response}"
            
            send_email(email_subject, email_body, screenshot_path)
            print(f"Email sent to {to_email}")
        except openai.OpenAIError as e:
            print(f"OpenAI API error: {e}")
    else:
        try:
            image_description = describe_image_with_vision_api(screenshot_path)
            print(f"Image Description: {image_description}")
            
            email_subject = "Google Vision API Described Screenshot"
            email_body = f"Image Description:\n{image_description}"
            
            send_email(email_subject, email_body, screenshot_path)
            print(f"Email sent to {to_email}")
        except GoogleAPIError as e:
            print(f"Google Vision API error: {e}")
