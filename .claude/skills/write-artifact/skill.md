---
name: write-artifact
description: Create structured artifact documents with Obsidian Properties for traceability. Use when the user wants to create meeting artifacts, email artifacts, project artifacts, open questions, or analysis artifacts. Triggers on phrases like "create an artifact", "document this meeting", "save these artifacts", "write meeting artifacts", "document email", "create open questions", or "write project artifacts".
argument-hint: artifact type or topic
disable-model-invocation: false
---

# Write Artifact Skill

Create structured, traceable artifact documents with Obsidian Properties (YAML frontmatter) that automatically link to requirements, wiki pages, people, and concepts. Artifacts serve as source material for requirements and wiki knowledge base.

## When to Use This Skill

- User says "create meeting artifacts" or "document this meeting"
- User wants to save email content as artifacts
- User asks to "create project artifacts" or "document research"
- User wants to track open questions
- User asks to "write analysis artifacts" or "document findings"
- User says "take artifacts" or "save these artifacts"

## Note Types

1. **Meeting Notes** - Team discussions, decisions, action items
2. **Email Notes** - Important email threads converted to markdown
3. **Project Notes** - Research, explorations, design thinking
4. **Open Questions** - Unresolved issues, pending decisions
5. **Analysis Notes** - Business analysis, feasibility studies, impact assessments

## Workflow

### Step 1: Determine Note Type

If not specified by user, ask using AskUserQuestion:

```json
{
  "questions": [
    {
      "question": "What type of note are you creating?",
      "header": "Note Type",
      "multiSelect": false,
      "options": [
        {"label": "Meeting Notes", "description": "Team meeting, discussion, review session"},
        {"label": "Email Notes", "description": "Important email thread documentation"},
        {"label": "Project Notes", "description": "Research, exploration, design thinking"},
        {"label": "Open Questions", "description": "Unresolved issues, pending decisions"},
        {"label": "Analysis Notes", "description": "Business analysis, impact assessment, feasibility study"}
      ]
    }
  ]
}
```

### Step 2: Gather Metadata (use AskUserQuestion)

Collect information using AskUserQuestion with options:

#### For ALL Note Types

**Question Set 1: Core metadata**
```json
{
  "questions": [
    {
      "question": "What's the title for this note?",
      "header": "Title",
      "multiSelect": false,
      "options": [
        {"label": "[Suggest title based on user context]", "description": "Primary option"},
        {"label": "[Alternative title]", "description": "Alternative phrasing"},
        {"label": "[Another alternative]", "description": "Different focus"}
      ]
    },
    {
      "question": "What's the status of this note?",
      "header": "Status",
      "multiSelect": false,
      "options": [
        {"label": "Draft", "description": "Work in progress, incomplete"},
        {"label": "Final", "description": "Complete, ready to share"},
        {"label": "Archived", "description": "Historical reference only"}
      ]
    },
    {
      "question": "Who owns or wrote this note?",
      "header": "Owner",
      "multiSelect": false,
      "options": [
        {"label": "[Suggest person 1]", "description": "Based on context"},
        {"label": "[Suggest person 2]", "description": "Alternative"},
        {"label": "[Suggest person 3]", "description": "Alternative"}
      ]
    }
  ]
}
```

#### For Meeting Notes (additional questions)

**Question Set 2: Meeting-specific metadata**
```json
{
  "questions": [
    {
      "question": "Who participated in the meeting?",
      "header": "Participants",
      "multiSelect": true,
      "options": [
        {"label": "[Person 1]", "description": "Role/team"},
        {"label": "[Person 2]", "description": "Role/team"},
        {"label": "[Person 3]", "description": "Role/team"},
        {"label": "[Person 4]", "description": "Role/team"}
      ]
    },
    {
      "question": "Which requirements were discussed?",
      "header": "Related Reqs",
      "multiSelect": true,
      "options": [
        {"label": "REQ-001", "description": "[Brief description]"},
        {"label": "REQ-003", "description": "[Brief description]"},
        {"label": "REQ-005", "description": "[Brief description]"},
        {"label": "None", "description": "No specific requirements discussed"}
      ]
    }
  ]
}
```

#### For Email Notes (additional questions)

