# Feature 3 — RAG-Grounded Roadmap & Resource Orientation

> **Core idea:** Don't generate advice. Retrieve reality — then personalise it.

---

## The Problem This Feature Solves

Once an entrepreneur has been diagnosed and scored, the natural question is: *what do I do now, and where do I go for help?* This is where every existing tool in the Tunisian ecosystem fails hardest.

The failure modes are consistent:
- **Generic recommendations** — advice that applies to any entrepreneur anywhere, with no connection to the specific project profile
- **Hallucinated resources** — plausible-sounding program names, funding instruments, or administrative steps that do not actually exist or no longer operate
- **Flat action lists** — a bullet list of suggestions with no order, no rationale, and no time horizon
- **Disconnected orientation** — the recommendation engine doesn't know what the diagnostic said, so it can't respond to the specific gaps identified

The result: entrepreneurs leave with a vague to-do list they don't trust, pointed at programs they may not qualify for, with no sense of sequencing or priority.

A recommendation that cannot be traced to a real program, a real document, or a real output from the diagnostic engine is not a recommendation. It is content generation.

---

## The Knowledge Base

The knowledge base is **core work, not optional enrichment**. It is the factual foundation that makes every recommendation in this feature traceable and trustworthy. A retrieval pipeline is only as good as the corpus it retrieves from.

### Mandatory Coverage Areas

| Domain | What to Include |
|---|---|
| **Support & Accompaniment Programs** | APII programs, BTS, Startup Act mechanisms, ANPE resources, active incubators and accelerators in Tunisia |
| **Financing Programs** | BFPME financing products, AFD programs, EU funding mechanisms applicable in Tunisia, UNDP acceleration programs, international development fund instruments |
| **Administrative & Regulatory Resources** | Business creation procedures, relevant forms, institutional contacts, APII registration steps, legal form options and requirements |
| **Business Guides & Standards** | Certification pathways, quality frameworks, reporting standards applicable in the MENA region |
| **Ecosystem Actors** | Mentors, professional networks, sector-specific associations, investor networks active in Tunisia |

> **Minimum requirement:** at least 30 documented, real resources structured and indexed in the knowledge base before demo day.

### Knowledge Base Schema
Each resource must be stored with structured metadata to enable precise retrieval:

```
Resource: "Startup Act — Labellisation"
  Type: support_program
  Operator: APII
  Eligibility_stages: [Structuration, Fundraising, Launch Planning]
  Eligibility_criteria:
    - Innovative project with IP or technology component
    - Registered legal form (SARL or SA)
    - Not yet operational for more than 3 years
  Domains_addressed: [legal, financial, market]
  Blockers_resolved: ["No structured legal framework", "No access to public financing"]
  Geographic_scope: national
  Language: fr
  Source_url: https://startup.gov.tn
  Last_verified: 2025-Q4
```

### Ingestion Pipeline
No single clean dataset for this knowledge base exists. Part of the challenge is building the ingestion pipeline itself. The pipeline must handle:
- **PDFs** — program guides, regulatory documents, official frameworks
- **Web pages** — program portals, institutional sites
- **Structured lists** — manually curated programme catalogues

Each ingested document must be chunked, embedded, and indexed for semantic retrieval. The pipeline design and documentation are evaluated — this is not a detail to defer to demo day.

---

## What the Engine Must Do — Expected Capabilities

### 1. RAG Pipeline
Retrieve relevant resources from the knowledge base in response to the specific diagnostic profile and scoring output produced by Features 1 and 2. Every retrieved item must:
- Be traceable to a named, documented source in the knowledge base
- Match the entrepreneur's maturity stage and identified gaps — not just their sector
- Be ranked by relevance to the specific blockers and low-scoring dimensions

Retrieval is not keyword search. The pipeline must use semantic similarity to surface resources that match the *intent* of the gap, not just its literal wording.

### 2. Personalised Roadmap Generation
Produce an **ordered, prioritised action plan** derived from the diagnostic output. A roadmap is not a flat list — it has structure:
- **Immediate actions** (0–30 days): resolve critical blockers, gather missing evidence
- **Short-term actions** (1–3 months): structural steps, program applications, validation milestones
- **Medium-term actions** (3–12 months): growth levers, financing access, scaling preparation

Each action must be:
- **Grounded** — linked to a specific diagnostic finding, low sub-score, or identified blocker
- **Sequenced** — ordered so that earlier actions unlock later ones
- **Specific** — not "improve your business model" but "document your revenue model using the BFPME pre-financing template and validate it with 3 paying customers before applying"

