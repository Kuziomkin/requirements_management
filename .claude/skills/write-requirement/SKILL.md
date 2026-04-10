---
name: write-requirement
description: Create structured requirement documents with YAML metadata, detailed implementation notes, and diagrams. Use this skill whenever the user mentions "requirement", "req", "requirements", or asks to document a feature specification. Make sure to use this skill when the user wants to write technical specifications, feature requirements, or create REQ-XXX documents, even if they don't explicitly say "use the requirement skill".
argument-hint: requirement
disable-model-invocation: false
---

# Requirements Writer Skill

Create structured, developer-ready requirement documents following a consistent YAML + markdown format with auto-generated IDs, detailed implementation guidance, and appropriate diagrams.

## Document Structure

Every requirement document follows this exact structure:

```markdown
---
id: REQ-XXX
name: [Requirement Name]
description: [One-line summary]
type: [functional_requirement|non_functional_requirement|technical_requirement]
status: [draft|in-review|approved|implemented]
priority: [low|medium|high|critical]
owner: [team-name]
owner_link: "[[Person Name]]"
domain: "[[Primary Concept]]"
tech_stack:
  - "[[Tool 1]]"
  - "[[Tool 2]]"
related_concepts:
  - "[[Concept A]]"
  - "[[Technique B]]"
related_to:
  - REQ-YYY
  - REQ-ZZZ
test_cases: []
---

# Notes

## Implementation

### Approach
[Detailed technical implementation guidance]

### Key decisions
[Bullet list of important design decisions with rationale]

### Out of scope
[What's explicitly NOT included]

### Open questions
[Unresolved items with checkbox, description, and owner]

### References
[Links to external docs, ADRs, designs]

## Acceptance Criteria

- [ ] **AC-1:** [Testable condition]
- [ ] **AC-2:** [Testable condition]

# Diagrams

[Appropriate mermaid diagrams based on requirement type]
```

**Important notes on YAML frontmatter format:**

- **type**: Classification of requirement. Options: `functional_requirement`, `non_functional_requirement`, `technical_requirement`
  - Functional: User-facing features and behaviors
  - Non-functional: Performance, security, scalability, compliance
  - Technical: Infrastructure, architecture, technical debt

- **owner**: Team name as plain text for Excel tracking (e.g., `backend-team`, `analytics-team`)

- **owner_link**: Person responsible, using Obsidian wikilink format to create graph connections. Quote wikilinks to ensure proper YAML parsing.
  ```yaml
  owner_link: "[[John Doe]]"  # Links to Wiki/People/john-doe.md
  ```

- **domain**: Primary concept area using wikilink to Wiki/Concepts/. Quote wikilinks to ensure proper YAML parsing.
  ```yaml
  domain: "[[Data Lineage]]"  # Links to Wiki/Concepts/data-lineage.md
  ```

- **tech_stack**: Array of wikilinks to Wiki/Tools/ pages for all technologies used. Use YAML array format with `-` prefix and quoted wikilinks.
  ```yaml
  tech_stack:
    - "[[dbt]]"
    - "[[Databricks]]"
    - "[[Azure Data Factory]]"
  ```

- **related_concepts**: Array of wikilinks to Wiki/Concepts/ or Wiki/Techniques/ pages (optional). Use YAML array format with `-` prefix and quoted wikilinks.
  ```yaml
  related_concepts:
    - "[[Schema Auditing]]"
    - "[[Incremental Loading]]"
  ```

- **related_to**: Simple string array of REQ-IDs. No comments or descriptions in YAML.
  ```yaml
  related_to:
    - REQ-001
    - REQ-003
  ```
  Document relationships in prose within the Implementation section instead.

- **test_cases**: Empty array initially. QA team adds TC-XXX IDs later when tests are created.
  ```yaml
  test_cases:
    - TC-001
    - TC-002
  ```

