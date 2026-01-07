# Ticket Execution

## MODIFIED Requirements

#### 1. Ticket Creation Validation
### Requirement: Param Validation
When creating a Ticket, the system MUST:
1. Merge `User Params` into `Agent.default_params` to get `Final Params`.
2. Validate `Final Params` against `Agent.params_schema` using strictly typed validation (e.g. jsonschema).
3. If validation fails, reject with 422.

#### Scenario: Invalid Params
Given an Agent requiring "repository"
When a Ticket is created without "repository"
Then the system MUST return 422 Unprocessable Entity.

#### 2. Prompt Compilation (Merge Strategy)
### Requirement: Merge Strategy
When executing a Ticket, the System Message MUST include:
1. `System Prompt` (Global)
2. `Skill Content` (Base Template)
3. `Agent Prompt` (Custom Instructions, rendered with Params)

#### Scenario: Prompt Ordering
Given System Prompt "S", Skill Content "Sk", and Agent Prompt "A"
When the Executor compiles the prompt
Then the resulting message MUST look like "S\n...\nSk\n...\nA".
