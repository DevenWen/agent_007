# Agent Configuration

## MODIFIED Requirements

#### 1. Agent Logic
### Requirement: Agent Config Fields
Agents MUST be configurable with:
- `skill_name`: Reference to a Skill (Optional).
- `max_iterations`: Integer limit for execution loop (Default: 10).
- `default_params`: JSON object with default values for Ticket creation.
- `tool_names`: JSON array of extra tool names (Union with Skill tools).
- `params_schema`: JSON Schema for validation.

#### Scenario: Agent with Skill
Given a Skill "analyst" with tools `[python]`
And an Agent configured with `skill_name="analyst"` and `tool_names=["search"]`
When the Agent is loaded
Then its effective tools should be `[python, search]`.

#### Scenario: Param Schema Validation
Given an Agent with `params_schema` requiring `filename`
When a user updates the Agent
The system MUST validate that `default_params` (if provided) conforms to `params_schema`.
