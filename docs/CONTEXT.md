# AINS Hackathon 2026 — Context & Overview

> **Organized by:** PNUD · GEWEET · ODC · IEEE Section · APII · AINS 4.0  
> **Theme:** AI for Entrepreneurship — Unlocking the entrepreneurship ecosystem through AI

---

## The Core Mission

Build AI systems that remove structural barriers entrepreneurs face in Tunisia and the MENA region — across orientation, diagnosis, financing access, and business evaluation.

The key phrase from the spec: **move beyond generic AI assistants**. The system must produce concrete, actionable outputs for real users. Whatever you build must demonstrably solve a real problem for an entrepreneur in Tunisia.

---

## The Problem Being Solved

Entrepreneurs at early and growth stages face compounding **orientation failures**:

- They lack visibility over their actual project maturity level
- They don't know which critical steps to take next
- They can't identify which support devices apply to their situation
- The information that exists is fragmented, rarely personalised, and almost never contextualised to a specific project profile

A deeper structural problem makes this worse: **entrepreneurs consistently overestimate or mischaracterise their maturity.** A founder who believes they are ready for financing may have no validated business model. A project described as scalable may be entirely dependent on manual processes.

Existing tools — static guides, generic chatbots, disconnected administrative portals — don't fix this. They answer questions but **do not diagnose**. They provide information but do not produce a structured, evidence-based assessment of where a project actually stands.

---

## The Vision

Build a **unified AI platform** that places the entrepreneur's project profile at the centre and activates three intelligent capabilities around it:

1. An **adaptive diagnostic engine** that classifies the project and surfaces gaps
2. An **explainable scoring system** that evaluates the project across multiple dimensions with transparent, weighted criteria
3. A **RAG-grounded recommendation layer** that orients the entrepreneur toward real resources, programs, and actions from a curated knowledge base

**The integration is the differentiator.** These three modules must interact — not merely coexist as independent panels. A diagnostic gap should trigger knowledge base retrieval. A low sub-score should surface targeted roadmap actions.

---

## What a Good Solution Must Achieve

| Requirement | Description |
|---|---|
| **Real-world relevance** | Addresses a concrete, documented pain point for entrepreneurs in Tunisia — not a hypothetical |
| **Actionable outputs** | Produces recommendations, scores, diagnoses, roadmaps — not raw data or open-ended conversation |
| **Structural intelligence** | Reasons over data to produce classification, scoring, gap detection — not merely retrieval or summarisation |
| **Explainability** | Every output is traceable; users can understand why the system produced any given result |
| **Evaluation** | The team defines at least one measurable metric and runs it on a test set, however small |

---

## Technical Freedom

No imposed stack. Anything goes:

- **AI/ML:** LLMs, classical ML, embeddings, rule-based engines, hybrid systems, or any combination
- **Data stores:** SQL, NoSQL, vector DB, graph DB, document store, or a combination
- **Frameworks:** Any language, ML framework, cloud service, or on-premise deployment
- **UI language:** French and/or Arabic strongly preferred for user-facing components
- **Data:** Public data, synthetic data, and realistic mock data are all acceptable (must be documented)

---

## What Is NOT Allowed

- A standalone chatbot or assistant as the core product — conversational features may exist only as a **secondary layer** connected to the diagnostic and scoring engines
- Solutions without a direct connection to entrepreneurship in the Tunisian context
- Reproducing an existing commercial product without a meaningful original contribution

---

## Submission Requirements

### First Submission (Concept & Prototype Foundation)
- Concept presentation: problem framing, proposed solution, target users, core AI mechanism, maturity taxonomy draft, initial scoring dimensions — max 10 pages/slides
- GitHub repo with: structured README, initial architecture sketch, early code or design decisions (even if not yet functional)

> A well-structured repo with a strong README and a clear scoring methodology draft is worth more than a working but misdirected prototype.

### Final Submission (Demo Day)
- **Pitch deck** — max 15 slides: problem, solution, users, value prop, demo walkthrough, limitations, next steps
- **Demo video** — max 5 min end-to-end walkthrough (or live demo)
- **Architecture diagram** — components, data flow, AI pipeline, cross-module integration
- **Knowledge base documentation** — sources, formats, ingestion pipeline, coverage notes
- **Scoring methodology document** — criteria definitions, weights, aggregation logic, justification
- **Explainability layer** — interface element showing why the system produced any specific output
- **Evaluation report** — metric(s) used, test protocol, results
- **GitHub/GitLab repo** — source code with clear README and setup instructions

---

## Judging Criteria

| Dimension | What Judges Look For | Weight |
|---|---|---|
| **Real-world Impact** | Direct relevance to Tunisia, clarity of value proposition, plausibility of real adoption | 25% |
| **Technical Depth** | Quality of AI pipeline, intelligence of diagnostic and scoring engines, non-trivial problem solving beyond keyword search | 25% |
| **Prototype Quality** | End-to-end demo works, handles realistic inputs, produces meaningful outputs, usable by a non-technical entrepreneur | 20% |
| **Explainability & Scoring Rigour** | Scores traceable to weighted criteria, diagnostic classifications linked to evidence, system communicates uncertainty | 15% |
| **Evaluation & Rigour** | Real evaluation protocol, documented metrics, test set, reported results | 15% |

---

## Bonus Points Available

- **Cross-module integration depth** — the three features interact meaningfully: diagnostic gaps trigger KB retrieval; low sub-scores surface targeted roadmap actions
- **Perception-reality gap detection** — system correctly flags ≥3 cases of entrepreneur self-assessment diverging from diagnostic output, with clear explanation
- **Real user validation** — at least one real potential user tested the prototype and provided documented feedback
- **Arabic language support** — system handles Arabic-language inputs or KB documents meaningfully (not just translation)
- **Original dataset contribution** — team built and curated a dataset that did not previously exist (e.g. structured Tunisian support program catalogue, maturity taxonomy with labelled examples)
- **Post-hackathon roadmap** — credible plan for continuing development toward real adoption with PNUD/GEWEET ecosystem

---

## Non-Functional Expectations

- **Responsiveness** — user-facing queries return results within a few seconds for a realistic dataset size
- **Reliability** — system handles missing, dirty, or incomplete data without crashing; edge cases documented
- **Privacy & Security** — sensitive data masked or anonymised; state clearly what data is used and how it is protected
- **Scalability mindset** — explain how the system would scale to more data, more users, or broader geographic scope