### 3. Resource Matching
Surface support programs, financing devices, and administrative steps that are **relevant to this entrepreneur's current stage and identified gaps** — not a generic catalogue.

Matching logic must account for:
- **Eligibility at the current maturity stage** — a Growth-stage program is not relevant to an Ideation-stage entrepreneur
- **Gap-to-resource alignment** — a project with a "no legal form" blocker should surface APII registration guidance before financing programs
- **Scoring profile** — a low Green Score should surface SDG-aligned support programs and certification pathways

### 4. Cross-Module Coherence ⚡ (the integration differentiator)
This is what separates a collection of panels from a unified platform. The connections between modules must be explicit and demonstrable:

- A **diagnostic gap** (Feature 1) → triggers retrieval of the specific support resources that address it
- A **low sub-score** (Feature 2) → surfaces knowledge base items that directly target that dimension
- A **maturity classification** (Feature 1) → filters the roadmap to stage-appropriate actions only
- An **anomaly flag** (Feature 2) → generates a specific cautionary note in the roadmap

**Minimum requirement:** at least one end-to-end demonstration where a diagnostic gap or low sub-score demonstrably triggers relevant knowledge base retrieval.

### 5. Dashboard Restitution
A single visual interface presenting:
- Current maturity stage with evidence summary
- All 5 composite scores with sub-score breakdowns
- Priority blockers ranked by urgency
- Recommended next actions linked to their sources
- The personalised roadmap across time horizons

The dashboard is the primary surface the entrepreneur interacts with. It must be usable by a non-technical entrepreneur — clarity and readability are evaluated alongside technical depth.

### 6. "Mon Parcours" Tracking View
A persistent view where the entrepreneur sees:
- Their current stage and how it has evolved
- Past recommendations and which actions they have marked as completed
- Next steps derived from the most recent diagnostic run
- How their scores have changed over time

This view reinforces the platform's longitudinal value — the system gets more useful as the entrepreneur progresses, not just on first use.

### 7. Connected Conversational Assistant
A **secondary** conversational layer that answers questions using the diagnostic results, scores, roadmap, and knowledge base as its grounding context.

The assistant is a layer — not the product. It must:
- Reference specific diagnostic findings when answering questions ("Based on your current structuration gap…")
- Cite knowledge base items when recommending programs ("The APII Startup Act programme, which your project qualifies for at Stage 3…")
- Refuse to answer outside its grounding context — it does not generate generic LLM advice bypassing the diagnostic

**What the assistant is not:** a standalone chatbot that happens to know about entrepreneurship. If it can answer questions without the diagnostic and KB outputs, it fails the requirement.

---

## Data & Knowledge Base Model

### Resource Types Catalogue

```
Type: support_program
  Fields: operator, eligibility_stages, eligibility_criteria, domains_addressed,
          blockers_resolved, geographic_scope, language, source_url, last_verified

Type: financing_device
  Fields: operator, financing_type (grant/loan/equity), amount_range,
          eligibility_stages, required_documents, application_deadline_type,
          geographic_scope, source_url

Type: administrative_procedure
  Fields: institution, procedure_name, required_documents, estimated_duration,
          prerequisite_procedures, output (legal_form/permit/certification),
          source_url

Type: ecosystem_actor
  Fields: actor_type (incubator/accelerator/investor/network), sectors_covered,
          stages_supported, contact, geographic_scope

Type: business_guide
  Fields: topic, applicable_stages, applicable_sectors, format (PDF/web),
          language, source_url
```

### Retrieval Architecture Options

```
Option A — Dense Retrieval (recommended)
  Embed all KB chunks using a sentence transformer
  At query time: embed the diagnostic profile summary
  Retrieve top-k chunks by cosine similarity
  Re-rank by eligibility stage match and blocker alignment

Option B — Hybrid Retrieval
  Combine dense retrieval (semantic) with sparse retrieval (BM25 keyword)
  Useful when KB items have specific named programs that exact-match is important for

Option C — Structured Filtering + Semantic Ranking
  Pre-filter by maturity stage and blocker domain (structured metadata)
  Apply semantic ranking only within the filtered set
  Lower computational cost; better precision for stage-gated resources
```

---

## Acceptance Criteria — What You Must Demonstrate

