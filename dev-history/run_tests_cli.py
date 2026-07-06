import json
import subprocess

with open('tests/eval/datasets/basic-dataset.json') as f:
    data = json.load(f)

cases = data.get('eval_cases', data.get('evals'))

for case in cases:
    print(f"\n=== SCENARIO: {case['name']} ===")
    payload = json.dumps(case['input'])
    
    try:
        out = subprocess.check_output(
            ['uv', 'run', 'agents-cli', 'run', '--mode', 'adk', '.', payload],
            stderr=subprocess.STDOUT
        )
        print(out.decode('utf-8'))
    except subprocess.CalledProcessError as e:
        print("FAILED:", e.output.decode('utf-8'))
