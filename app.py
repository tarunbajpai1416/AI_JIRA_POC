from flask import Flask, request, jsonify, render_template
import os
from dotenv import load_dotenv
import requests
import json
import re

load_dotenv()

app = Flask(__name__)

# --- Jira Config ---
JIRA_BASE_URL = os.getenv('JIRA_BASE_URL')
JIRA_EMAIL = os.getenv('JIRA_EMAIL')
JIRA_API_TOKEN = os.getenv('JIRA_API_TOKEN')
jira_auth = (JIRA_EMAIL, JIRA_API_TOKEN)
jira_headers = {
    'Accept': 'application/json',
    'Content-Type': 'application/json'
}

# --- Gemini Config ---
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

# --- Zephyr Scale Config ---
ZEPHYR_BASE = os.getenv("ZEPHYR_BASE")
ZEPHYR_API_TOKEN = os.getenv("ZEPHYR_API_TOKEN")
ZEPHYR_PROJECT_KEY = os.getenv("ZEPHYR_PROJECT_KEY")
zephyr_headers = {
    "Authorization": f"Bearer {ZEPHYR_API_TOKEN}",
    "Content-Type": "application/json"
}


# 1️⃣ Fetch Jira story
def get_jira_story(story_key):
    # Use 'renderedFields' to get description as HTML
    url = f"{JIRA_BASE_URL}/rest/api/3/issue/{story_key}?expand=renderedFields"
    resp = requests.get(url, auth=jira_auth, headers=jira_headers)
    if resp.status_code == 200:
        data = resp.json()
        # The rendered description is available in the 'renderedFields' object
        description = data.get('renderedFields', {}).get('description', 'Description not available.')
        summary_text = data.get('fields', {}).get('summary', 'Summary not available.')

        # The Gemini prompt needs a plain-text version of the description.
        # We will parse the ADF from the 'fields' object for this.
        plain_description = ""
        desc_data = data['fields'].get('description', {})
        if desc_data and 'content' in desc_data:
            for block in desc_data['content']:
                for inner in block.get('content', []):
                    if inner.get('type') == 'text':
                        plain_description += inner.get('text', '')
                plain_description += "\n" # Add a newline between paragraphs

        return {
            'key': data['key'],
            'id': data['id'],
            'summary': summary_text,
            'description': description, # This is the HTML version for the UI
            'plain_description': plain_description.strip() # Plain text for Gemini
        }
    return None
    return None


# 2️⃣ Generate test cases + steps from Gemini
def generate_test_cases_with_gemini(story):
    prompt = (
        "Generate functional test cases for the following Jira user story. "
        "For each test case, include: id, description, and steps "
        "(array of objects with fields: step, data, result). "
        "Return ONLY valid JSON. No markdown, no extra text.\n\n"
        f"Summary: {story['summary']}\nDescription: {story['plain_description']}"
    )

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    resp = requests.post(url, headers={'Content-Type': 'application/json'}, json=payload)

    if resp.status_code == 200:
        try:
            text = resp.json()['candidates'][0]['content']['parts'][0]['text']
            match = re.search(r"\[.*\]", text, re.DOTALL)
            if match:
                return json.loads(match.group(0))
        except Exception as e:
            print("Gemini parse error:", e)
    return []


# 3️⃣ Create test case in Zephyr Scale
def create_zephyr_scale_test_case(project_id, test_case):
    if not ZEPHYR_BASE or not ZEPHYR_API_TOKEN:
        print("Zephyr Scale configuration missing")
        return None
        
    url = f"{ZEPHYR_BASE}/testcases"
    payload = {
        "projectKey": ZEPHYR_PROJECT_KEY,
        "name": test_case['description'],  # Use description as the test case name
        "objective": test_case['description']  # Add objective field
    }
    print(f"Creating Zephyr test case: {payload}")
    print(f"URL: {url}")
    
    resp = requests.post(url, json=payload, headers=zephyr_headers)
    print(f"Zephyr response status: {resp.status_code}")
    print(f"Zephyr response text: {resp.text}")
    
    if resp.status_code in (200, 201):
        return resp.json().get("key")
    print("Error creating test case:", resp.status_code, resp.text)
    return None


# 4️⃣ Add steps to Zephyr Scale test case
def add_steps_to_zephyr_test_case(test_case_key, steps):
    for step in steps:
        payload = {
            "step": step.get('step', ''),
            "data": step.get('data', ''),
            "result": step.get('result', '')
        }
        url = f"{ZEPHYR_BASE}/testcases/{test_case_key}/teststeps"
        resp = requests.post(url, json=payload, headers=zephyr_headers)
        if resp.status_code not in (200, 201):
            print(f"Error adding step to {test_case_key}:", resp.status_code, resp.text)


