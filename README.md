# JIRA Story Unit Test Case Generator

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