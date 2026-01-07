# Skill Management

## ADDED Requirements

#### 1. Skill File Format
### Requirement: File Structure
Skills MUST be defined as Markdown files in `backend/prompt/skill/`.
- **FrontMatter (YAML)**:
    - `name`: string (Unique identifier)
    - `description`: string
    - `tools`: string[] (List of tool names)
- **Body**: Jinja2 template string for the prompt.

#### Scenario: Valid Skill File
Given a file `backend/prompt/skill/analyst.md`:
```markdown
---
name: analyst
description: Data analysis skill
tools: [python, read_file]
---
You are an analyst...
```
When the system loads skills
Then it should parse the metadata and content correctly.

#### 2. Service: Skill Loader
### Requirement: Loader Service
The system MUST provide a service to scan, parse, and cache skills from the filesystem at startup.

#### 3. API: List Skills
### Requirement: List Endpoint
`GET /api/skills` MUST return a list of available skills (metadata only).

#### 4. API: Get Skill Details
### Requirement: Detail Endpoint
`GET /api/skills/{name}` MUST return the full content of a skill.

#### Scenario: Get Existing Skill
Given a skill "analyst" exists
When a GET request is made to `/api/skills/analyst`
Then the response MUST contain the full markdown content.
