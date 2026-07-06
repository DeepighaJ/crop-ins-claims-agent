import subprocess
import json

payload = json.dumps({
  "policy_id": "POL-001",
  "claimant": "Test Claimant",
  "farm_location": "centralvalleyfarm",
  "lat": 36.7,
  "lon": -119.8,
  "crop_type": "almonds",
  "claimed_damage_type": "drought",
  "event_date": "2024-05-20",
  "description": "Severe drought damage to almond orchard",
  "date_submitted": "2026-06-01"
})

payload_escaped = payload.replace('"', '\\"')
command = f'uv run agents-cli run "{payload_escaped}" --start-server -v'
print("Running command:", command)

result = subprocess.run(
    command,
    shell=True,
    capture_output=True,
    text=True
)
print("STDOUT:\n", result.stdout)
print("STDERR:\n", result.stderr)

# Assuming it works, we should be able to get the session ID from stdout and then run a second command.
# But let's just see if it runs the first one!
