from flask import Flask, request, jsonify, render_template
import os
from dotenv import load_dotenv
import requests
import base64
import csv
import io

load_dotenv()

app = Flask(__name__)

JIRA_BASE_URL = os.getenv('JIRA_BASE_URL')
JIRA_EMAIL = os.getenv('JIRA_EMAIL')
JIRA_API_TOKEN = os.getenv('JIRA_API_TOKEN')
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

# Helper: JIRA auth header
jira_auth = (JIRA_EMAIL, JIRA_API_TOKEN)
jira_headers = {
    'Accept': 'application/json',
    'Content-Type': 'application/json'
}

def get_jira_story(story_id):
    url = f"{JIRA_BASE_URL}/rest/api/3/issue/{story_id}"
    resp = requests.get(url, auth=jira_auth, headers=jira_headers)
    if resp.status_code == 200:
        data = resp.json()
        return {
            'id': data['key'],
            'summary': data['fields'].get('summary', ''),
            'description': data['fields'].get('description', {}).get('content', [{}])[0].get('content', [{}])[0].get('text', '')
        }
    return None

def generate_test_cases_with_gemini(story):
    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key=" + GEMINI_API_KEY
    prompt = f"Generate all possible unit test cases for the following user story. Return as a JSON array of objects with 'id' and 'description'. User Story: {story['summary']} {story['description']}"
    payload = {
        "contents": [{"parts": [{"text": prompt}]}]
    }
    resp = requests.post(url, json=payload)
    if resp.status_code == 200:
        try:
            candidates = resp.json()['candidates']
            text = candidates[0]['content']['parts'][0]['text']
            # Try to extract JSON from the response
            import json
            start = text.find('[')
            end = text.rfind(']') + 1
            if start != -1 and end != -1:
                test_cases = json.loads(text[start:end])
                return test_cases
        except Exception as e:
            pass
    return []

def publish_csv_to_jira(story_id, test_cases):
    # Create CSV in memory
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['ID', 'Description'])
    for tc in test_cases:
        writer.writerow([tc['id'], tc['description']])
    output.seek(0)
    files = {
        'file': (f"test_cases_{story_id}.csv", output.read(), 'text/csv')
    }
    url = f"{JIRA_BASE_URL}/rest/api/3/issue/{story_id}/attachments"
    headers = {
        "X-Atlassian-Token": "no-check",
        "Authorization": "Basic " + base64.b64encode(f"{JIRA_EMAIL}:{JIRA_API_TOKEN}".encode()).decode()
    }
    resp = requests.post(url, headers=headers, files=files)
    return resp.status_code == 200 or resp.status_code == 201

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/fetch_story', methods=['POST'])
def fetch_story():
    story_id = request.json.get('story_id')
    story = get_jira_story(story_id)
    if story:
        return jsonify({'success': True, 'story': story})
    else:
        return jsonify({'success': False, 'error': 'Story not found'}), 404

@app.route('/generate_tests', methods=['POST'])
def generate_tests():
    story = request.json.get('story')
    test_cases = generate_test_cases_with_gemini(story)
    if test_cases:
        return jsonify({'success': True, 'test_cases': test_cases})
    else:
        return jsonify({'success': False, 'error': 'Failed to generate test cases'}), 500

@app.route('/publish_tests', methods=['POST'])
def publish_tests():
    story_id = request.json.get('story_id')
    test_cases = request.json.get('test_cases')
    success = publish_csv_to_jira(story_id, test_cases)
    if success:
        return jsonify({'success': True, 'message': f'Test cases published for story {story_id}'})
    else:
        return jsonify({'success': False, 'message': 'Failed to publish test cases'}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)