**Question Set 2: Email-specific metadata**
```json
{
  "questions": [
    {
      "question": "Who sent this email?",
      "header": "From",
      "multiSelect": false,
      "options": [
        {"label": "[Person 1]", "description": "Most likely sender"},
        {"label": "[Person 2]", "description": "Alternative"},
        {"label": "[Person 3]", "description": "Alternative"}
      ]
    },
    {
      "question": "Who received this email?",
      "header": "To",
      "multiSelect": true,
      "options": [
        {"label": "[Person 1]", "description": "Recipient"},
        {"label": "[Person 2]", "description": "Recipient"},
        {"label": "[Person 3]", "description": "Recipient"}
      ]
    }
  ]
}
```

#### For Open Questions (additional questions)

**Question Set 2: Question-specific metadata**
```json
{
  "questions": [
    {
      "question": "What's the priority/urgency?",
      "header": "Priority",
      "multiSelect": false,
      "options": [
        {"label": "🔴 Critical - Blocking progress", "description": "Must resolve immediately"},
        {"label": "🟡 Medium - Important but not blocking", "description": "Resolve soon"},
        {"label": "🟢 Low - Nice to clarify", "description": "Can defer"}
      ]
    }
  ]
}
```

#### For All Note Types (optional linking)

**Question Set 3: Traceability links (optional)**
```json
{
  "questions": [
    {
      "question": "Which domain/concept area does this relate to?",
      "header": "Domain",
      "multiSelect": false,
      "options": [
        {"label": "[Concept 1]", "description": "Primary concept"},
        {"label": "[Concept 2]", "description": "Alternative"},
        {"label": "[Concept 3]", "description": "Alternative"},
        {"label": "None/Not applicable", "description": "No specific domain"}
      ]
    },
    {
      "question": "Which tools or technologies are mentioned?",
      "header": "Tools",
      "multiSelect": true,
      "options": [
        {"label": "[Tool 1]", "description": "E.g., Databricks"},
        {"label": "[Tool 2]", "description": "E.g., dbt"},
        {"label": "[Tool 3]", "description": "E.g., Azure"},
        {"label": "None", "description": "No specific tools"}
      ]
    },
    {
      "question": "Which concepts or techniques are mentioned?",
      "header": "Concepts",
      "multiSelect": true,
      "options": [
        {"label": "[Concept 1]", "description": "E.g., Data Lineage"},
        {"label": "[Concept 2]", "description": "E.g., Schema Auditing"},
        {"label": "[Concept 3]", "description": "E.g., Incremental Loading"},
        {"label": "None", "description": "No specific concepts"}
      ]
    }
  ]
}
```

### Step 3: Generate Note Content Template

Based on note type, provide an appropriate template:

#### Meeting Notes Template

```markdown
---
type: meeting_notes
date: [YYYY-MM-DD]
title: [Title from Step 2]
status: [draft|final|archived]
participants:
  - "[[Person A]]"
  - "[[Person B]]"
  - "[[Person C]]"
owner: "[[Person Name]]"
related_requirements:
  - "[[REQ-XXX]]"
  - "[[REQ-YYY]]"
domain: "[[Concept Name]]"
mentioned_tools:
  - "[[Tool 1]]"
  - "[[Tool 2]]"
mentioned_concepts:
  - "[[Concept A]]"
  - "[[Technique B]]"
tags:
  - tag1
  - tag2
  - tag3
---

# [Note Title]

**Meeting Date:** [Date]
**Duration:** [Duration]
**Location:** [Location/Zoom]

## Attendees
- [[Person A]] - [Role]
- [[Person B]] - [Role]
- [[Person C]] - [Role]

## Agenda
1. [Topic 1]
2. [Topic 2]
3. [Topic 3]

## Discussion

### [Topic 1]
[Summary of discussion, key points, decisions]

### [Topic 2]
[Summary of discussion, key points, decisions]

## Key Decisions
- **Decision 1:** [What was decided]
  - **Rationale:** [Why]
  - **Owner:** [[Person Name]]
  - **Date:** [YYYY-MM-DD]

- **Decision 2:** [What was decided]
  - **Rationale:** [Why]
  - **Owner:** [[Person Name]]
  - **Date:** [YYYY-MM-DD]

## Action Items
- [ ] **[[Person A]]** - [Action item] (Due: [Date])
- [ ] **[[Person B]]** - [Action item] (Due: [Date])
- [ ] **[[Person C]]** - [Action item] (Due: [Date])

## Open Questions
- [ ] [Question 1] — Owner: [[Person]], [context]
- [ ] [Question 2] — Owner: [[Person]], [context]

## Related
- [[REQ-XXX]] — [How it relates]
- [[Concept Name]] — [How it relates]
- [[Tool Name]] — [How it relates]

## Next Meeting
**Date:** [Date]
**Agenda:** [Topics for next time]
```

