# AI-Powered JIRA Test Case Generator

This web application automates the process of creating and managing test cases for JIRA user stories. It uses the Google Gemini AI to generate functional test cases based on a story's summary and description, creates them in Zephyr Scale, and links them back to the original JIRA story.

## Features

-   **Fetch JIRA Story:** Enter a JIRA story key to fetch its details, including summary and a fully-formatted description.
-   **AI-Powered Test Case Generation:** Automatically generate relevant and detailed functional test cases using Google's Gemini 1.5 Flash model.
-   **Zephyr Scale Integration:** Create the generated test cases directly in your Zephyr Scale project.
-   **Automated JIRA Linking:** Automatically link the newly created Zephyr test cases back to the corresponding JIRA story.
-   **Interactive UI:** A simple, clean web interface to manage the entire workflow.

## Tech Stack

-   **Backend:** Python with Flask
-   **Frontend:** HTML, Bootstrap, jQuery
-   **APIs:**
    -   JIRA REST API
    -   Google Gemini API
    -   Zephyr Scale API

## Setup and Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/tarunbajpai1416/AI_JIRA_POC.git
    cd AI_JIRA_POC
    ```

2.  **Create a virtual environment and install dependencies:**
    ```bash
    # For Windows
    python -m venv venv
    venv\Scripts\activate

    # For macOS/Linux
    python3 -m venv venv
    source venv/bin/activate

    # Install packages
    pip install -r requirements.txt
    ```

## Configuration

Before running the application, you need to set up your environment variables.

1.  Create a file named `.env` in the root of the project.
2.  Add your credentials and keys to the `.env` file:

    ```env
    # JIRA Configuration
    JIRA_BASE_URL="https://your-domain.atlassian.net"
    JIRA_EMAIL="your-jira-email@example.com"
    JIRA_API_TOKEN="your-jira-api-token"

    # Google Gemini API Key
    GEMINI_API_KEY="your-gemini-api-key"

    # Zephyr Scale Configuration
    ZEPHYR_BASE="https://api.zephyrscale.smartbear.com/v2"
    ZEPHYR_API_TOKEN="your-zephyr-scale-api-token"
    ZEPHYR_PROJECT_KEY="YOUR_PROJECT_KEY" # e.g., USERSTORY
    ```

## Usage

1.  **Run the Flask application:**
    ```bash
    python app.py
    ```

2.  Open your web browser and navigate to `http://127.0.0.1:5000`.

3.  Enter a JIRA story key (e.g., `USERSTORY-164`) and click **"Fetch Story"**.

4.  Review the generated test cases.

5.  Click **"Create Test Cases in Zephyr"** to create and link the test cases in Zephyr Scale.

This project provides a Python-based web utility to automate the generation of unit test cases for JIRA user stories using Gemini 1.5 Flash. It features a simple HTML/jQuery frontend for user interaction.

## Features
- Enter a JIRA story ID to fetch its details.
- Automatically generate all possible unit test cases for the story using Gemini 1.5 Flash.
- Display the story details and generated test cases in a user-friendly web interface.
- Publish the generated test cases as a CSV file attached to the JIRA story.

## Tech Stack
- **Backend:** Python, Flask
- **Frontend:** HTML, jQuery, Bootstrap (optional for styling)
- **APIs:** JIRA REST API, Gemini 1.5 Flash API

## Prerequisites
- Python 3.8+
- JIRA account with API access
- Gemini 1.5 Flash API key

## Setup
1. **Clone the repository:**
   ```bash
   git clone <repo-url>
   cd <repo-directory>
   ```
2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
3. **Configure environment variables:**
   Create a `.env` file or set the following environment variables:
   - `JIRA_BASE_URL` (e.g., https://your-domain.atlassian.net)
   - `JIRA_EMAIL`
   - `JIRA_API_TOKEN`
   - `GEMINI_API_KEY`

4. **Run the application:**
   ```bash
   python app.py
   ```
5. **Access the UI:**
   Open your browser and go to `http://localhost:5000`

## Usage
1. Enter a JIRA story ID in the input field and click "Fetch".
2. Review the fetched story details.
3. View the generated unit test cases in the table.
4. Click "Publish" to attach the test cases as a CSV to the JIRA story.

## File Structure
- `app.py` - Main Flask backend
- `templates/` - HTML templates
- `static/` - Static files (JS, CSS)
- `requirements.txt` - Python dependencies

## Notes
- Ensure your JIRA account has permission to add attachments to stories.
- Gemini 1.5 Flash API usage may incur costs or rate limits.

## License
MIT 