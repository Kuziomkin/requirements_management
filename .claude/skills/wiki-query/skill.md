---
name: wiki-query
description: Search the Wiki and answer questions using cross-linked knowledge pages. Use this skill when the user asks questions about the knowledge base, wants to search for concepts, or needs information from requirements. Triggers on phrases like "what does the wiki say about", "search wiki for", "find in wiki", "what do we know about", or any question that should be answered from the knowledge base.
argument-hint: question or search term
disable-model-invocation: false
---

# Wiki Query Skill

Search the Wiki knowledge base and synthesize answers from cross-linked pages, requirements, and notes. Creates new wiki pages if the analysis reveals valuable insights worth preserving.

## When to Use This Skill

- User asks "What do we know about [topic]?"
- User says "Search wiki for [term]"
- User asks "How does [concept A] relate to [concept B]?"
- User wants to understand requirements related to a topic
- User asks "What requirements mention [technology]?"
- User wants to trace relationships between concepts

## Workflow

### Step 1: Parse the Query

Identify what the user is asking for:

**Query types:**
- **Concept lookup** - "What is data lineage?" → Find and explain the concept
- **Requirement search** - "What requirements use Databricks?" → Find related requirements
- **Relationship tracing** - "How does X relate to Y?" → Trace cross-links
- **Implementation details** - "How should we implement authentication?" → Find technique pages
- **Ownership/responsibility** - "Who owns the data pipeline?" → Find people pages
- **Technology stack** - "What tools do we use for ETL?" → Find tool pages

### Step 2: Search the Wiki

Use Grep to search wiki pages for relevant information:

```bash
# Search all wiki pages for a term
grep pattern="data lineage" path="Wiki" output_mode="files_with_matches"

# Search specific category
grep pattern="databricks" path="Wiki/Tools" output_mode="content"

# Search for requirement references
grep pattern="REQ-001" path="Wiki" output_mode="content"
```

**Search strategy:**
1. Start with exact term match
2. If no results, try related terms or partial matches
3. Search across all categories (Concepts, Techniques, Tools, People, Sources)
4. Look for cross-references using `[[wikilinks]]`

### Step 3: Read Relevant Pages

Read the pages that match the search:

```bash
read file_path="Wiki/Concepts/data-lineage.md"
read file_path="Wiki/Techniques/dbt-modeling-patterns.md"
```

**Follow cross-links:**
- If a page links to `[[related-concept]]`, read that page too
- Trace relationships through the "Related" section
- Check "Requirements" section to find source documents

**Cross-reference with requirements:**
- If wiki pages reference `[[REQ-001]]`, read the requirement for authoritative details
- Use wiki for synthesized understanding, requirements for specifications

### Step 4: Synthesize Answer

Combine information from multiple pages into a coherent answer:

**Answer structure:**
1. **Direct answer** - Lead with the core answer to the user's question
2. **Context and details** - Provide supporting information from wiki pages
3. **Citations** - Reference wiki pages using `[[page-name]]` and requirements using `[[REQ-001]]`
4. **Related information** - Mention related concepts the user might be interested in

**Example answer format:**

```markdown
**Data lineage** tracks the flow of data through a system, documenting transformations and dependencies ([[data-lineage]]).

In our requirements, it's used in:
- [[REQ-001]] — Customer 360 pipeline uses lineage tracking for compliance
- [[REQ-005]] — Analytics dashboard requires lineage for drill-down

The implementation uses [[dbt-modeling-patterns]] with [[databricks]] as the platform.
The [[analytics-team]] owns this capability.

Related concepts: [[idempotency]], [[schema-auditing]], [[event-sourcing]]

Sources: [REQ-001](../../requirements/REQ-001%20Customer%20360.md), [[dbt-modeling-patterns]]
```

**Citation guidelines:**
- Always cite wiki pages using `[[page-name]]` format
- Cite requirements using `[[REQ-XXX]]` format
- Include "Sources:" section at the end with markdown links to files
- Don't make claims without citations

### Step 5: Create New Pages (Optional)

If your analysis reveals insights worth preserving, create new wiki pages:

**When to create pages from queries:**

✅ **Create pages when:**
- You've synthesized a comparison between concepts (e.g., "Batch vs Stream Processing")
- You've documented a pattern that appears across multiple requirements
- You've identified a decision or principle worth capturing
- The user asks to save the analysis: "Can you add this to the wiki?"

❌ **Don't create pages when:**
- The answer is already well-documented in existing pages
- The query was too specific or one-off
- You're just summarizing a single requirement

