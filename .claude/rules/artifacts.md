---
paths: ["artifacts/*.md"]
---

# Artifacts Documentation Rules

## Purpose

Artifacts capture business analytical information, meeting discussions, emails, research, and open questions. They serve as source material for requirements and wiki pages, and use Obsidian Properties for traceability.

## Artifact Types

### Meeting Notes
- Team discussions, requirement reviews, architecture decisions
- Include participants, agenda, decisions, action items

### Email Notes
- Important email threads converted to markdown
- Include sender, recipients, key points, action items

### Project Notes
- Research findings, architectural explorations, design thinking
- Include context, findings, recommendations

### Open Questions
- Unresolved issues, pending decisions, blocked items
- Include question owner, deadline, context

### Analysis Notes
- Business analysis, impact assessments, feasibility studies
- Include scope, findings, recommendations

## Obsidian Properties Structure

**All artifacts MUST include YAML frontmatter with Obsidian Properties for automatic linking.**

### Required Properties

```yaml
---
type: meeting_notes | email | project_notes | open_questions | analysis
date: YYYY-MM-DD
title: [Descriptive title]
status: draft | final | archived
---
```

### Optional Properties for Traceability

**IMPORTANT: All wikilinks in YAML must be quoted, and arrays must use proper YAML syntax with `-` prefix.**

```yaml
---
participants:  # Links to Wiki/People/ (for meetings)
  - "[[Person A]]"
  - "[[Person B]]"
from: "[[Person Name]]"  # Links to Wiki/People/ (for emails)
to:  # Links to Wiki/People/ (for emails)
  - "[[Person A]]"
  - "[[Person B]]"
owner: "[[Person Name]]"  # Links to Wiki/People/ (who wrote/owns this note)
related_requirements:  # Links to requirements
  - "[[REQ-001]]"
  - "[[REQ-005]]"
domain: "[[Concept Name]]"  # Links to Wiki/Concepts/
mentioned_tools:  # Links to Wiki/Tools/
  - "[[Tool 1]]"
  - "[[Tool 2]]"
mentioned_concepts:  # Links to Wiki/Concepts/ or Wiki/Techniques/
  - "[[Concept A]]"
  - "[[Technique B]]"
tags:  # Free-form tags for filtering
  - architecture
  - decision
  - urgent
---
```

## Complete Example: Meeting Notes

**File:** `artifacts/2026-04-09-data-pipeline-review.md`

```markdown
---
type: meeting_notes
date: 2026-04-09
title: Data Pipeline Architecture Review
status: final
participants: [[John Doe]], [[Jane Smith]], [[Alice Johnson]]
owner: [[John Doe]]
related_requirements: [[REQ-003]], [[REQ-007]]
domain: [[Data Lineage]]
mentioned_tools: [[Databricks]], [[dbt]], [[Azure Data Factory]]
mentioned_concepts: [[Incremental Loading]], [[Schema Auditing]]
tags: [architecture, data-engineering, decision]
---

# Data Pipeline Architecture Review

**Meeting Date:** April 9, 2026
**Duration:** 1 hour
**Location:** Conf Room B / Zoom

## Attendees
- [[John Doe]] - Data Architect (organizer)
- [[Jane Smith]] - Analytics Lead
- [[Alice Johnson]] - Data Engineer

## Agenda
1. Review [[REQ-003]] requirements for data pipeline
2. Discuss [[Databricks]] vs [[Snowflake]] decision
3. Define [[Data Lineage]] tracking approach

## Discussion

### Pipeline Architecture
We reviewed the proposed architecture for [[REQ-003]] (Customer 360 Data Pipeline). Key points:

- **Technology Stack**: Decided on [[Databricks]] with [[dbt]] for transformations
- **Lineage Tracking**: Will use [[dbt]]'s built-in lineage + custom metadata extraction
- **Loading Strategy**: [[Incremental Loading]] for large tables, full refresh for dimensions

### Key Decisions
- **Decision 1:** Use [[Databricks]] over [[Snowflake]]
  - **Rationale:** Better ML integration, team already familiar, cost advantages for large data volumes
  - **Owner:** [[John Doe]]
  - **Date:** 2026-04-09

- **Decision 2:** Implement [[Schema Auditing]] via dbt tests
  - **Rationale:** Catch schema drift early, integrate with CI/CD
  - **Owner:** [[Alice Johnson]]
  - **Date:** 2026-04-09

## Action Items
- [ ] **[[Alice Johnson]]** - Create POC for [[dbt]] incremental models (Due: 2026-04-16)
- [ ] **[[Jane Smith]]** - Document lineage requirements in [[REQ-007]] (Due: 2026-04-12)
- [ ] **[[John Doe]]** - Set up [[Databricks]] dev workspace (Due: 2026-04-11)

## Open Questions
- [ ] How to handle historical data migration? — Owner: [[Jane Smith]], review needed with data-ops team
- [ ] Should we implement CDC (Change Data Capture)? — Owner: [[Alice Johnson]], research spike needed

## Related
- [[REQ-003]] — Customer 360 Data Pipeline (primary requirement)
- [[REQ-007]] — Data Lineage Tracking
- [[Data Lineage]] concept page (wiki)
- [[Incremental Loading]] technique page (wiki)

## Next Meeting
**Date:** 2026-04-16
**Agenda:** Review POC results, finalize pipeline architecture
```