| Criterion | What to Show | Priority |
|---|---|---|
| Knowledge base is real | ≥30 documented, real resources structured and indexed | **Must** |
| Retrieval is traceable | Every recommended resource cites at least one source in the knowledge base | **Must** |
| Roadmap is personalised | Different diagnostic outputs produce meaningfully different roadmaps | **Must** |
| Cross-module coherence | A diagnostic gap or low sub-score demonstrably triggers relevant KB retrieval | **Must** |
| Dashboard is functional | Maturity level, scores, blockers, roadmap all visible in a single interface | **Must** |
| "Mon Parcours" view exists | Persistent tracking view updates with project profile evolution | Should |
| Conversational assistant is grounded | Assistant responses reference diagnostic results, scores, or KB items — not generic LLM output | Should |
| Evaluation protocol | Retrieval relevance or roadmap coherence metric reported on a test set | Should |
| Knowledge base is updatable | New resources can be added without rebuilding the retrieval pipeline | Could |

---

## Key Design Considerations

### Knowledge base construction is core work
Building a structured, diverse, and documented knowledge base of real Tunisian resources is a significant deliverable in its own right. It cannot be improvised the day before demo day. Plan for it in your timeline — sourcing, cleaning, structuring, and indexing heterogeneous documents takes time.

### Recommendations must be grounded — no exceptions
A recommendation that cannot be traced to a specific item in the knowledge base or a specific output from the diagnostic engine is a critical failure. Hallucinated program names, invented administrative steps, or fabricated funding amounts are disqualifying. Every named resource must exist and be verifiable.

### The roadmap is not a list
A personalised roadmap has an order, a rationale, and time horizons. Sequencing matters: an entrepreneur cannot apply for financing before they have a legal form, and they cannot get an APII label before their project is registered. The roadmap must encode these dependencies.

### The assistant is a layer, not the product
The conversational assistant must be demonstrably connected to the structured outputs of Features 1 and 2. An assistant that answers questions from general LLM knowledge, bypassing the diagnostic results and knowledge base, does not meet the requirement. Ground every response.

### Language matters
French and/or Arabic for all user-facing surfaces. The knowledge base should include sources in both languages where available — Arabic-language resources from ANPE, APII, and regional bodies are part of what the primary user population actually encounters.

---

## How This Feature Completes the Platform

Feature 3 is the surface the entrepreneur actually sees and acts on. It is only as good as what precedes it:

- **Receives from Feature 1:** Maturity stage, identified blockers, gap detection results, full entrepreneur profile
- **Receives from Feature 2:** Composite scores, sub-score breakdowns, anomaly flags, highest-leverage improvement gaps

Without real diagnostic depth from Feature 1, the roadmap is generic. Without meaningful scores from Feature 2, the resource matching has no targeting signal. The integration is the differentiator — and this feature is where that integration becomes visible to the entrepreneur.

---

## Implementation Approach Ideas

### For the knowledge base
- Start with a manually curated CSV or JSON catalogue of 30–50 real programs (APII, BFPME, BTS, Startup Act, EU mechanisms) — this is faster to build and easier to verify than crawling
- Enrich each entry with structured metadata (eligibility stage, blocker domains, source URL) before embedding
- Use a vector store (Chroma, Pinecone, Weaviate, pgvector) for semantic retrieval; keep the structured metadata in a relational or document store for filtering

### For the RAG pipeline
- Build a query from the diagnostic output: maturity stage + top 3 blockers + lowest-scoring dimensions → embed this composite query
- Retrieve top-k candidates, filter by eligibility stage, re-rank by blocker alignment
- Pass retrieved chunks + entrepreneur profile to an LLM to generate the grounded recommendation text
- Always surface the source citation alongside the generated text

### For the roadmap generator
- Define roadmap action templates per blocker type and per maturity stage transition
- Populate templates with specific KB-retrieved resources and profile-specific details
- Use an LLM to produce natural-language phrasing around the structured template output — not to generate the structure itself

### For the dashboard
- Single-page interface with clear sections: Diagnostic Summary · Scores · Priority Blockers · Recommended Actions · Roadmap
- Each score card expandable to show sub-score breakdown and improvement guidance
- Each recommended resource linked to its source

### For the conversational assistant
- System prompt grounds the assistant on: the entrepreneur's current diagnostic summary, their score breakdown, their roadmap, and a retrieved KB context window
- Every turn: re-retrieve the top-k KB items relevant to the user's question before generating a response
- Explicitly instruct the model to decline answering outside its grounding context and redirect to the diagnostic outputs