#### Email Notes Template

```markdown
---
type: email
date: [YYYY-MM-DD]
title: [Email subject or summary]
status: [draft|final|archived]
from: "[[Sender Name]]"
to:
  - "[[Person A]]"
  - "[[Person B]]"
owner: "[[Person Name]]"
related_requirements:
  - "[[REQ-XXX]]"
domain: "[[Concept Name]]"
mentioned_tools:
  - "[[Tool 1]]"
  - "[[Tool 2]]"
mentioned_concepts:
  - "[[Concept A]]"
tags:
  - tag1
  - tag2
---

# Email: [Subject Line]

**From:** [[Sender Name]] <email@company.com>
**To:** [[Person A]], [[Person B]]
**Date:** [Date]
**Subject:** [Original subject line]

## Summary

[2-3 sentence summary of the email's main point]

## Key Points

### [Point 1]
[Detail about this point]

### [Point 2]
[Detail about this point]

### [Point 3]
[Detail about this point]

## Action Items
- [ ] **[[Person A]]** - [Action item] (Due: [Date])
- [ ] **[[Person B]]** - [Action item] (Due: [Date])

## Impact Assessment

**Affected Requirements:**
- [[REQ-XXX]] — [How it's affected]

**Technical Implications:**
- [Implication 1]
- [Implication 2]

## Related
- [[REQ-XXX]] — [How it relates]
- [[Concept Name]] — [How it relates]
```

#### Project Notes Template

```markdown
---
type: project_notes
date: [YYYY-MM-DD]
title: [Project or research topic]
status: [draft|final|archived]
owner: "[[Person Name]]"
related_requirements:
  - "[[REQ-XXX]]"
domain: "[[Concept Name]]"
mentioned_tools:
  - "[[Tool 1]]"
  - "[[Tool 2]]"
mentioned_concepts:
  - "[[Concept A]]"
  - "[[Technique B]]"
tags:
  - research
  - architecture
  - exploration
---

# [Project Topic]

**Date:** [Date]
**Author:** [[Person Name]]
**Context:** [Why this research/exploration was needed]

## Objective

[What are we trying to understand or achieve?]

## Background

[Context, previous decisions, current situation]

## Findings

### [Finding 1]
[Description, evidence, implications]

### [Finding 2]
[Description, evidence, implications]

### [Finding 3]
[Description, evidence, implications]

## Recommendations

1. **[Recommendation 1]**
   - **Rationale:** [Why]
   - **Impact:** [What changes]
   - **Effort:** [High/Medium/Low]

2. **[Recommendation 2]**
   - **Rationale:** [Why]
   - **Impact:** [What changes]
   - **Effort:** [High/Medium/Low]

## Trade-offs

| Approach | Pros | Cons |
|----------|------|------|
| [Option 1] | [Pros] | [Cons] |
| [Option 2] | [Pros] | [Cons] |

## Next Steps
- [ ] [Action 1] — Owner: [[Person]], Due: [Date]
- [ ] [Action 2] — Owner: [[Person]], Due: [Date]

## Related
- [[REQ-XXX]] — [How it relates]
- [[Concept Name]] — [How it relates]
- [[Tool Name]] — [How it relates]
```

#### Open Questions Template