## Complete Example: Email Notes

**File:** `artifacts/2026-04-08-email-compliance-requirements.md`

```markdown
---
type: email
date: 2026-04-08
title: Compliance Requirements for Customer Data
status: final
from: [[Sarah Compliance-Lead]]
to: [[John Doe]], [[Jane Smith]]
owner: [[John Doe]]
related_requirements: [[REQ-003]], [[REQ-012]]
domain: [[Data Privacy]]
mentioned_concepts: [[GDPR Compliance]], [[Data Retention]]
tags: [compliance, legal, urgent]
---

# Email: Compliance Requirements for Customer Data

**From:** [[Sarah Compliance-Lead]] <sarah@company.com>
**To:** [[John Doe]], [[Jane Smith]]
**Date:** April 8, 2026
**Subject:** URGENT: Compliance Requirements for Customer 360 Pipeline

## Summary

Legal and compliance team reviewed [[REQ-003]] (Customer 360 Data Pipeline) and identified mandatory requirements for [[GDPR Compliance]] and [[Data Retention]].

## Key Points

### GDPR Requirements
1. **Right to be forgotten**: Must support customer data deletion within 30 days
2. **Data portability**: Must support exporting customer data in machine-readable format
3. **Consent tracking**: Must track consent for each data processing purpose

### Data Retention
1. **Maximum retention**: Customer data cannot be stored longer than 7 years
2. **Audit logs**: Must retain audit logs for 10 years (legal requirement)
3. **Automatic deletion**: Implement automated deletion for expired data

### PII Handling
- All PII must be encrypted at rest and in transit
- PII access must be logged and auditable
- Only authorized roles can access raw PII

## Action Items
- [ ] **[[John Doe]]** - Update [[REQ-003]] with compliance requirements (Due: 2026-04-10)
- [ ] **[[Jane Smith]]** - Create new requirement for "Right to be Forgotten" feature (Due: 2026-04-12)
- [ ] **[[John Doe]]** - Schedule architecture review with security team (Due: 2026-04-11)

## Impact Assessment

**Affected Requirements:**
- [[REQ-003]] — Must add encryption, deletion, export capabilities
- [[REQ-012]] — Audit logging requirement elevated to critical priority

**Technical Implications:**
- Need to implement soft-delete pattern in [[Databricks]]
- Need to add data classification tags
- May need to add [[Data Masking]] for non-production environments

## Related
- [[Data Privacy]] (wiki concept)
- [[GDPR Compliance]] (wiki concept)
- [[Data Retention]] (wiki technique)
```

## Complete Example: Open Questions

**File:** `artifacts/2026-04-09-open-questions-data-pipeline.md`

