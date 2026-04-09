---
name: update-requirement
description: Update existing requirement documents - modify status, priority, implementation details, Obsidian Properties, or add related requirements. Use when the user wants to update, modify, change, or edit an existing requirement. Triggers on phrases like "update REQ-001", "change requirement status", "modify REQ-005", "add related requirement", "update implementation details", or "change priority".
argument-hint: REQ-ID or requirement name
disable-model-invocation: false
---

# Update Requirement Skill

Modify existing requirement documents with structured changes to metadata, implementation details, Obsidian Properties, and relationships. Maintains Excel tracker sync via post-tool-use hook.

## When to Use This Skill

- User says "update REQ-001" or "modify requirement"
- User wants to change status (draft → in-review → approved → implemented)
- User wants to update priority, owner, or other metadata
- User wants to add/remove related requirements
- User wants to update implementation details or acceptance criteria
- User wants to modify Obsidian Properties (domain, tech_stack, etc.)
- User wants to add diagrams or modify existing ones

## Workflow

### Step 1: Identify the Requirement

If not specified, ask which requirement to update:

```json
{
  "questions": [
    {
      "question": "Which requirement do you want to update?",
      "header": "Requirement",
      "multiSelect": false,
      "options": [
        {"label": "REQ-001", "description": "[Requirement name from search]"},
        {"label": "REQ-003", "description": "[Requirement name]"},
        {"label": "REQ-005", "description": "[Requirement name]"},
        {"label": "I'll specify", "description": "Enter a different REQ-ID"}
      ]
    }
  ]
}
```

**If user provides partial info** (e.g., "update the authentication requirement"):
1. Use Grep to search requirements/ for matching names
2. Present matching options
3. Let user select

### Step 2: Read the Current Requirement

```bash
# Find the requirement file
glob pattern="requirements/REQ-{ID}*.md"

# Read the full file
read file_path="requirements/REQ-001 Feature Name.md"
```

**Parse the current state:**
- Extract YAML frontmatter (all fields)
- Identify current status, priority, owner
- Note existing related_to, tech_stack, domain
- Review implementation details and acceptance criteria

### Step 3: Determine What to Update

Ask the user what they want to change using AskUserQuestion:

```json
{
  "questions": [
    {
      "question": "What would you like to update?",
      "header": "Update Type",
      "multiSelect": true,
      "options": [
        {"label": "Status", "description": "Change draft/in-review/approved/implemented"},
        {"label": "Priority", "description": "Change low/medium/high/critical"},
        {"label": "Owner", "description": "Change responsible team or person"},
        {"label": "Implementation Details", "description": "Update approach, decisions, or scope"},
        {"label": "Acceptance Criteria", "description": "Add/modify/remove criteria"},
        {"label": "Related Requirements", "description": "Add/remove related REQ-IDs"},
        {"label": "Obsidian Properties", "description": "Update domain, tech_stack, or concepts"},
        {"label": "Diagrams", "description": "Add/modify/remove diagrams"}
      ]
    }
  ]
}
```

### Step 4: Gather New Values

Based on selections in Step 3, ask follow-up questions:

#### If updating Status

```json
{
  "questions": [
    {
      "question": "What's the new status?",
      "header": "Status",
      "multiSelect": false,
      "options": [
        {"label": "draft", "description": "Work in progress"},
        {"label": "in-review", "description": "Ready for review"},
        {"label": "approved", "description": "Approved for implementation"},
        {"label": "implemented", "description": "Fully implemented"}
      ]
    }
  ]
}
```

**Status transition validation:**
- Can't go backwards (e.g., implemented → draft) without confirmation
- Warn if moving to "approved" without acceptance criteria
- Suggest running `check-requirement-quality` before moving to in-review

#### If updating Priority

```json
{
  "questions": [
    {
      "question": "What's the new priority?",
      "header": "Priority",
      "multiSelect": false,
      "options": [
        {"label": "critical", "description": "Must be implemented immediately"},
        {"label": "high", "description": "Important feature needed soon"},
        {"label": "medium", "description": "Nice to have in near term"},
        {"label": "low", "description": "Can be deferred"}
      ]
    }
  ]
}
```

#### If updating Owner

