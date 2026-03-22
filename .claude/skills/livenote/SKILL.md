---
name: livenote
description: Transforms rough, broken lecture/seminar notes into comprehensive, consultant psychiatrist-level academic documents and publishes them to Notion. Use when the user provides raw notes from a class, seminar, conference (e.g., CAMCON), or lecture and wants them expanded into full scholarly notes. TRIGGER when the user says /LiveNote or asks to process lecture notes.
---

# LiveNote: Lecture Note Transformer

Transform rough, shorthand lecture/seminar notes into **exhaustive, consultant psychiatrist-level academic documents** and publish to Notion.

## What You Must Produce

You are generating notes for **Dr. Wilfred D'souza**, a psychiatry resident. The output must match the depth and style of his existing Notion pages (e.g., "Gen-Z and Behavioural Addictions", "History, Culture and SUDs", "Bipolar Disorder - a Complete Overview"). These are 50-70KB multi-page academic documents, NOT reformatted bullet points.

### Content Depth Rules

- **NO LENGTH LIMITS.** The output length is determined entirely by the clinical/academic importance of the content. If the user gives 20 rough points, the output could easily be 15-30 pages.
- Each rough point must become a **full section** with explanatory paragraphs. A single bullet like "executive functions" should expand into a multi-paragraph section covering: definition, neural substrates (DLPFC, frontostriatal loops, ACC), specific impairments (cognitive flexibility, response inhibition, planning), clinical significance, and mapping to the disorder under discussion.
- Include **mechanistic explanations** where warranted: receptor systems, neural circuits, signaling pathways, pharmacokinetics, brain regions, neurotransmitter dynamics.
- Include **epidemiological data** with proper tables where available.
- Include **diagnostic criteria** (DSM-5/ICD-11) in structured format when diagnostic topics are mentioned.
- Include **India-specific context** where relevant: NFHS data, NIMHANS references, Indian policy, Indian epidemiology.
- **Never fabricate specific statistics or study findings.** If you are uncertain about a number, use the research tools to verify. If unverifiable, say "data suggest" or qualify appropriately.

### What These Notes Are NOT

- NOT a simple reformatting of bullets into sentences
- NOT limited to 2-5 sentence expansions per point
- NOT generic medical knowledge dumps — they must reflect **specialist psychiatric knowledge** at consultant level
- NOT summaries — they are **comprehensive expansions** that a resident could use as a primary study resource

### Formatting Style (Mandatory)

Every page MUST follow this formatting:

1. **Author attribution** at the very top:
   ```
   > ***Dr. Wilfred D'souza (IG: doc.wilfred.md)***
   ```

2. **Bold key terms** throughout: `**term**`

3. **Heading hierarchy**: H1 (`#`) for major topic, H2 (`##`) for sections, H3 (`###`) for subsections — with logical nesting

4. **Nested bullet points** with indented sub-bullets using tabs:
   ```
   - **Main point** with explanation
   	- Sub-point with detail
   	- Another sub-point
   		- Further nesting if needed
   ```

5. **Tables** for structured data (prevalence, comparisons, diagnostic criteria, risk factors, mechanism summaries). Use Notion-compatible table markdown:
   ```
   <table header-row="true">
   <colgroup>
   <col width="345">
   <col width="345">
   </colgroup>
   <tr>
   <td>**Header 1**</td>
   <td>**Header 2**</td>
   </tr>
   <tr>
   <td>Data</td>
   <td>Data</td>
   </tr>
   </table>
   ```

6. **Clinical emphasis / Teaching point blocks** where pedagogically useful:
   ```
   **Clinical emphasis**
   - Key teaching point here

   **Teaching point**
   - Important concept

   **How to think about this (mechanism, not moralizing):**
   - Systems-level explanation

   **Why this matters clinically:**
   - Clinical implication
   ```

7. **References section** at the end with numbered citations including DOIs:
   ```
   ## References
   1. Author AB, et al. Title. Journal. Year;Vol(Issue):Pages. DOI: 10.xxxx/xxxxx
   2. ...
   ```

8. **Topic-appropriate emoji** for the page icon (e.g., 🧠 neurocognition, 🎭 bipolar/mood, 📜 history, 🎰 addiction, 💊 pharmacology, 🧬 genetics, 👶 child psychiatry)

## Workflow

Make a todo list for all tasks and work through them sequentially.

### Step 1: Parse & Plan