**Why Obsidian Properties Matter:**
These wikilink properties (`owner_link`, `domain`, `tech_stack`, `related_concepts`) create automatic bidirectional connections in Obsidian's graph view. This enables:
- Clicking a tool page shows all requirements using that technology
- Viewing a person page shows all requirements they own
- Navigating from concept to all related requirements
- Impact analysis when technologies or concepts change

## Workflow

### Step 1: Auto-generate REQ-ID and check for duplicates

Before starting the interview, ensure the Excel tracker exists, then delegate to the `requirements-tracker` subagent to analyze it. This protects the main context from large Excel data.

#### Step 1.1: Ensure Excel tracker exists

First, call the MCP tool to create the tracker if it doesn't exist:

```
mcp__requirements-manager__create_requirement_tracker(
  excel_path="requirements/requirements_tracker.xlsx"
)
```

This tool:
- Creates `requirements/requirements_tracker.xlsx` if missing
- Creates the `requirements/` directory if needed
- Returns `status: "created"` if the file was created, or `status: "exists"` if already present
- Sets up the correct column structure: ID, Name, Description, Status, Priority, Owner, Related To, Test Cases, File Path, Last Updated

**Always call this tool first**, even if you think the Excel exists. It's a safe no-op if the file is already there, and prevents errors if the user is starting fresh.

**Error handling:**
- If the tool returns an error, check:
  1. pandas and openpyxl are installed: `pip list | grep -E "pandas|openpyxl"`
  2. The requirements/ directory is writable
  3. Disk space is available
- If dependencies are missing, inform the user: "The Excel tracker requires pandas and openpyxl. Install with: `pip install pandas openpyxl`"
- If the error persists, proceed without Excel tracking and inform the user

#### Step 1.2: Invoke the requirements-tracker subagent

Use the **Agent tool** with these exact parameters:

```
Agent(
  subagent_type="requirements-tracker",
  description="Analyze requirements tracker",
  prompt="The user wants to create a requirement for: [summarize user's request in 1-2 sentences].

  Call the analyze_requirements_tracker MCP tool with this user request, then return the JSON response directly."
)
```

**Why use a subagent?** As the requirements tracker grows (potentially to 1000+ requirements), reading the full Excel file would clutter the main conversation context. The subagent reads the data, analyzes it, and returns only the essential findings, keeping the main context lean.

#### Step 1.3: Parse the subagent's JSON response

The subagent returns JSON with this structure:
```json
{
  "next_id": "REQ-XXX",
  "analysis_status": "none|duplicate_found|contradiction_found|related_found",
  "conflicts": [...],
  "related_requirements": [...],
  "recommendation": {
    "action": "proceed|update_existing|user_decision",
    "details": "..."
  }
}
```

Extract:
- `next_id` - Use this as the new requirement ID
- `analysis_status` - Check if conflicts exist
- `conflicts[]` - Array of conflicting requirements with `req_id`, `name`, `conflict_type`, `reason`
- `related_requirements[]` - Array of related requirements with `req_id`, `name`, `relationship`
- `recommendation.action` - Determines how to proceed

**Error handling:**
- If the subagent's response is not valid JSON:
  1. Try to extract `next_id` from the text (look for "REQ-XXX" pattern)
  2. If found, use that ID and proceed (skip duplicate checking)
  3. If not found, manually generate: read existing requirement files, find highest number, increment
  4. Inform the user: "The analyzer had an issue. I'll use REQ-XXX and skip duplicate checking."
- If the subagent returns an error object in JSON:
  1. Use the `next_id` from the error response (defaults to REQ-001)
  2. Proceed without duplicate checking
  3. Inform the user about the error
- Maximum 2 retry attempts if subagent fails completely, then fallback to manual ID generation

#### Step 1.4: Inform user based on analysis

Always start with: "I'll create this as **[next_id]**."

**If `analysis_status` is "duplicate_found":**
Present the conflict details and ask:
"**[req_id]** ([name]) already covers [brief reason]. Should I:
1. Create a new requirement anyway (if this is a different aspect)
2. Update [req_id] with additional details
3. Cancel this requirement"

