# Integrate Skill System

Change ID: `integrate-skill-system`
Status: **Draft** (Proposed)

## Summary

Integrate a file-based "Skill" system to decouple Agent configuration from execution logic, and enhance the Ticket creation/execution flow with strict parameter validation and dynamic prompt composition.

## Motivation

As defined in PRD 0.0.3, the current Agent system lacks reusability and strict contract validation. 
- **Skill Reuse**: Multiple agents should be able to reuse the same "Skill" (Prompt Template + Tools) with different configurations.
- **Param Validation**: Agents need strict JSON Schema validation for inputs to prevent runtime errors.
- **Prompt Architecture**: A layered prompt strategy (System > Skill > Agent) is needed for better steerability.

## Design

### 1. Skill Abstraction
- **Definition**: A Markdown file in `backend/prompt/skill/{name}.md`.
- **Structure**: FrontMatter (YAML) for metadata & tools, Body for Jinja2 prompt template.
- **Loading**: `SkillLoader` service scans files at startup.

### 2. Agent Configuration
- **New Fields**: `skill_name`, `max_iterations`, `default_params`, `tool_names`.
- **Validation**: `params_schema` is mandatory for Agents using parametrized Skills.

### 3. Execution Logic
- **Prompt Merge**: `System Prompt` + `Skill Content` + `Agent Prompt`.
- **Param Validation**: Server-side `jsonschema` validation before Ticket creation.

## Spec Deltas

- `specs/skill-management`: New spec for Skill file structure and API.
- `specs/agent-configuration`: Update Agent spec with new fields.
- `specs/ticket-execution`: Update Ticket spec with validation and prompt logic.
