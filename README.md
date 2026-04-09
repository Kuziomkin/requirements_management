# Requirements Management System with Knowledge Base

A comprehensive requirements management system that combines structured requirement documentation with an AI-maintained knowledge base (Wiki). Built on FastMCP and designed to work seamlessly with Claude Code and Obsidian.

## Features

### 🎯 Requirements Management
- **Structured Requirements**: YAML frontmatter + markdown format with auto-generated REQ-IDs
- **Automatic Excel Tracking**: Requirements synced to `requirements_tracker.xlsx` via post-tool-use hooks
- **Duplicate Detection**: AI checks for conflicts before creating requirements
- **Rich Documentation**: Implementation guidance, acceptance criteria, Mermaid diagrams
- **Traceability**: Related requirements, test cases, stakeholders tracked in YAML

### 📚 Knowledge Base (Wiki)
- **AI-Maintained Wiki**: Automatically extracts concepts, techniques, tools, and people from requirements and notes
- **Cross-Linked Pages**: Obsidian-compatible wikilinks create a navigable knowledge graph
- **Compounding Knowledge**: Wiki grows over time instead of re-processing from scratch
- **Organized Categories**: Concepts, Techniques, Tools, People, Sources
- **Query System**: Ask questions and get synthesized answers with citations

### 🔧 Obsidian Integration
- **Graph View**: Visualize relationships between requirements, concepts, and decisions
- **Backlinks Panel**: See what references each page
- **Standard Wikilinks**: Use `[[page-name]]` syntax throughout
- **Markdown Compatible**: Works with any markdown editor

## Prerequisites

- **Python 3.12+** (recommended)
- **Claude Code CLI** (`codemie-claude` or `claude`)
- **Git** (for version control)

## Installation & Setup

### 1. Clone or Navigate to Repository

```bash
cd ~/repositories/requirements_management
```

### 2. Run Setup Script

The setup script will automatically:
- Create a Python virtual environment (`.venv`)
- Install all dependencies (FastMCP, pandas, openpyxl, pyyaml)
- Initialize the Wiki structure with required files

```bash
bash setup.sh
```

### 3. Activate Virtual Environment

After setup completes, activate the virtual environment:

```bash
source .venv/bin/activate
```

### 4. Verify MCP Server (Optional)

Test that the MCP server starts correctly:

```bash
python server.py
```

You should see FastMCP server logs. Press `Ctrl+C` to stop.

## Usage

### Starting Claude Code

```bash
claude
```

The system automatically loads the MCP server and skills when you start Claude Code in this directory.

### Creating Requirements

Simply describe what you need:

```
"I need a requirement for user authentication with OAuth2"
```

Claude Code will:
1. Generate the next REQ-ID (e.g., REQ-001)
2. Check for duplicate/conflicting requirements
3. Conduct an interactive interview to gather details
4. Create a structured requirement document
5. Automatically sync to the Excel tracker

### Creating Notes

Document meeting notes, decisions, or research:

```
"Create a note for today's requirements review meeting"
```

### Ingesting into Wiki

Process requirements and notes into the knowledge base:

```
"Ingest the new requirements into the wiki"
```

Claude will create 8-12 cross-linked wiki pages extracting:
- **Concepts**: Data models, architectural patterns, business logic
- **Techniques**: Implementation approaches, best practices
- **Tools**: Technologies, platforms, frameworks
- **People**: Stakeholders, owners, SMEs
- **Sources**: Requirement summaries, external docs

### Querying the Wiki

Ask questions about your knowledge base:

```
"What requirements relate to authentication?"
"How does data lineage work in our system?"
"What are the key decisions for the API design?"
```

### Other Operations

**Update a requirement:**
```
"Update REQ-001 status to approved"
```

**Check requirement quality:**
```
"Check REQ-005 for completeness"
```

**Visualize dependencies:**
```
"Visualize requirements graph"
```

**Check wiki health:**
```
"Lint the wiki"
```

**Analyze impact:**
```
"Analyze impact of changing REQ-003"
```

## Project Structure

