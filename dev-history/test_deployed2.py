import json
import requests
import uuid
import subprocess

token = subprocess.check_output('gcloud auth print-access-token', shell=True).decode('utf-8').strip()

project_id = '442050909694'
location = 'us-central1'
reasoning_engine_id = '2727614020361125888'

url = f'https://{location}-aiplatform.googleapis.com/v1beta1/projects/{project_id}/locations/{location}/reasoningEngines/{reasoning_engine_id}:streamQuery?alt=sse'

headers = {
    'Authorization': f'Bearer {token}',
    'Content-Type': 'application/json'
}

with open('tests/eval/datasets/basic-dataset.json') as f:
    data = json.load(f)

cases = data.get('eval_cases', data.get('evals'))

for case in cases:
    print(f"\n=== SCENARIO: {case['name']} ===")
    claim_input = case['input']
    
    session_id = str(uuid.uuid4())
    
    payload = {
        'input': {
            'user_id': 'tester',
            'session_id': session_id,
            'message': json.dumps(claim_input)
        }
    }
    
    resp = requests.post(url, headers=headers, json=payload, stream=True)
    needs_resume = False
    print("Response Status:", resp.status_code)
    for line in resp.iter_lines():
        if line:
            text = line.decode('utf-8')
            print(text)
            if "adk_request_input" in text or "human_review" in text:
                needs_resume = True

    if needs_resume:
        print("RESUMING...")
        resume_payload = {
            'input': {
                'user_id': 'tester',
                'session_id': session_id,
                'message': json.dumps({
                    "functionResponse": {
                        "id": "human_review",
                        "name": "adk_request_input",
                        "response": {"decision": "monitor"}
                    }
                })
            }
        }
        resp2 = requests.post(url, headers=headers, json=resume_payload, stream=True)
        for line in resp2.iter_lines():
            if line:
                print(line.decode('utf-8'))
