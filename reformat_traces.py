import json
import os

trace_path = os.path.join(os.path.dirname(__file__), "tests", "eval", "eval_traces.json")
with open(trace_path, "r") as f:
    data = json.load(f)

new_data = {
    "eval_set_id": "claims_eval",
    "eval_cases": []
}

for case in data.get("evals", []):
    new_data["eval_cases"].append({
        "eval_case_id": case["name"],
        "invocations": [
            {
                "input": case["input"],
                "expected_output": case["expected_output"],
                "agent_data": case.get("agent_data")
            }
        ]
    })

with open(trace_path, "w") as f:
    json.dump(new_data, f, indent=2)
