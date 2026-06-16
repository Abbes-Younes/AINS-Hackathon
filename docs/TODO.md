# AINS Hackathon 2026 - Intelligent Entrepreneurial Orientation Engine
## Project TODO & Implementation Guide for Coding Agent

---

## 1. PROJECT OVERVIEW

**Mission:** Build a unified AI platform for Tunisian entrepreneurs that combines three mandatory features:
- **Feature 1:** Adaptive Diagnostic Engine (maturity classification + gap detection)
- **Feature 2:** Explainable Multi-Dimensional Scoring (5 composite scores with sub-criteria)
- **Feature 3:** RAG-Grounded Roadmap & Resource Orientation (real Tunisian programs)

**Primary Users:** Entrepreneurs in Tunisia (French/Arabic UI preferred)
**Key Constraint:** NOT a chatbot. Conversational layer is secondary ONLY. The core is structured diagnostic + scoring + RAG retrieval.

**What Wins:**
- Real-world relevance to Tunisian entrepreneurship
- Cross-module integration (diagnostic gaps trigger KB retrieval, low scores trigger roadmap actions)
- Explainability (every output traceable to evidence)
- Real knowledge base of 30+ verified Tunisian programs
- Perception-reality gap detection (self-assessed vs evidence-based stage)

**Judging Criteria:**
- Real-world Impact (25%): Direct relevance to Tunisia, value proposition clarity
- Technical Depth (25%): AI pipeline quality, non-trivial problem solving
- Prototype Quality (20%): End-to-end demo, realistic inputs, usable interface
- Explainability & Scoring Rigour (15%): Traceable scores, linked evidence, uncertainty communication
- Evaluation & Rigour (15%): Real metrics, test set, reported results

---

## 2. REPOSITORY STRUCTURE (Target)