**If `analysis_status` is "contradiction_found":**
Explain the conflict and ask:
"**[req_id]** ([name]) may conflict: [reason]. Should we:
1. Reconcile the approaches (update existing or adjust this requirement)
2. Document this as an alternative approach
3. Proceed anyway and flag the contradiction in `related_to`"

**If `analysis_status` is "related_found":**
"This requirement seems related to [list req_ids with names]. I'll add them to the `related_to` field."
Then proceed to Step 2.

**If `analysis_status` is "none":**
"Continuing with the details..."
Proceed directly to Step 2.

**Let user decide:** If conflicts were found, always give the user final say on whether to proceed, update existing, or cancel.

**Important:** This is not about blocking requirements—it's about surfacing conflicts early so users can make informed decisions. Always provide options, never unilaterally reject a requirement.

### Step 2: Interview for core details

Ask focused questions to gather essential information. Do NOT assume or invent details.

**IMPORTANT: Use AskUserQuestion with options wherever possible** to make the interview easier. Users prefer selecting from options over typing answers from scratch. Provide 3-4 contextually relevant options for each question, with "Other" added automatically so users can provide custom input if none of the options fit.

#### Step 2.1: Basic metadata (use AskUserQuestion)

Start by gathering the foundational details using AskUserQuestion with multiple-choice options:

**Question set 1: Core identification and Obsidian Properties**
- **Name**: Provide 3-4 naming options based on the user's description (e.g., "Sales Performance Dashboard", "Monthly Performance Comparison", "Sales Team Analytics")
- **Type**: Options: Functional Requirement, Non-Functional Requirement, Technical Requirement
- **Priority**: Options: Critical, High, Medium, Low (with descriptions explaining urgency)
- **Status**: Options: draft, in-review, approved, implemented
- **Owner**: Suggest likely teams based on requirement type (e.g., "backend-team", "frontend-team", "sales-engineering", "full-stack-team")
- **Owner Link**: Person responsible (for Obsidian graph) - provide 3-4 likely options or "I'll specify" (e.g., "John Smith", "Jane Doe", "Alice Johnson")
- **Domain**: Primary concept area - provide 3-4 relevant concept options (e.g., "Data Lineage", "Authentication", "Performance Optimization")
- **Tech Stack**: Technologies to be used - use `multiSelect: true` for multiple tools (e.g., "dbt", "Databricks", "Azure Data Factory", "React")
- **Related Concepts** (optional): Related concepts/techniques - use `multiSelect: true` (e.g., "Schema Auditing", "Incremental Loading", "Error Handling")

Example AskUserQuestion call:
```json
{
  "questions": [
    {
      "question": "What should I call this requirement?",
      "header": "Name",
      "multiSelect": false,
      "options": [
        {"label": "Sales Performance Tracking Dashboard", "description": "Focus on UI/dashboard aspect"},
        {"label": "Monthly Salesperson Performance Comparison", "description": "Emphasizes comparison capability"},
        {"label": "Sales Team Performance Analytics", "description": "Broader analytics focus"}
      ]
    },
    {
      "question": "What's the priority level for this requirement?",
      "header": "Priority",
      "multiSelect": false,
      "options": [
        {"label": "Critical", "description": "Must be implemented immediately"},
        {"label": "High", "description": "Important feature needed soon"},
        {"label": "Medium", "description": "Nice to have in near term"},
        {"label": "Low", "description": "Can be deferred"}
      ]
    }
  ]
}
```

#### Step 2.2: Implementation details (use AskUserQuestion)

Continue with technical implementation questions using options:

