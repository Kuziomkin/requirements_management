---
name: check-requirement-quality
description: Validate requirement quality by checking for missing acceptance criteria, vague language, incomplete Obsidian Properties, and missing implementation details. Use when the user wants to check, validate, or review requirement quality before approval. Triggers on phrases like "check REQ-001", "validate requirement quality", "review REQ-003", "is this requirement complete", or "check requirement before approval".
argument-hint: REQ-ID or "all"
disable-model-invocation: false
---

# Check Requirement Quality Skill

Validate requirement documents against quality standards. Checks for completeness, clarity, traceability, and readiness for approval/implementation.

## When to Use This Skill

- User says "check REQ-001" or "validate requirement"
- Before moving requirement to "in-review" or "approved" status
- User asks "is this requirement ready?"
- User wants to review quality before implementation
- Periodic quality audits of all requirements

## Quality Checklist

### 1. YAML Frontmatter Completeness
- ✅ `id` field present and correct
- ✅ `name` field descriptive
- ✅ `description` is clear one-liner
- ✅ `type` specified (functional/non-functional/technical)
- ✅ `status` is valid value
- ✅ `priority` is set
- ✅ `owner` team specified
- ✅ `owner_link` uses [[Person]] format
- ✅ `domain` uses [[Concept]] format
- ✅ `tech_stack` lists technologies using [[Tool]] format
- ✅ `related_to` array (can be empty but must exist)
- ✅ `test_cases` array (should be empty initially)

### 2. Obsidian Properties Validation
- ✅ `owner_link` points to person (format: `[[Name]]`)
- ✅ `domain` points to concept (format: `[[Concept]]`)
- ✅ `tech_stack` uses wikilinks for each tool (format: `[[Tool1]], [[Tool2]]`)
- ✅ `related_concepts` uses wikilinks if present
- ✅ All wikilinks use proper format (no spaces before/after brackets)

### 3. Implementation Section
- ✅ **Approach** subsection exists and is detailed (>100 words)
- ✅ Specific technologies mentioned (not vague "we'll use a database")
- ✅ **Key decisions** subsection exists with rationale
- ✅ **Out of scope** subsection exists (explicit exclusions)
- ✅ **Open questions** subsection exists (can be empty)
- ✅ **References** subsection exists (external docs/ADRs)

### 4. Acceptance Criteria
- ✅ At least 3 acceptance criteria defined
- ✅ Each criterion is testable (can verify pass/fail)
- ✅ Criteria use checkbox format: `- [ ] **AC-X:** description`
- ✅ Criteria are numbered sequentially (AC-1, AC-2, AC-3...)
- ✅ Criteria are specific (not vague like "system works well")

### 5. Diagram Presence
- ✅ At least 1 diagram included for complex requirements
- ✅ Diagrams use Mermaid format (not ASCII art)
- ✅ Diagrams are relevant to the requirement
- ⚠️  Warning if no diagrams for requirements with >5 acceptance criteria

### 6. Language Quality
- ❌ Avoid vague words: "should", "might", "could", "probably"
- ❌ Avoid ambiguous terms: "fast", "secure", "scalable" without specifics
- ❌ Avoid passive voice: "will be implemented" → "system implements"
- ✅ Use concrete numbers: "responds within 200ms", "handles 10,000 requests/sec"

### 7. Traceability
- ✅ Related requirements exist (if `related_to` is non-empty)
- ✅ Domain concept should exist or be ingested soon
- ✅ Tech stack tools should exist or be ingested soon
- ✅ Owner person page should exist or be created

### 8. Readiness Gates

**For status = "in-review":**
- ✅ All implementation subsections complete
- ✅ At least 3 acceptance criteria
- ✅ No open questions marked as blocking
- ✅ Owner assigned

**For status = "approved":**
- ✅ All "in-review" checks pass
- ✅ At least 1 diagram present
- ✅ No vague language in critical sections
- ✅ Related requirements are also approved/implemented

**For status = "implemented":**
- ✅ All "approved" checks pass
- ✅ Test cases linked (test_cases array non-empty)

## Workflow

### Step 1: Identify Requirement(s)

Ask which requirement to check:

```json
{
  "questions": [
    {
      "question": "Which requirement do you want to check?",
      "header": "Requirement",
      "multiSelect": false,
      "options": [
        {"label": "Specific REQ-ID", "description": "Check one requirement"},
        {"label": "All requirements", "description": "Check all REQ-*.md files"},
        {"label": "All draft requirements", "description": "Check only draft status"},
        {"label": "All in-review requirements", "description": "Check only in-review"}
      ]
    }
  ]
}
```

