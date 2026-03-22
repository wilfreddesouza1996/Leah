---
name: paper-fetcher
description: Extracts paper references from the conversation, searches PubMed and academic databases to find full metadata (DOI, abstract, authors, journal), checks for related clinical trials, and generates a formatted .docx reference document plus a Notion page. Use when the user wants to look up papers mentioned in notes or discussion. TRIGGER when the user says /PaperFetcher or asks to find/fetch papers from the conversation.
---

# PaperFetcher: Academic Reference Finder & Document Generator

Extract paper references from the conversation, search scientific databases for full metadata (DOIs, abstracts, authors), and generate a formatted `.docx` reference document plus a Notion page.

## Workflow

Make a todo list for all tasks and work through them sequentially.

### Step 1: Extract Paper References

Scan the **entire conversation** (including any LiveNote output) for citation patterns:

- `Author et al. (YYYY)` or `Author et al., YYYY`
- `Author & Author (YYYY)` or `Author and Author (YYYY)`
- `Author, YYYY`
- `Author (YYYY)`
- Direct DOIs (e.g., `10.xxxx/xxxxx`)
- Direct PMIDs (e.g., `PMID: 12345678`)
- Informal references (e.g., "the Bora meta-analysis" — infer author + approximate year from context)

Build a numbered list of all unique references found. Include the **topic context** for each (what subject was being discussed when the paper was mentioned — this helps narrow searches).

**Present the list to the user for confirmation** before searching. Ask if there are any additional papers to include or any to skip.

### Step 2: Search Cascade (Per Reference)

For each confirmed reference, execute the following search cascade:

#### Step 2A: PubMed Search (Primary)

Use `mcp__5b029436-4ec6-42ee-8ea8-c9e94604e39f__search_articles` with a query constructed as:
- `"AuthorLastName[Author] AND YYYY[pdat]"` combined with topic keywords from the context
- Example: For "Bora et al (2009)" discussed in context of bipolar cognition → search `"Bora[Author] AND 2009[pdat] AND bipolar AND cognition"`
- If the search returns multiple results, use the topic context to identify the most relevant paper

#### Step 2B: Get Full Metadata (If PubMed Found Results)

- Use `mcp__5b029436-4ec6-42ee-8ea8-c9e94604e39f__get_article_metadata` with the PMID to get: title, full author list, journal, year, volume, issue, pages, abstract
- Use `mcp__5b029436-4ec6-42ee-8ea8-c9e94604e39f__convert_article_ids` with the PMID to obtain DOI and PMCID

#### Step 2C: Disambiguation (If Ambiguous)

If the PubMed search returns multiple plausible results:
- Use `mcp__5b029436-4ec6-42ee-8ea8-c9e94604e39f__lookup_article_by_citation` with author/year/journal details to narrow down
- If still ambiguous, present top 2-3 candidates to the user and ask which one

#### Step 2D: Consensus API Fallback (If PubMed Fails)

If PubMed returns no results or the paper is not in biomedical literature:
- Use `mcp__7ba40731-40b5-4edb-ab9e-f18bc4f81cec__search` (Consensus API) with query `"AuthorLastName YYYY [topic keywords]"`
- This searches 200M+ papers including Semantic Scholar, ArXiv, and other academic sources
- Batch at most 3 search calls at a time to avoid rate limits
- If rate limited, wait 30 seconds before retrying

#### Step 2E: Clinical Trials Check (Contextual)

If the paper relates to an **intervention, drug, clinical condition, or treatment outcome**:
- Use `mcp__328ec501-9550-4501-a301-e8b97232d794__search_trials` with the intervention or condition as query
- Use `mcp__328ec501-9550-4501-a301-e8b97232d794__get_trial_details` for the top 1-2 most relevant trials
- Record NCT IDs and brief trial descriptions

#### Step 2F: Related Articles (Optional Enrichment)

