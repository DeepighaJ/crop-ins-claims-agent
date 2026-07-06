import json
import os

trace_path = os.path.join(os.path.dirname(__file__), "tests", "eval", "eval_traces.json")

with open(trace_path, "r") as f:
    data = json.load(f)

# Convert to ADK expected format
new_data = []
for item in data:
    eval_id = item.get("evalId", "unknown")
    if "data" in item:
        data_item = item["data"][0]
        # ensure query and expected_output
        query = data_item.get("input", data_item.get("query", ""))
        expected_output = data_item.get("expected_output", "")
        agent_data = data_item.get("agent_data")
        
        new_data.append({
            "evalId": eval_id,
            "data": [
                {
                    "query": query,
                    "expected_output": expected_output,
                    "agent_data": agent_data
                }
            ]
        })

with open(trace_path, "w") as f:
    json.dump(new_data, f, indent=2)
