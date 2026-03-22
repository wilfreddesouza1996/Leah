# Leah - Psychiatry Resident Skills for Claude Code

Two Claude Code skills built for psychiatry residents: **LiveNote** transforms rough lecture notes into exhaustive consultant-level academic documents, and **PaperFetcher** extracts paper references and generates formatted `.docx` reference documents.

## Skills

### `/LiveNote`
Transforms rough, shorthand lecture/seminar notes into comprehensive, consultant psychiatrist-level academic documents and publishes them to Notion.

- Expands each bullet into multi-paragraph sections with neurobiological detail, tables, and clinical emphasis blocks
- Verifies data via PubMed, Consensus API, and ClinicalTrials.gov
- Includes DSM-5/ICD-11 criteria, India-specific epidemiology, and mechanistic explanations
- Publishes directly to Notion with proper formatting

### `/PaperFetcher`
Extracts paper references from the conversation, searches PubMed and academic databases for full metadata, and generates a formatted `.docx` reference document plus a Notion page.

- Detects citation patterns automatically (Author et al., DOIs, PMIDs)
- Search cascade: PubMed -> Consensus API -> ClinicalTrials.gov
- Generates APA 7th edition `.docx` with hyperlinked DOIs
- Publishes reference list to Notion

## Install

### One-liner (from this repo)

```bash
git clone https://github.com/wilfreddesouza1996/Leah.git && cd Leah && ./skill-exports/install-skills.sh
```

### Manual install

Copy the skill folders into your Claude Code skills directory:

```bash
mkdir -p ~/.claude/skills/livenote ~/.claude/skills/paper-fetcher
cp skill-exports/livenote/SKILL.md ~/.claude/skills/livenote/SKILL.md
cp skill-exports/paper-fetcher/SKILL.md ~/.claude/skills/paper-fetcher/SKILL.md
```

### Project-level install

To add these skills to a specific project instead of globally:

```bash
./skill-exports/install-skills.sh /path/to/your/project/.claude/skills
```

## Requirements

These skills use the following MCP servers (configure in your Claude Code settings):

| MCP Server | Purpose |
|---|---|
| **Notion** | Publishing notes and reference pages |
| **PubMed / NCBI** | Article search, metadata, DOI lookup |
| **Consensus API** | Broad academic paper search (200M+ papers) |
| **ClinicalTrials.gov** | Clinical trial data |

Additionally, `python-docx` is needed for `.docx` generation (auto-installed by PaperFetcher).

## Usage

In any Claude Code session:

```
/LiveNote
[paste your rough lecture notes]
```

```
/PaperFetcher
```
(Scans the conversation for paper references automatically)

## Author

Dr. Wilfred D'souza
