from typing import Literal, Any
from pydantic import BaseModel, Field, model_validator
import json

class ClaimInput(BaseModel):
    policy_id: str
    claimant: str = "Unknown"
    farm_location: str
    lat: float
    lon: float
    crop_type: str
    claimed_damage_type: str
    event_date: str
    description: str
    date_submitted: str

    @model_validator(mode='before')
    @classmethod
    def parse_content(cls, data: Any) -> Any:
        if hasattr(data, 'parts'):
            # It's a Content object from Vertex AI SDK
            for part in data.parts:
                if hasattr(part, 'text') and part.text:
                    try:
                        parsed = json.loads(part.text)
                        # Set default for claimant if not provided in JSON
                        if 'claimant' not in parsed:
                            parsed['claimant'] = 'Unknown'
                        return parsed
                    except json.JSONDecodeError:
                        pass
        elif isinstance(data, dict):
             if 'claimant' not in data:
                  data['claimant'] = 'Unknown'
        return data

class DamageAssessment(BaseModel):
    assessed_severity: Literal["low", "medium", "high", "critical"]
    confidence: float = Field(ge=0.0, le=1.0)
    evidence_supports_claim: bool
    reasoning: str

class ReviewDecision(BaseModel):
    decision: Literal["dismiss", "monitor", "escalate"]
