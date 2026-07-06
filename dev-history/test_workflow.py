import asyncio
import pytest
from app.tools import get_ndvi_comparison, get_historical_weather
from app.agent import human_review
from google.adk.events.request_input import RequestInput

class MockContext:
    def __init__(self, resume_inputs=None):
        self.resume_inputs = resume_inputs or {}

@pytest.mark.asyncio
async def test_all():
    print("--- 1. Testing get_ndvi_comparison ---")
    # Using 'centralvalleyfarm' and '2024-05-20'
    ndvi_result = get_ndvi_comparison("centralvalleyfarm", "2024-05-20")
    print("NDVI Result:", ndvi_result)

    print("\n--- 2. Testing get_historical_weather ---")
    # Using lat/lon for the farm and '2024-05-20'
    weather_result = get_historical_weather(36.7, -119.8, "2024-05-20")
    print("Weather Result:", weather_result)

    print("\n--- 3. Testing Human Review Pause ---")
    mock_node_input = {"status": "auto-closed", "assessment": {"severity": "critical"}}
    ctx = MockContext()
    
    async for event in human_review(ctx, mock_node_input):
        if isinstance(event, RequestInput):
            print("Successfully paused! Yielded RequestInput with interrupt_id:", event.interrupt_id)
        else:
            print("Yielded something else:", event)
            
    print("\n--- 4. Testing Human Review Resume ---")
    resume_ctx = MockContext(resume_inputs={"human_review": {"decision": "monitor"}})
    async for event in human_review(resume_ctx, mock_node_input):
        print("Resumed! Event Output:", event.output)

if __name__ == "__main__":
    asyncio.run(test_all())
