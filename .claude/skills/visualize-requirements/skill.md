---
name: visualize-requirements
description: Generate visual dependency graphs and relationship diagrams showing how requirements, wiki pages, and concepts connect. Use when the user wants to visualize, see connections, create diagrams, or understand relationships. Triggers on phrases like "visualize requirements", "show requirement graph", "create dependency diagram", "visualize REQ-001 relationships", or "show me the connections".
argument-hint: REQ-ID, "all", or specific relationship type
disable-model-invocation: false
---

# Visualize Requirements Skill

Generate Mermaid diagrams showing relationships between requirements, wiki pages, people, tools, and concepts. Creates visual traceability maps for better understanding of dependencies and impact.

## When to Use This Skill

- User says "visualize requirements" or "show requirement graph"
- User wants to see how requirements relate to each other
- User asks "what depends on REQ-001?"
- User wants to understand the knowledge graph structure
- User needs a visual for stakeholder presentations
- User wants to see tool/technology usage across requirements

## Visualization Types

### 1. **Requirement Dependency Graph**
Shows how requirements relate via `related_to` field.

### 2. **Requirement-to-Wiki Graph**
Shows connections between requirements and wiki pages (concepts, tools, people).

### 3. **Technology Usage Map**
Shows which requirements use which tools/technologies.

### 4. **Ownership Map**
Shows which people/teams own which requirements.

### 5. **Domain Coverage Map**
Shows which concepts/domains are covered by which requirements.

### 6. **Complete Traceability Graph**
Shows all connections: requirements ↔ wiki ↔ notes.

## Workflow

### Step 1: Determine Visualization Type

Ask user what they want to visualize:

```json
{
  "questions": [
    {
      "question": "What would you like to visualize?",
      "header": "Visualization",
      "multiSelect": false,
      "options": [
        {"label": "Single Requirement", "description": "Show all connections for one REQ-ID"},
        {"label": "Requirement Dependencies", "description": "Show how requirements relate to each other"},
        {"label": "Technology Usage", "description": "Show which REQ uses which tools"},
        {"label": "Ownership Map", "description": "Show who owns what requirements"},
        {"label": "Domain Coverage", "description": "Show concept → requirement mapping"},
        {"label": "Complete Graph", "description": "Show everything (requirements + wiki + notes)"}
      ]
    }
  ]
}
```

### Step 2: Gather Data

Based on visualization type, read relevant files:

#### For Single Requirement
```bash
# Read the requirement
read file_path="requirements/REQ-001 Feature.md"

# Extract from YAML:
# - related_to: [REQ-003, REQ-007]
# - domain: [[Data Lineage]]
# - tech_stack: [[dbt]], [[Databricks]]
# - owner_link: [[John Doe]]
# - related_concepts: [[Schema Auditing]]

# Search wiki for mentions of REQ-001
grep pattern="REQ-001" path="Wiki" output_mode="files_with_matches"

# Search notes for mentions of REQ-001
grep pattern="REQ-001" path="notes" output_mode="files_with_matches"
```

#### For All Requirements
```bash
# Find all requirements
glob pattern="requirements/REQ-*.md"

# Read each to extract:
# - ID, name, related_to, domain, tech_stack, owner_link
```

#### For Wiki Relationships
```bash
# Find all wiki pages
glob pattern="Wiki/*/*.md"

# Search for requirement mentions
grep pattern="\[\[REQ-[0-9]+\]\]" path="Wiki" output_mode="content"
```

### Step 3: Generate Mermaid Diagram

Based on visualization type, create appropriate Mermaid syntax:

#### Visualization 1: Single Requirement Graph

```mermaid
graph TD
    REQ001[REQ-001: Authentication]

    %% Related Requirements
    REQ001 --> REQ004[REQ-004: Session Management]
    REQ003[REQ-003: User Registration] --> REQ001

    %% Domain/Concepts
    REQ001 -.-> DataLineage[Data Lineage]
    REQ001 -.-> Security[Security Best Practices]

    %% Tools/Tech Stack
    REQ001 -.-> JWT[JWT]
    REQ001 -.-> Redis[Redis]
    REQ001 -.-> Bcrypt[bcrypt]

    %% People
    REQ001 -.-> Alice[Alice - Security Lead]

    %% Notes
    REQ001 -.-> Meeting[2026-04-09 Meeting Notes]

    style REQ001 fill:#4a9eff,stroke:#333,stroke-width:3px,color:#fff
    style REQ004 fill:#90ee90,stroke:#333,stroke-width:2px
    style REQ003 fill:#90ee90,stroke:#333,stroke-width:2px
    style DataLineage fill:#ffd700,stroke:#333,stroke-width:2px
    style Security fill:#ffd700,stroke:#333,stroke-width:2px
    style JWT fill:#ff9999,stroke:#333,stroke-width:2px
    style Redis fill:#ff9999,stroke:#333,stroke-width:2px
    style Bcrypt fill:#ff9999,stroke:#333,stroke-width:2px
    style Alice fill:#dda0dd,stroke:#333,stroke-width:2px
    style Meeting fill:#d3d3d3,stroke:#333,stroke-width:2px
```