```json
{
  "questions": [
    {
      "question": "Who should own this requirement?",
      "header": "Owner",
      "multiSelect": false,
      "options": [
        {"label": "backend-team", "description": "Backend engineering team"},
        {"label": "frontend-team", "description": "Frontend engineering team"},
        {"label": "analytics-team", "description": "Analytics/data team"},
        {"label": "full-stack-team", "description": "Full-stack team"}
      ]
    },
    {
      "question": "Who is the person responsible (for Obsidian graph)?",
      "header": "Person",
      "multiSelect": false,
      "options": [
        {"label": "[Current owner_link]", "description": "Keep current"},
        {"label": "[Person 1]", "description": "Change to this person"},
        {"label": "[Person 2]", "description": "Alternative"},
        {"label": "[Person 3]", "description": "Alternative"}
      ]
    }
  ]
}
```

#### If updating Implementation Details

Ask open-ended or use AskUserQuestion for specific changes:

```json
{
  "questions": [
    {
      "question": "What aspect of implementation do you want to update?",
      "header": "Section",
      "multiSelect": true,
      "options": [
        {"label": "Approach", "description": "Technical implementation approach"},
        {"label": "Key Decisions", "description": "Add/modify design decisions"},
        {"label": "Out of Scope", "description": "Update what's excluded"},
        {"label": "Open Questions", "description": "Add/resolve questions"},
        {"label": "References", "description": "Add links to docs"}
      ]
    }
  ]
}
```

Then ask: "What changes do you want to make to [selected section]?"

#### If updating Acceptance Criteria

Ask: "Do you want to:
1. Add new acceptance criteria
2. Modify existing criteria
3. Remove criteria
4. Mark criteria as completed"

Then gather the specific changes.

#### If updating Related Requirements

```json
{
  "questions": [
    {
      "question": "Do you want to add or remove related requirements?",
      "header": "Action",
      "multiSelect": false,
      "options": [
        {"label": "Add", "description": "Add new related requirement IDs"},
        {"label": "Remove", "description": "Remove existing relationships"},
        {"label": "Replace", "description": "Replace entire list"}
      ]
    }
  ]
}
```

Then ask: "Which requirement IDs? (e.g., REQ-003, REQ-007)"

#### If updating Obsidian Properties

```json
{
  "questions": [
    {
      "question": "Which Obsidian Properties do you want to update?",
      "header": "Properties",
      "multiSelect": true,
      "options": [
        {"label": "domain", "description": "Primary concept area"},
        {"label": "tech_stack", "description": "Technologies used"},
        {"label": "related_concepts", "description": "Related concepts/techniques"},
        {"label": "type", "description": "functional/non-functional/technical"}
      ]
    }
  ]
}
```

Then ask for new values using AskUserQuestion with options (same as write-requirement).

#### If updating Diagrams

```json
{
  "questions": [
    {
      "question": "What do you want to do with diagrams?",
      "header": "Diagram Action",
      "multiSelect": false,
      "options": [
        {"label": "Add new diagram", "description": "Create additional diagram"},
        {"label": "Modify existing", "description": "Update current diagram"},
        {"label": "Remove diagram", "description": "Delete diagram section"},
        {"label": "Replace all", "description": "Replace entire diagrams section"}
      ]
    }
  ]
}
```

Then ask for diagram type and content.

### Step 5: Apply Changes

Use Edit tool to modify the requirement file:

**For YAML frontmatter changes:**
```bash
edit file_path="requirements/REQ-001 Feature.md"
old_string="status: draft"
new_string="status: in-review"
```

**For adding to arrays (related_to, tech_stack):**
```bash
edit file_path="requirements/REQ-001 Feature.md"
old_string="related_to:
  - REQ-003"
new_string="related_to:
  - REQ-003
  - REQ-007"
```

**For markdown section updates:**
```bash
edit file_path="requirements/REQ-001 Feature.md"
old_string="### Approach
[Current implementation approach]"
new_string="### Approach
[Updated implementation approach]"
```

**Best practices:**
- Make one Edit call per logical change
- Use specific old_string matches (include context lines)
- Preserve formatting and indentation
- Update "Last Updated" metadata if present

### Step 6: Add Change Note (Optional)

Consider adding a change log section to the requirement:

```markdown
## Change History

- **2026-04-09**: Status changed to in-review, added acceptance criteria AC-5 and AC-6 (updated by [[John Doe]])
- **2026-04-01**: Initial draft created
```

### Step 7: Confirm Changes

After updates, confirm to user:

```
✅ Updated REQ-001 Feature Name

**Changes made:**
- Status: draft → in-review
- Priority: medium → high
- Added related requirement: REQ-007
- Updated implementation approach
- Added 2 new acceptance criteria (AC-5, AC-6)

The Excel tracker has been automatically updated.

**Next steps:**
- Run `check-requirement-quality REQ-001` to validate
- Run `analyze-impact REQ-001` to see affected items
- Consider updating related requirements
```