**Question set 2: Technical approach**
- **Data source**: Options based on common patterns (e.g., "CRM system API", "Internal database", "Excel/CSV uploads", "Multiple sources")
- **Key metrics**: Use `multiSelect: true` to let users choose multiple metrics (e.g., "Total revenue", "Deal count", "Conversion rate", "Average deal size")
- **UI/Display approach**: Options for how features are presented (e.g., "Side-by-side table", "Charts/graphs", "Dashboard with both", "Drill-down report")
- **Tech stack**: Options for platform/technology (e.g., "Web app (React/Vue)", "Mobile app", "BI tool (Tableau/Power BI)", "Backend API + flexible frontend")

**Question set 3: Access and scope**
- **User access**: Use `multiSelect: true` for who can access (e.g., "Managers only", "Salespeople (own data)", "Executive team", "Admin/ops")
- **Time ranges**: Use `multiSelect: true` for supported date ranges (e.g., "Any two months", "Year-over-year", "Quarterly", "Rolling 12-month")
- **Integration specifics**: When applicable, ask about specific systems (e.g., "Salesforce", "HubSpot", "Dynamics", "Custom CRM")

**Question set 4: Technical specifics (ALWAYS use options)**

**CRITICAL: For ALL technical detail questions, provide 3-4 options using AskUserQuestion.** Never ask these as open-ended text questions. Common patterns:

- **Database field names**: Provide 3-4 common naming conventions
  - Example: "expires_at", "expiry_date", "valid_until", "membership_end_date"
- **Cache/timeout durations**: Provide 3-4 time ranges with trade-off descriptions
  - Example: "5 minutes (frequent refresh)", "15 minutes (balanced)", "1 hour (longer cache)", "Session-based (until user logs out)"
- **API endpoints/paths**: Provide 3-4 RESTful or common patterns
  - Example: "/api/auth/login", "/auth/login", "/v1/authenticate", "/login"
- **Security/auth methods**: List 3-4 standard approaches
  - Example: "JWT tokens", "Session cookies", "OAuth 2.0", "API keys"
- **Rate limits**: Provide 3-4 common rate limit patterns
  - Example: "10 requests/minute per user", "100 requests/hour per IP", "1000 requests/day per API key", "No rate limiting"
- **Error handling behavior**: Describe 3-4 approaches with trade-offs
  - Example: "Return 4XX with error message", "Silent failure (log only)", "Retry with exponential backoff", "Fail fast and alert"
- **Logging strategies**: Options for what/how to log
  - Example: "Log with user ID and timestamp", "Aggregate metrics only (no PII)", "No logging", "Log only errors/failures"
- **Grace periods/timeouts**: Provide concrete durations
  - Example: "No grace period", "7-day grace period", "24-hour grace period", "30-day soft expiration"
- **Status/state values**: List 3-4 possible states
  - Example: "active/expired (binary)", "active/expired/suspended", "active/grace_period/expired", "active/pending/expired/cancelled"

**Pro tips for AskUserQuestion:**
- Group related questions into sets (2-4 questions per AskUserQuestion call) to reduce back-and-forth
- Use descriptive labels (3-8 words) and descriptions that explain trade-offs or implications
- Set `multiSelect: true` when users might want multiple options (metrics, access roles, features, multiple states)
- Make options contextually relevant to the user's initial request — don't use generic options
- **Always provide at least 3 options** - never ask a yes/no question (add "Other approach" as third option)
- If you're unsure what options to provide, think of the 3-4 most common industry patterns for that technical decision

#### Step 2.3: Open-ended probing (RARE - prefer options)

**DEFAULT TO OPTIONS.** Only ask open-ended questions when the question is truly unique or narrative-based and cannot be broken into choices.

**When open-ended questions are appropriate (rare cases):**
- Workflow narratives: "Walk me through how a manager would use this feature on a typical day"
- Business context: "What's the business driver for this feature?"
- Unique constraints: "Are there any compliance/legal requirements specific to your industry?"
- Free-form edge cases: "Are there any unusual scenarios I should consider?"

