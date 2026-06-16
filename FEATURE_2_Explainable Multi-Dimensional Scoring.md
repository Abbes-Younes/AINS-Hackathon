# Feature 2 — Explainable Multi-Dimensional Scoring

> **Core idea:** Don't assign a number. Build a mirror that shows the entrepreneur exactly where they stand — and why.

---

## The Problem This Feature Solves

A single score tells an entrepreneur nothing actionable. Knowing that a project "scored 62/100" does not reveal which dimension is dragging it down, why, or what to do about it. Yet this is exactly what most evaluation tools produce: an opaque aggregate that collapses five distinct dimensions into one meaningless label.

The deeper problem is structural:
- **Market readiness and scalability are not the same thing** — a project can be commercially strong but operationally fragile
- **A weak score on a critical dimension cannot be masked by strength elsewhere** — yet simple averages do exactly that
- **Entrepreneurs cannot improve what they cannot see** — without per-criterion visibility, the score is a verdict, not a guide

No existing tool in the Tunisian entrepreneurial ecosystem evaluates a project across multiple weighted, transparent dimensions and explains each output in plain language. The result: entrepreneurs receive either no evaluation at all, or one so generic it could apply to any project anywhere.

---

## The 5 Composite Scores

Each composite score must decompose into explicit sub-scores with defined, weighted criteria. The score is not an average — the aggregation logic must reflect domain reality.

| # | Composite Score | What It Measures |
|---|---|---|
| 1 | **Market Score** | The size and accessibility of the opportunity, the competitive landscape, and the evidence that real customers exist and will pay |
| 2 | **Commercial Offer Score** | The clarity, differentiation, and maturity of what the project is selling — value proposition, pricing, and product-market fit signals |
| 3 | **Innovation Score** | The degree of novelty in the local context, technological intensity, and how defensible the project is against imitation |
| 4 | **Scalability Score** | Whether the project can grow without proportional cost increase — replicability, process dependency, and addressable market ceiling |
| 5 | **Green Score** | Environmental and sustainability alignment — ecological footprint, SDG relevance, resource efficiency, and circular economy practices |

> **Design note:** Composite scores are not averages. A project with a very weak score on a foundational sub-dimension (e.g. no customer validation evidence) must not be rescued by strong scores elsewhere. The aggregation logic must enforce this.

---

## What the Engine Must Do — Expected Capabilities

### 1. Weighted Criteria Model
Every sub-score is computed from a defined set of criteria with **explicit, documented weights**. The weights must be:
- Justifiable — grounded in domain reasoning, not arbitrary
- Transparent — surfaced to users and judges
- Consistent — applied identically across all evaluated profiles

Example sub-score breakdown for Market Score:

```
Market Score (100 pts)
├── Addressable market size          — 25 pts
├── Competitive landscape analysis   — 20 pts
├── Customer validation evidence     — 35 pts  ← highest weight: absence is disqualifying
└── Revenue model clarity            — 20 pts
```

### 2. Score Decomposition
The system must surface **not just the composite score, but the contribution of each sub-criterion**. The entrepreneur must be able to see:
- Their composite score per dimension
- Their score per sub-criterion within that dimension
- Which sub-criteria are dragging the composite down
- How far they are from the next threshold

This is explainability — not an optional UI addition, but the core output.

### 3. Natural-Language Justification
Every score is accompanied by a **plain-language explanation** of what drove the result. The explanation must:
- Reference specific collected data points from the entrepreneur's profile
- Avoid generic filler ("your market score is moderate because the market analysis could be improved")
- State what is missing or what specific evidence would raise the score

**Example justification for a low Customer Validation sub-score:**
> "You indicated that you have spoken with potential customers but have no documented interviews, no pilot users, and no signed letters of intent. Customer validation evidence carries the highest weight within the Market Score because it is the most direct signal of real demand. This sub-score is currently 8/35."

### 4. Anomaly and Inconsistency Detection
The system must **flag contradictory or unsubstantiated signals** in a profile. These are not errors — they are diagnostic signals that something in the self-reported data doesn't add up.

**Example anomaly cases:**
- Project claims "high market traction" → but has zero documented customer validation evidence
- Project claims "fully scalable model" → but reports heavy reliance on manual accompaniment at every delivery step
- Project self-assessed at Fundraising stage → but Green Score and Scalability Score flag critical unresolved gaps that most financing programs require

**Minimum requirement:** at least 2 demonstrated anomaly cases flagged with clear explanation.

### 5. Improvement Guidance
For each composite score, the system must identify the **highest-leverage gap** — the single sub-criterion whose improvement would move the composite score most — and suggest a concrete action.

This is not a generic tip. It is derived from the specific profile data. Example:

> **Highest-leverage action for Commercial Offer Score:**  
> "Your value proposition is defined but your pricing strategy is marked as undefined. Pricing coherence carries 20% of the Commercial Offer Score. Documenting a pricing model — even a draft — would move your score from 48 to an estimated 62."

### 6. Score Evolution
As the entrepreneur updates their project profile (via Feature 1), scores must **recalculate automatically** and surface the delta:
- Which scores improved and by how much
- Which sub-criteria changed
- Whether the overall maturity classification has shifted

This creates a feedback loop: the entrepreneur sees the concrete impact of each step they take.

---

## Data & Scoring Model

### Criteria Definition Template
Each scoring criterion must be defined with the following structure:

