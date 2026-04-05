---
name: lex-uk-law
description: >
  Query the UK Government's official legal database via the i.AI Lex API.
  Use when you need to search 8.4 million UK legal documents including Acts,
  Statutory Instruments, amendments, and explanatory notes. Built by the UK
  Government's i.AI team with support from The National Archives and Ministry
  of Justice. Triggers on: "verify UK law", "search legislation", "check statute",
  "what does the Act say", "is this in force", "find UK regulation", "i.AI Lex",
  "lex API", or any request to verify a UK legal citation against authoritative sources.
  WORKSPACE SCOPE: This skill is specific to the UK_Lanzarote_Repatriation workspace.
  Do NOT use in US-law contexts.
---

# i.AI Lex — UK Government Legal Database Skill

## Overview

The **i.AI Lex** is the UK Government's official legal research API, built by the
Incubator for Artificial Intelligence (i.AI) with support from:
- **The National Archives** (legislation.gov.uk — the official UK statute database)
- **Ministry of Justice**

It provides programmatic access to **8.4 million UK legal documents** with hybrid
semantic + keyword search. All data is sourced verbatim from official government
sources — zero LLM-generated content.

**Live API:** https://lex.lab.i.ai.gov.uk  
**API Docs:** https://lex.lab.i.ai.gov.uk/docs  
**GitHub:** https://github.com/i-dot-ai/lex

---

## Dataset Coverage

| Dataset | Volume | Coverage |
|---------|--------|----------|
| UK Acts & Statutory Instruments | 220,000 | 1267–present (complete from 1963) |
| Legislative amendments | 892,000 | All modifications to UK statutes |
| Explanatory Notes | 89,000 | Legislative context and intent |
| Case Law | 70,000 judgments | Temporarily disabled pending TNA licence |
| Total indexed | **8.4 million documents** | |

---

## When to Use This Skill

Use the Lex API to:

1. **Verify statutory citations** — confirm exact wording of a provision before including in legal documents
2. **Search by legal concept** — find relevant provisions using plain English
3. **Check if legislation is still in force** — verify statutes haven't been repealed or amended
4. **Find supporting legislation** — locate related Acts and SIs
5. **Ground AI legal analysis** — replace training-data-based citations with live statute text

---

## How to Query the Lex API

### Method 1: Search by keyword or concept (most common)

Use `read_url_content` to query the Lex search endpoint:

```
URL: https://lex.lab.i.ai.gov.uk/api/v1/legislation/search?q={query}&limit=5
```

**Examples:**

| Legal Question | Query URL |
|----------------|-----------|
| UK GDPR legitimate interests | `https://lex.lab.i.ai.gov.uk/api/v1/legislation/search?q=legitimate+interests+personal+data&limit=5` |
| Companies Act public register | `https://lex.lab.i.ai.gov.uk/api/v1/legislation/search?q=companies+house+public+register+inspection&limit=5` |
| Insolvency Act MVL | `https://lex.lab.i.ai.gov.uk/api/v1/legislation/search?q=members+voluntary+liquidation+solvent&limit=5` |
| CGT disposal proceeds | `https://lex.lab.i.ai.gov.uk/api/v1/legislation/search?q=capital+gains+tax+disposal+proceeds&limit=5` |
| ICAEW disciplinary | `https://lex.lab.i.ai.gov.uk/api/v1/legislation/search?q=accountant+professional+negligence+disciplinary&limit=5` |

### Method 2: Browse API documentation

Full interactive API documentation:
```
https://lex.lab.i.ai.gov.uk/docs
```

### Method 3: Direct statute lookup

If you know the exact Act name:
```
https://lex.lab.i.ai.gov.uk/api/v1/legislation/search?q=Data+Protection+Act+2018+section+6&limit=3
```

---

## Key Statutes for This Workspace

The following are the primary statutes relevant to the Wincham/Lanzarote case:

### Data Protection & GDPR
- **UK GDPR** (retained EU law, as amended by DPA 2018)
- **Data Protection Act 2018** — domestic implementation
- **Privacy and Electronic Communications Regulations 2003**

### Corporate & Insolvency
- **Companies Act 2006** — Companies House register obligations
- **Insolvency Act 1986** — MVL procedure (ss.89-96, 165)
- **Limited Liability Partnerships Act 2000**

### Professional Negligence
- **Limitation Act 1980** — 6-year limitation period
- **Civil Liability Act 2018** — contributory negligence
- **Legal Services Act 2007** — regulated activities

### Tax
- **Taxation of Chargeable Gains Act 1992** — CGT
- **Income Tax Act 2007** — income treatment
- **Inheritance Tax Act 1984** — IHT
- **Finance Act** (annual — must specify year)

### Regulatory
- **Financial Services and Markets Act 2000 (FSMA)** — FCA regulated activities
- **Proceeds of Crime Act 2002 (POCA)** — money laundering, tipping off

---

## Instructions

1. When asked to verify a legal claim or citation, formulate the appropriate search query
2. Use `read_url_content` to fetch from the Lex API endpoint
3. Return the verbatim statutory text in your response
4. Format citations per UK convention: `[Act Name] [Year], s.[section]([subsection])`
5. Always note the data source: "Source: legislation.gov.uk via i.AI Lex API"
6. If the provision has been amended, note the amendment details

---

## Companion Tools in This Workspace

This skill works alongside:
- **`uk-law` MCP server** — local Ansvar Systems server (3,241 statutes, 512,651 provisions)
- **`companies-house` MCP server** — live Companies House API
- **`uk-law-remote` MCP server** — hosted Ansvar Systems fallback

---

## Scope Warning

> ⚠️ **This skill is scoped to the UK_Lanzarote_Repatriation workspace only.**
> It queries UK government databases and returns UK law citations.
> Do NOT use in any US-law project context.