**When open-ended questions are NOT appropriate (use AskUserQuestion instead):**
- ❌ "What field stores the expiration?" → ✅ Provide 3-4 field name options
- ❌ "How long should the cache last?" → ✅ Provide 3-4 duration options
- ❌ "What should happen when [X]?" → ✅ Provide 3-4 behavior options
- ❌ "Should we log this?" → ✅ Provide 3-4 logging strategy options
- ❌ "What technologies should we use?" → ✅ Provide 3-4 tech stack options

**Rule of thumb:** If you can imagine 3-4 common answers to a question, provide those as options using AskUserQuestion. Only ask open-ended if the answer is truly unbounded or narrative.

#### Step 2.4: When to finish the interview

**Stop asking questions once you have enough detail.** You don't need to know every possible edge case upfront.

Stop asking questions when:
- You have enough detail to write a specific **Implementation → Approach** section with concrete technologies, endpoints, and configuration
- All mandatory fields (name, description, status, priority, owner) are known
- You understand the core technical approach and key decisions
- Further questions would be overly speculative or implementation-specific

**Don't over-interview.** If unsure about edge cases or details, add them to **Open questions** in the document rather than prolonging the interview. The requirement can evolve.

### Step 3: Structure the Implementation section

Write a detailed **Implementation → Approach** section that gives developers clear technical guidance:

**Good implementation guidance includes:**
- Specific technologies/libraries with version considerations
- API endpoint definitions with HTTP methods
- Data storage approach (database fields, indexes, caching)
- Security measures (hashing algorithms, token expiry, rate limits)
- Configuration values (timeouts, retry counts, cost factors)
- Error handling strategy

**Example pattern (from REQ-001):**
```
Authentication is handled via a POST `/auth/login` endpoint. The backend validates
credentials against a hashed password store (bcrypt, cost factor 12) and returns
a short-lived JWT (15 min) plus a rotating refresh token (7 days) stored in an
httpOnly cookie.
```

This level of detail is the target — specific enough for implementation planning.

**Also complete these subsections:**

**Key decisions:** List important design choices with rationale. Format as:
```markdown
- **[Decision]:** [Rationale/context]
```

**Out of scope:** List related features or approaches that are explicitly NOT included. This prevents scope creep.

**Open questions:** Use checkbox format for unresolved items:
```markdown
- [ ] Should failed login attempts trigger an email alert? — pending security review, assigned to @alice
```

**References:** Link to external documentation, ADRs, API docs, or design documents.

### Step 4: Suggest appropriate diagrams

Based on the requirement content gathered in Step 3, recommend diagram types. Present options if multiple apply:

**Diagram selection guide:**
- **Flow diagram** - For decision logic, state machines, user journeys, or branching workflows
- **Sequence diagram** - For API calls, multi-step interactions, or time-based flows between components
- **Relationship diagram** - For showing dependencies between requirements (REQ-XXX → REQ-YYY)
- **ERD (Entity-Relationship)** - For database schemas, data models, or entity structures
- **Component diagram** - For system architecture, service boundaries, or module structure
- **State diagram** - For status transitions or lifecycle management

**Diagram complexity guidelines:**
- **ERDs**: Include 5-10 key entities, not every field. Focus on relationships.
- **Sequence diagrams**: Show 3-7 main interactions, not every validation step.
- **Flow diagrams**: Focus on decision points and major steps, not every detail.
- **Keep diagrams readable** - If too complex when rendered, split into multiple focused diagrams.

**When multiple diagrams fit:**
Present options to the user: "Based on this requirement, I'd suggest a **sequence diagram** (to show the auth flow) and a **relationship diagram** (to link related requirements). Should I include both, or prefer one over the other?"

**When unsure:**
If the requirement doesn't clearly need diagrams, ask: "Would any diagrams help clarify this? I can add flow, sequence, ERD, or relationship diagrams."

Generate mermaid syntax for chosen diagrams based on the implementation details from Step 3.

### Step 5: Add acceptance criteria

Provide detailed acceptance criteria that define testable conditions:

