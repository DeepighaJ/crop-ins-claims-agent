from google.adk.events.event import Event
from google.adk.workflow import Workflow, node

@node
def dummy_run(node_input: str) -> Event:
    return Event(output=node_input)

root_agent = Workflow(
    name="eval_agent",
    edges=[("START", dummy_run)],
    input_schema=str
)