```
ains-hackathon-2026/
├── README.md                          # Project overview, setup, architecture
├── docs/
│   ├── CONTEXT.md                     # Problem statement (provided)
│   ├── feature_1_diagnostic_engine.md   # Feature 1 spec (provided)
│   ├── feature_2_scoring.md           # Feature 2 spec (provided)
│   ├── feature_3_rag_roadmap.md       # Feature 3 spec (provided)
│   ├── scoring_methodology.md         # Criteria, weights, aggregation logic
│   ├── knowledge_base_documentation.md # KB sources, schema, coverage
│   ├── evaluation_report.md           # Metrics, test protocol, results
│   └── architecture_diagram.md        # System components, data flow
├── data/
│   ├── raw/
│   │   └── kb_raw.json                # Provided: 50+ Tunisian programs
│   └── processed/
│       ├── kb_clean.json              # Validated KB items
│       ├── kb_flagged.json            # Items needing manual review
│       ├── kb_summary.csv             # Quick audit spreadsheet
│       └── test_profiles.json         # Synthetic test personas (Amine, Fatima, Omar)
├── src/
│   ├── __init__.py
│   ├── config.py                      # Central config (paths, model names, thresholds)
│   ├── models/
│   │   ├── __init__.py
│   │   ├── profile.py                 # Entrepreneur profile schema & persistence
│   │   ├── diagnostic.py              # Diagnostic result schema (stage, gaps, blockers)
│   │   ├── scoring.py                 # Score result schema (composite + sub-scores)
│   │   └── roadmap.py                 # Roadmap action schema
│   ├── feature_1_diagnostic/
│   │   ├── __init__.py
│   │   ├── intake_engine.py           # Adaptive questionnaire engine
│   │   ├── decision_tree.yml          # Branching logic for 3+ personas
│   │   ├── classifier.py              # Maturity stage classifier (rule-based + confidence)
│   │   ├── gap_detector.py            # Self-assessment vs evidence comparison
│   │   └── blocker_taxonomy.yml       # Structured blocker catalogue
│   ├── feature_2_scoring/
│   │   ├── __init__.py
│   │   ├── scoring_config.yml         # Criteria, weights, floor constraints
│   │   ├── scoring_engine.py          # Computes 5 composite scores
│   │   ├── anomaly_detector.py        # Flags contradictory signals
│   │   ├── justification_engine.py    # Plain-language explanations (LLM prompt)
│   │   └── improvement_guidance.py    # Highest-leverage gap identification
│   ├── feature_3_rag/
│   │   ├── __init__.py
│   │   ├── ingestion_pipeline.py      # KB -> SQLite + ChromaDB
│   │   ├── retrieval_engine.py        # Hybrid retrieval (semantic + structured filter)
│   │   ├── query_generator.py         # Converts diagnostic output -> KB query
│   │   ├── roadmap_generator.py       # Ordered, time-horizon action plans
│   │   └── conversational_layer.py    # Secondary assistant (grounded on structured outputs)
│   ├── kb/
│   │   ├── __init__.py
│   │   ├── validator.py               # kb_raw.json -> clean/flagged (provided script)
│   │   └── schema.py                  # KB item schema & validation rules
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── llm_client.py              # LLM wrapper (OpenAI/Anthropic/local)
│   │   ├── embeddings.py              # Embedding model wrapper
│   │   └── persistence.py             # JSON/DB save-load helpers
│   └── api/
│       ├── __init__.py
│       ├── main.py                    # FastAPI entry point
│       ├── routes/
│       │   ├── __init__.py
│       │   ├── diagnostic.py          # Intake, classification, gap detection endpoints
│       │   ├── scoring.py             # Score computation, evolution tracking
│       │   ├── roadmap.py             # Roadmap generation, resource retrieval
│       │   └── dashboard.py           # Mon Parcours tracking view
│       └── middleware/
│           ├── error_handler.py
│           └── logging.py
├── tests/
│   ├── __init__.py
│   ├── test_profiles/                 # 15+ synthetic labelled test cases
│   ├── test_diagnostic.py             # Classification accuracy tests
│   ├── test_scoring.py                # Scoring consistency tests
│   ├── test_retrieval.py              # Retrieval relevance tests
│   └── test_integration.py            # End-to-end pipeline tests
├── scripts/
│   ├── kb_validator_transformer.py    # Provided
│   ├── kb_ingestion_pipeline.py       # Provided
│   ├── run_tests.py                   # Test suite runner
│   └── demo_walkthrough.py            # End-to-end demo script
├── notebooks/
│   ├── 01_kb_exploration.ipynb        # Validate KB coverage
│   ├── 02_diagnostic_prototyping.ipynb # Test classification logic
│   └── 03_scoring_analysis.ipynb      # Score distribution analysis
├── frontend/                          # Optional: React/Vue dashboard
│   ├── public/
│   └── src/
│       ├── components/
│       │   ├── Dashboard.jsx          # Mon Parcours view
│       │   ├── DiagnosticPanel.jsx    # Intake + results
│       │   ├── ScoreCard.jsx          # Expandable score breakdown
│       │   ├── RoadmapTimeline.jsx    # Time-horizon action plan
│       │   └── ChatAssistant.jsx      # Grounded conversational layer
│       ├── App.jsx
│       └── index.js
├── requirements.txt                   # Python dependencies
├── setup.py                           # Package setup
├── .env.example                       # Environment variables template
├── .gitignore
└── TODO.md                            # This file
```

---

## 3. TECHNICAL REQUIREMENTS

### Core Stack (Recommended for hackathon speed)
- **Backend:** Python 3.10+, FastAPI (async, auto-docs, fast to build)
- **Data Stores:** 
  - SQLite (structured metadata, project profiles, score history)
  - ChromaDB (vector store for semantic retrieval)
- **AI/ML:**
  - Sentence-Transformers: `paraphrase-multilingual-MiniLM-L12-v2` (French/Arabic support)
  - LLM via API for natural language generation ONLY (justification, explanations)
  - Rule-based engines for classification, scoring, gap detection (auditable, deterministic)
- **Frontend:** React or plain HTML/JS for demo (optional but recommended)
- **Language:** French primary, Arabic secondary for UI text

### Dependencies (requirements.txt)
```
fastapi==0.111.0
uvicorn==0.30.0
pydantic==2.7.0
chromadb==0.5.0
sentence-transformers==3.0.0
pyyaml==6.0.1
python-dotenv==1.0.1
httpx==0.27.0
pytest==8.2.0
pandas==2.2.0
numpy==1.26.0
```

---

## 4. IMPLEMENTATION PHASES

### PHASE 0: Foundation (Hours 0-4)
**Goal:** Working repo structure, validated KB, test personas ready.

