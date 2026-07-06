import json
import asyncio
import os
os.environ['GOOGLE_GENAI_USE_VERTEXAI'] = 'true'

from google.adk.events.event import Event
from google.adk.events.request_input import RequestInput
from app.agent import workflow, ClaimInput
from google.adk.agents.context import Context

async def run_evals():
    with open('tests/eval/datasets/basic-dataset.json') as f:
        data = json.load(f)
    
    for case in data['evals']:
        print(f"\n--- {case['name']} ---")
        input_data = ClaimInput(**case['input'])
        
        ctx = Context()
        
        events = []
        try:
            async for evt in workflow.stream_run(input_data, context=ctx):
                events.append(evt)
        except AttributeError:
            events = [evt async for evt in workflow(input_data, context=ctx)]
        
        final_record = None
        needs_resume = False
        
        for evt in events:
            if isinstance(evt, RequestInput):
                needs_resume = True
            elif isinstance(evt, Event) and hasattr(evt, 'output') and evt.output:
                final_record = evt.output
                
        if needs_resume:
            ctx.resume_inputs['human_review'] = {'decision': 'monitor'}
            events2 = [evt async for evt in workflow(input_data, context=ctx)]
            for evt in events2:
                if isinstance(evt, Event) and hasattr(evt, 'output') and evt.output:
                    final_record = evt.output
        
        if isinstance(final_record, dict):
            status = final_record.get('status')
            decision = final_record.get('decision')
            print(f"Status: {status}, Decision: {decision}")
        elif hasattr(final_record, 'model_dump'):
            d = final_record.model_dump()
            print(f"Status: {d.get('status')}, Decision: {d.get('decision')}")
        else:
            print(final_record)

if __name__ == '__main__':
    asyncio.run(run_evals())
