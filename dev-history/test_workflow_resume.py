import asyncio
from app.agent import human_review
from google.adk.events.request_input import RequestInput

class MockContext:
    def __init__(self, resume_inputs=None):
        self.resume_inputs = resume_inputs or {}

async def test_human_review():
    print("\n--- 3. Testing Human Review Pause ---")
    mock_node_input = {"status": "auto-closed", "assessment": {"severity": "critical"}}
    ctx = MockContext()
    
    # In ADK 2.0, the original function is wrapped. We can access it via ._func or just run the generator
    func = human_review._func if hasattr(human_review, "_func") else getattr(human_review, "func", None)
    
    if not func:
        print("Could not find the original function inside FunctionNode.")
        return

    async for event in func(ctx, mock_node_input):
        if isinstance(event, RequestInput):
            print("Successfully paused! Yielded RequestInput with interrupt_id:", event.interrupt_id)
        else:
            print("Yielded something else:", event)
            
    print("\n--- 4. Testing Human Review Resume ---")
    resume_ctx = MockContext(resume_inputs={"human_review": {"decision": "monitor"}})
    async for event in func(resume_ctx, mock_node_input):
        print("Resumed! Event Output:", getattr(event, 'output', event))

if __name__ == "__main__":
    asyncio.run(test_human_review())