**If creating pages:**
1. Follow the same template as wiki-ingest
2. Cross-link to related pages
3. Cite the requirements that led to this insight
4. Update `Wiki/index.md`
5. Log the operation in `Wiki/log.md`

### Step 6: Log Significant Queries

For substantial research queries, append to `Wiki/log.md`:

```markdown
## [TODAY'S DATE]

### Query: [Topic]
- **Question**: What the user asked
- **Type**: Query
- **Pages Consulted**: List of wiki pages and requirements referenced
- **Answer Summary**: Brief summary of what was found
- **New Pages**: Any pages created from this analysis (if applicable)
```

**When to log:**
- Query involved reading 5+ pages
- Query led to creating new wiki pages
- Query revealed gaps or contradictions in the wiki
- User explicitly asks to log the research

**When not to log:**
- Simple lookups of a single page
- Quick searches with no findings
- Routine "what is X" questions

### Step 7: Report Findings

Provide the synthesized answer with clear citations.

**If no results found:**
"I couldn't find information about [topic] in the Wiki. This might be worth adding if we have requirements or notes that cover it. Should I search the requirements/ or notes/ directories directly?"

**If partial results:**
"I found some information about [topic] in [[page-1]] and [[page-2]], but it's not fully documented. What specific aspect are you interested in? I can search the requirements for more details."

**If contradictions found:**
"I found conflicting information: [[page-1]] says X, but [[REQ-005]] specifies Y. This might need reconciliation. Should I create an issue or update the wiki?"

## Important Guidelines

### DO trace relationships
- Follow `[[wikilinks]]` to related concepts
- Check both directions of relationships
- Look at "Requirements" sections to see usage context

### DO synthesize across sources
- Combine information from multiple wiki pages
- Cross-reference with original requirements
- Provide a coherent narrative, not just quotes

### DO cite everything
- Use `[[page-name]]` for wiki pages
- Use `[[REQ-XXX]]` for requirements
- Include "Sources:" section with markdown links

### DO suggest related information
- Point to related concepts the user might find useful
- Mention cross-links that weren't directly relevant but might be interesting

### DO NOT invent information
- Only report what's documented in the wiki or requirements
- If information is missing, say so explicitly
- Don't fill gaps with assumptions

### DO NOT summarize without understanding
- Read pages thoroughly before synthesizing
- Trace cross-links to understand context
- Verify claims against source requirements

## Search Optimization

**Use multiple search strategies:**

1. **Exact match** - Search for exact term
2. **Partial match** - Search for word stems or variants
3. **Category-specific** - Search within likely categories (Tools for tech, Techniques for methods)
4. **Cross-reference** - Search for requirement IDs if looking for implementation details
5. **People search** - Look in People/ for ownership questions

**Example search progression:**

```bash
# Try exact term
grep pattern="data lineage" path="Wiki" output_mode="files_with_matches"

# Try partial/variant
grep pattern="lineage" path="Wiki" output_mode="files_with_matches"

# Try related terms
grep pattern="data flow|data tracking|data provenance" path="Wiki" output_mode="files_with_matches"

# Search requirements if wiki doesn't have it
grep pattern="lineage" path="requirements" output_mode="files_with_matches"
```

## Examples

### Example 1: Simple concept lookup

**User:** "What is idempotency?"

**Claude:** [Searches Wiki for "idempotency"]

**Claude:** [Finds Wiki/Concepts/idempotency.md]

**Claude:** [Reads the page]

**Claude:** "**Idempotency** ensures that operations can be safely retried without unintended side effects ([[idempotency]]).

In our requirements:
- [[REQ-003]] — Data pipeline requires idempotent batch jobs
- [[REQ-007]] — API endpoints must support safe retries

This is implemented using [[incremental-loading]] techniques with [[databricks]], owned by [[analytics-team]].

Related concepts: [[data-lineage]], [[exactly-once-processing]]

Sources: [REQ-003](../../requirements/REQ-003%20Data%20Pipeline.md), [[idempotency]]"

**Claude:** [Does not log - simple lookup]

### Example 2: Complex relationship query

**User:** "How does our authentication approach relate to session management?"

**Claude:** [Searches for "authentication" and "session management"]

**Claude:** [Finds Wiki/Concepts/authentication.md and Wiki/Concepts/session-management.md]

**Claude:** [Reads both pages and follows cross-links]

**Claude:** [Finds references to [[REQ-001]] and [[REQ-004]]]

**Claude:** [Reads requirements for authoritative details]