### Step 2: Read Requirement(s)

```bash
# Single requirement
read file_path="requirements/REQ-001 Feature.md"

# All requirements
glob pattern="requirements/REQ-*.md"
# Then read each file
```

### Step 3: Run Quality Checks

Execute all 8 check categories in parallel:

1. **Parse YAML frontmatter** - Check all required fields
2. **Validate Obsidian Properties** - Check wikilink format
3. **Check Implementation section** - Verify subsections exist and have content
4. **Check Acceptance Criteria** - Count, format, testability
5. **Check Diagrams** - Presence and format
6. **Scan for vague language** - Use Grep for problematic words
7. **Validate traceability** - Check if related REQ-IDs exist
8. **Check readiness gates** - Based on current status

### Step 4: Generate Quality Report

Create a structured report with scores:

```markdown
# Quality Check: REQ-001 Feature Name

**Overall Score: 75/100** 🟡

## Summary
- ✅ 12 checks passed
- ⚠️  4 warnings
- ❌ 2 failures

---

## ✅ Passed Checks (12)

### YAML Frontmatter
- ✅ All required fields present
- ✅ Valid status value: 'draft'
- ✅ Priority set: 'high'

### Obsidian Properties
- ✅ owner_link uses [[Person]] format
- ✅ domain uses [[Concept]] format
- ✅ tech_stack uses [[Tool]] wikilinks

### Implementation
- ✅ Approach section detailed (235 words)
- ✅ Key decisions documented
- ✅ Out of scope explicit

### Acceptance Criteria
- ✅ 5 criteria defined (exceeds minimum)
- ✅ All use checkbox format
- ✅ Numbered sequentially

---

## ⚠️  Warnings (4)

### Language Quality
- ⚠️  Line 45: Vague term "system should be fast" - specify latency target
- ⚠️  Line 67: Ambiguous "secure enough" - define security requirements

### Diagrams
- ⚠️  No diagrams present - consider adding sequence or flow diagram for 5 acceptance criteria

### Traceability
- ⚠️  [[Data Lineage]] (domain) wiki page doesn't exist - run `wiki-ingest` to create it

---

## ❌ Failures (2)

### Acceptance Criteria
- ❌ AC-3: Not testable - "User experience is good" is subjective
  **Fix:** Change to measurable criterion like "Page loads in <2 seconds"

### Implementation
- ❌ Open Questions has 1 blocking question unresolved
  **Fix:** Resolve question before moving to in-review

---

## Readiness Assessment

**Current Status:** draft

**Can move to in-review?** ❌ No
- Fix 2 failures first
- Resolve warnings (recommended but not blocking)

**Can move to approved?** ❌ No
- Must be in-review first
- Add at least 1 diagram

---

## Recommendations

**High Priority (fix before in-review):**
1. Make AC-3 testable with measurable criterion
2. Resolve blocking open question

**Medium Priority (fix before approval):**
3. Add sequence or flow diagram
4. Replace vague language with specific requirements

**Low Priority (nice to have):**
5. Run `wiki-ingest` to create [[Data Lineage]] wiki page
6. Add more implementation details to Approach section

---

## Quick Fixes

```bash
# Fix AC-3
update-requirement REQ-001 --section "Acceptance Criteria" --change "AC-3: Page loads in under 2 seconds (measured at 95th percentile)"

# Add diagram
update-requirement REQ-001 --add-diagram sequence
```
```

### Step 5: Calculate Score

**Scoring system (100 points total):**

- **YAML Completeness (20 points):**
  - All required fields: 15 points
  - Obsidian Properties correct: 5 points

- **Implementation Quality (25 points):**
  - Approach detailed (>100 words): 10 points
  - All subsections present: 10 points
  - References included: 5 points

- **Acceptance Criteria (20 points):**
  - At least 3 criteria: 10 points
  - All testable: 10 points

- **Diagrams (10 points):**
  - At least 1 diagram: 10 points

- **Language Quality (10 points):**
  - No vague language: 5 points
  - Concrete specifications: 5 points

- **Traceability (10 points):**
  - Related REQ-IDs exist: 5 points
  - Wiki links valid: 5 points

- **Readiness (5 points):**
  - Status appropriate for completeness: 5 points