For key foundational papers (landmark studies, meta-analyses):
- Use `mcp__5b029436-4ec6-42ee-8ea8-c9e94604e39f__find_related_articles` to find closely related work
- Include 1-2 most relevant related papers as "See also" entries

### Step 3: Collect Metadata

For each successfully found paper, collect and organize:

| Field | Description |
|-------|-------------|
| Title | Full paper title |
| Authors | Complete author list |
| Journal | Journal name (abbreviated and full) |
| Year | Publication year |
| Volume/Issue/Pages | If available |
| DOI | As clickable URL: `https://doi.org/[DOI]` |
| PMID | PubMed ID |
| PMCID | PubMed Central ID (if available) |
| Abstract | Full abstract text |
| Key Findings | 2-3 sentence summary of main findings |
| Related Trials | NCT IDs and descriptions (if any) |
| Context | Why this paper was mentioned (from user's notes) |

Track any references that **could not be found** with the reason (no PubMed match, ambiguous results, etc.).

### Step 4: Generate .docx (APA 7th Edition)

#### 4A: Ensure python-docx is available

```bash
pip list 2>/dev/null | grep -i python-docx || pip install python-docx
```

#### 4B: Generate the document

Create a Python script with the collected paper data embedded and execute it via Bash. The script should produce a professionally formatted `.docx` with:

**Document structure:**

1. **Title page / header:**
   - Title: "Paper References: [Topic]"
   - Subtitle: "Generated from lecture notes"
   - Date: Today's date
   - Author: Dr. Wilfred D'souza

2. **Per-paper sections** (one per paper found):
   - **Heading (Level 1):** Paper number + Title (bold)
   - **Authors** (italic): Full author list
   - **Publication details:** Journal, Year, Volume(Issue), Pages
   - **DOI:** As hyperlink
   - **PMID / PMCID:** If available
   - **Abstract** (sub-heading): Full abstract text
   - **Key Findings** (sub-heading): 2-3 sentence summary
   - **Context** (sub-heading): Why this paper was mentioned in the notes
   - **Related Clinical Trials** (sub-heading, if any): NCT ID, trial title, status, brief description

3. **Formatted Reference List** (APA 7th edition):
   - Each paper formatted as:
     ```
     Author, A. B., Author, C. D., & Author, E. F. (Year). Title of article. Journal Name, Volume(Issue), Pages. https://doi.org/xxxxx
     ```
   - Alphabetically ordered by first author surname

4. **Unfound References** (if any):
   - List of references that could not be located with notes on what was tried

**Styling:**
- Font: Calibri or Times New Roman, 11pt body, 14pt headings
- Line spacing: 1.15
- Margins: 1 inch all sides
- DOIs as blue hyperlinks

**Save location:** `/home/user/Leah/paper_references_YYYYMMDD_[topic_slug].docx`

**Fallback:** If python-docx installation fails, generate a well-formatted Markdown file (`.md`) with the same structure.

#### 4C: Python script template

The skill should generate a script like the following pattern (with actual data injected):

```python
from docx import Document
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
from datetime import date
import re

def add_hyperlink(paragraph, url, text):
    """Add a hyperlink to a paragraph."""
    part = paragraph.part
    r_id = part.relate_to(url, "http://schemas.openxmlformats.org/officeDocument/2006/relationships/hyperlink", is_external=True)
    hyperlink = OxmlElement('w:hyperlink')
    hyperlink.set(qn('r:id'), r_id)
    new_run = OxmlElement('w:r')
    rPr = OxmlElement('w:rPr')
    color = OxmlElement('w:color')
    color.set(qn('w:val'), '0563C1')
    rPr.append(color)
    u = OxmlElement('w:u')
    u.set(qn('w:val'), 'single')
    rPr.append(u)
    new_run.append(rPr)
    new_run.text = text
    hyperlink.append(new_run)
    paragraph._p.append(hyperlink)

# Paper data would be injected here as a list of dicts
papers = [...]  # Populated with actual data

doc = Document()

# Style setup
style = doc.styles['Normal']
font = style.font
font.name = 'Calibri'
font.size = Pt(11)

# Title
title = doc.add_heading('Paper References: [Topic]', level=0)
doc.add_paragraph(f'Generated: {date.today().isoformat()}')
doc.add_paragraph('Source: Lecture notes')
doc.add_paragraph('Author: Dr. Wilfred D\'souza')
doc.add_paragraph('')

# Per-paper sections
for i, paper in enumerate(papers, 1):
    doc.add_heading(f'{i}. {paper["title"]}', level=1)

    # Authors (italic)
    p = doc.add_paragraph()
    run = p.add_run(paper['authors'])
    run.italic = True

    # Journal info
    doc.add_paragraph(f'{paper["journal"]}, {paper["year"]}; {paper.get("volume", "")}{paper.get("issue", "")}: {paper.get("pages", "")}')

    # DOI
    if paper.get('doi'):
        p = doc.add_paragraph()
        p.add_run('DOI: ')
        add_hyperlink(p, f'https://doi.org/{paper["doi"]}', f'https://doi.org/{paper["doi"]}')

    # Abstract
    doc.add_heading('Abstract', level=2)
    doc.add_paragraph(paper.get('abstract', 'Not available'))

    # Key Findings
    doc.add_heading('Key Findings', level=2)
    doc.add_paragraph(paper.get('key_findings', 'See abstract'))

    # Context
    doc.add_heading('Context', level=2)
    doc.add_paragraph(paper.get('context', ''))

    doc.add_paragraph('')  # Spacer

# APA Reference List
doc.add_heading('Formatted Reference List (APA 7th Edition)', level=1)
for paper in sorted(papers, key=lambda x: x.get('authors', '').split(',')[0] if x.get('authors') else ''):
    ref = format_apa_reference(paper)
    doc.add_paragraph(ref)

doc.save('/home/user/Leah/paper_references_YYYYMMDD_topic.docx')
print(f'Document saved successfully.')
```

### Step 5: Publish to Notion

1. **Fetch the Notion enhanced markdown spec:**
   - Use `mcp__f7a1508d-ebdc-42f5-9d74-7be70ae2fa05__notion-fetch` with `id` set to `notion://docs/enhanced-markdown-spec`

2. **Find the "Lecture Notes - Raw" parent page:**
   - Use `mcp__f7a1508d-ebdc-42f5-9d74-7be70ae2fa05__notion-search` with query `"Lecture Notes - Raw"`
   - If not found, create it under "Psychiatry Residency" (page ID: `4aa0302e-c74b-40e3-b0d8-5131233251e4`)

3. **Create a Notion page** with the reference content:
   - Use `mcp__f7a1508d-ebdc-42f5-9d74-7be70ae2fa05__notion-create-pages`
   - Title: "Paper References: [Topic] - [Date]"
   - Icon: 📚
   - Content: Structured reference information in Notion-flavored markdown:
     - Per paper: heading, authors, journal info, DOI as link, abstract, key findings
     - Formatted reference list at the end

### Step 6: Present Results

Show the user a **summary table** in the chat:

```
| # | Title | Authors | Year | DOI |
|---|-------|---------|------|-----|
| 1 | Paper title... | Author et al. | 2009 | [link](https://doi.org/...) |
| 2 | ... | ... | ... | ... |
```

Then report:
- **Found:** N out of M papers successfully identified
- **Not found:** List any references that could not be located, with notes on what was tried
- **.docx file:** Full path to the generated document
- **Notion page:** Link to the created Notion page

## Error Handling

- **Rate limits on Consensus API:** Wait 30 seconds and retry. Batch at most 3 calls at a time.
- **PubMed returns no results:** Try broadening the search (remove year filter, use fewer keywords), then fall back to Consensus API.
- **Ambiguous results:** Present top candidates to user and ask for clarification.
- **python-docx installation fails:** Generate a `.md` file instead and notify user.
- **Notion publish fails:** Save content as a local `.md` file and notify user with the file path.