```markdown
---
type: open_questions
date: [YYYY-MM-DD]
title: Open Questions - [Topic]
status: [draft|final]
owner: "[[Person Name]]"
related_requirements:
  - "[[REQ-XXX]]"
domain: "[[Concept Name]]"
mentioned_tools:
  - "[[Tool 1]]"
tags:
  - blocked
  - decision-needed
---

# Open Questions - [Topic]

Last Updated: [Date]

## Critical Questions (blocking progress)

### Q1: [Question title]
- **Question:** [Full question]
- **Context:** [Why this matters, background]
- **Options:**
  1. [Option 1] ([trade-offs])
  2. [Option 2] ([trade-offs])
  3. [Option 3] ([trade-offs])
- **Owner:** [[Person Name]]
- **Deadline:** [Date]
- **Stakeholders:** [[Person A]], [[Person B]]
- **Status:** 🔴 Blocking | 🟡 In progress | 🟢 Proposed solution

### Q2: [Question title]
- **Question:** [Full question]
- **Context:** [Why this matters]
- **Options:**
  1. [Option 1]
  2. [Option 2]
- **Owner:** [[Person Name]]
- **Deadline:** [Date]
- **Status:** [Status emoji and description]

## Medium Priority Questions

### Q3: [Question title]
[Same structure as above]

## Resolved Questions

### ~~Q4: [Question title]~~ ✅ RESOLVED
- **Decision:** [What was decided]
- **Rationale:** [Why]
- **Decided By:** [[Person Name]]
- **Date:** [Date]
- **Related:** [Link to note/requirement where decision is documented]

## Related
- [[REQ-XXX]] — [How it relates]
- [[Concept Name]] — [How it relates]
```

#### Analysis Notes Template

```markdown
---
type: analysis
date: [YYYY-MM-DD]
title: [Analysis topic]
status: [draft|final|archived]
owner: "[[Person Name]]"
related_requirements:
  - "[[REQ-XXX]]"
domain: "[[Concept Name]]"
mentioned_tools:
  - "[[Tool 1]]"
  - "[[Tool 2]]"
mentioned_concepts:
  - "[[Concept A]]"
tags:
  - analysis
  - business
  - impact
---

# Analysis: [Topic]

**Date:** [Date]
**Analyst:** [[Person Name]]
**Requested By:** [[Person Name]]

## Executive Summary

[2-3 sentence summary of findings and recommendation]

## Scope

**In Scope:**
- [Item 1]
- [Item 2]
- [Item 3]

**Out of Scope:**
- [Item 1]
- [Item 2]

## Analysis

### Current State
[Description of current situation]

### Proposed State
[Description of proposed changes]

### Gap Analysis
| Area | Current | Proposed | Gap |
|------|---------|----------|-----|
| [Area 1] | [Current] | [Proposed] | [Gap] |
| [Area 2] | [Current] | [Proposed] | [Gap] |

### Impact Assessment

**Business Impact:**
- [Impact 1]
- [Impact 2]

**Technical Impact:**
- [Impact 1]
- [Impact 2]

**Resource Impact:**
- [Impact 1]
- [Impact 2]

### Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| [Risk 1] | High/Med/Low | High/Med/Low | [Mitigation strategy] |
| [Risk 2] | High/Med/Low | High/Med/Low | [Mitigation strategy] |

## Recommendations

**Primary Recommendation:** [Recommendation with rationale]

**Alternative Options:**
1. [Option 1] - [Pros/cons]
2. [Option 2] - [Pros/cons]

## Implementation Considerations

- **Timeline:** [Estimated duration]
- **Effort:** [High/Medium/Low]
- **Dependencies:** [[REQ-XXX]], [[Tool Name]]
- **Prerequisites:** [What needs to happen first]

## Related
- [[REQ-XXX]] — [How it relates]
- [[Concept Name]] — [How it relates]
```

### Step 4: Write the File

Save to `notes/YYYY-MM-DD-[type]-[topic].md` with proper naming:

**File naming rules:**
- Format: `notes/YYYY-MM-DD-[type-or-topic-keywords].md`
- Use today's date (YYYY-MM-DD format)
- Use descriptive keywords in kebab-case
- Examples:
  - `notes/2026-04-09-meeting-data-pipeline-review.md`
  - `notes/2026-04-08-email-compliance-requirements.md`
  - `notes/2026-04-09-open-questions-data-pipeline.md`

**Converting answers to Obsidian wikilink format:**

When writing the YAML frontmatter, convert names to wikilinks:

1. **participants, from, to, owner**: Wrap in `[[]]`
   - User says: "John Smith", "Jane Doe" → Write: `participants: [[John Smith]], [[Jane Doe]]`