```markdown
---
type: open_questions
date: 2026-04-09
title: Open Questions - Data Pipeline Architecture
status: draft
owner: [[John Doe]]
related_requirements: [[REQ-003]], [[REQ-007]]
domain: [[Data Lineage]]
mentioned_tools: [[Databricks]], [[dbt]]
tags: [blocked, decision-needed]
---

# Open Questions - Data Pipeline Architecture

Last Updated: 2026-04-09

## Critical Questions (blocking progress)

### Q1: Historical Data Migration Strategy
- **Question:** Should we migrate 5 years of historical customer data or start fresh?
- **Context:** [[REQ-003]] requires Customer 360 view, but historical data quality is poor
- **Options:**
  1. Full migration (12-month effort)
  2. Rolling 2-year migration (3-month effort)
  3. Start fresh, keep legacy system available for historical queries
- **Owner:** [[Jane Smith]]
- **Deadline:** 2026-04-12 (architecture decision date)
- **Stakeholders:** [[Sarah Compliance-Lead]], [[Tom Data-Lead]]
- **Status:** 🔴 Blocking [[REQ-003]] implementation

### Q2: Change Data Capture (CDC) Approach
- **Question:** Should we implement CDC or stick with batch incremental loads?
- **Context:** Real-time requirements are unclear; CDC adds complexity
- **Options:**
  1. Implement CDC with [[Debezium]] (real-time, complex)
  2. Batch incremental loads every 15 minutes (simpler, near-real-time)
  3. Hybrid: CDC for critical tables, batch for others
- **Owner:** [[Alice Johnson]]
- **Deadline:** 2026-04-16 (after POC review)
- **Stakeholders:** [[Jane Smith]], [[Product-Owner]]
- **Status:** 🟡 Research spike in progress

## Medium Priority Questions

### Q3: Schema Evolution Strategy
- **Question:** How do we handle schema changes without breaking downstream consumers?
- **Context:** Multiple teams consume pipeline output, schema changes risky
- **Proposed Solution:** Implement [[Schema Registry]] with versioning
- **Owner:** [[Alice Johnson]]
- **Deadline:** 2026-04-20
- **Status:** 🟢 Proposed solution, needs validation

### Q4: Data Quality Metrics
- **Question:** What data quality metrics should we track and alert on?
- **Context:** Need to define SLAs for data freshness, completeness, accuracy
- **Owner:** [[Jane Smith]]
- **Deadline:** 2026-04-18
- **Status:** 🟡 Discussion scheduled

## Resolved Questions

### ~~Q5: Databricks vs Snowflake~~ ✅ RESOLVED
- **Decision:** [[Databricks]]
- **Rationale:** Better ML integration, team expertise, cost advantages
- **Decided By:** [[John Doe]]
- **Date:** 2026-04-09
- **Related:** See `artifacts/2026-04-09-data-pipeline-review.md`

## Related
- [[REQ-003]] — Customer 360 Data Pipeline
- [[REQ-007]] — Data Lineage Tracking
- [[Data Lineage]] (wiki concept)
```

## File Naming Convention

Use descriptive, date-prefixed names:

**Meeting Notes:**
- Format: `YYYY-MM-DD-meeting-topic.md`
- Example: `2026-04-09-data-pipeline-review.md`

**Email Notes:**
- Format: `YYYY-MM-DD-email-subject-keywords.md`
- Example: `2026-04-08-email-compliance-requirements.md`

**Project Notes:**
- Format: `YYYY-MM-DD-project-topic.md`
- Example: `2026-04-05-project-databricks-evaluation.md`

**Open Questions:**
- Format: `YYYY-MM-DD-open-questions-topic.md`
- Example: `2026-04-09-open-questions-data-pipeline.md`

**Analysis Notes:**
- Format: `YYYY-MM-DD-analysis-topic.md`
- Example: `2026-04-07-analysis-cost-comparison.md`

## Why Obsidian Properties Matter

**Automatic Graph Building:**
- Click on [[John Doe]] in wiki → see all meetings, artifacts, requirements they're involved in
- Click on [[Databricks]] → see all artifacts, requirements, decisions mentioning this tool
- Click on [[Data Lineage]] → see all artifacts, requirements, wiki pages about this concept

**Impact Analysis:**
- When a decision changes, find all artifacts and requirements affected
- Trace from meeting note → decision → requirement → wiki concept

**Knowledge Discovery:**
- Find related artifacts through shared participants, tools, or concepts
- Discover connections between decisions made in different meetings

## Integration with Requirements and Wiki

**Notes feed into Requirements:**
- Meeting decisions become requirements
- Email action items become requirements
- Open questions get resolved and documented in requirements

**Notes feed into Wiki:**
- Repeated concepts in artifacts get extracted to Wiki/Concepts/
- Tools mentioned frequently get documented in Wiki/Tools/
- People in artifacts get pages in Wiki/People/

**Workflow:**
1. Create note with Obsidian Properties
2. Link to people, tools, concepts using `[[wikilinks]]`
3. Run `wiki-ingest` to process artifacts into wiki pages
4. Link artifacts to requirements using `related_requirements:` property
5. Use Obsidian graph to navigate connections

## Validation with wiki-lint

When running `wiki-lint`, the tool checks:
- All `participants:`, `from:`, `to:`, `owner:` links point to Wiki/People/
- All `domain:` links point to Wiki/Concepts/
- All `mentioned_tools:` links point to Wiki/Tools/
- All `mentioned_concepts:` links point to Wiki/Concepts/ or Wiki/Techniques/
- All `related_requirements:` links point to existing requirements

**Rationale:** Notes with Obsidian Properties create a traceable knowledge graph where decisions, discussions, and analysis are automatically linked to requirements, people, and concepts. This transforms scattered artifacts into a navigable, searchable knowledge base.