**Tasks:**
1. Create all directories in the target structure above.
2. Copy `kb_raw.json` to `data/raw/`.
3. Run `kb_validator_transformer.py` -> produce `data/processed/kb_clean.json`, `kb_flagged.json`, `kb_summary.csv`.
4. **CRITICAL:** Manually verify URLs for ALL APII, BFPME, BTS, ANPE items in `kb_flagged.json`. Fix in `kb_raw.json` and re-run validator until >=30 clean items exist.
5. Run `kb_ingestion_pipeline.py` -> verify ChromaDB + SQLite are populated.
6. Create `data/processed/test_profiles.json` with 3 personas:
   - **Amine** (tech, overconfident, claims Fundraising, evidence = Structuration)
   - **Fatima** (agri-food, Validation stage, missing scalability plan)
   - **Omar** (artisan, Arabic-preferred, Ideation->Structuration transition)
   Include: full profile, expected stage, expected gaps, expected scores.

**Definition of Done:**
- [ ] `kb_clean.json` has >=30 items with valid URLs
- [ ] ChromaDB query returns relevant Tunisian programs for test queries
- [ ] `test_profiles.json` has 3 complete personas with expected outputs
- [ ] README.md has setup instructions and architecture overview

---

### PHASE 1: Feature 1 - Adaptive Diagnostic Engine (Hours 4-12)
**Goal:** End-to-end intake -> classification -> gap detection for all 3 personas.

**Tasks:**
1. **Profile Schema** (`src/models/profile.py`):
   - Pydantic model: `EntrepreneurProfile` with all fields from spec (sector, legal_form, team, revenue, validation_evidence, business_model_clarity, location, accompaniment_history, self_assessed_stage)
   - JSON persistence to SQLite with `project_id` and `session_id`

2. **Decision Tree** (`src/feature_1_diagnostic/decision_tree.yml`):
   - Define branching logic for 3 distinct profile types
   - Example branches:
     - Sector = agri-food -> ask certification questions
     - Self-assessed = Fundraising -> probe validation evidence deeply
     - No legal form -> skip equity questions, ask registration intent
   - Each node: `question_id`, `question_text_fr`, `question_text_ar`, `input_type`, `next_rules` (conditional branching)

3. **Intake Engine** (`src/feature_1_diagnostic/intake_engine.py`):
   - Load decision tree, track conversation state
   - Accept answers, update profile, determine next question
   - Endpoint: `POST /diagnostic/intake` (accepts answer, returns next question or completion signal)
   - Endpoint: `GET /diagnostic/intake/{project_id}` (resume session)

