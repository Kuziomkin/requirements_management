---
name: wiki-lint
description: Check Wiki health by finding orphaned pages, broken links, contradictions, and stale content. Use this skill when the user asks to "lint the wiki", "check wiki health", "find broken links", "check for orphans", or wants to validate the wiki structure. Triggers on phrases like "lint wiki", "check wiki", "validate wiki", "find wiki issues", or "audit wiki".
argument-hint: none (runs full check) or specific check type
disable-model-invocation: false
---

# Wiki Lint Skill

Audit the Wiki knowledge base for structural issues, broken links, contradictions, and stale content. Maintains wiki health and ensures consistency with requirements.

## When to Use This Skill

- User says "lint the wiki" or "check wiki"
- User asks "are there any broken links?"
- User wants to find orphaned pages
- User asks "check for contradictions"
- User wants to validate wiki health
- Periodic maintenance (recommended: monthly)

## Workflow

### Step 0: Check Wiki Exists

Verify `Wiki/index.md` exists:

```bash
if [ ! -f Wiki/index.md ]; then
  echo "Wiki not initialized. Run 'ingest requirements' first."
  exit 1
fi
```

### Step 1: Run All Checks

Execute these checks in parallel for efficiency:

1. **Orphaned pages** - Pages not in index
2. **Broken wikilinks** - `[[links]]` to non-existent pages
3. **Broken requirement links** - `[[REQ-XXX]]` to missing requirements
4. **Broken source citations** - Markdown links to missing files
5. **Contradictions** - Conflicting claims between wiki and requirements
6. **Requirements coverage** - Requirements without wiki pages
7. **Stale content** - Wiki pages outdated by newer requirements

### Check 1: Orphaned Pages

**Goal:** Find wiki pages not linked from `Wiki/index.md`

**Method:**
1. Use Glob to find all wiki pages: `Wiki/*/*.md`
2. Read `Wiki/index.md`
3. Check if each page is mentioned in the index

**Code pattern:**
```bash
# Find all wiki pages
glob pattern="Wiki/*/*.md"

# Read index
read file_path="Wiki/index.md"

# Check each page: is "[[page-name]]" in the index?
# Report orphans
```

**Report format:**
```markdown
## Orphaned Pages (not in index.md)

- Wiki/Concepts/forgotten-concept.md
- Wiki/Techniques/unused-technique.md

**Recommendation:** Add these to `Wiki/index.md` or verify they should exist.
```

### Check 2: Broken Wikilinks

**Goal:** Find `[[wikilinks]]` pointing to non-existent pages

**Method:**
1. Use Grep to find all `[[...]]` patterns in wiki pages
2. Extract page names from wikilinks
3. Check if corresponding files exist

**Code pattern:**
```bash
# Find all wikilinks
grep pattern="\[\[([^\]]+)\]\]" path="Wiki" output_mode="content"

# For each wikilink, check if file exists:
# - [[page-name]] should map to Wiki/*/page-name.md
# - [[REQ-001]] is a requirement reference (handled separately)

# Report missing pages
```

**Report format:**
```markdown
## Broken Wikilinks

### In Wiki/Concepts/data-lineage.md:
- [[non-existent-concept]] (line 15)
- [[missing-technique]] (line 23)

### In Wiki/Techniques/dbt-modeling.md:
- [[invalid-tool]] (line 42)

**Recommendation:** Either create these pages or remove the broken links.
```

### Check 3: Broken Requirement Links

**Goal:** Find `[[REQ-XXX]]` references to non-existent requirements

**Method:**
1. Use Grep to find all `[[REQ-...]]` patterns in wiki pages
2. Extract requirement IDs
3. Check if requirement files exist in `requirements/`

**Code pattern:**
```bash
# Find all requirement references
grep pattern="\[\[REQ-[0-9]+\]\]" path="Wiki" output_mode="content"

# For each REQ-ID, check if file exists:
# - requirements/REQ-001*.md should exist

# Report missing requirements
```

**Report format:**
```markdown
## Broken Requirement Links

### In Wiki/Concepts/authentication.md:
- [[REQ-099]] (line 18) — File not found

### In Wiki/Tools/databricks.md:
- [[REQ-042]] (line 31) — File not found

**Recommendation:** Update references to correct REQ-IDs or remove if requirements were deleted.
```

