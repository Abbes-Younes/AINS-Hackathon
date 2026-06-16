# Feature 1 — Adaptive Diagnostic Engine

> **Core idea:** Don't build a form. Build an interview that thinks.

---

## The Problem This Feature Solves

Entrepreneurs are rarely able to accurately position themselves within their development cycle. They either:
- **Overestimate** their readiness — claiming to be at the financing stage without a validated business model
- **Underestimate** the structuring work already done — and miss opportunities they already qualify for

No existing tool in the Tunisian entrepreneurial ecosystem performs a dynamic, evidence-based diagnostic that combines:
- Structured data collection
- Adaptive questioning
- Maturity classification
- Explicit gap detection between self-perception and project reality

The result of this gap: entrepreneurs get sent to programs they don't qualify for, offered resources that don't match their stage, and left without a clear picture of what is genuinely blocking their progress.

---

## The 6-Stage Maturity Taxonomy

The engine must classify every project into one of six stages. Each stage must have **defined, defensible criteria** — not vague labels.

| # | Stage | What It Means |
|---|---|---|
| 1 | **Ideation** | An idea exists. No validation, no team, no structured plan. |
| 2 | **Market Validation** | Actively testing assumptions with real users or real data. Seeking evidence that the problem exists and the solution resonates. |
| 3 | **Structuration** | Building the foundations: legal form, team composition, business model clarity, operational structure. |
| 4 | **Fundraising** | Ready (or believes they're ready) to seek external capital. Business model validated, pitch prepared. |
| 5 | **Launch Planning** | Preparing to go to market: go-to-market strategy, early customer acquisition, operational readiness. |
| 6 | **Growth** | Operating, generating revenue, and scaling. Focus shifts to replication and expansion. |

> **Design note:** Six stages with clear boundaries are more valuable than ten ambiguous ones. Scope discipline here is part of what gets evaluated.

---

## What the Engine Must Do — Expected Capabilities

### 1. Adaptive Structured Intake
The intake is **not a static form**. Questions must evolve in response to prior answers:
- A project flagged as operating in the agri-food sector → triggers sector-specific questions
- A project claiming market traction → triggers validation evidence probes (what evidence? how many users? what conversion rate?)
- A project with no legal form → skips questions about team equity structure

The branching logic is itself evaluated. The spec explicitly states: *"The intelligence of the intake is part of what will be evaluated."*

**Minimum requirement:** branching logic produces meaningfully different question sequences for at least 3 distinct profiles.

### 2. Maturity Classification
Assign the project to a stage in the taxonomy, with **evidence linking the classification to collected data points**. The classification must not be a black box.

Example: if the system classifies a project as "Structuration" (stage 3), it must surface which collected data points drove that conclusion — e.g. "You have a defined team but no registered legal form and no documented business model."

### 3. Gap Detection ⚡ (the core differentiator)
This is the most technically interesting and most evaluated capability. The system must:
- Hold two things simultaneously: what the entrepreneur **claimed** about themselves vs. what the **evidence supports**
- Surface the contradiction explicitly and clearly
- Flag which specific dimensions are causing the divergence

**Example gap case:**
> Entrepreneur self-assessment: "I am at the Fundraising stage"  
> System diagnosis: "Structuration"  
> Gap explanation: "You have indicated no validated business model and no documented customer validation evidence. These are prerequisites for the Fundraising stage."

**Minimum requirement:** at least 3 demonstrated cases where self-assessed stage diverges from system diagnosis.

### 4. Blocker Identification
Detect and rank the specific things blocking this entrepreneur's progress. Blockers must be:
- **Ranked by priority** (not a flat list)
- **Linked to the maturity stage** (a Fundraising-stage blocker is different from an Ideation-stage blocker)
- **Categorised by domain:** financial · legal · market · technical · organisational

### 5. Diagnostic Synthesis
Produce a **structured, readable diagnostic output** — not a raw score — that the entrepreneur can actually act on. This is the deliverable the entrepreneur sees: their project's current position, the evidence behind it, the gaps detected, and the priority blockers.

### 6. Contextual Project Memory
The project profile must **persist across sessions**. When the entrepreneur returns and adds new information, the diagnosis refines — it doesn't restart. This implies a persistent data store for each project profile.

---

## Data & Domain Model

The entrepreneur profile must capture at minimum:

| Dimension | Examples |
|---|---|
| **Sector** | Agri-food, fintech, health, education, energy, manufacturing... |
| **Legal form** | Not yet registered, auto-entrepreneur, SARL, SA, association... |
| **Team composition** | Solo founder, co-founders, number of employees, technical/non-technical split |
| **Revenue status** | Pre-revenue, first revenue, recurring revenue, profitable |
| **Validation evidence** | None, user interviews only, pilot users, paying customers, signed LOIs |
| **Business model clarity** | Undefined, draft, tested, documented |
| **Geographic location** | Tunis, regional city, rural, targeting export |
| **Prior accompaniment history** | None, attended incubator, received mentoring, part of accelerator |

### Blocker Taxonomy
You need to define a structured catalogue of common blockers, mapped to stages and domains. Example structure:

```
Blocker: "No validated business model"
  Stage: affects Structuration → Fundraising transition
  Domain: market
  Priority signal: blocks access to financing programs

Blocker: "No legal form"
  Stage: affects Structuration
  Domain: legal
  Priority signal: blocks APII registration, bank account opening

Blocker: "No customer validation evidence"
  Stage: affects Market Validation → Structuration transition
  Domain: market
  Priority signal: high — absence contradicts any claim of traction
```

---

## Acceptance Criteria — What You Must Demonstrate

| Criterion | What to Show | Priority |
|---|---|---|
| Adaptive intake is real | Branching logic produces meaningfully different question sequences for ≥3 distinct profiles | **Must** |
| Classification is traceable | Every maturity stage assignment links to specific collected data points | **Must** |
| Gap detection works | ≥3 demonstrated cases where self-assessed stage diverges from system diagnosis | **Must** |
| End-to-end demo | Intake to diagnostic output runs without manual intervention | **Must** |
| Blocker identification | Priority blockers are ranked and linked to the maturity stage | Should |
| Handles ambiguity | Incomplete profiles handled gracefully; uncertainty surfaced, not hidden | Should |
| Persistent project context | Re-entering with updated information refines the diagnosis | Should |
| Evaluation protocol | At least one classification metric reported on a labelled test set | Should |

---

## Key Design Considerations

### Classification accuracy matters
Misclassifying a project stage can send an entrepreneur down the wrong path. Be explicit about confidence levels and edge cases. When the system is uncertain between two stages, say so — don't force a binary output.

### The perception gap is a feature, not a side effect
Design the gap detection explicitly. It should not be an afterthought computed at the end. The intake questions themselves should be designed to probe both self-assessment (what stage do you think you're at?) and objective evidence (what can you demonstrate?).

### Language
The intake must operate in **French and/or Arabic** to be accessible to the primary user population in Tunisia.

### Scope discipline
Define a focused maturity taxonomy with clear, defensible criteria per stage. Resist the urge to add more stages to seem thorough — clarity is more valuable than comprehensiveness here.

---

## How This Feature Feeds Into Features 2 & 3

This engine is the **data source for everything else**. The profile it builds becomes the input for:
- **Feature 2:** the scoring engine uses the collected data points to compute the 5 composite scores
- **Feature 3:** the RAG system uses the maturity stage, blockers, and gaps to retrieve relevant Tunisian resources and generate a personalised roadmap

If Feature 1 produces a weak or shallow profile, Features 2 and 3 have nothing real to work with. This is the foundation — it must be solid.

---

## Implementation Approach Ideas

### For the adaptive intake
- Use an LLM with a structured prompt that receives the conversation history and the current profile state, and decides the next best question to ask
- Alternatively, build a rule-based decision tree with LLM-generated question phrasing
- Hybrid: rule-based branching for structural decisions (which domain to probe next), LLM for natural language question formulation

### For classification
- Train or prompt-engineer a classifier on synthetic labelled examples (entrepreneur profile → maturity stage)
- Use a rule-based scoring system where each stage has defined threshold criteria
- A confidence score alongside the classification is a strong explainability signal

### For gap detection
- Simple and effective: ask the entrepreneur directly for their self-assessed stage early in the intake, then compare it to the system's output at the end
- Flag specific collected data points that contradict the self-assessment

### For persistence
- Store the project profile as a JSON document in a database, keyed by project ID
- Each session loads the existing profile, updates it with new answers, and triggers re-classification