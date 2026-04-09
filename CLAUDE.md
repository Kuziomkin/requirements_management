# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a requirements management system with an integrated knowledge base (Wiki). It combines structured requirement documentation with automatic Excel tracking and an AI-maintained wiki that compounds knowledge over time. The system is also an **Obsidian vault** compatible with Obsidian's graph view and wikilink navigation.

**Three-layer architecture:**
1. **requirements/** - Structured REQ-XXX documents (YAML frontmatter + markdown)
2. **notes/** - Meeting notes, design discussions, research, decisions
3. **Wiki/** - AI-maintained knowledge base (Concepts, Techniques, Tools, People, Sources)

**Core workflow:**
1. User creates requirements via `write-requirement` skill or adds notes via `write-note` skill
2. System generates REQ-XXX ID and checks for duplicates using requirements-tracker subagent
3. Interactive interview gathers implementation details
4. Document is written to `requirements/REQ-XXX [Name].md` or `notes/`
5. Post-tool-use hook automatically syncs YAML frontmatter to `requirements/requirements_tracker.xlsx`
6. User runs `wiki-ingest` to process requirements/notes into cross-linked wiki pages
7. User queries wiki via `wiki-query` to get synthesized answers from the knowledge base

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

### Wiki System (`Wiki/`, `SYSTEM_PROMPT.md`)
- **Purpose**: AI-maintained knowledge base that compounds over time instead of repeatedly parsing requirement documents
- **Structure**:
  - `Concepts/` - Abstract ideas, principles, patterns, domain models
  - `Techniques/` - Methods, procedures, algorithms, best practices
  - `Tools/` - Technologies, platforms, frameworks (Databricks, dbt, Azure, etc.)
  - `People/` - Stakeholders, SMEs, team members, decision makers
  - `Sources/` - Requirement summaries, external documentation references
  - `index.md` - Table of contents
  - `log.md` - Chronological operation history
  - `overview.md` - Wiki introduction
  - `CLAUDE.md` - Detailed maintenance schema
- **Operations**:
  - **Ingest** (`wiki-ingest` skill): Process requirements/notes, create 8-12 focused wiki pages with cross-links
  - **Query** (`wiki-query` skill): Search wiki and synthesize answers with citations
  - **Lint** (`wiki-lint` skill): Check for orphaned pages, broken links, contradictions, stale content
- **Key principles**:
  - Create atomic, focused pages (not broad summaries)
  - Cross-link aggressively using `[[wikilink]]` syntax
  - Cite sources with relative paths: `[REQ-001](../../requirements/REQ-001%20Name.md)`
  - Build on existing pages rather than creating duplicates
  - Obsidian-compatible (kebab-case filenames, proper wikilinks)

### Skills Overview

**Requirement Management:**
- `write-requirement` - Create new structured requirements with YAML frontmatter
- `update-requirement` - Modify existing requirement status, priority, relationships
- `check-requirement-quality` - Validate requirements for completeness before approval

**Note Management:**
- `write-note` - Create structured notes (meeting notes, email notes, open questions, analysis)

**Wiki Operations:**
- `wiki-ingest` - Process requirements/notes into cross-linked wiki pages
- `wiki-query` - Search wiki and answer questions from knowledge base
- `wiki-lint` - Check wiki health (orphans, broken links, contradictions, coverage gaps)

**Analysis:**
- `visualize-requirements` - Generate dependency graphs showing requirement relationships
- `analyze-impact` - Analyze impact of changing requirements, concepts, tools, or people

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

### Initial Setup
```bash
bash setup.sh  # Creates venv, installs dependencies, initializes Wiki structure
source .venv/bin/activate
```

The setup script automatically:
1. Creates Python virtual environment
2. Installs dependencies (FastMCP, pandas, openpyxl, pyyaml)
3. Initializes Wiki structure (runs `claude -p "Execute the automatic setup check from @SYSTEM_PROMPT.md"`)
4. Creates `Wiki/` directory with all required files and subdirectories

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

### When working with the Wiki:
- **Always use appropriate skills** - `wiki-ingest`, `wiki-query`, `wiki-lint` instead of manual operations
- **Create 8-12 focused pages per ingest** - Extract key concepts, techniques, tools, people from requirements/notes
- **Cross-link aggressively** - Use `[[page-name]]` wikilinks to connect related concepts
- **Cite sources** - Link back to requirements using `[REQ-001](../../requirements/REQ-001%20Name.md)`
- **Keep pages atomic** - One concept per page, not broad summaries
- **Use kebab-case filenames** - e.g., `data-lineage.md`, not `Data Lineage.md`
- **Update index and log** - Always update `Wiki/index.md` and log operations in `Wiki/log.md`
- **Build on existing pages** - Update rather than duplicate
- **Follow category rules**:
  - **Concepts/** - Abstract ideas, principles, patterns (e.g., "idempotency", "data-lineage")
  - **Techniques/** - Methods, procedures, algorithms (e.g., "dbt-modeling-patterns", "schema-auditing")
  - **Tools/** - Software, platforms, frameworks (e.g., "databricks", "dbt", "azure-data-factory")
  - **People/** - Stakeholders, team members, SMEs (e.g., "john-smith-data-architect", "analytics-team")
  - **Sources/** - Requirement summaries, external docs (e.g., "req-001-summary", "databricks-api-docs")

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

## Obsidian Compatibility

This repository is also an **Obsidian vault**. The Wiki system follows Obsidian conventions:

- **Wikilinks**: Use `[[page-name]]` syntax (not `[page name](./page-name.md)`)
- **No file extensions in wikilinks**: `[[data-lineage]]` not `[[data-lineage.md]]`
- **Relative paths for external links**: Use `../../requirements/` and `../../notes/` for citations
- **URL-encode spaces**: Use `%20` in markdown links: `[REQ-001](../../requirements/REQ-001%20Feature.md)`
- **Kebab-case filenames**: Required for reliable linking across systems
- **Graph view**: Obsidian can visualize the wiki's cross-link structure
- **Backlinks panel**: Shows bidirectional relationships between pages and requirements

**To use with Obsidian:**
1. Open Obsidian
2. Open this repository as a vault
3. Navigate using graph view or search
4. View backlinks for any page to see what references it

## Common Workflows

### Creating a new requirement
1. User: "I need a requirement for [feature]"
2. Claude triggers `write-requirement` skill automatically
3. Requirements-tracker subagent generates next REQ-ID and checks for duplicates
4. Interactive interview gathers implementation details
5. Requirement written to `requirements/REQ-XXX [Name].md`
6. Post-tool-use hook syncs to Excel tracker
7. User: "Ingest this requirement into the wiki"
8. Claude triggers `wiki-ingest` skill, creates 8-12 wiki pages with cross-links

### Querying knowledge base
1. User: "What requirements relate to [topic]?"
2. Claude triggers `wiki-query` skill
3. Searches wiki pages using Grep
4. Cross-references with requirements
5. Synthesizes answer with `[[wikilink]]` and REQ-ID citations

### Updating a requirement
1. User: "Update REQ-001 status to approved"
2. Claude triggers `update-requirement` skill
3. Updates YAML frontmatter
4. Post-tool-use hook syncs to Excel tracker
5. User: "Ingest the updates" (optional, to update wiki)

### Checking wiki health
1. User: "Lint the wiki"
2. Claude triggers `wiki-lint` skill
3. Checks for orphaned pages, broken links, contradictions, coverage gaps
4. Reports issues and suggests fixes
5. Logs operation in `Wiki/log.md`