### Check 4: Broken Source Citations

**Goal:** Find markdown links `[text](../../path)` to missing files

**Method:**
1. Use Grep to find all markdown links in wiki pages
2. Extract file paths (especially to requirements/ and artifacts/)
3. Check if files exist

**Code pattern:**
```bash
# Find all markdown links
grep pattern="\[([^\]]+)\]\(([^\)]+)\)" path="Wiki" output_mode="content"

# For each link, resolve relative path and check existence:
# - From Wiki/Concepts/ → ../../requirements/REQ-001.md
# - From Wiki/Tools/ → ../../artifacts/2026-04-09.md

# Report missing files
```

**Report format:**
```markdown
## Broken Source Citations

### In Wiki/Concepts/idempotency.md:
- [REQ-003](../../requirements/REQ-003%20Data%20Pipeline.md) (line 45) — File not found

### In Wiki/Techniques/dbt-modeling.md:
- [Meeting Notes](../../artifacts/2026-03-15-meeting.md) (line 67) — File not found

**Recommendation:** Update paths or remove citations to deleted files.
```

### Check 5: Contradictions

**Goal:** Find conflicting claims between wiki pages and requirements

**Method:**
1. For each wiki page, check which requirements it references
2. Read the requirements and compare key details
3. Flag discrepancies

**What to check:**
- Wiki says "JWT expires in 15 min" but requirement says "30 min"
- Wiki says "owned by team-A" but requirement YAML says "owner: team-b"
- Wiki describes approach X but requirement specifies approach Y

**Code pattern:**
```bash
# For pages in Wiki/Concepts/ and Wiki/Techniques/:
# 1. Read the page
# 2. Extract requirement references
# 3. Read those requirements
# 4. Compare claims (manually or with pattern matching)
# 5. Report discrepancies
```

**Report format:**
```markdown
## Contradictions

### Wiki/Concepts/authentication.md vs REQ-001
- **Wiki says:** JWT expires in 15 minutes
- **REQ-001 says:** JWT expires in 30 minutes
- **Line:** Wiki line 23, REQ-001 line 45
- **Recommendation:** Update wiki to match requirement (authoritative source)

### Wiki/Tools/databricks.md vs REQ-003
- **Wiki says:** Owned by analytics-team
- **REQ-003 YAML says:** owner: data-engineering-team
- **Recommendation:** Sync owner information
```

### Check 6: Requirements Coverage

**Goal:** Find requirements that lack corresponding wiki pages

**Method:**
1. List all requirement files in `requirements/REQ-*.md`
2. For each requirement, check if it's referenced in any wiki page
3. Flag requirements with zero wiki mentions

**Code pattern:**
```bash
# Find all requirements
glob pattern="requirements/REQ-*.md"

# For each requirement:
# - Extract REQ-ID from filename
# - Search wiki for [[REQ-XXX]] or mentions in "Sources" sections
# - If zero mentions, mark as uncovered

# Report uncovered requirements
```

**Report format:**
```markdown
## Requirements Without Wiki Coverage

- REQ-008 — API Rate Limiting (no wiki pages reference this)
- REQ-011 — Notification Service (no wiki pages reference this)
- REQ-019 — Audit Logging (no wiki pages reference this)

**Recommendation:** Run 'ingest requirements' to process these into wiki pages, or verify if they're too new/trivial to warrant wiki entries.
```

### Check 7: Stale Content

**Goal:** Find wiki pages that might be outdated by newer requirements

**Method:**
1. Read wiki pages and note their source citations
2. Check if newer requirements modify or supersede those sources
3. Flag pages that might need updates

**Heuristics for staleness:**
- Wiki cites REQ-003 but REQ-015 later modifies the same feature
- Wiki page hasn't been updated in 6+ months but related requirements changed recently
- Requirement status changed from "draft" to "approved" but wiki still describes draft approach

**Code pattern:**
```bash
# For each wiki page:
# 1. Extract requirement citations from "Sources" section
# 2. Check "related_to" fields in those requirements for newer REQ-IDs
# 3. Compare last modified dates (wiki page vs requirements)
# 4. Flag if requirements are significantly newer

# Use git log to check modification dates:
git log -1 --format="%ai" -- Wiki/Concepts/some-page.md
git log -1 --format="%ai" -- requirements/REQ-003.md
```