Read the user's raw notes from the conversation carefully. Identify:
- The **overarching topic** and subject area
- **Sub-topics** and logical groupings of points
- A suitable **lecture/page title** (ask user if unclear)
- Today's date for the page
- Any **papers mentioned** (Author et al., YYYY patterns) — note these for later

Present the user with your proposed structure (main sections and subsections) before proceeding to research and expansion. Get confirmation or adjustments.

### Step 2: Research & Verify

Before expanding any content, use research tools to ensure accuracy:

**For verifying statistics, prevalence data, and key findings:**
- Use `mcp__5b029436-4ec6-42ee-8ea8-c9e94604e39f__search_articles` (PubMed) with relevant search terms
- Use `mcp__5b029436-4ec6-42ee-8ea8-c9e94604e39f__get_article_metadata` for specific papers mentioned by the user

**For broader academic verification and finding seminal papers:**
- Use `mcp__7ba40731-40b5-4edb-ab9e-f18bc4f81cec__search` (Consensus API — searches 200M+ papers across Semantic Scholar, PubMed, ArXiv)
- Batch at most 3 search calls at a time to avoid rate limits

**For recent guidelines and Indian data:**
- Use `WebSearch` for: clinical guidelines (NICE, APA, ISBD, WFSBP), diagnostic criteria updates, Indian epidemiological data (NFHS, NIMHANS reports)

**For clinical trials and interventions:**
- Use `mcp__328ec501-9550-4501-a301-e8b97232d794__search_trials` (ClinicalTrials.gov) when interventions, pharmacotherapy, or psychotherapy outcomes are discussed

**For papers the user cited:**
- Use `mcp__5b029436-4ec6-42ee-8ea8-c9e94604e39f__search_articles` with author name + year + topic keywords
- Use `mcp__5b029436-4ec6-42ee-8ea8-c9e94604e39f__get_article_metadata` to get full details
- Use `mcp__5b029436-4ec6-42ee-8ea8-c9e94604e39f__convert_article_ids` to get DOIs

Research in parallel where possible — launch multiple search calls simultaneously for different sub-topics.

### Step 3: Generate Comprehensive Notes

For each rough point or group of related points, generate content following this pattern:

**For a concept/mechanism point** (e.g., "executive functions"):
- Define the concept with proper terminology
- Explain the neurobiological basis (brain regions, circuits, neurotransmitters)
- Describe specific impairments/manifestations in the relevant disorder
- Add clinical significance and implications
- Include a table if there's structured data to present
- Add a "Clinical emphasis" or "Teaching point" block if pedagogically useful

**For a data point** (e.g., "12-14% have global deficits"):
- Present the statistic with its proper source
- Contextualize it (what does this mean clinically?)
- Compare with related data (other disorders, other populations)
- Present related statistics in a table
- Explain the methodology briefly (how was this measured?)

**For a paper/study reference** (e.g., "Bora et al (2009)"):
- Describe what the study found
- Explain why it matters for the topic at hand
- Connect it to other evidence in the section
- Include in the References section with full citation

**For a clinical tool/scale** (e.g., "SCIP, COBRA and MoCA"):
- Describe each tool: what it measures, how many items, time to administer
- Explain when to use each one
- Present in a comparison table
- Note any limitations or cultural adaptations

**For a treatment/intervention** (e.g., "IPSRT"):
- Full name and description
- Mechanism of action (biological and psychological)
- Evidence base (key trials, effect sizes if available)
- Practical implementation considerations
- Indian context/availability if relevant

### Step 4: Structure the Final Document

Assemble all expanded content into the following structure:

```markdown
> ***Dr. Wilfred D'souza (IG: doc.wilfred.md)***
# [Main Topic / Lecture Title]

[Opening paragraph: 3-5 sentences providing clinical context — why this topic matters, current state of understanding, what this document covers]

## [Major Section 1]
[Full explanatory paragraphs with **bold key terms**]

### [Subsection 1a]
- Detailed points with nested sub-bullets
- Tables for structured data

**Clinical emphasis**
- Teaching point about the clinical implications

### [Subsection 1b]
...

## [Major Section 2]
...

## [Continue for all sections]
...

## Key Papers Mentioned
- Author et al. (Year) — brief description of what the paper found and its relevance
- ...

## Summary
[3-5 sentence synthesis of the lecture's main clinical takeaways — what a resident should walk away knowing]

## References
1. Author AB, et al. Title. Journal. Year;Vol(Issue):Pages. DOI: 10.xxxx/xxxxx
2. ...
```

### Step 5: Publish to Notion