**Claude:** "Our **authentication** approach ([[authentication]]) is tightly integrated with **session management** ([[session-management]]):

**How they relate:**
- Authentication generates short-lived JWT tokens (15 min) that serve as session identifiers
- Session state is stored in [[redis]] with the JWT as the key
- [[REQ-001]] specifies the auth flow, [[REQ-004]] specifies session lifecycle

**Key decision:** We chose stateless JWT + server-side session store (hybrid approach) to balance performance and security, as documented in [[jwt-token-strategy]].

**Implementation:**
- Auth service: [[backend-team]] (owner: [[alice-security-lead]])
- Session store: [[redis]] cluster managed by [[ops-team]]
- Token rotation: Handled by [[refresh-token-mechanism]]

Related concepts: [[oauth-integration]], [[token-expiry]], [[security-best-practices]]

Sources: [REQ-001](../../requirements/REQ-001%20Authentication.md), [REQ-004](../../requirements/REQ-004%20Session%20Management.md), [[authentication]], [[session-management]]"

**Claude:** [Logs to Wiki/log.md - substantial query involving multiple pages]

### Example 3: Technology search

**User:** "What requirements use Databricks?"

**Claude:** [Searches Wiki for "Databricks"]

**Claude:** [Finds Wiki/Tools/databricks.md]

**Claude:** [Reads page, checks "Requirements" section]

**Claude:** "**Databricks** ([[databricks]]) is used in these requirements:

- [[REQ-003]] — Data pipeline for customer analytics
- [[REQ-007]] — Real-time event processing
- [[REQ-012]] — Machine learning model training

**How it's used:**
- Primary platform for ETL jobs ([[dbt-modeling-patterns]])
- Notebooks for exploratory data analysis
- MLflow integration for model tracking

**Owner:** [[analytics-team]] manages Databricks infrastructure

Related tools: [[dbt]], [[azure-data-factory]], [[spark]]

Sources: [[databricks]], [REQ-003](../../requirements/REQ-003%20Data%20Pipeline.md)"

**Claude:** [Does not log - straightforward search]

### Example 4: Query with new page creation

**User:** "Compare batch processing vs stream processing for our data pipeline"

**Claude:** [Searches for "batch processing" and "stream processing"]

**Claude:** [Finds references in multiple requirement documents]

**Claude:** [Reads requirements and extracts comparison points]

**Claude:** "Based on our requirements, here's how **batch processing** compares to **stream processing**:

**Batch Processing** (current approach in [[REQ-003]]):
- Pros: Simpler, cheaper, works for daily reports
- Cons: Higher latency (24hr), not suitable for real-time needs
- Tech: [[databricks]] with scheduled jobs

**Stream Processing** (proposed in [[REQ-015]]):
- Pros: Real-time updates, lower latency (<1 min)
- Cons: More complex, higher operational cost
- Tech: [[kafka]] + [[spark-streaming]]

**Our approach:** Hybrid - batch for historical analytics, stream for real-time dashboards ([[REQ-018]]).

This comparison seems valuable. Should I create a wiki page for 'batch-vs-stream-processing' to capture this analysis?"

**User:** "Yes, please"

**Claude:** [Creates Wiki/Concepts/batch-vs-stream-processing.md]

**Claude:** [Updates Wiki/index.md]

**Claude:** [Logs the operation]

**Claude:** "✅ Created [[batch-vs-stream-processing]] page with this comparison. Updated index and log."

## Success Criteria

A good query response includes:
- ✅ Direct answer to the user's question
- ✅ Citations to wiki pages using `[[wikilinks]]`
- ✅ Citations to requirements using `[[REQ-XXX]]`
- ✅ Cross-references to related concepts
- ✅ "Sources:" section with markdown links
- ✅ Suggests related information
- ✅ Creates new pages only when valuable insights emerge
- ✅ Logs substantial queries

## Error Handling

**If Wiki doesn't exist:**
"The Wiki hasn't been initialized yet. Run 'ingest requirements' first to create the knowledge base."

**If search returns no results:**
"I couldn't find '[term]' in the Wiki. Should I search the requirements/ or notes/ directories directly to see if we have information about this?"

**If pages are missing expected content:**
"The wiki page for [topic] exists but seems incomplete. Should I re-ingest the requirements to update it?"

**If contradictions are found:**
"I found conflicting information:
- [[page-1]] says X
- [[REQ-005]] specifies Y

This needs reconciliation. Should I update the wiki page or flag this for review?"
