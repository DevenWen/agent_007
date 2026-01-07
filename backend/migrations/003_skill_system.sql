-- ============================================================
-- Migration: 0.0.3 - Agent Skill System Integration
-- ============================================================

-- Add new columns to agents table for Skill System
ALTER TABLE agents ADD COLUMN skill_name TEXT;
ALTER TABLE agents ADD COLUMN max_iterations INTEGER DEFAULT 10 NOT NULL;
ALTER TABLE agents ADD COLUMN default_params TEXT;  -- JSON string
ALTER TABLE agents ADD COLUMN tool_names TEXT;      -- JSON array of strings

-- Note: The 'tools' many-to-many relationship via agent_tools table is preserved
-- for backward compatibility. The new 'tool_names' field provides an alternative
-- method for specifying tools by name rather than UUID.