# 5️⃣ Link test case to Jira story
def link_test_case_to_jira_issue(test_case_key, jira_issue_id):
    url = f"{ZEPHYR_BASE}/testcases/{test_case_key}/links/issues"
    payload = {"issueId": int(jira_issue_id)}  # Ensure issueId is an integer
    print(f"Linking test case {test_case_key} to JIRA issue {jira_issue_id}")
    print(f"Link URL: {url}")
    print(f"Link payload: {payload}")
    
    resp = requests.post(url, json=payload, headers=zephyr_headers)
    print(f"Link response status: {resp.status_code}")
    print(f"Link response text: {resp.text}")
    
    if resp.status_code in (200, 201):
        print(f"Successfully linked {test_case_key} to JIRA issue {jira_issue_id}")
        return True
    else:
        print(f"Failed to link {test_case_key} to JIRA issue {jira_issue_id}")
        return False


# 6️⃣ Orchestrator function
def process_story_to_zephyr(story_key, project_id):
    story = get_jira_story(story_key)
    if not story:
        return {"success": False, "error": "Story not found in Jira"}

    test_cases = generate_test_cases_with_gemini(story)
    if not test_cases:
        return {"success": False, "error": "No test cases generated"}

    created = []
    for tc in test_cases:
        tc_key = create_zephyr_scale_test_case(project_id, tc)
        if tc_key:
            if 'steps' in tc and isinstance(tc['steps'], list):
                add_steps_to_zephyr_test_case(tc_key, tc['steps'])
            if link_test_case_to_jira_issue(tc_key, story['id']):
                created.append(tc_key)

    return {"success": True, "created": created}


# Flask routes
@app.route('/')
def index():
    from flask import render_template
    return render_template('index.html')

@app.route('/fetch_story', methods=['POST'])
def fetch_story():
    story_id = request.json.get('story_id')
    story_data = get_jira_story(story_id)
    if story_data:
        return jsonify({"success": True, "story": story_data})
    else:
        return jsonify({"success": False, "message": "Story not found"})

@app.route('/generate_tests', methods=['POST'])
def generate_tests():
    story = request.json.get('story')
    test_cases = generate_test_cases_with_gemini(story)
    return jsonify({"success": True, "test_cases": test_cases})

@app.route('/publish_tests', methods=['POST'])
def publish_tests():
    story_id = request.json.get('story_id')
    test_cases = request.json.get('test_cases')
    # For now, just return success - you can implement CSV attachment logic here
    return jsonify({"success": True, "message": "Test cases published successfully!"})

@app.route('/create_zephyr_tests_ui', methods=['POST'])
def create_zephyr_tests_ui():
    story_key = request.json.get('story_key')
    test_cases = request.json.get('test_cases', [])
    project_id = request.json.get('project_id', 10000) # Note: project_id is legacy, projectKey is used

    if not ZEPHYR_PROJECT_KEY:
        return jsonify({"success": False, "message": "ZEPHYR_PROJECT_KEY is not configured in .env"})

    try:
        created_count = 0
        created_keys = []
        for test_case in test_cases:
            # Create test case in Zephyr Scale
            zephyr_key = create_zephyr_scale_test_case(project_id, test_case)
            if zephyr_key:
                created_keys.append(zephyr_key)
                # Add steps if available (for now, we'll create basic steps from description)
                basic_steps = [{"step": test_case['description'], "data": "", "result": "Expected result"}]
                add_steps_to_zephyr_test_case(zephyr_key, basic_steps)
                
                # Link to JIRA story
                story_data = get_jira_story(story_key)
                if story_data:
                    link_test_case_to_jira_issue(zephyr_key, story_data['id'])
                
                created_count += 1
        
        return jsonify({
            "success": True, 
            "created": created_count,
            "created_keys": created_keys,
            "message": f"Successfully created {created_count} test cases in Zephyr Scale and linked to story {story_key}"
        })
    except Exception as e:
        return jsonify({"success": False, "message": f"Error: {str(e)}"})

@app.route('/create_zephyr_tests', methods=['POST'])
def create_zephyr_tests():
    story_key = request.json.get('story_key')
    project_id = request.json.get('project_id')  # Zephyr Scale project ID
    result = process_story_to_zephyr(story_key, project_id)
    return jsonify(result)


if __name__ == '__main__':
    app.run(debug=True)
