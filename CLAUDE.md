# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a requirements management system built on FastMCP that enables structured requirement documentation with automatic Excel tracking. Requirements follow a standardized YAML + markdown format with auto-generated IDs, implementation guidance, and diagrams.

**Core workflow:**
1. User requests a new requirement (via the `write-requirement` skill)
2. System generates REQ-XXX ID and checks for duplicates using a subagent
3. Interactive interview gathers implementation details
4. Document is written to `requirements/REQ-XXX [Name].md`
5. Post-tool-use hook automatically extracts YAML frontmatter and syncs to `requirements/requirements_tracker.xlsx`

## Architecture

### MCP Server (`server.py`)
- FastMCP server exposing requirement management tools
- Configured in `.mcp.json` as "requirements-manager"
- Run with: `python server.py`
- Logs at DEBUG level for troubleshooting

### Client (`client.py`)
- Example HTTP client for testing MCP server connectivity
- Connects to `http://localhost:8000/mcp`
- Run with: `python client.py`

### Hook System (`hooks/update_excel.py`)
- **Trigger**: Automatically runs after Write/Edit tool calls (configured in `.claude/settings.local.json`)
- **Purpose**: Extracts YAML frontmatter from requirement files matching `requirements/REQ-\d+.*\.md` and syncs to Excel tracker
- **Dependencies**: pandas, openpyxl (lazy-loaded)
- **Excel structure**: ID, Name, Description, Status, Priority, Owner, Related To, Test Cases, File Path, Last Updated
- **Behavior**: Updates existing rows by ID, appends new requirements, sorts by ID

### Requirements Skill (`.claude/skills/write-requirement/`)
- **Trigger phrases**: "requirement", "req", "requirements", "feature specification", "REQ-XXX"
- **Workflow**:
  1. Uses `requirements-tracker` subagent to analyze Excel and generate next REQ-ID
  2. Checks for duplicate/conflicting requirements before proceeding
  3. Conducts interactive interview for implementation details
  4. Suggests appropriate diagram types (flow, sequence, ERD, component, state, relationship)
  5. Writes structured markdown with YAML frontmatter to `requirements/`

## Requirement Document Structure

Every requirement follows this exact format:

```markdown
---
id: REQ-XXX
name: [Requirement Name]
description: [One-line summary]
status: [draft|in-review|approved|implemented]
priority: [low|medium|high|critical]
owner: [team-name]
related_to:
  - REQ-YYY   # [relationship type]: [description]
test_cases:
  - TC-XXX
---

# Notes

## Implementation

### Approach
[Detailed technical guidance with specific technologies, endpoints, data models, security measures]

### Key decisions
[Bullet list: **[Decision]:** [Rationale]]

### Out of scope
[What's explicitly NOT included]

### Open questions
[Checkbox list with description and owner]

### References
[External docs, ADRs, designs]

## Acceptance Criteria

- [ ] **AC-1:** [Testable condition]
- [ ] **AC-2:** [Testable condition]

# Diagrams

[Mermaid diagrams based on requirement type]
```

## Development Commands

### Setup
```bash
bash setup.sh  # Creates venv, installs dependencies
source .venv/bin/activate
```

### Run MCP Server
```bash
python server.py
```

### Test Client
```bash
python client.py
```

### Install Additional Dependencies
```bash
pip install pandas openpyxl  # Required for Excel tracking hook
```

## Key Implementation Guidelines

### When creating requirements:
- **Always use the `write-requirement` skill** - triggers automatically when user mentions "requirement" or "req"
- **Never invent details** - ask follow-up questions if implementation approach is unclear
- **Probe for technical specifics**: technologies, API endpoints, data models, security measures, performance requirements, configuration values
- **Check for duplicates** - the requirements-tracker subagent analyzes existing requirements and surfaces conflicts before writing
- **Use appropriate diagrams** - sequence for API flows, flow for decision logic, ERD for data models, component for architecture, relationship for dependencies
- **Write detailed Implementation → Approach** - specific enough for developers to implement without ambiguity
- **Capture Key decisions with rationale** - explain why certain design choices were made
- **Define Out of scope explicitly** - prevents scope creep
- **Provide acceptance criteria** - use checkbox format with AC-X identifiers

### When modifying requirements:
- **Update YAML frontmatter** if status, priority, owner, or relationships change
- **Add to related_to** when linking requirements (use format: `REQ-YYY  # [relationship]: [description]`)
- **Update Last Updated timestamp** - handled automatically by Excel hook
- **Mark open questions as resolved** - change `[ ]` to `[x]` when questions are answered

### Subagent Usage:
- **requirements-tracker subagent**: Used by write-requirement skill to analyze Excel tracker and generate REQ-IDs
  - Keeps main context lean by processing large Excel files in isolated context
  - Returns JSON with `next_id`, `analysis_status`, `conflicts`, `related_requirements`, `recommendation`
  - Do not invoke manually - the skill handles this

## Hook Troubleshooting

If Excel tracking fails:
1. Check that pandas and openpyxl are installed: `pip list | grep -E "pandas|openpyxl"`
2. Verify hook is configured in `.claude/settings.local.json` under `PostToolUse` → `Write|Edit` matcher
3. Check hook logs in stderr output: `[update_excel.py]` prefix
4. Ensure requirement files match pattern: `requirements/REQ-\d+.*\.md`
5. Confirm YAML frontmatter has `id` field - hook skips files without valid IDs

## Excel Tracker Details

**Location**: `requirements/requirements_tracker.xlsx`

**Automatic sync on**:
- Write tool calls to requirement markdown files
- Edit tool calls to requirement markdown files

**Columns**:
- ID (primary key for updates)
- Name, Description, Status, Priority, Owner
- Related To (comma-separated REQ-IDs)
- Test Cases (comma-separated TC-XXX)
- File Path (relative path to .md file)
- Last Updated (timestamp)

**Behavior**:
- New requirements are appended
- Existing requirements (matched by ID) are updated in-place
- Sorted by ID after each update
- Creates `requirements/` directory if missing
