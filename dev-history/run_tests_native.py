import os
os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "true"
import json
import asyncio
from app.agent import app

async def run_evals():
    with open('tests/eval/datasets/basic-dataset.json') as f:
        data = json.load(f)
    
    cases = data.get('eval_cases', data.get('evals'))
    
    for case in cases:
        print(f"\n=== SCENARIO: {case['name']} ===")
        # App.run accepts a list of events or yields them
        try:
            # send initial
            stream = app.stream_run(
                message=json.dumps(case['input']),
                user_id="test_user",
                session_id="test_session"
            )
            needs_resume = False
            async for event in stream:
                print(event)
                if "adk_request_input" in str(event):
                    needs_resume = True
            
            if needs_resume:
                print("RESUMING...")
                stream2 = app.stream_run(
                    message=json.dumps({
                        "functionResponse": {
                            "id": "human_review",
                            "name": "adk_request_input",
                            "response": {"decision": "monitor"}
                        }
                    }),
                    user_id="test_user",
                    session_id="test_session"
                )
                async for event in stream2:
                    print(event)
                    
        except Exception as e:
            print(f"Error: {e}")

asyncio.run(run_evals())