2. **domain**: Wrap in `[[]]`
   - User says: "Data Lineage" → Write: `domain: [[Data Lineage]]`

3. **mentioned_tools**: Wrap each tool in `[[]]`, comma-separated
   - User says: ["Databricks", "dbt"] → Write: `mentioned_tools: [[Databricks]], [[dbt]]`

4. **mentioned_concepts**: Same as tools
   - User says: ["Schema Auditing", "Incremental Loading"] → Write: `mentioned_concepts: [[Schema Auditing]], [[Incremental Loading]]`

5. **related_requirements**: Wrap REQ-IDs in `[[]]`
   - User says: ["REQ-001", "REQ-003"] → Write: `related_requirements: [[REQ-001]], [[REQ-003]]`

After writing, confirm: "Created note at `notes/[filename].md`"

### Step 5: Suggest Next Actions

After creating the note, suggest appropriate follow-up actions:

**For meeting notes:**
"Note created! Next steps:
- Run `ingest notes` to add concepts/tools/people to Wiki
- Create requirements from decisions using `write requirement`
- Link this note from related requirements"

**For email notes:**
"Note created! Consider:
- Creating requirements from action items
- Running `ingest notes` to extract concepts
- Adding this to related requirement documents"

**For open questions:**
"Note created! Remember to:
- Update status emojis as questions progress
- Move resolved questions to the Resolved section
- Link back to this note from requirements when questions are answered"

**For project/analysis notes:**
"Note created! Consider:
- Running `ingest notes` to extract concepts to Wiki
- Creating requirements based on recommendations
- Sharing with stakeholders mentioned in the note"

## Important Guidelines

### DO use Obsidian Properties consistently
- Always include required fields (type, date, title, status)
- Use wikilinks `[[Name]]` for all person, tool, concept references
- Link to existing requirements using `[[REQ-XXX]]` format

### DO create rich internal links
- Link people, tools, concepts even if wiki pages don't exist yet
- Use descriptive link text
- Create bidirectional connections

### DO provide templates appropriate to note type
- Use the correct template structure for each note type
- Include relevant sections based on note type
- Don't remove sections - user can delete if not needed

### DO capture actionable items
- Use checkbox format `- [ ]` for action items
- Include owner and due date
- Make action items specific and measurable

### DO NOT invent content
- Provide templates only
- Let user fill in actual content
- Don't assume meeting details or email content

### DO NOT skip Obsidian Properties
- Always include YAML frontmatter
- Always use wikilinks for traceability
- Don't use plain text where wikilinks are appropriate

## Examples

### Example 1: Meeting notes

**User:** "Create meeting notes for today's data pipeline review"

**Claude:** [Uses AskUserQuestion to gather: participants, related requirements, mentioned tools]

**User selects:**
- Participants: John Doe, Jane Smith, Alice Johnson
- Related Requirements: REQ-003, REQ-007
- Domain: Data Lineage
- Tools: Databricks, dbt, Azure Data Factory

**Claude:** [Writes file with proper YAML and template]

**Claude:** "Created note at `notes/2026-04-09-meeting-data-pipeline-review.md`

The note template is ready. Please fill in:
- Agenda items
- Discussion summaries
- Key decisions with rationale
- Action items with owners and due dates

Next steps:
- Run `ingest notes` to add participants and tools to Wiki
- Create requirements from decisions
- Update related requirements with links to this note"

### Example 2: Open questions

**User:** "Create open questions note for the data pipeline project"

**Claude:** [Asks for: owner, related requirements, domain, priority]

**Claude:** [Writes file with open questions template]

**Claude:** "Created note at `notes/2026-04-09-open-questions-data-pipeline.md`

Template ready for your questions. Use:
- 🔴 for critical/blocking questions
- 🟡 for medium priority
- 🟢 for low priority/proposed solutions
- ✅ for resolved (move to Resolved section)

Remember to update status emojis as questions progress!"

## Success Criteria

A good note includes:
- ✅ Complete YAML frontmatter with Obsidian Properties
- ✅ Wikilinks to people, tools, concepts
- ✅ Links to related requirements
- ✅ Appropriate template structure for note type
- ✅ Clear, descriptive filename
- ✅ Ready for `wiki-ingest` to process