**Report format:**
```markdown
## Potentially Stale Content

### Wiki/Concepts/authentication.md
- **Last updated:** 2026-02-15
- **Cited requirements:** REQ-001 (last updated 2026-04-01)
- **Issue:** REQ-001 was updated 6 weeks after the wiki page
- **Recommendation:** Review REQ-001 changes and update wiki if needed

### Wiki/Techniques/dbt-modeling.md
- **Cited requirements:** REQ-003
- **Related requirements:** REQ-015 (modifies REQ-003)
- **Issue:** REQ-015 may have changed the approach
- **Recommendation:** Check if REQ-015 impacts this technique page
```

### Step 2: Generate Summary Report

Combine all findings into a summary:

```markdown
# Wiki Lint Report
Generated: [TODAY'S DATE]

## Summary

- ✅ Total pages: X
- ⚠️  Orphaned pages: Y
- ❌ Broken wikilinks: Z
- ❌ Broken requirement links: A
- ❌ Broken source citations: B
- ⚠️  Contradictions: C
- ⚠️  Requirements without coverage: D
- ⚠️  Potentially stale pages: E

## Health Score: [X/100]

### Scoring:
- 100 points starting score
- -5 points per orphaned page
- -10 points per broken wikilink
- -15 points per broken requirement link
- -10 points per broken source citation
- -20 points per contradiction
- -5 points per uncovered requirement
- -10 points per stale page

[Detailed findings from each check]

## Recommendations

1. **High priority** - Fix contradictions and broken requirement links
2. **Medium priority** - Fix broken wikilinks and source citations
3. **Low priority** - Add orphaned pages to index, review stale content
4. **Maintenance** - Process uncovered requirements with 'ingest requirements'
```

### Step 3: Offer Auto-Fix Options

For some issues, offer to fix automatically:

**Auto-fixable issues:**
- ✅ Orphaned pages → Add to index.md
- ✅ Missing index entries → Generate entry from page content
- ⚠️  Broken wikilinks → Ask user if page should be created
- ❌ Contradictions → Requires user decision

**Prompt user:**
"I found [X] issues. I can automatically fix:
- [Y] orphaned pages (add to index)
- [Z] missing index entries

Should I fix these automatically? (yes/no)"

If user says yes:
1. Update `Wiki/index.md` with missing entries
2. Log fixes to `Wiki/log.md`
3. Report: "✅ Fixed [Y] issues automatically. [X] issues require manual review."

### Step 4: Log the Lint Operation

Append to `Wiki/log.md`:

```markdown
## [TODAY'S DATE]

### Lint: Wiki Health Check
- **Type**: Lint
- **Health Score**: X/100
- **Issues Found**:
  - Orphaned pages: Y
  - Broken wikilinks: Z
  - Broken requirement links: A
  - Broken source citations: B
  - Contradictions: C
  - Uncovered requirements: D
  - Stale pages: E
- **Auto-fixes Applied**:
  - Added [Y] pages to index.md
- **Manual Review Needed**:
  - [Z] broken wikilinks
  - [C] contradictions
- **Recommendations**: [Summary of top 3 actions]
```

## Important Guidelines

### DO check thoroughly
- Run all 7 checks even if early checks find issues
- Don't stop at first error - provide comprehensive report

### DO prioritize issues
- Contradictions and broken requirement links are critical
- Orphaned pages and stale content are lower priority
- Focus user attention on high-impact fixes

### DO offer auto-fixes
- Fix mechanical issues (orphans, missing index entries) automatically
- Ask before creating new pages or modifying content
- Never auto-fix contradictions - requires user judgment

### DO provide context
- Show line numbers for broken links
- Explain why an issue matters
- Suggest concrete next steps

### DO NOT be overly strict
- Not every requirement needs wiki pages (trivial ones are OK to skip)
- Some "stale" content might be intentionally unchanged
- Use judgment - lint is guidance, not law

## Examples

### Example 1: Clean wiki

**User:** "Lint the wiki"

**Claude:** [Runs all 7 checks]

**Claude:** [Finds zero issues]

**Claude:** "✅ Wiki health check complete!