```
requirements_management/
├── requirements/              # Structured requirement documents
│   ├── REQ-001 Feature.md    # Individual requirements with YAML frontmatter
│   ├── REQ-002 Enhancement.md
│   └── requirements_tracker.xlsx  # Auto-synced Excel tracker
├── notes/                     # Meeting notes, design discussions, research
│   └── (created as needed)
├── Wiki/                      # AI-maintained knowledge base
│   ├── Concepts/             # Abstract ideas, principles, patterns
│   ├── Techniques/           # Methods, procedures, algorithms
│   ├── Tools/                # Technologies, platforms, frameworks
│   ├── People/               # Stakeholders, SMEs, team members
│   ├── Sources/              # Requirement summaries, external docs
│   ├── index.md              # Table of contents
│   ├── log.md                # Operation history
│   ├── overview.md           # Wiki introduction
│   └── CLAUDE.md             # Maintenance schema
├── .claude/                   # Claude Code configuration
│   ├── skills/               # Custom skills (write-requirement, wiki-ingest, etc.)
│   ├── agents/               # Subagents (requirements-tracker)
│   └── settings.local.json   # Hooks and permissions
├── hooks/                     # Post-tool-use hooks
│   └── update_excel.py       # Syncs requirements to Excel tracker
├── server.py                  # FastMCP server for requirement management tools
├── .mcp.json                  # MCP server configuration
├── setup.sh                   # Setup script
├── requirements.txt           # Python dependencies
├── CLAUDE.md                  # Instructions for Claude Code
├── SYSTEM_PROMPT.md           # Wiki system schema
└── README.md                  # This file
```

## Using with Obsidian

This repository is also an Obsidian vault:

1. Open Obsidian
2. **Open folder as vault** → Select this repository
3. Use **Graph View** to visualize relationships
4. Navigate using wikilinks and backlinks panel
5. Edit wiki pages directly in Obsidian

## Configuration Files

### `.claude/settings.local.json`
- **Permissions**: Pre-approved tool calls and bash commands
- **Hooks**: Post-tool-use hook to sync requirements to Excel
- **MCP Servers**: Enabled "requirements-manager" server

### `.mcp.json`
- MCP server configuration for requirements management tools
- Runs `server.py` with Python

### `CLAUDE.md`
- Comprehensive instructions for Claude Code instances
- Project architecture, workflows, guidelines

### `SYSTEM_PROMPT.md`
- Detailed Wiki system schema and operational rules
- Used during Wiki initialization

## Available Skills

| Skill | Description | Example Trigger |
|-------|-------------|-----------------|
| `write-requirement` | Create structured requirements | "I need a requirement for..." |
| `update-requirement` | Modify existing requirements | "Update REQ-001 status to approved" |
| `check-requirement-quality` | Validate requirement completeness | "Check REQ-003 quality" |
| `write-note` | Create structured notes | "Create a meeting note" |
| `wiki-ingest` | Process requirements/notes into wiki | "Ingest requirements into wiki" |
| `wiki-query` | Search and answer from wiki | "What does the wiki say about...?" |
| `wiki-lint` | Check wiki health | "Lint the wiki" |
| `visualize-requirements` | Generate dependency graphs | "Visualize requirements" |
| `analyze-impact` | Analyze change impact | "Analyze impact of REQ-001" |

## Troubleshooting

### Excel Tracking Not Working

1. Verify dependencies are installed:
   ```bash
   pip list | grep -E "pandas|openpyxl"
   ```

2. Check hook configuration in `.claude/settings.local.json`

3. Ensure requirement files match pattern: `requirements/REQ-\d+.*\.md`

4. Confirm YAML frontmatter has `id` field

### MCP Server Won't Start

1. Activate virtual environment:
   ```bash
   source .venv/bin/activate
   ```

2. Check FastMCP installation:
   ```bash
   python -c "import fastmcp; print(fastmcp.__file__)"
   ```

3. Try running server directly:
   ```bash
   python server.py
   ```

### Wiki Not Initializing

1. Run setup script again:
   ```bash
   bash setup.sh
   ```

2. Or manually initialize:
   ```bash
   claude -p "Execute the automatic setup check from @SYSTEM_PROMPT.md"
   ```

## Dependencies

Installed automatically by `setup.sh`:

- `fastmcp` - FastMCP framework for MCP server
- `pandas` - Excel file manipulation
- `openpyxl` - Excel file engine
- `pyyaml` - YAML parsing for frontmatter
- `pydantic` - Data validation for MCP tools

## Support

For issues or questions:
1. Check `CLAUDE.md` for detailed operational guidance
2. Review `SYSTEM_PROMPT.md` for Wiki system details
3. Examine `.claude/skills/*/skill.md` for skill documentation
4. Check Claude Code logs for errors

## License

[Specify your license here]

## Contributing

[Specify contribution guidelines if applicable]
