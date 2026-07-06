import json
import requests
import uuid
import os

def run_scenarios():
    dataset_path = os.path.join(os.path.dirname(__file__), "datasets", "basic-dataset.json")
    with open(dataset_path, "r") as f:
        dataset = json.load(f)

    traces = []
    
    for eval_case in dataset["evals"]:
        case_name = eval_case["name"]
        claim_input = eval_case["input"]
        print(f"\n--- Running scenario: {case_name} ---")
        
        user_id = str(uuid.uuid4())
        
        # 1. Create a session
        sess_resp = requests.post(f"http://127.0.0.1:8080/apps/app/users/{user_id}/sessions")
        if sess_resp.status_code != 200:
            session_id = str(uuid.uuid4())
        else:
            session_id = sess_resp.json()["id"]

        # 2. Run graph
        payload = {
            "appName": "app",
            "userId": user_id,
            "sessionId": session_id,
            "newMessage": {
                "parts": [{"text": json.dumps(claim_input)}]
            }
        }
        
        resp = requests.post("http://127.0.0.1:8080/run", json=payload)
        resp_json = resp.json()
        
        # 3. Detect if it paused for human_review
        needs_resume = False
        for event in resp_json:
            if event.get("content", {}).get("parts"):
                for part in event["content"]["parts"]:
                    if part.get("functionCall", {}).get("name") == "adk_request_input":
                        needs_resume = True
                        break
        
        final_events = resp_json
        if needs_resume:
            print(f"[{case_name}] Pause detected! Resuming with decision: monitor...")
            resume_payload = {
                "appName": "app",
                "userId": user_id,
                "sessionId": session_id,
                "newMessage": {
                    "parts": [{
                        "functionResponse": {
                            "id": "human_review",
                            "name": "adk_request_input",
                            "response": {"decision": "monitor"}
                        }
                    }]
                }
            }
            resume_resp = requests.post("http://127.0.0.1:8080/run", json=resume_payload)
            final_events = resume_resp.json()
        else:
            print(f"[{case_name}] No pause needed (auto-closed or bypassed).")

        # Extract final output
        final_record = None
        for event in final_events:
            # We want the output of the final node
            if event.get("output"):
                final_record = event["output"]
                
        # To make it compatible with ADK LLM judge, we format it as a valid eval instance
        traces.append({
            "name": case_name,
            "input": json.dumps(claim_input),
            "expected_output": "",
            # We shove the trace into the prompt so the LLM-judge evaluates it.
            # And for custom function parsing, we can just dump it to the agent_data field
            "agent_data": final_record
        })
        
    out_path = os.path.join(os.path.dirname(__file__), "eval_traces.json")
    with open(out_path, "w") as f:
        json.dump({"evals": traces}, f, indent=2)
    print(f"\nAll scenarios completed. Traces saved to {out_path}.")

if __name__ == "__main__":
    run_scenarios()
