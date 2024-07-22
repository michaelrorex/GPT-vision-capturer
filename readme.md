v0.1.0

# Automated Screenshot Processing

## Description
This project automates the process of taking screenshots, extracting text using Tesseract-OCR, and analyzing images with Google Cloud Vision. It also includes functionality to interact with OpenAI's ChatGPT and send results via email using Gmail. This tool can be highly useful for automating documentation processes, archiving, or even monitoring specific areas of your screen for changes and extracting useful insights.

### Stream Deck Integration
A practical use case for this tool is converting the Python script into a batch file and assigning it as a button prompt on Stream Deck. This integration allows users to activate the script with a single button press, making it exceptionally convenient for live streamers, content creators, or anyone needing to quickly capture and process screen content without interrupting their workflow.

## Prerequisites
Before you can run this script, there are several setup steps and configurations you need to complete:

### 1. Environment Setup
#### Python Installation
Ensure that Python is installed on your machine. This project is compatible with Python 3.7 and above.

#### Clone the Repository
Clone this repository to your local machine:

### 2. Dependency Installation
Install all required Python libraries:

### 3. Configure Environment Variables
Create a `.env` file in the project root directory and populate it with your credentials and API keys:

OPENAI_API_KEY=your_openai_api_key_here
SMTP_PASSWORD=your_app_password_here
SMTP_USERNAME=your_email_username_here
FROM_EMAIL=your_email_here
TO_EMAIL=email_to_receive_notifications_here
GOOGLE_CREDENTIALS_PATH=path_to_your_google_service_account_json

## Configuration Steps
To ensure the script works correctly, follow these detailed setup instructions:

### Setting Up Tesseract-OCR
1. **Download and Install Tesseract-OCR**: [Download link](https://github.com/tesseract-ocr/tesseract)
    - Install Tesseract and ensure it is added to your system's PATH.
    - You can verify the installation by running `tesseract -v` in your command prompt.

### Configuring Google Cloud Vision
1. **Enable Google Cloud Vision API**: Make sure that the Google Cloud Vision API is enabled in your Google Cloud Console.
2. **Service Account and JSON Key**:
    - Navigate to IAM & Admin > Service Accounts in your Google Cloud Console.
    - Create a new service account, and download the JSON key file.
    - Place the JSON file in a secure location and reference its path in your `.env` file.

3. **Enable Billing**: Ensure that billing is enabled on your Google Cloud project to use the Vision API.

### Setting Up Email Notifications
1. **Enable 2-Factor Authentication** on your Google account.
2. **Generate an App Password**:
    - Visit https://myaccount.google.com/u/4/apppasswords
    - Select 'Other' as the app and type 'Python'.
    - Use the generated password in your `.env` file as `SMTP_PASSWORD`.

## Obtaining and Configuring OpenAI API Key
To utilize OpenAI services, such as ChatGPT for processing the extracted text, you will need an OpenAI API key. Follow these steps to obtain and configure it:

### Getting Your OpenAI API Key
1. **Create an OpenAI Account**:
   - Visit [OpenAI's official website](https://www.openai.com/) and sign up for an account.
   - After signing up, navigate to the API section in your account dashboard.

2. **Subscribe to an API Plan**:
   - Choose an API plan that suits your needs. OpenAI offers various pricing tiers, including a free trial tier which is suitable for development and testing.

3. **Access Your API Key**:
   - Once you have subscribed to a plan, you can find your API key in the API section. Copy this key as you will need it for the next steps.

### Configuring Your OpenAI API Key
- Add your OpenAI API key to your `.env` file as follows:
- This key will be used by the script to authenticate API requests to OpenAI.

### Using OpenAI API in the Script
The script uses the OpenAI API key to send requests to OpenAI's ChatGPT for interpreting and processing text extracted from screenshots. This interaction allows the script to utilize advanced AI for text analysis, which can be beneficial for various applications like data extraction, summarization, or even generating responses based on the screenshot content.

## Running the Script
Once all configurations are done, including the OpenAI API key setup, you can run the script but make sure that all environment variables are set correctly in your `.env` file before running the script to avoid any unauthorized or failed requests.

## Troubleshooting
- **API Key Issues**: If you encounter any issues related to the OpenAI API, such as `401 Unauthorized` errors, check to ensure that your API key is correctly set in the `.env` file and that it hasn't expired or been revoked.
- **API Limitations**: Be aware of the API usage limits based on your subscription plan. Exceeding these limits might result in temporary blocking of API access.

## Contributing
Contributions to this project are welcome! Please fork the repository and submit a pull request with your enhancements.

## License
This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details.