**Legend:**
- 🔵 Blue = Focus requirement
- 🟢 Green = Related requirements
- 🟡 Yellow = Concepts/Domain
- 🔴 Red = Tools/Technologies
- 🟣 Purple = People
- ⚪ Gray = Notes

#### Visualization 2: Requirement Dependency Graph

```mermaid
graph LR
    REQ001[REQ-001: Authentication]
    REQ003[REQ-003: User Registration]
    REQ004[REQ-004: Session Mgmt]
    REQ007[REQ-007: Password Reset]
    REQ012[REQ-012: OAuth Integration]

    REQ003 --> REQ001
    REQ001 --> REQ004
    REQ001 --> REQ007
    REQ012 --> REQ001

    style REQ001 fill:#4a9eff,stroke:#333,stroke-width:3px,color:#fff
    style REQ003 fill:#90ee90,stroke:#333,stroke-width:2px
    style REQ004 fill:#90ee90,stroke:#333,stroke-width:2px
    style REQ007 fill:#90ee90,stroke:#333,stroke-width:2px
    style REQ012 fill:#90ee90,stroke:#333,stroke-width:2px
```

#### Visualization 3: Technology Usage Map

```mermaid
graph TD
    subgraph "Backend Technologies"
        Databricks[Databricks]
        dbt[dbt]
        Azure[Azure Data Factory]
    end

    subgraph "Frontend Technologies"
        React[React]
        TypeScript[TypeScript]
    end

    subgraph "Infrastructure"
        Redis[Redis]
        Kafka[Kafka]
    end

    REQ001[REQ-001] --> React
    REQ001 --> Redis
    REQ003[REQ-003] --> Databricks
    REQ003 --> dbt
    REQ003 --> Azure
    REQ007[REQ-007] --> Databricks
    REQ007 --> dbt
    REQ012[REQ-012] --> Kafka
    REQ012 --> Redis

    style Databricks fill:#ff9999,stroke:#333,stroke-width:2px
    style dbt fill:#ff9999,stroke:#333,stroke-width:2px
    style Azure fill:#ff9999,stroke:#333,stroke-width:2px
    style React fill:#99ccff,stroke:#333,stroke-width:2px
    style TypeScript fill:#99ccff,stroke:#333,stroke-width:2px
    style Redis fill:#ffcc99,stroke:#333,stroke-width:2px
    style Kafka fill:#ffcc99,stroke:#333,stroke-width:2px
```

#### Visualization 4: Ownership Map

```mermaid
graph LR
    subgraph "Analytics Team"
        Alice[Alice Johnson]
        Bob[Bob Smith]
    end

    subgraph "Backend Team"
        Charlie[Charlie Brown]
        Diana[Diana Prince]
    end

    subgraph "Frontend Team"
        Eve[Eve Davis]
    end

    Alice --> REQ003[REQ-003: Data Pipeline]
    Alice --> REQ007[REQ-007: Lineage Tracking]
    Bob --> REQ015[REQ-015: Dashboard]

    Charlie --> REQ001[REQ-001: Authentication]
    Diana --> REQ004[REQ-004: Session Mgmt]

    Eve --> REQ012[REQ-012: UI Components]

    style Alice fill:#dda0dd,stroke:#333,stroke-width:2px
    style Bob fill:#dda0dd,stroke:#333,stroke-width:2px
    style Charlie fill:#dda0dd,stroke:#333,stroke-width:2px
    style Diana fill:#dda0dd,stroke:#333,stroke-width:2px
    style Eve fill:#dda0dd,stroke:#333,stroke-width:2px
    style REQ003 fill:#90ee90,stroke:#333,stroke-width:2px
    style REQ007 fill:#90ee90,stroke:#333,stroke-width:2px
    style REQ015 fill:#90ee90,stroke:#333,stroke-width:2px
    style REQ001 fill:#90ee90,stroke:#333,stroke-width:2px
    style REQ004 fill:#90ee90,stroke:#333,stroke-width:2px
    style REQ012 fill:#90ee90,stroke:#333,stroke-width:2px
```