```markdown
## Acceptance Criteria

- [ ] **AC-1:** User can log in with valid email and password, receives JWT token
- [ ] **AC-2:** Invalid credentials return 401 Unauthorized
- [ ] **AC-3:** 5 failed login attempts within 10 minutes trigger rate limiting (429)
- [ ] **AC-4:** JWT expires after 15 minutes
- [ ] **AC-5:** Refresh token allows re-authentication without password
```

**Acceptance criteria numbering:**
- Always use format `AC-X` where X starts at 1 for each requirement
- Numbering is per-requirement, not global (REQ-001 has AC-1, AC-2; REQ-002 also starts with AC-1)
- For requirements with 10+ criteria, use `AC-01`, `AC-02`, etc. for alignment
- For 100+ criteria (rare), use `AC-001` format

**Important: test_cases vs acceptance criteria**

- **Acceptance criteria (AC-X)**: Define WHAT needs to work - written in the markdown body under "## Acceptance Criteria", these are the testable conditions for the requirement
- **Test cases (TC-X)**: Specific test implementations created later by QA/dev teams - referenced in the YAML frontmatter only after they exist

**Always leave `test_cases: []` empty in the YAML frontmatter when creating new requirements.** Test case IDs (TC-001, TC-002, etc.) should only be added later when the QA team creates actual test implementations. Don't invent placeholder test case IDs - they cause confusion and make the tracker inaccurate.

Acceptance criteria should appear after the References subsection in the Notes section, before the Diagrams section.

### Step 6: Write the file

Save to `requirements/REQ-XXX [Requirement Name].md` using the name from Step 2.

