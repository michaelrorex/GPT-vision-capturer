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

# Load environment variables
load_dotenv()

# Get your OpenAI API key from environment variable
openai_api_key = os.getenv("OPENAI_API_KEY")

# Initialize OpenAI client
openai.api_key = openai_api_key

# Set the path to your Google Cloud service account JSON file
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "File_Path_to_.json"

# Initialize Google Vision client
vision_client = vision.ImageAnnotatorClient()

# Email configuration for Gmail
smtp_server = 'smtp.gmail.com'
smtp_port = 587
smtp_password = os.getenv("SMTP_PASSWORD")
smtp_username = os.getenv("SMTP_USERNAME")
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

def send_text_to_chatgpt(text):
    prompt = (
        "For each multiple-choice question, provide the correct answer followed by an explanation. "
        "If the question is long-form, just provide the explanation.\n\n"
        f"Text from screenshot:\n{text}"
    )
    
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
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
        try:
            chatgpt_response = send_text_to_chatgpt(extracted_text)
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
