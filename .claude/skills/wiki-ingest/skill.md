---
name: wiki-ingest
description: Process requirements and notes into structured Wiki pages with cross-links. Use this skill when the user asks to "ingest", "process", "update wiki", "add to wiki", or mentions processing requirements/notes into the knowledge base. Triggers on phrases like "ingest requirements", "process new notes", "update the wiki", or "add these to the knowledge base".
argument-hint: source path or "requirements" or "notes"
disable-model-invocation: false
---

# Wiki Ingest Skill

Process requirements and notes into a structured, cross-linked knowledge base following the LLM Wiki pattern. Creates focused wiki pages for concepts, techniques, tools, people, and sources with bidirectional links.

## When to Use This Skill

- User says "ingest requirements" or "ingest notes"
- User adds new requirements and asks to process them into the wiki
- User wants to update the wiki with new information
- User asks "process these into the knowledge base"
- User says "add this to the wiki"

## Workflow

### Step 0: Check for Wiki Structure

**First, check if `Wiki/index.md` exists:**

```bash
if [ ! -f Wiki/index.md ]; then
  # Wiki not initialized - run setup
fi
```

If the Wiki doesn't exist, **automatically initialize it** following the SYSTEM_PROMPT.md setup instructions:

1. Create directory structure: `mkdir -p Wiki/{Concepts,Techniques,Tools,People,Sources}`
2. Create all required files in parallel (Welcome.md, Wiki/index.md, Wiki/log.md, Wiki/overview.md, Wiki/CLAUDE.md, CLAUDE.md)
3. Confirm setup: "✅ Requirements Wiki structure initialized. Ready for first ingest!"
4. Proceed to Step 1

### Step 1: Identify Sources to Ingest

Ask the user which sources to process using AskUserQuestion:

```json
{
  "questions": [
    {
      "question": "What would you like me to ingest into the Wiki?",
      "header": "Source",
      "multiSelect": true,
      "options": [
        {"label": "All requirements (REQ-* files)", "description": "Process all requirement documents in requirements/"},
        {"label": "Recent requirements (last 7 days)", "description": "Only process requirements modified in the last week"},
        {"label": "Specific requirements", "description": "You'll specify which REQ-IDs to process"},
        {"label": "All artifacts", "description": "Process all markdown files in artifacts/"},
        {"label": "Recent notes (last 7 days)", "description": "Only process notes modified in the last week"},
        {"label": "Specific artifacts", "description": "You'll specify which note files to process"}
      ]
    }
  ]
}
```

**If user selects "Specific requirements" or "Specific artifacts":**
- Ask for file paths or REQ-IDs
- Example: "Which requirements? (e.g., REQ-001, REQ-005, REQ-012)"

**If user initially provided a path/pattern:**
- Use that directly (e.g., "ingest requirements/REQ-001.md" → process that file)

### Step 2: Read and Analyze Sources

Read the selected files thoroughly:

```bash
# Use Glob to find files
glob pattern="requirements/REQ-*.md"
glob pattern="artifacts/*.md"

# Use Read to read each file
read file_path="requirements/REQ-001 Feature.md"
```

**For each source, extract:**

1. **YAML frontmatter** (for requirements):
   - `id`, `name`, `description`, `status`, `priority`, `owner`
   - `related_to` (array of REQ-IDs)
   - `test_cases` (array of TC-XXX)

2. **Markdown content**:
   - Implementation approach and technical details
   - Key decisions and rationale
   - Technologies, tools, frameworks mentioned
   - People/teams referenced
   - External documentation links
   - Acceptance criteria

**Identify 8-12 key extractable elements per batch of sources:**

- **Concepts** - Abstract ideas, principles, patterns, domain models
  - Examples: "data-lineage", "idempotency", "event-sourcing"
  - Test: "Is this an abstract idea referenced multiple times?"

- **Techniques** - Methods, procedures, algorithms, practices
  - Examples: "dbt-modeling-patterns", "schema-auditing", "incremental-loading"
  - Test: "Is this a process or methodology?"

- **Tools** - Technologies, platforms, frameworks
  - Examples: "databricks", "azure-data-factory", "dbt"
  - Test: "Is this a concrete tool or technology?"

- **People** - Stakeholders, owners, teams
  - Examples: "john-smith-data-architect", "analytics-team"
  - Test: "Is this a person or team?"

- **Sources** - Requirement summaries (meta-pages about requirements)
  - Examples: "req-001-summary", "authentication-requirements-overview"
  - Test: "Is this a summary of a source document?"

**Extraction principles:**
- Extract concepts that are **defined explicitly** (not assumed)
- Extract elements **referenced multiple times** (important to requirements)
- Extract elements that are **linkable** (other wiki pages would reference them)
- Focus on **reusable knowledge** (not one-off examples or test data)