**File naming rules:**
- Format: `requirements/REQ-XXX [Requirement Name].md`
- Use the exact name provided by the user
- Replace special characters (`/`, `\`, `:`, `*`, `?`, `"`, `<`, `>`, `|`) with hyphens
- Maximum filename length: 200 characters (truncate if needed)
- Example: `REQ-005 Password Reset via Email.md`

**Converting answers to Obsidian wikilink format:**

When writing the YAML frontmatter, convert the user's answers to proper Obsidian wikilink format:

1. **owner_link**: Convert person name to kebab-case and wrap in `[[]]`
   - User says: "John Smith" → Write: `owner_link: [[John Smith]]`
   - This will link to `Wiki/People/john-smith.md`

2. **domain**: Convert concept to kebab-case and wrap in `[[]]`
   - User says: "Data Lineage" → Write: `domain: [[Data Lineage]]`
   - This will link to `Wiki/Concepts/data-lineage.md`

3. **tech_stack**: Convert each tool to kebab-case and wrap in `[[]]`, comma-separated
   - User says: ["dbt", "Databricks", "Azure Data Factory"] → Write: `tech_stack: [[dbt]], [[Databricks]], [[Azure Data Factory]]`
   - These will link to `Wiki/Tools/dbt.md`, `Wiki/Tools/databricks.md`, etc.

4. **related_concepts**: Same as tech_stack but for concepts/techniques
   - User says: ["Schema Auditing", "Incremental Loading"] → Write: `related_concepts: [[Schema Auditing]], [[Incremental Loading]]`

**Important:** The wiki-ingest skill will later create the actual wiki pages for these links. If the pages don't exist yet, Obsidian will show them as unlinked references (which is fine - they become active links once the pages are created).

After writing, confirm: "Created **REQ-XXX [Name]** at `requirements/REQ-XXX [Name].md`"

**Note:** The Excel tracker (`requirements/requirements_tracker.xlsx`) will be automatically updated via post-tool-use hook. You don't need to manually sync the Excel file.

## Important Guidelines

**Do NOT invent details:**
If you don't have enough information to write a detailed implementation section, ask follow-up questions. Better to gather details than make assumptions.

**Do NOT rush:**
Take time to understand the requirement fully before writing. The document will be used by developers to implement the feature.

**Do maintain consistency:**
Follow the exact structure shown in the Document Structure section. YAML frontmatter first, then Notes with Implementation subsections and Acceptance Criteria, then Diagrams.

**Do suggest improvements:**
If you notice the requirement is underspecified or has potential issues (security concerns, scalability problems, ambiguous dependencies), flag them diplomatically: "Should we clarify how [X] handles [edge case]?"

## Examples

### Example 1: Complete workflow with AskUserQuestion

**User:** "Create a requirement for password reset functionality"

**Claude:** [Calls mcp__requirements-manager__create_requirement_tracker]

**Claude:** [Calls Agent with requirements-tracker subagent]

**Claude:** "I'll create this as **REQ-002**. No conflicts found. Let me gather the details:"

[Uses AskUserQuestion with 2 question sets:]

**Question Set 1:**
1. "What should I call this requirement?"
   - Password Reset via Email (Recommended)
   - Account Password Recovery
   - Forgotten Password Flow
   - User Password Reset Feature

2. "What's the priority for this?"
   - Critical - Users locked out need immediate recovery
   - High - Important security feature
   - Medium - Nice to have (Recommended)
   - Low - Can defer

**Question Set 2:**
3. "How should the reset be delivered?"
   - Email with time-limited link (Recommended)
   - SMS with verification code
   - Security questions
   - Admin-assisted reset

4. "What tech stack will this use?"
   - Backend API + Web frontend (Recommended)
   - Mobile app only
   - Email service + Web app
   - Full-stack web application

**User selects:** Password Reset via Email, Medium, Email with link, Backend API + Web

**Claude:** [Uses AskUserQuestion for technical details:]

**Question Set 3 (Technical Details):**
1. "How long should the reset token be valid?"
   - 15 minutes (high security, short window)
   - 1 hour (balanced approach) (Recommended)
   - 24 hours (user convenience)
   - 7 days (very long expiry)

2. "Should there be rate limiting on reset requests?" (multiSelect: false)
   - 3 requests per hour per email (Recommended)
   - 5 requests per hour per email
   - 10 requests per day per email
   - No rate limiting

3. "Should old sessions be invalidated after password reset?" (multiSelect: false)
   - Yes, invalidate all sessions immediately (Recommended)
   - Yes, but keep current session active
   - No, let sessions expire naturally
   - User chooses during reset flow

**User selects:** 1 hour, 3 requests per hour, invalidate all sessions

**Claude:** [Writes detailed Implementation → Approach with these specifics]

**Claude:** [Suggests sequence diagram for the email → token → reset flow]

**Claude:** [Writes 8 acceptance criteria covering token generation, expiry, rate limiting, session invalidation]

**Claude:** [Writes file]

**Claude:** "Created **REQ-002 Password Reset via Email** at `requirements/REQ-002 Password Reset via Email.md`

The Excel tracker has been automatically updated with this requirement."

### Example 2: Handling duplicates

**User:** "Create a requirement for sales performance tracking"

**Claude:** [Calls create_requirement_tracker]

**Claude:** [Calls requirements-tracker subagent]

**Subagent returns:**
```json
{
  "next_id": "REQ-003",
  "analysis_status": "duplicate_found",
  "conflicts": [{
    "req_id": "REQ-001",
    "name": "Monthly Salesperson Performance Comparison",
    "conflict_type": "duplicate",
    "reason": "Already covers sales performance tracking with revenue, deal count, and conversion metrics"
  }],
  ...
}
```

**Claude:** "I'll create this as **REQ-003**.

However, **REQ-001** (Monthly Salesperson Performance Comparison) already covers sales performance tracking with revenue, deal count, and conversion metrics.

Should I:
1. Create a new requirement anyway (if this focuses on a different aspect)
2. Update REQ-001 with additional details
3. Cancel this requirement

What would you like to do?"

**User:** "Actually, update REQ-001 to add forecasting"

**Claude:** [Reads REQ-001, adds forecasting to Implementation and acceptance criteria, updates file]

**Claude:** "Updated **REQ-001** with forecasting capabilities. The Excel tracker has been automatically updated."