### Step 8: Suggest Follow-up Actions

Based on the changes made, suggest relevant actions:

**If status changed to in-review:**
"Consider:
- Notifying reviewers [[Person A]], [[Person B]]
- Running `check-requirement-quality` to validate completeness
- Updating related requirements that depend on this"

**If implementation details changed:**
"Consider:
- Running `wiki-ingest` to update wiki pages with new concepts/tools
- Checking if related requirements need updates
- Running `analyze-impact` to see affected notes/wiki pages"

**If related requirements added:**
"Consider:
- Reviewing those requirements to ensure consistency
- Updating their implementation sections to reference this change"

## Important Guidelines

### DO validate changes
- Check that new status is valid transition
- Verify related REQ-IDs exist before adding
- Confirm Obsidian Property links are in correct format

### DO preserve existing content
- Only update what user requested
- Keep other sections unchanged
- Maintain YAML formatting and structure

### DO track significant changes
- Add change history notes for major updates
- Document rationale for status changes
- Note who made the change and when

### DO maintain Excel sync
- Excel tracker auto-updates via post-tool-use hook
- No manual Excel editing needed
- Hook extracts updated YAML frontmatter

### DO NOT make unrequested changes
- Don't "improve" sections that weren't asked to change
- Don't reformat or restructure unnecessarily
- Don't add content beyond what was requested

### DO NOT skip validation
- Always read the current requirement first
- Verify changes make sense in context
- Check for broken references when removing related_to

## Common Update Patterns

### Pattern 1: Status Progression

```
User: "Move REQ-001 to in-review"

Claude: [Reads REQ-001]
Claude: [Validates has acceptance criteria]
Claude: [Updates status field]
Claude: ✅ REQ-001 moved to in-review. Consider running quality check.
```

### Pattern 2: Add Implementation Details

```
User: "Update REQ-003 to add error handling approach"

Claude: [Reads REQ-003]
Claude: "What error handling approach should I document?"
User: [Provides details]
Claude: [Updates Implementation → Approach section]
Claude: ✅ Added error handling details to REQ-003
```

### Pattern 3: Link Related Requirements

```
User: "REQ-005 depends on REQ-003"

Claude: [Reads both requirements]
Claude: [Adds REQ-003 to REQ-005's related_to]
Claude: [Optionally adds REQ-005 to REQ-003's related_to for bidirectional link]
Claude: ✅ Linked REQ-005 → REQ-003. Consider running analyze-impact.
```

### Pattern 4: Bulk Property Update

```
User: "Add Databricks to tech stack for REQ-003"

Claude: [Reads REQ-003]
Claude: [Finds current tech_stack: [[dbt]], [[Azure]]]
Claude: [Updates to: tech_stack: [[dbt]], [[Azure]], [[Databricks]]]
Claude: ✅ Added [[Databricks]] to REQ-003 tech stack
```

### Pattern 5: Acceptance Criteria Addition

```
User: "Add acceptance criteria for timeout handling to REQ-001"

Claude: [Reads REQ-001]
Claude: [Finds current AC-1 through AC-4]
Claude: "What should AC-5 specify about timeout handling?"
User: [Provides details]
Claude: [Adds AC-5 to acceptance criteria section]
Claude: ✅ Added AC-5 to REQ-001
```

## Error Handling

**If requirement not found:**
"REQ-XXX not found. Use Glob to search: `requirements/REQ-XXX*.md`
Available requirements: [list first 5]"

**If status transition invalid:**
"Cannot move from 'implemented' to 'draft' - this is a backwards transition.
Are you sure? This might indicate the implementation needs rework."

**If related requirement doesn't exist:**
"REQ-XXX (specified in related_to) doesn't exist. Please verify the ID or create it first."

**If Excel update fails:**
"Requirement updated successfully, but Excel tracker sync may have failed.
Check `.claude/settings.local.json` for hook configuration."

## Success Criteria

A good update includes:
- ✅ Only requested sections modified
- ✅ YAML frontmatter correctly formatted
- ✅ Obsidian Properties use [[wikilink]] format
- ✅ Change history documented (if significant)
- ✅ Excel tracker auto-updated via hook
- ✅ User informed of what changed
- ✅ Follow-up actions suggested
- ✅ No unintended side effects

## Integration with Other Skills

**Before updating:**
- Use `wiki-query` to understand current state
- Use `analyze-impact` to see what will be affected

**After updating:**
- Use `check-requirement-quality` to validate changes
- Use `wiki-ingest` if concepts/tools changed
- Use `visualize-requirements` to see new relationships