### Step 3: Create Wiki Pages in Parallel

**CRITICAL: Create 8-12 pages simultaneously using multiple Write tool calls in a single message.**

Use this template for each page:

```markdown
# Page Title

One-line summary of the concept/technique/tool/person.

## Overview
2-3 paragraphs explaining the topic with cross-references using [[other-page-name]].

## Key Points / Characteristics / How It Works
- Important detail 1
- Important detail 2
- Important detail 3

## [Context-Specific Section]
Examples, requirements using this, implementation details, responsibilities, etc.

## Requirements
- [[REQ-001]] — Brief description of how this requirement relates
- [[REQ-002]] — Brief description

## Related
- [[related-concept-1]] — Brief description
- [[related-concept-2]] — Brief description
- [[related-concept-3]] — Brief description

## Sources
- [REQ-001 Feature Name](../../requirements/REQ-001%20Feature%20Name.md)
- [Meeting Notes 2026-04-09](../../artifacts/2026-04-09-meeting.md)
```

**Category assignment:**

Place each page in the correct subdirectory:

- `Wiki/Concepts/` — Abstract ideas, principles, patterns
- `Wiki/Techniques/` — Methods, procedures, algorithms
- `Wiki/Tools/` — Technologies, platforms, frameworks
- `Wiki/People/` — Individuals, teams, stakeholders
- `Wiki/Sources/` — Requirement summaries, reference docs

**Naming convention:**
- Use **kebab-case**: `data-lineage.md`, not `Data Lineage.md`
- Keep names concise but descriptive
- Avoid abbreviations unless universal (API, ETL, etc.)

**Cross-linking strategy:**

Link aggressively using `[[page-name]]` syntax:

- Link when explaining: "This relies on [[incremental-loading]] to..."
- Link related concepts: "Unlike [[batch-processing]], this approach..."
- Link to requirements using `[[REQ-001]]` format
- Link to people: "Owned by [[john-smith]]"
- Add 3-5 related links in the "Related" section

**Source citations:**

Always cite sources with relative paths (URL-encode spaces as `%20`):

```markdown
## Sources
- [REQ-001 Feature](../../requirements/REQ-001%20Feature.md)
- [Meeting Notes](../../artifacts/2026-04-09-meeting.md)
```

### Step 4: Update Index

Add all new pages to `Wiki/index.md`:

```markdown
## Concepts

- [[data-lineage]] — Tracking data flow through the system
- [[idempotency]] — Ensuring operations can be safely retried
- [[customer-360]] — Unified customer data view

## Techniques

- [[dbt-modeling-patterns]] — Best practices for dbt model organization
- [[schema-auditing]] — Detecting schema drift in pipelines

## Tools

- [[databricks]] — Unified analytics platform
- [[dbt]] — Data transformation tool
- [[azure-data-factory]] — Cloud ETL service

## People

- [[john-smith]] — Data architect, owns data pipeline requirements
- [[analytics-team]] — Team responsible for reporting features

## Sources

- [[req-001-summary]] — Overview of authentication requirements
```

**Keep descriptions under 80 characters for scannability.**

Sort entries alphabetically within each category.

### Step 5: Log the Operation

Append to `Wiki/log.md`:

```markdown
## [TODAY'S DATE]

### Ingest: [Requirements Batch / Meeting Notes]
- **Sources**:
  - requirements/REQ-001 Feature.md
  - requirements/REQ-002 Enhancement.md
  - artifacts/2026-04-09-meeting.md
- **Type**: Ingest
- **Description**: Processed requirements for data pipeline and related meeting notes
- **Pages Created** (X total):
  - Concepts (N): data-lineage, idempotency, event-sourcing
  - Techniques (N): dbt-modeling-patterns, schema-auditing
  - Tools (N): databricks, dbt, azure-data-factory
  - People (N): john-smith, analytics-team
  - Sources (N): req-001-summary
- **Cross-links**: Created bidirectional links between requirements and concepts
- **Citations**: All pages cite source requirements and notes
- **Index**: Confirmed index updated with all new pages
```

### Step 6: Report Results

Summarize what was created:

```
✅ Wiki ingest complete!

**Processed sources:**
- 3 requirements (REQ-001, REQ-002, REQ-005)
- 2 notes files

**Created pages (12 total):**
- Concepts: data-lineage, idempotency, customer-360, event-sourcing
- Techniques: dbt-modeling, schema-auditing, incremental-loading
- Tools: databricks, dbt, azure-data-factory
- People: john-smith, analytics-team
- Sources: req-001-summary

**Index and log updated.**

Your knowledge base now has [X] pages across [Y] categories.
```

## Important Guidelines

### DO create focused, atomic pages
- Each page should cover ONE concept, technique, tool, or person
- Don't create overly broad pages like "Data" or "System"
- Don't create overly specific pages like "REQ-001 Section 2.3"