**Summary:**
- Total pages: 24
- Orphaned pages: 0
- Broken wikilinks: 0
- Broken requirement links: 0
- Broken source citations: 0
- Contradictions: 0
- Requirements without coverage: 0
- Potentially stale pages: 0

**Health Score: 100/100**

Your wiki is in excellent health! All pages are properly linked, citations are valid, and content is up to date."

### Example 2: Issues found

**User:** "Check wiki health"

**Claude:** [Runs all 7 checks]

**Claude:** [Finds 3 orphaned pages, 2 broken wikilinks, 1 contradiction]

**Claude:** "⚠️  Wiki health check found some issues.

**Summary:**
- Total pages: 18
- ⚠️  Orphaned pages: 3
- ❌ Broken wikilinks: 2
- ❌ Contradictions: 1
- ✅ All other checks passed

**Health Score: 60/100**

## Detailed Findings

### Orphaned Pages (not in index.md)
- Wiki/Concepts/caching-strategy.md
- Wiki/Techniques/error-handling.md
- Wiki/Tools/redis.md

### Broken Wikilinks
**In Wiki/Concepts/authentication.md:**
- [[token-rotation]] (line 15) — Page doesn't exist

**In Wiki/Tools/databricks.md:**
- [[spark-configuration]] (line 28) — Page doesn't exist

### Contradictions
**Wiki/Concepts/authentication.md vs REQ-001:**
- **Wiki says:** JWT expires in 15 minutes (line 23)
- **REQ-001 says:** JWT expires in 30 minutes (line 45)
- **Recommendation:** Update wiki to match REQ-001

## Auto-Fix Available

I can automatically fix the 3 orphaned pages by adding them to index.md. Should I do this? (yes/no)"

**User:** "Yes"

**Claude:** [Updates Wiki/index.md]

**Claude:** [Logs to Wiki/log.md]

**Claude:** "✅ Fixed orphaned pages - added 3 entries to index.md.

**Remaining issues (manual review needed):**
1. Create [[token-rotation]] page or remove link in authentication.md
2. Create [[spark-configuration]] page or remove link in databricks.md
3. Update authentication.md line 23 to match REQ-001 (30 min expiry)

Would you like me to create the missing pages?"

### Example 3: Stale content detected

**User:** "Lint wiki"

**Claude:** [Runs all 7 checks]

**Claude:** [Finds 2 potentially stale pages]

**Claude:** "⚠️  Wiki health check detected potential staleness.

**Summary:**
- Total pages: 20
- ✅ No structural issues (orphans, broken links)
- ⚠️  Potentially stale pages: 2

**Health Score: 80/100**

## Potentially Stale Content

### Wiki/Concepts/authentication.md
- **Last updated:** 2026-02-15
- **Cited requirements:** REQ-001 (last updated 2026-04-01)
- **Issue:** REQ-001 was updated 6 weeks after the wiki page
- **Recommendation:** Review REQ-001 changes and update wiki if needed

### Wiki/Techniques/dbt-modeling.md
- **Last updated:** 2026-01-20
- **Cited requirements:** REQ-003
- **Related requirements:** REQ-015 (modifies REQ-003, created 2026-03-10)
- **Issue:** REQ-015 may have changed the approach
- **Recommendation:** Check if REQ-015 impacts this technique page

## Recommendation

Run 'ingest requirements REQ-001 REQ-015' to refresh these wiki pages with the latest requirement changes."

## Success Criteria

A good lint run provides:
- ✅ Comprehensive report covering all 7 check types
- ✅ Clear prioritization (critical, medium, low)
- ✅ Health score (0-100)
- ✅ Auto-fix options for mechanical issues
- ✅ Concrete next steps
- ✅ Logged to Wiki/log.md

## Error Handling

**If Wiki doesn't exist:**
"The Wiki hasn't been initialized yet. Run 'ingest requirements' first to create the knowledge base."

**If checks fail (e.g., can't read files):**
"Lint check encountered an error: [error message]. This might indicate file permission issues or corrupted wiki files."

**If too many issues found (>50):**
"Found [X] issues - the wiki may need significant maintenance. Top 3 priorities:
1. [Most critical issue]
2. [Second most critical]
3. [Third most critical]

Should I generate a full report and save it to a file?"