1. **Fetch the Notion enhanced markdown spec** to ensure correct formatting:
   - Use `mcp__f7a1508d-ebdc-42f5-9d74-7be70ae2fa05__notion-fetch` with `id` set to `notion://docs/enhanced-markdown-spec`

2. **Find or create the "Lecture Notes - Raw" parent page:**
   - Use `mcp__f7a1508d-ebdc-42f5-9d74-7be70ae2fa05__notion-search` with query `"Lecture Notes - Raw"` to find it
   - If it does NOT exist, create it using `mcp__f7a1508d-ebdc-42f5-9d74-7be70ae2fa05__notion-create-pages` as a child of "Psychiatry Residency" (page ID: `4aa0302e-c74b-40e3-b0d8-5131233251e4`) with title "Lecture Notes - Raw" and icon "📝"

3. **Create the note page:**
   - Use `mcp__f7a1508d-ebdc-42f5-9d74-7be70ae2fa05__notion-create-pages` to create the page as a child of "Lecture Notes - Raw"
   - Set `properties.title` to the lecture title
   - Set `icon` to the appropriate emoji
   - Set `content` to the fully structured notes (using the Notion-flavored markdown from the spec)

4. **Adapt content to Notion markdown spec:**
   - Use the spec fetched in step 1 to ensure tables, toggles, callouts, and formatting render correctly in Notion
   - Use `<table>` tags for tables (not pipe tables)
   - Use proper heading levels
   - Bold and italic formatting as specified

### Step 6: Wrap Up

Present to the user:
- **Summary**: Number of sections created, approximate word count, number of papers detected
- **Notion link**: Direct URL to the created page
- **Paper references found**: List them and suggest: "I found N paper references in your notes. You can use `/PaperFetcher` to retrieve full citations, DOIs, and abstracts for a .docx reference document."

## Example: Input → Output Mapping

**User input (rough notes):**
```
executive functions
verbal learning and memory
processing speed and attention
working memory
```

**Expected output (excerpt — each becomes a FULL section):**

```markdown
## Core Cognitive Domains Affected
The domains most consistently affected in bipolar disorder include the following.

### Executive Functions
**Executive functioning** refers to higher-order cognitive processes mediated largely by the **prefrontal cortex** and **frontostriatal networks**. These processes allow individuals to:
- **Plan and organize** behaviour
- **Shift** between cognitive sets
- **Inhibit** inappropriate responses
- **Maintain goal-directed activity**

In bipolar disorder, impairments are commonly observed in:
- **Cognitive flexibility** (measured by the Wisconsin Card Sorting Test)
- **Response inhibition** (measured by the Stroop task, Go/No-Go paradigms)
- **Planning and decision making** (measured by the Tower of London task)

Neurobiologically, these impairments are linked to dysfunction in the **dorsolateral prefrontal cortex (DLPFC)**, **anterior cingulate cortex (ACC)**, and **frontostriatal loops**, which regulate executive control over behaviour and emotional responses. Neuroimaging studies demonstrate reduced activation in the DLPFC during executive tasks in euthymic bipolar patients, suggesting that these deficits are trait-related rather than state-dependent.

<table header-row="true">
<colgroup>
<col width="230">
<col width="230">
<col width="230">
</colgroup>
<tr>
<td>**Executive Subdomain**</td>
<td>**Key Assessment Tool**</td>
<td>**Typical Finding in BD**</td>
</tr>
<tr>
<td>Cognitive flexibility</td>
<td>WCST (perseverative errors)</td>
<td>Impaired across mood states</td>
</tr>
<tr>
<td>Response inhibition</td>
<td>Stroop Color-Word Test</td>
<td>Impaired, especially in mania</td>
</tr>
<tr>
<td>Planning</td>
<td>Tower of London</td>
<td>Moderately impaired</td>
</tr>
<tr>
<td>Decision making</td>
<td>Iowa Gambling Task</td>
<td>Impaired risk evaluation</td>
</tr>
</table>

**Clinical emphasis**
- Executive dysfunction in bipolar disorder is **not merely a consequence of acute mood episodes**. Meta-analytic evidence shows persisting deficits during euthymia, supporting a trait-level impairment model.

### Verbal Learning and Memory
**Verbal learning and memory** is one of the most robustly impaired domains in bipolar disorder...
[continues with similar depth]
```

Notice: Each bullet from the user's notes became a full multi-paragraph section with tables, bold terms, neurobiological detail, and clinical emphasis blocks.
