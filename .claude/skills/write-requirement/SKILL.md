---
name: write-requirement
description: Create structured requirement documents with YAML metadata, detailed implementation notes, and diagrams. Use this skill whenever the user mentions "requirement", "req", "requirements", or asks to document a feature specification. Make sure to use this skill when the user wants to write technical specifications, feature requirements, or create REQ-XXX documents, even if they don't explicitly say "use the requirement skill".
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
status: [draft|in-review|approved|implemented]
priority: [low|medium|high|critical]
owner: [team-name]
related_to:
  - REQ-YYY
  - REQ-ZZZ
test_cases: []  # Leave empty initially; TC-XXX IDs added later by QA team
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

**Question set 1: Core identification**
- **Name**: Provide 3-4 naming options based on the user's description (e.g., "Sales Performance Dashboard", "Monthly Performance Comparison", "Sales Team Analytics")
- **Priority**: Options: Critical, High, Medium, Low (with descriptions explaining urgency)
- **Status**: Options: draft, in-review, approved, implemented
- **Owner**: Suggest likely teams based on requirement type (e.g., "backend-team", "frontend-team", "sales-engineering", "full-stack-team")

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

**Pro tips for AskUserQuestion:**
- Group related questions into sets (2-4 questions per AskUserQuestion call) to reduce back-and-forth
- Use descriptive labels (3-8 words) and descriptions that explain trade-offs or implications
- Set `multiSelect: true` when users might want multiple options (metrics, access roles, features)
- Make options contextually relevant to the user's initial request — don't use generic options
- If you're unsure what options to provide, ask one open-ended question first, then use the answer to generate relevant options for follow-up questions

#### Step 2.3: Open-ended probing (when options don't fit)

For implementation details that are too specific or technical for multiple-choice, ask open-ended follow-up questions:

**Implementation depth probing:**
- Technologies/frameworks involved (e.g., "JWT tokens", "bcrypt hashing")
- API endpoints, data models, or architecture patterns
- Configuration details (timeouts, limits, cost factors)
- Security considerations
- Performance requirements
- Edge cases or error handling

**Example open-ended questions:**
- "Walk me through how a manager would use this feature on a typical day"
- "What happens when [edge case occurs]?"
- "Are there any security or compliance concerns I should know about?"
- "What performance requirements or data volume constraints should I consider?"

**When to use open-ended vs. options:**
- Use **AskUserQuestion with options** for: naming, prioritization, technology choices, access control, feature toggles, common patterns
- Use **open-ended questions** for: workflows, edge cases, specific technical constraints, security requirements, unique business logic

#### Step 2.4: When to finish the interview

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

**Claude:** "Great! A few technical details:
- How long should the reset token be valid?
- Should there be rate limiting on reset requests?
- Should old sessions be invalidated immediately after password reset?"

**User:** "Token valid 1 hour, rate limit 3 requests per hour per email, yes invalidate sessions"

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
