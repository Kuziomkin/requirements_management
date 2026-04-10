#!/bin/bash
set -e  # Exit on error

echo "🚀 Setting up Requirements Management System..."

# 1. Create venv
echo "📦 Creating virtual environment..."
python3 -m venv .venv
source .venv/bin/activate

# 2. Install dependencies
echo "📚 Installing dependencies..."
pip install -r requirements.txt --quiet

# 3. Create directory structure
echo "🗂️  Creating directory structure..."
mkdir -p Wiki/{Concepts,Techniques,Tools,People,Sources}
mkdir -p requirements
mkdir -p notes

# 4. Initialize Wiki files (only if not already present)
if [ ! -f "Wiki/index.md" ]; then
    echo "📝 Initializing Wiki files..."

    TODAY=$(date +"%Y-%m-%d")

    # Create Welcome.md
    cat > Welcome.md << 'EOF'
# Welcome to Your Requirements Wiki

This is your personal requirements knowledge base powered by AI.

## Quick Start

### Add Requirements or Notes
```bash
# Requirements are automatically tracked in requirements/
# Add notes for additional context
echo "# Meeting Notes" > notes/2026-04-09-requirements-review.md
```

Then say: **"Ingest the new requirements"** or **"Process notes from yesterday's meeting"**

### Ask Questions
Just ask naturally:
- "What requirements relate to [topic]?"
- "Summarize the key decisions from [REQ-ID]"
- "How does [concept A] relate to [concept B]?"
- "What's the implementation approach for [feature]?"

### Browse the Wiki
- See [[index]] for the complete table of contents
- Check [[log]] for operation history
- Read [[overview]] for more details

## Structure

```
requirements/           → Structured requirement documents (REQ-XXX format)
notes/                  → Meeting notes, design discussions, research
Wiki/
  ├── Concepts/         → Abstract ideas, principles, patterns
  ├── Techniques/       → Methods, algorithms, procedures
  ├── Tools/            → Tech stack, platforms, utilities
  ├── People/           → Stakeholders, SMEs, team members
  ├── Sources/          → Requirement summaries, reference docs
  ├── index.md          → Table of contents
  ├── log.md            → Operation history
  └── CLAUDE.md         → Maintenance rules
```

## Philosophy

Instead of repeatedly parsing requirement documents, this wiki:
- **Compounds knowledge** through persistent, maintained pages
- **Cross-links** related concepts, requirements, and decisions
- **Evolves** as you add more requirements and notes
- **Maintains itself** through AI bookkeeping

Start by creating requirements or adding notes, then ask AI to process them!
EOF

    # Create Wiki/index.md
    cat > Wiki/index.md << EOF
# Index

Complete table of contents for the requirements knowledge base.

## Concepts

*No pages yet*

## Techniques

*No pages yet*

## Tools

*No pages yet*

## People

*No pages yet*

## Sources

*No pages yet*

---

*Last updated: ${TODAY}*
EOF

    # Create Wiki/log.md
    cat > Wiki/log.md << EOF
# Operation Log

Chronological record of all wiki operations (ingests, queries, maintenance).

## ${TODAY}

### Initialization
- **Type**: Setup
- **Description**: Created wiki structure for requirements documentation
- **Actions**:
  - Created directory structure: Wiki/{Concepts,Techniques,Tools,People,Sources}
  - Created index.md, log.md, overview.md, CLAUDE.md
  - Created root-level Welcome.md
- **Status**: Ready for first ingest

---

*Format: Date, operation type (Ingest/Query/Lint), description, pages affected*
EOF

    # Create Wiki/overview.md
    cat > Wiki/overview.md << EOF
# Overview

This is a requirements-focused knowledge base built using the LLM Wiki pattern.

## What is this?

A persistent, compounding knowledge base where:
- **You** create requirements in \`requirements/\` and add notes in \`notes/\`
- **AI** maintains organized wiki pages with concepts, decisions, and cross-references
- **Knowledge compounds** over time rather than being re-processed from scratch

## How it works

### Three Layers

1. **requirements/** - Structured requirement documents (REQ-XXX format with YAML frontmatter)
2. **notes/** - Meeting notes, design discussions, research, decisions
3. **Wiki/** - AI-maintained knowledge pages organized by category

### Operations

- **Ingest** - Process requirements/notes, create/update wiki pages, maintain cross-links
- **Query** - Ask questions, get synthesized answers from wiki, save valuable analyses
- **Lint** - Check for contradictions, stale content, broken links

## Wiki Organization

- **Concepts/** - Abstract ideas, principles, patterns, frameworks
- **Techniques/** - Methods, algorithms, procedures, best practices
- **Tools/** - Tech stack, platforms, utilities (Databricks, Azure, dbt, etc.)
- **People/** - Stakeholders, SMEs, team members, decision makers
- **Sources/** - Requirement summaries, reference documentation

## Getting Started

1. Create requirements using the \`write-requirement\` skill
2. Add notes to \`notes/\` for meeting minutes, design decisions, research
3. Ask AI to ingest them: "Ingest new requirements" or "Process recent notes"
4. Query the wiki for information
5. Watch your requirements knowledge base grow

---

*Initialized: ${TODAY}*
EOF

    # Create Wiki/CLAUDE.md (simplified version)
    cat > Wiki/CLAUDE.md << 'EOF'
# Requirements Wiki Schema

This is a requirements-focused knowledge base following the LLM Wiki pattern. You are responsible for maintaining and growing this wiki.

## Structure

- **requirements/** - Structured requirement documents (REQ-XXX format with YAML frontmatter)
- **notes/** - Meeting notes, design discussions, research, decisions
- **Wiki/** - Your maintained knowledge base
  - `Concepts/` - Ideas, principles, patterns, domain models
  - `Techniques/` - Methods, procedures, algorithms, practices
  - `Tools/` - Tech stack, platforms, frameworks, utilities
  - `People/` - Stakeholders, SMEs, team members, decision makers
  - `Sources/` - Requirement summaries, external documentation
  - `index.md` - Categorized table of contents
  - `log.md` - Chronological operation history
  - `overview.md` - Wiki overview and introduction
  - `CLAUDE.md` - This schema file

## Core Operations

See SYSTEM_PROMPT.md in the repository root for complete operational details including:
- INGEST workflow (create 8-12 focused pages with cross-links)
- QUERY workflow (search and synthesize answers)
- LINT workflow (check wiki health)
- Page templates and naming conventions
- Category assignment rules
- Cross-linking strategy
- Obsidian compatibility rules

## Quick Guidelines

1. **Parallel page creation**: Create multiple wiki pages simultaneously (8-12 pages per ingest)
2. **Cross-link everything**: Connect related concepts using `[[wikilink]]` syntax
3. **Build on existing pages**: Update existing pages rather than creating duplicates
4. **Keep index current**: Always update `Wiki/index.md` when creating new pages
5. **Obsidian compatibility**: Use kebab-case filenames, proper wikilinks
6. **Requirements traceability**: Always link back to source requirements using REQ-IDs

For detailed operational rules, see SYSTEM_PROMPT.md.
EOF

    echo "✅ Wiki initialized successfully"
else
    echo "✅ Wiki already initialized"
fi

# 5. Inform the user
echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "  1. Activate virtual environment: source .venv/bin/activate"
echo "  2. Start Claude: claude"
echo "  3. Start creating requirements or notes!"
echo ""
echo "Try these commands in Claude:"
echo "  - 'I need a requirement for user authentication'"
echo "  - 'Create a note for today's meeting'"
echo "  - 'Ingest the new requirements into the wiki'"
echo ""