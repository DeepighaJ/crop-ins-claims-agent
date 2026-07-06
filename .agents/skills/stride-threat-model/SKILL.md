---
name: stride-threat-model
description: Performs a systematic STRIDE threat modeling assessment on the current project's codebase and architecture. Use this when starting a new implementation phase or reviewing existing components.
---

# STRIDE Threat Modeling Skill

## Goal
Analyze the workspace directory structure, configuration files, and code files to produce a structured threat_model.md assessment.

## Instructions
1. Analyze System Boundaries: map entry points (the claim intake via intake_validator, the get_ndvi_comparison and get_historical_weather tool calls, the security_checkpoint, the human_review resume mechanism) and data storage/state layers (ctx.state persistence).
2. STRIDE Evaluation across the six pillars, applied specifically to this project's real stakes (financial payout decisions, policyholder PII):
   - Spoofing: Can the resume endpoint be called by anyone, or only an authenticated adjuster? Can a claim's farm_location/lat/lon be spoofed to pull evidence for a different location than the actual claim site?
   - Tampering: Can the claim payload, the NDVI CSV, or the resume payload be manipulated in transit or at rest?
   - Repudiation: Is every decision (auto-closed or human-reviewed) traceable to its evidence and, for human decisions, to a specific adjuster's identity? Note our unified audit-trail record design.
   - Information Disclosure: Does security_checkpoint's regex-based PII redaction have gaps (non-standard SSN/phone formats, other PII types like addresses or claim numbers)? Could tool failures leak stack traces?
   - Denial of Service: Can the system be flooded with claims to exhaust the LLM budget or the Open-Meteo API quota? Is there any caching or rate limiting?
   - Elevation of Privilege: Can a claim bypass security_checkpoint entirely? Can auto_close_gate's confidence threshold be gamed via a crafted claim to force an auto-close?
3. Given this project's stakes (real financial decisions, sensitive policyholder data), flag any HIGH severity findings distinctly from MEDIUM/LOW, and note which are acceptable for a capstone demo scope versus which would block real production use.
4. Output: generate threat_model.md in the workspace root.
