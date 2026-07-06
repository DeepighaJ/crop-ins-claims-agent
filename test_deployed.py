import json
import requests
import uuid
import subprocess

# 1. Get access token
token = subprocess.check_output('gcloud auth print-access-token', shell=True).decode('utf-8').strip()

project_id = "442050909694"
location = "us-central1"
reasoning_engine_id = "2727614020361125888"

url = f"https://{location}-aiplatform.googleapis.com/v1beta1/projects/{project_id}/locations/{location}/reasoningEngines/{reasoning_engine_id}:streamQuery"

headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

with open('tests/eval/datasets/basic-dataset.json') as f:
    data = json.load(f)

for case in data['evals']:
    print(f"\n--- {case['name']} ---")
    claim_input = case['input']
    
    user_id = str(uuid.uuid4())
    session_id = str(uuid.uuid4())
    
    payload = {
        "input": {
            "app_name": "app",
            "user_id": user_id,
            "session_id": session_id,
            "message": json.dumps(claim_input)
        }
    }
    
    resp = requests.post(url, headers=headers, json=payload)
    resp_json = resp.json()
    
    needs_resume = False
    for event in resp_json:
        if event.get("content", {}).get("parts"):
            for part in event["content"]["parts"]:
                if part.get("functionCall", {}).get("name") == "adk_request_input":
                    needs_resume = True
                    break
    
    final_events = resp_json
    if needs_resume:
        resume_payload = {
            "input": {
                "app_name": "app",
                "user_id": user_id,
                "session_id": session_id,
                "message": json.dumps({
                    "functionResponse": {
                        "id": "human_review",
                        "name": "adk_request_input",
                        "response": {"decision": "monitor"}
                    }
                })
            }
        }
        resume_resp = requests.post(url, headers=headers, json=resume_payload)
        final_events = resume_resp.json()

    final_record = None
    for event in final_events:
        if event.get("output"):
            final_record = event["output"]
            
    if isinstance(final_record, dict):
        status = final_record.get('status')
        decision = final_record.get('decision')
        print(f"Status: {status}, Decision: {decision}")
    else:
        print(final_record)
