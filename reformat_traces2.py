import json
import os

trace_path = os.path.join(os.path.dirname(__file__), "tests", "eval", "eval_traces.json")

# I have the raw eval_traces.json content from earlier:
# I will use the original format from generate_traces.py to reformat it correctly.
# The previous reformat script might have overwritten it. Let me just rebuild it.

# I'll first read it, if it's my new format, I extract it. If it's old, I handle it.
with open(trace_path, "r") as f:
    data = json.load(f)

cases = []
if "eval_cases" in data:
    cases = data["eval_cases"]
    old_cases = []
    for c in cases:
        old_cases.append({
            "name": c["eval_case_id"],
            "input": c["invocations"][0]["input"],
            "expected_output": c["invocations"][0]["expected_output"],
            "agent_data": c["invocations"][0].get("agent_data")
        })
    cases = old_cases
elif "evals" in data:
    cases = data["evals"]
else:
    cases = data

new_data = []
for case in cases:
    name = case.get("name", case.get("eval_case_id", "unknown"))
    new_data.append({
        "evalId": name,
        "data": [
            {
                "input": case["input"],
                "expected_output": case["expected_output"],
                "agent_data": case.get("agent_data")
            }
        ]
    })

with open(trace_path, "w") as f:
    json.dump(new_data, f, indent=2)