4. **Classifier** (`src/feature_1_diagnostic/classifier.py`):
   - Rule-based classifier with 6 stages: Ideation, Validation, Structuration, Fundraising, Launch_Planning, Growth
   - Define threshold criteria per stage in code (e.g., Structuration requires legal_form OR business_model_clarity)
   - Output: `assigned_stage`, `confidence_score` (0.0-1.0), `evidence_trace` (list of data points that drove decision)
   - If between two stages, output both with confidence split (don't force binary)

5. **Gap Detector** (`src/feature_1_diagnostic/gap_detector.py`):
   - Compare `self_assessed_stage` vs `assigned_stage`
   - Identify missing prerequisites for the self-assessed stage
   - Output structured gap objects with: `gap_type`, `claimed_stage`, `actual_stage`, `missing_dimensions`, `explanation`
   - Minimum 3 demonstrated divergence cases in test suite

6. **Blocker Taxonomy** (`src/feature_1_diagnostic/blocker_taxonomy.yml`):
   - Catalogue of common blockers mapped to stages and domains
   - Each blocker: `name`, `affected_stages`, `domain`, `priority`, `description`
   - Rank blockers by: (1) blocks stage transition, (2) missing information, (3) nice-to-have

7. **Diagnostic Synthesis** (`src/feature_1_diagnostic/synthesis.py`):
   - Combine stage, gaps, blockers into structured `DiagnosticResult`
   - Generate plain-language summary (use LLM prompt with structured inputs)

**API Endpoints:**
```
POST /diagnostic/start              -> Create project, return first question
POST /diagnostic/answer             -> Submit answer, return next question or results
GET  /diagnostic/{project_id}       -> Get current diagnostic state
POST /diagnostic/classify           -> Run classification on complete profile
GET  /diagnostic/{project_id}/gaps  -> Get gap analysis
```

**Definition of Done:**
- [ ] Branching produces meaningfully different question sequences for 3 personas
- [ ] Every stage assignment links to specific collected data points (evidence_trace)
- [ ] >=3 test cases where self-assessed stage diverges from system diagnosis
- [ ] Intake to diagnostic output runs end-to-end without manual intervention
- [ ] Blockers are ranked and linked to maturity stage
- [ ] Incomplete profiles handled gracefully (uncertainty surfaced, not hidden)
- [ ] Profile persists across sessions (SQLite storage)
- [ ] Classification accuracy metric reported on test set (accuracy >= 0.8 on synthetic data)

---

### PHASE 2: Feature 2 - Explainable Multi-Dimensional Scoring (Hours 12-20)
**Goal:** 5 composite scores with sub-score decomposition, anomaly detection, improvement guidance.

**Tasks:**
1. **Scoring Config** (`src/feature_2_scoring/scoring_config.yml`):
   - Define 5 composite scores: Market, Commercial_Offer, Innovation, Scalability, Green
   - Each composite: 3-5 sub-criteria with weights (sum to 1.0 per composite)
   - Define levels per sub-criterion (0-4 or 0-5 scale)
   - Define floor constraints (e.g., customer_validation = 0 caps Market at 40)
   - Define aggregation logic (weighted sum, NOT average)
   - Document justification for each weight in YAML comments

2. **Scoring Engine** (`src/feature_2_scoring/scoring_engine.py`):
   - Input: `EntrepreneurProfile` + `DiagnosticResult`
   - Map profile fields to sub-criteria scores
   - Apply weights, compute composites, enforce floor constraints
   - Output: `ScoreResult` with all composites, sub-scores, and per-criterion contributions
   - Track score history (versioned snapshots in SQLite)

3. **Anomaly Detector** (`src/feature_2_scoring/anomaly_detector.py`):
   - Hardcoded consistency rules (not LLM-based):
     - IF claimed_traction == "high" AND validation_evidence == "none" -> flag
     - IF scalability_score > 80 AND manual_dependency == "high" -> flag
     - IF self_assessed_stage == "Fundraising" AND market_score < 40 -> flag
   - Output: `AnomalyFlag` with `severity`, `rule_triggered`, `explanation`
   - Minimum 2 demonstrated anomaly cases in test suite

4. **Justification Engine** (`src/feature_2_scoring/justification_engine.py`):
   - Use LLM prompt with tight constraints:
     - Input: sub-score value, criterion definition, level achieved, specific profile data
     - Output: 2-3 sentence plain-language explanation referencing actual data
     - Example: "You indicated no documented customer interviews. Customer validation carries 35% of Market Score because it is the most direct signal of demand. This sub-score is 8/35."
   - Cache results to avoid repeated LLM calls

5. **Improvement Guidance** (`src/feature_2_scoring/improvement_guidance.py`):
   - For each composite score, identify highest-leverage gap (sub-criterion with biggest impact if improved)
   - Suggest concrete action linked to KB (e.g., "Document pricing model using BFPME template")
   - Compute estimated score improvement if gap is closed

6. **Score Evolution** (`src/feature_2_scoring/evolution_tracker.py`):
   - Store versioned snapshots keyed by timestamp
   - On recalculation, diff against previous and surface changed sub-scores
   - Output: `ScoreEvolution` with deltas and trend indicators

**API Endpoints:**
```
POST /scoring/compute/{project_id}       -> Compute scores for profile
GET  /scoring/{project_id}               -> Get current scores with breakdown
GET  /scoring/{project_id}/history       -> Score evolution timeline
GET  /scoring/{project_id}/anomalies     -> Detected anomalies
GET  /scoring/{project_id}/improvements  -> Highest-leverage gaps per score
```

**Definition of Done:**
- [ ] 5 composite scores implemented (Market, Commercial_Offer, Innovation, Scalability, Green)
- [ ] Each composite decomposes into >=3 sub-dimensions with visible contributions
- [ ] Weighting methodology described, justified, and reproducible in YAML
- [ ] Every score accompanied by plain-language explanation referencing specific profile data
- [ ] >=2 demonstrated anomaly cases flagged with explanation
- [ ] Highest-leverage gap per score identified with concrete suggested action
- [ ] Profile update triggers score recalculation with change delta surfaced
- [ ] Scoring consistency metric reported on test set (inter-rater agreement or consistency score)

---

### PHASE 3: Feature 3 - RAG-Grounded Roadmap & Resource Orientation (Hours 20-28)
**Goal:** Hybrid retrieval, personalised roadmap generation, cross-module coherence, dashboard.

**Tasks:**
1. **Retrieval Engine** (`src/feature_3_rag/retrieval_engine.py`):
   - Hybrid retrieval combining:
     - Dense retrieval: ChromaDB semantic search on `embedding_text`
     - Structured filtering: SQLite queries on `eligibility_stages`, `domains_addressed`, `blockers_resolved`
   - Re-ranking: Boost score for eligibility match, filter by stage appropriateness
   - Input: Diagnostic profile summary (stage, blockers, low-scoring dimensions)
   - Output: Ranked list of resources with relevance scores and source citations

2. **Query Generator** (`src/feature_3_rag/query_generator.py`):
   - Convert diagnostic output to semantic query string
   - Example: stage="Structuration", blockers=["No legal form", "No validated business model"] -> query: "Tunisian support program for Structuration-stage entrepreneur needing legal registration and business model validation"
   - Include sector and domain context for precision

3. **Roadmap Generator** (`src/feature_3_rag/roadmap_generator.py`):
   - Produce ordered, prioritised action plan with time horizons:
     - Immediate (0-30 days): Resolve critical blockers, gather missing evidence
     - Short-term (1-3 months): Structural steps, program applications, validation milestones
     - Medium-term (3-12 months): Growth levers, financing access, scaling preparation
   - Each action must be:
     - Grounded: linked to specific diagnostic finding, low sub-score, or identified blocker
     - Sequenced: ordered so earlier actions unlock later ones
     - Specific: not "improve business model" but "Document revenue model using BFPME pre-financing template and validate with 3 paying customers"
   - Use dependency graph logic: legal form -> APII registration -> Startup Act label -> BFPME financing

4. **Cross-Module Coherence** (integration logic in `src/feature_3_rag/`):
   - Diagnostic gap (Feature 1) -> triggers retrieval of specific support resources
   - Low sub-score (Feature 2) -> surfaces KB items targeting that dimension
   - Maturity classification (Feature 1) -> filters roadmap to stage-appropriate actions only
   - Anomaly flag (Feature 2) -> generates cautionary note in roadmap
   - Minimum 1 end-to-end demonstration where diagnostic gap triggers relevant KB retrieval

5. **Conversational Layer** (`src/feature_3_rag/conversational_layer.py`):
   - Secondary layer ONLY, not the core product
   - System prompt grounds assistant on: diagnostic summary, score breakdown, roadmap, retrieved KB context
   - Every turn: re-retrieve top-k KB items relevant to user question before generating response
   - Assistant must decline to answer outside grounding context and redirect to diagnostic outputs
   - Example: "Based on your current Structuration gap and Market Score of 32, I recommend the APII Startup Act programme..."

6. **Dashboard API** (`src/api/routes/dashboard.py`):
   - Single endpoint returning complete project state:
     - Current maturity stage with evidence summary
     - All 5 composite scores with sub-score breakdowns
     - Priority blockers ranked by urgency
     - Recommended next actions linked to sources
     - Personalised roadmap across time horizons
     - "Mon Parcours" tracking: current stage, past recommendations, actions taken, next steps, score evolution

**API Endpoints:**
```
POST /roadmap/generate/{project_id}      -> Generate personalised roadmap
GET  /roadmap/{project_id}               -> Get current roadmap
GET  /resources/search                   -> Search KB (query + optional filters)
GET  /resources/{resource_id}            -> Get specific resource details
POST /assistant/ask                      -> Grounded conversational assistant
GET  /dashboard/{project_id}           -> Full dashboard state (Mon Parcours)
```

**Definition of Done:**
- [ ] >=30 documented, real resources structured and indexed in KB
- [ ] Every recommended resource cites at least one source in the KB
- [ ] Different diagnostic outputs produce meaningfully different roadmaps
- [ ] Diagnostic gap or low sub-score demonstrably triggers relevant KB retrieval
- [ ] Maturity level, scores, blockers, roadmap all visible in single interface
- [ ] Persistent tracking view (Mon Parcours) updates with project profile evolution
- [ ] Assistant responses reference diagnostic results, scores, or KB items (not generic LLM output)
- [ ] Retrieval relevance or roadmap coherence metric reported on test set
- [ ] New resources can be added without rebuilding retrieval pipeline (updatable KB)

---

### PHASE 4: Integration & Evaluation (Hours 28-36)
**Goal:** End-to-end pipeline works, evaluation metrics computed, demo script ready.

**Tasks:**
1. **Integration Tests** (`tests/test_integration.py`):
   - Test complete flow: Intake -> Classification -> Gap Detection -> Scoring -> Retrieval -> Roadmap
   - For each of the 3 personas, verify:
     - Correct stage assignment
     - Gap detection matches expected divergence
     - Scores computed with correct floor constraints
     - Retrieved resources are relevant to stage and blockers
     - Roadmap actions are sequenced and grounded

2. **Evaluation Metrics**:
   - **Classification Accuracy:** Accuracy + confusion matrix on 15-20 synthetic test profiles
   - **Scoring Consistency:** Compute standard deviation of scores for similar profiles, or inter-rater agreement
   - **Retrieval Relevance:** Precision@K (top 3 retrieved resources judged relevant by team)
   - **Roadmap Coherence:** Check that roadmap actions are ordered correctly (e.g., legal form before financing)
   - Document all in `docs/evaluation_report.md`

3. **Demo Script** (`scripts/demo_walkthrough.py`):
   - Automated script that runs the full pipeline for each persona
   - Outputs structured JSON results for each stage
   - Can be run with: `python scripts/demo_walkthrough.py --persona amine`
   - Produces console output suitable for recording demo video

4. **Documentation**:
   - `docs/scoring_methodology.md`: Criteria definitions, weights, aggregation logic, justification
   - `docs/knowledge_base_documentation.md`: Sources, formats, ingestion pipeline, coverage notes
   - `docs/architecture_diagram.md`: System components, data flow, AI pipeline, cross-module integration points
   - `docs/evaluation_report.md`: Metric(s), test protocol, results

**Definition of Done:**
- [ ] All 3 personas run end-to-end without errors
- [ ] Classification accuracy >= 0.8 on synthetic test set
- [ ] >=1 retrieval relevance metric reported
- [ ] Demo script produces consistent, presentable output
- [ ] All documentation files complete and accurate
- [ ] README includes setup instructions and architecture overview

---

### PHASE 5: Frontend & Polish (Hours 36-48) - Optional but Recommended
**Goal:** Usable dashboard for demo, French/Arabic UI elements.

**Tasks:**
1. **Dashboard Components:**
   - DiagnosticPanel: Show current question, progress, completion status
   - ScoreCard: Expandable cards for each composite score with sub-criteria breakdown
   - RoadmapTimeline: Visual timeline with Immediate/Short-term/Medium-term sections
   - MonParcoursView: Project history, stage evolution, score trends, completed actions
   - ChatAssistant: Grounded chat interface with context sidebar showing diagnostic summary

2. **UI Language:**
   - Primary: French
   - Secondary: Arabic (RTL layout, Arabic translations for key terms)
   - Use i18n framework or simple JSON translation files

3. **Responsive Design:**
   - Mobile-friendly (many Tunisian entrepreneurs access via mobile)
   - Clean, non-technical interface (judges evaluate usability by non-technical entrepreneurs)

**Definition of Done:**
- [ ] Dashboard displays all mandatory elements in single view
- [ ] French UI text complete
- [ ] Mobile-responsive layout
- [ ] Demo video can be recorded showing full dashboard interaction

---

## 5. CODING STANDARDS & CONVENTIONS

### Code Quality
- Use **Pydantic v2** for all data models (validation, serialization, documentation)
- Use **FastAPI** for API layer (automatic OpenAPI docs, async support)
- Use **pytest** for all tests (fixtures for personas, mock LLM responses)
- Use **type hints** everywhere (Python 3.10+ syntax)
- Use **async/await** for I/O operations (LLM calls, DB queries)

### Error Handling
- All API endpoints return structured error responses: `{"error": "...", "detail": "...", "suggestion": "..."}`
- Never crash on missing/incomplete data. Surface uncertainty explicitly.
- Log all LLM calls with input/output hashes for debugging

### Configuration
- All paths, model names, thresholds in `src/config.py` or `.env`
- Never hardcode API keys in source code
- Use `python-dotenv` for environment variables

### Documentation
- Every module has module-level docstring explaining purpose
- Every function has Google-style docstring (Args, Returns, Raises)
- Complex logic (scoring, classification) has inline comments explaining domain reasoning

---

## 6. CRITICAL SUCCESS FACTORS

### What Will Disqualify You
- Hallucinated program names or invented administrative steps in KB
- Standalone chatbot as core product (must be secondary layer only)
- Generic advice not grounded in diagnostic output or KB
- Scores without traceable justification (opaque labels)
- Roadmap as flat list without order, rationale, or time horizons

### What Will Win You Bonus Points
- **Cross-module integration depth:** Show explicit event chain in demo
- **Perception-reality gap detection:** 3+ non-trivial divergence cases with clear explanations
- **Real user validation:** Test with 1+ real Tunisian entrepreneur, document feedback
- **Arabic language support:** Handle Arabic inputs or KB documents meaningfully
- **Original dataset contribution:** Publish curated KB as standalone dataset
- **Post-hackathon roadmap:** Credible plan for pilot with PNUD/GEWEET ecosystem

### What Judges Will Spot-Check
- APII Startup Act details (correct URL, eligibility criteria)
- BFPME pre-financing requirements
- BTS solidarity guarantee conditions
- Scoring weights and floor constraints (are they defensible?)
- Gap detection for the "overconfident founder" persona
- Whether retrieved resources actually exist and are current

---

## 7. IMMEDIATE NEXT ACTIONS (Do These Now)

1. **Create directory structure** from Section 2
2. **Run validator** on `kb_raw.json` -> fix flagged items -> re-run until >=30 clean
3. **Run ingestion pipeline** -> verify ChromaDB returns relevant results for test queries
4. **Create `src/config.py`** with all paths and model names
5. **Create `src/models/profile.py`** with Pydantic schema
6. **Draft `src/feature_1_diagnostic/decision_tree.yml`** with branching for 3 personas
7. **Draft `src/feature_2_scoring/scoring_config.yml`** with 5 composites, weights, floor constraints
8. **Create `data/processed/test_profiles.json`** with Amine, Fatima, Omar

---

## 8. DEMO DAY CHECKLIST

- [ ] Pitch deck (max 15 slides): problem, solution, users, value prop, demo walkthrough, limitations, next steps
- [ ] Demo video (max 5 min) or live demo: end-to-end scenario for at least one persona
- [ ] Architecture diagram: components, data flow, AI pipeline, cross-module integration
- [ ] Knowledge base documentation: sources, formats, ingestion pipeline, coverage notes
- [ ] Scoring methodology document: criteria, weights, aggregation logic, justification
- [ ] Explainability layer: interface element showing why system produced specific output
- [ ] Evaluation report: metric(s), test protocol, results
- [ ] GitHub repo: source code, clear README, setup instructions
- [ ] All 3 features interact meaningfully (not independent panels)
- [ ] French and/or Arabic UI components

---

## 9. ARCHITECTURE PRINCIPLES

1. **Deterministic core, LLM wrapper:** Classification, scoring, gap detection are rule-based and auditable. LLM is used ONLY for natural language generation (justifications, explanations, summaries).
2. **Structured over generative:** Every output is a structured object (Pydantic model) before it becomes text. The LLM receives structured inputs, not raw prompts.
3. **Event-driven integration:** When Feature 1 detects a gap, it emits an event. Feature 3 listens and triggers retrieval. This makes cross-module coherence explicit and testable.
4. **Version everything:** Profile versions, score snapshots, KB updates. Mon Parcours requires history.
5. **Fail gracefully:** Incomplete profiles, missing KB items, LLM timeouts -> all handled with explicit uncertainty messages, never silent failures.

---

## 10. CONTACT & CONTEXT

- **Hackathon:** AINS Hackathon 2026
- **Organizers:** PNUD, GEWEET, ODC, IEEE Section, APII, AINS 4.0
- **Theme:** AI for Entrepreneurship - Unlocking the entrepreneurship ecosystem through AI
- **Primary Context:** Entrepreneurship in Tunisia and the MENA region
- **Target Users:** Tunisian entrepreneurs at early and growth stages
- **Language Requirement:** French and/or Arabic strongly preferred for UI
- **Data:** Public, synthetic, and realistic mock data acceptable (must be documented)
- **Technical Freedom:** No imposed stack. Any combination of tools, frameworks, models, databases.

**Remember:** The integration is the differentiator. A diagnostic finding that identifies a missing market validation step should surface relevant support programs that address it. A scalability gap should connect to specific actions in the roadmap. The three modules must interact - not merely coexist.