```
Criterion: "Customer validation evidence"
  Composite: Market Score
  Weight: 35% of Market Score
  Levels:
    0  — No contact with potential customers
    1  — Informal conversations, no documentation
    2  — Structured interviews documented (≥5 users)
    3  — Pilot users with usage data
    4  — Paying customers or signed LOIs
  Aggregation note: A score of 0 here caps the Market Score at 40/100 regardless of other sub-scores
```

### Sub-Criterion Catalogue (Minimum Coverage)

| Composite Score | Sub-Dimensions |
|---|---|
| **Market Score** | Addressable market size · Competitive landscape · Customer validation evidence · Revenue model clarity |
| **Commercial Offer Score** | Value proposition clarity · Differentiation · Product/service maturity · Pricing strategy · Offer-need alignment |
| **Innovation Score** | Local novelty · Technology intensity · Barrier to entry · Departure from existing offerings |
| **Scalability Score** | Replicability without linear cost · Manual dependency · Deployment cost structure · Geographic addressability |
| **Green Score** | Environmental impact assessment · SDG alignment · Resource efficiency · Circular economy practices · Carbon footprint awareness |

### Aggregation Logic Principles
- Sub-scores aggregate to composite scores using **weighted sums**, not simple averages
- Certain sub-criteria act as **floor constraints**: a score of 0 on a critical criterion caps the composite regardless of other results
- Composite scores aggregate to an **overall readiness index** using stage-adjusted weights (e.g. Market Score carries higher weight for Fundraising-stage projects)
- The aggregation formula must be documented and reproducible

---

## Acceptance Criteria — What You Must Demonstrate

| Criterion | What to Show | Priority |
|---|---|---|
| Five composite scores implemented | Market, Commercial Offer, Innovation, Scalability, and Green scores all computed and displayed | **Must** |
| Sub-scores are explicit | Each composite decomposes into ≥3 sub-dimensions with visible per-criterion contributions | **Must** |
| Criteria weights are documented | Weighting methodology described, justified, and reproducible | **Must** |
| Natural-language justification | Every score accompanied by a plain-language explanation referencing specific profile data | **Must** |
| Anomaly detection works | ≥2 demonstrated cases of contradictory or unsubstantiated signals flagged with explanation | Should |
| Improvement guidance is specific | Highest-leverage gap per score identified with a concrete suggested action | Should |
| Score evolution tracked | Profile update triggers score recalculation with change delta surfaced | Should |
| Evaluation protocol | Scoring consistency or inter-rater agreement measured on a test set | Should |

---

## Key Design Considerations

### Explainability is not optional
A score without a traceable justification is an opaque label, not a decision-support tool. Every criterion contribution must be surfaced. If the system cannot explain a sub-score in terms of specific collected data points, the sub-score should not be shown.

### Scoring is modelling work
Defining the criteria, weights, aggregation logic, and floor constraints is a significant design effort — not a UI task. The scoring methodology document submitted for judging is evaluated as part of Technical Depth. Treat it accordingly.

### Composite scores are not averages
The aggregation logic must reflect domain reality. A project that has no customer validation evidence is not a "slightly below average" project on the Market Score — it is a project with a fundamental unresolved gap. The scoring model must encode this.

### Avoid over-engineering the score count
Five composite scores with deep, well-justified sub-criteria are more valuable than eight shallow composites. Scope discipline is part of what gets evaluated.

---

## How This Feature Feeds Into Features 1 & 3

Feature 2 sits in the middle of the pipeline. It consumes Feature 1's output and feeds Feature 3:

- **Receives from Feature 1:** The full entrepreneur profile — sector, legal form, team, revenue status, validation evidence, business model clarity — collected through the adaptive intake
- **Feeds into Feature 3:** Low sub-scores and identified improvement gaps become the triggers for targeted knowledge base retrieval; the RAG system surfaces resources specifically matched to the highest-leverage gaps identified here

A weak scoring model produces vague improvement guidance, which gives Feature 3 nothing meaningful to retrieve against. The quality of this scoring layer directly determines the quality of the roadmap the entrepreneur receives.

---

## Implementation Approach Ideas

### For the weighted criteria model
- Define the full criteria catalogue as a structured JSON or YAML config — weights, levels, floor constraints, and aggregation rules all in one place
- This makes the model auditable, versioned, and easy to update without touching application code
- Separate the scoring logic from the presentation layer so the same engine can serve both the dashboard and the conversational assistant

### For score computation
- Map each profile field (collected by Feature 1) to one or more scoring criteria
- Compute sub-scores programmatically from the mapping — no LLM needed for the computation itself
- Use an LLM only for generating the natural-language justification, given the computed sub-score values and the profile data that drove them

### For natural-language justification
- Prompt an LLM with: the sub-score value, the criterion definition, the level achieved, and the specific profile data point — ask it to explain the result in 2–3 sentences
- Keep the prompt tightly constrained to prevent generic output; the explanation must reference the actual data

### For anomaly detection
- Define a set of consistency rules as explicit conditions (e.g. `IF claimed_traction == "high" AND customer_validation_evidence == 0 THEN flag anomaly`)
- Surface flagged anomalies as a separate section in the scoring output — not buried in the justification text

### For score evolution
- Store a versioned history of score snapshots alongside the project profile (keyed by session or timestamp)
- On each recalculation, diff the new snapshot against the last and surface changed sub-scores