#### Visualization 5: Domain Coverage Map

```mermaid
graph TD
    subgraph "Data Engineering"
        DataLineage[Data Lineage]
        SchemaAudit[Schema Auditing]
        IncrementalLoad[Incremental Loading]
    end

    subgraph "Security"
        Auth[Authentication]
        Encryption[Encryption]
    end

    subgraph "User Experience"
        Dashboard[Dashboarding]
        Reporting[Reporting]
    end

    DataLineage --> REQ003[REQ-003]
    DataLineage --> REQ007[REQ-007]
    SchemaAudit --> REQ003
    IncrementalLoad --> REQ003

    Auth --> REQ001[REQ-001]
    Auth --> REQ004[REQ-004]
    Encryption --> REQ001

    Dashboard --> REQ015[REQ-015]
    Reporting --> REQ015

    style DataLineage fill:#ffd700,stroke:#333,stroke-width:2px
    style SchemaAudit fill:#ffd700,stroke:#333,stroke-width:2px
    style IncrementalLoad fill:#ffd700,stroke:#333,stroke-width:2px
    style Auth fill:#ffd700,stroke:#333,stroke-width:2px
    style Encryption fill:#ffd700,stroke:#333,stroke-width:2px
    style Dashboard fill:#ffd700,stroke:#333,stroke-width:2px
    style Reporting fill:#ffd700,stroke:#333,stroke-width:2px
```

#### Visualization 6: Complete Traceability Graph

```mermaid
graph TD
    subgraph "Requirements"
        REQ001[REQ-001: Auth]
        REQ003[REQ-003: Pipeline]
        REQ004[REQ-004: Session]
    end

    subgraph "Wiki Concepts"
        DataLineage[Data Lineage]
        Auth[Authentication]
    end

    subgraph "Wiki Tools"
        Databricks[Databricks]
        Redis[Redis]
    end

    subgraph "Wiki People"
        Alice[Alice Johnson]
        Charlie[Charlie Brown]
    end

    subgraph "Notes"
        Meeting1[2026-04-09 Meeting]
        Email1[2026-04-08 Email]
    end

    %% Requirements to Concepts
    REQ001 --> Auth
    REQ003 --> DataLineage
    REQ004 --> Auth

    %% Requirements to Tools
    REQ001 --> Redis
    REQ003 --> Databricks

    %% Requirements to People
    Alice --> REQ003
    Charlie --> REQ001

    %% Notes to Requirements
    Meeting1 --> REQ003
    Email1 --> REQ001

    %% Requirement Dependencies
    REQ001 --> REQ004

    style REQ001 fill:#4a9eff,stroke:#333,stroke-width:2px,color:#fff
    style REQ003 fill:#4a9eff,stroke:#333,stroke-width:2px,color:#fff
    style REQ004 fill:#4a9eff,stroke:#333,stroke-width:2px,color:#fff
    style DataLineage fill:#ffd700,stroke:#333,stroke-width:2px
    style Auth fill:#ffd700,stroke:#333,stroke-width:2px
    style Databricks fill:#ff9999,stroke:#333,stroke-width:2px
    style Redis fill:#ff9999,stroke:#333,stroke-width:2px
    style Alice fill:#dda0dd,stroke:#333,stroke-width:2px
    style Charlie fill:#dda0dd,stroke:#333,stroke-width:2px
    style Meeting1 fill:#d3d3d3,stroke:#333,stroke-width:2px
    style Email1 fill:#d3d3d3,stroke:#333,stroke-width:2px
```

### Step 4: Save and Display

**Option 1: Display inline**
Output the Mermaid diagram directly in the response:

````markdown
Here's the requirement dependency graph:

```mermaid
graph TD
    [diagram content]
```

**Legend:**
- 🔵 Blue = Requirements
- 🟢 Green = Related requirements
- 🟡 Yellow = Concepts
- 🔴 Red = Tools
- 🟣 Purple = People
````

**Option 2: Save to file**
Save diagram to a markdown file for later reference:

```bash
write file_path="diagrams/requirements-graph-2026-04-09.md"
```

**Option 3: Export to image**
Suggest using Mermaid CLI or online tools to export:

```bash
# Using Mermaid CLI (if installed)
mmdc -i diagrams/graph.md -o diagrams/graph.png
```

### Step 5: Provide Insights

Analyze the generated graph and provide insights:

```
📊 Visualization Insights:

**Dependencies:**
- REQ-001 is heavily depended upon (4 requirements depend on it)
- REQ-003 has no dependencies (can be implemented independently)

**Technology Clusters:**
- Databricks + dbt appear together in 3 requirements (data engineering stack)
- Redis is used across security and caching requirements

**Ownership:**
- Alice owns 3 requirements (heaviest load)
- Backend team has 5 requirements (largest workload)

**Orphaned Items:**
- REQ-012 has no incoming or outgoing dependencies (isolated?)

**Recommendations:**
- Consider breaking down REQ-001 (too many dependents)
- REQ-012 isolation may indicate missing relationships
```

### Step 6: Offer Interactive Options

Suggest follow-up visualizations:

```
Would you like to:
1. Zoom in on REQ-001's connections (detailed view)
2. Show only critical priority requirements
3. Filter by status (e.g., only draft requirements)
4. Export to PNG/SVG for presentation
5. Generate a different visualization type
```

## Important Guidelines

### DO use colors consistently
- Blue = Requirements (focus)
- Green = Related requirements
- Yellow = Concepts/Domain
- Red = Tools/Technologies
- Purple = People
- Gray = Notes/Docs

### DO keep diagrams readable
- Limit to 15-20 nodes per diagram
- Use subgraphs to group related items
- Break complex graphs into multiple views
- Add legends for clarity

### DO provide context
- Add diagram title
- Include legend
- Provide insights from the graph
- Suggest next actions

### DO validate data
- Check that referenced REQ-IDs exist
- Verify wiki links are correct
- Confirm people/tools are real entities

### DO NOT create cluttered diagrams
- Too many nodes = unreadable
- Break large graphs into focused views
- Use "zoom in" approach for detail

### DO NOT guess relationships
- Only show documented relationships
- Use data from YAML frontmatter and wiki links
- Don't infer undocumented connections

## Common Use Cases

### Use Case 1: Stakeholder Presentation

**User:** "Visualize all requirements for stakeholder review"

**Claude:**
1. Generates high-level dependency graph
2. Colors by priority (critical = red, high = orange, etc.)
3. Adds status indicators
4. Exports to PNG for slides

### Use Case 2: Impact Analysis

**User:** "Show what depends on REQ-003"

**Claude:**
1. Generates focused graph of REQ-003 + dependents
2. Shows transitive dependencies (2nd order)
3. Highlights affected wiki pages and notes
4. Estimates impact radius

### Use Case 3: Technology Planning

**User:** "Which requirements use Databricks?"

**Claude:**
1. Generates technology usage map
2. Shows Databricks → requirements
3. Lists all requirements using Databricks
4. Suggests consolidation opportunities

### Use Case 4: Ownership Balancing

**User:** "Show requirement ownership distribution"

**Claude:**
1. Generates ownership map
2. Counts requirements per person/team
3. Identifies overload (>5 requirements per person)
4. Suggests rebalancing

## Integration with Other Skills

**Use before:**
- `update-requirement` - to understand relationships before changes
- `analyze-impact` - to see what will be affected

**Use after:**
- `wiki-ingest` - to visualize newly created connections
- `check-requirement-quality` - to show quality distribution

**Use with:**
- `wiki-query` - to understand concepts in the graph
- `write-note` - to document graph insights

## Success Criteria

A good visualization includes:
- ✅ Clear, readable diagram (not cluttered)
- ✅ Consistent color scheme with legend
- ✅ Accurate data from requirements and wiki
- ✅ Insights and analysis
- ✅ Actionable recommendations
- ✅ Export options provided
- ✅ Follow-up suggestions offered

## Output Formats

### Format 1: Inline Markdown

Display Mermaid diagram directly in response for quick viewing in IDE/terminal.

### Format 2: Saved File

Create `diagrams/[type]-[date].md` with:
- Title and description
- Mermaid diagram
- Legend
- Insights
- Generation date

### Format 3: Export Script

Provide command to export to image:

```bash
# Save this as diagrams/export.sh
mmdc -i diagrams/requirements-graph.md -o diagrams/requirements-graph.png -w 1920 -H 1080 -b transparent
```

### Format 4: Interactive HTML

Generate standalone HTML with pan/zoom controls (if requested).