**Grade mapping:**
- 90-100: 🟢 Excellent - Ready for next stage
- 75-89: 🟡 Good - Minor improvements recommended
- 60-74: 🟠 Fair - Several issues to address
- Below 60: 🔴 Poor - Major rework needed

### Step 6: Offer Auto-Fixes

For some issues, offer automatic fixes:

"I can automatically fix some issues. Would you like me to:
1. Add missing YAML fields with default values
2. Format acceptance criteria with proper numbering
3. Add empty subsections for missing implementation sections
4. Create wiki stub pages for missing links

Which fixes should I apply? (Select multiple)"

### Step 7: Report Results

For single requirement:
```
🟡 Quality Check: REQ-001 Feature Name
Score: 75/100

12 passed, 4 warnings, 2 failures

Key issues:
- AC-3 not testable
- 1 blocking open question

Can move to in-review? ❌ No (fix 2 failures first)

Run `check-requirement-quality REQ-001 --detailed` for full report.
```

For multiple requirements:
```
📊 Quality Check: All Requirements

Total: 12 requirements checked

🟢 Excellent (90-100): 3 requirements
🟡 Good (75-89): 5 requirements
🟠 Fair (60-74): 3 requirements
🔴 Poor (<60): 1 requirement

Worst performers:
- REQ-005: 55/100 - Missing acceptance criteria
- REQ-008: 62/100 - Vague language, no diagrams

Best performers:
- REQ-001: 95/100 - Nearly perfect
- REQ-003: 92/100 - Excellent quality

Run `check-requirement-quality REQ-XXX` for individual reports.
```

## Important Guidelines

### DO be specific in feedback
- Don't just say "acceptance criteria vague"
- Show the problematic text: "AC-3: 'User experience is good'"
- Suggest fix: "Change to 'Page loads in <2 seconds'"

### DO prioritize issues
- Failures block status transitions
- Warnings are recommended fixes
- Info items are nice-to-haves

### DO check context
- Draft requirements can be incomplete
- In-review requirements need stricter checks
- Approved requirements should be nearly perfect

### DO offer actionable fixes
- Provide exact edit commands
- Offer to make changes automatically
- Link to related skills (update-requirement, wiki-ingest)

### DO NOT be overly strict
- Some requirements are intentionally simple
- Non-functional requirements may not need diagrams
- Allow flexibility based on requirement type

### DO NOT fail for missing wiki pages
- Warn if wiki links don't exist
- But don't block - wiki pages can be created later
- Suggest running wiki-ingest

## Common Quality Issues

### Issue 1: Vague Acceptance Criteria

**Bad:**
```
- [ ] **AC-1:** System is fast
- [ ] **AC-2:** Data is secure
- [ ] **AC-3:** Users are happy
```

**Good:**
```
- [ ] **AC-1:** API responds in <200ms at 95th percentile
- [ ] **AC-2:** All PII encrypted at rest using AES-256
- [ ] **AC-3:** User satisfaction score >4.5/5 in surveys
```

### Issue 2: Missing Implementation Details

**Bad:**
```
### Approach
We'll build a data pipeline using modern tools.
```

**Good:**
```
### Approach
The data pipeline will use Databricks for compute and dbt for transformations.
Source data will be extracted from Salesforce API using Airbyte, loaded into
Delta Lake tables, and transformed using dbt models with incremental materialization.
Lineage will be tracked via dbt's built-in metadata plus custom tags.
Pipeline runs on a schedule (every 6 hours) with Airflow orchestration.
```

### Issue 3: No Diagrams for Complex Features

**When to require diagrams:**
- 5+ acceptance criteria
- Multiple system interactions
- Complex workflows
- Data transformations
- State transitions

### Issue 4: Broken Traceability

**Check:**
- related_to: [[REQ-999]] → REQ-999 doesn't exist
- domain: [[Data Lineage]] → Wiki page missing
- tech_stack: [[Databricks]] → Wiki page missing

**Fix:** Either create the referenced items or remove broken links.

## Integration with Other Skills

**Use before:**
- `update-requirement` - to fix issues
- `write-requirement` - to set quality standards

**Use after:**
- `update-requirement` - to apply suggested fixes
- `wiki-ingest` - to create missing wiki pages
- `visualize-requirements` - to see relationships

## Success Criteria

A good quality check provides:
- ✅ Clear score (0-100) with grade
- ✅ Specific failures with line numbers
- ✅ Actionable recommendations
- ✅ Auto-fix options where possible
- ✅ Readiness assessment for next status
- ✅ Prioritized issues (high/medium/low)