### DO cross-link aggressively
- Link related concepts using `[[page-name]]`
- Link back to requirements using `[[REQ-001]]`
- Add 3-5 related links in the "Related" section
- Create bidirectional connections

### DO cite sources accurately
- Always include "## Sources" section
- Use relative paths: `../../requirements/REQ-001%20Name.md`
- URL-encode spaces as `%20` in markdown links

### DO build on existing pages
- Before creating a new page, check if one exists using Grep
- Update existing pages rather than creating duplicates
- Add new requirements to the "Requirements" section of existing pages

### DO NOT invent information
- Only extract concepts explicitly mentioned in sources
- Don't assume relationships not documented
- If a concept is vague, skip it or ask for clarification

### DO NOT create narrative pages
- Don't summarize requirements as stories
- Don't create timeline or chronological pages
- Focus on extracting reusable, linkable concepts

## Error Handling

**If Wiki structure doesn't exist:**
- Automatically run setup (Step 0)
- Don't ask user permission - just initialize

**If no sources found:**
- Report: "No requirements or notes found matching your criteria. Please add documents to requirements/ or artifacts/ first."

**If Wiki files are corrupted:**
- Report the issue to user
- Suggest running lint operation to check for broken links

## Examples

### Example 1: Ingest all requirements

**User:** "Ingest all requirements"

**Claude:** [Checks if Wiki/index.md exists - it does]

**Claude:** [Uses Glob to find all REQ-*.md files]

**Claude:** [Reads 5 requirement files]

**Claude:** [Identifies 12 elements: 4 concepts, 3 techniques, 3 tools, 2 people]

**Claude:** [Creates 12 wiki pages in parallel using multiple Write calls]

**Claude:** [Updates Wiki/index.md with all 12 new entries]

**Claude:** [Appends operation to Wiki/log.md]

**Claude:** "✅ Wiki ingest complete!

**Processed sources:**
- 5 requirements (REQ-001 through REQ-005)

**Created pages (12 total):**
- Concepts: data-lineage, idempotency, customer-360, event-sourcing
- Techniques: dbt-modeling, schema-auditing, incremental-loading
- Tools: databricks, dbt, azure-data-factory
- People: john-smith, analytics-team

**Index and log updated.**

Your knowledge base now has 12 pages across 4 categories."

### Example 2: Ingest specific requirements

**User:** "Ingest REQ-001 and REQ-002"

**Claude:** [Asks using AskUserQuestion if not clear, or uses provided REQ-IDs directly]

**Claude:** [Reads REQ-001 and REQ-002]

**Claude:** [Identifies 8 elements from these two requirements]

**Claude:** [Creates 8 wiki pages in parallel]

**Claude:** [Updates index and log]

**Claude:** "✅ Ingested REQ-001 and REQ-002.

**Created pages (8 total):**
- Concepts: authentication, session-management
- Techniques: jwt-token-strategy, password-hashing
- Tools: bcrypt, redis
- People: alice-security-lead
- Sources: authentication-requirements-overview

Your Wiki now has 8 new pages."

### Example 3: First-time setup

**User:** "Ingest requirements"

**Claude:** [Checks Wiki/index.md - doesn't exist]

**Claude:** [Automatically creates directory structure]

**Claude:** [Creates Welcome.md, Wiki/index.md, Wiki/log.md, Wiki/overview.md, Wiki/CLAUDE.md, CLAUDE.md]

**Claude:** "✅ Requirements Wiki structure initialized. Ready for first ingest!"

**Claude:** [Proceeds with normal ingest workflow]

## Success Criteria

A good ingest creates:
- ✅ 8-12 focused, atomic pages per batch of sources
- ✅ Dense cross-linking between related concepts
- ✅ All pages cited in index.md
- ✅ Operation logged in log.md
- ✅ All pages cite source requirements and notes
- ✅ Bidirectional links between requirements and wiki pages
- ✅ People pages for stakeholders and owners
- ✅ Tools pages for all technologies mentioned
- ✅ Knowledge is reusable and composable

## What NOT to Create

Avoid these mistakes:

❌ **Too Broad** - Don't create "Data" or "System" pages
❌ **Too Specific** - Don't create "REQ-001 Section 2.3" pages
❌ **Redundant** - Don't create near-duplicate pages
❌ **Narrative** - Don't create timeline/story pages
❌ **Obvious** - Don't create pages for universally known concepts
❌ **Examples** - Don't create pages for test cases or sample data

✅ **Create** - Reusable concepts other requirements would reference

## The "Would I Link to This?" Test

Before creating a page, ask:
- Would 3+ requirements or wiki pages want to link to this?
- Is this a standalone, atomic concept?
- Does this add to the knowledge graph or just repeat the source?
- Will this be useful when writing future requirements?

If no to any, skip creating the page.
