# 🧭 Intelligent Entrepreneurial Orientation Engine

> **AINS Hackathon 2026** — AI-powered diagnostic, scoring, and roadmap platform for Tunisian entrepreneurs.

## 🎯 The Problem

Entrepreneurs in Tunisia face three compounding failures:

1. **They don't know where they really are** — they overestimate or misjudge their project's maturity
2. **They can't see what's dragging them down** — they get vague feedback that doesn't pinpoint specific weaknesses
3. **They don't know what to do next** — generic advice without connecting to real Tunisian programs

## 🏗️ Architecture

```
┌────────────────────────────────────────────┐
│  Feature 1: Adaptive Diagnostic Engine      │
│  (Questionnaire → Classification → Gaps)   │
└──────────────────┬─────────────────────────┘
                   │ Profile data
                   ▼
┌────────────────────────────────────────────┐
│  Feature 2: Multi-Dimensional Scoring       │
│  (5 composites with weighted sub-criteria) │
└──────────────────┬─────────────────────────┘
                   │ Scores + gaps
                   ▼
┌────────────────────────────────────────────┐
│  Feature 3: RAG Roadmap & Resources         │
│  (Tunisian programs → Action plan)         │
└────────────────────────────────────────────┘
```

### Tech Stack

| Layer | Technology |
|-------|-----------|
| **API** | FastAPI (Python) |
| **Data Validation** | Pydantic v2 |
| **Vector Store** | ChromaDB (cosine similarity) |
| **Embeddings** | `paraphrase-multilingual-MiniLM-L12-v2` (384d) |
| **Relational DB** | SQLite |
| **Language** | French, Arabic, English |

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- pip

### Setup

```bash
# 1. Clone the repository
git clone <repo-url>
cd entrepreneurial-orientation-engine

# 2. Install dependencies
pip install -r requirements.txt

# 3. (Optional) Copy environment template
cp .env.example .env

# 4. Validate the knowledge base (run once)
python scripts/kb_validator_transformer.py

# 5. Run the ingestion pipeline (run once)
python scripts/kb_ingestion_pipeline.py

# 6. Start the API server
uvicorn src.api.main:app --reload
```

### Verify Installation

```bash
# Check the knowledge base
python -c "import json; d=json.load(open('data/processed/kb_clean.json')); print(f'{len(d)} clean KB items')"

# Check ChromaDB + SQLite
python -c "
import chromadb; client = chromadb.PersistentClient(path='data/chroma')
print(f'Vector store: {client.get_collection(\"tunisian_programs\").count()} items')
import sqlite3; conn = sqlite3.connect('data/sqlite/engine.db')
print(f'SQLite: {conn.execute(\"SELECT COUNT(*) FROM programs\").fetchone()[0]} programs')
"
```

## 📁 Project Structure

```
├── src/
│   ├── api/              # FastAPI endpoints
│   ├── engine/           # Adaptive diagnostic engine (Feature 1)
│   ├── scoring/          # Multi-dimensional scoring (Feature 2)
│   ├── rag/              # RAG resource orientation (Feature 3)
│   ├── models/           # Pydantic data models
│   │   ├── profile.py    # EntrepreneurProfile schema
│   │   ├── diagnostic.py # DiagnosticResult schema
│   │   ├── scoring.py    # ScoreResult schema
│   │   └── roadmap.py    # RoadmapAction schema
│   └── config.py         # Central configuration
├── scripts/              # One-shot setup scripts
│   ├── kb_validator_transformer.py   # KB validation pipeline
│   └── kb_ingestion_pipeline.py      # KB → ChromaDB + SQLite
├── data/
│   ├── raw/              # Raw data (kb_raw.json)
│   ├── processed/        # Validated KB + test profiles
│   ├── chroma/           # ChromaDB persistent storage
│   └── sqlite/           # SQLite database
├── tests/                # Unit tests
├── docs/                 # Documentation & feature specs
├── notebooks/            # Jupyter notebooks
├── frontend/             # Web frontend
├── README.md             # This file
├── requirements.txt      # Python dependencies
├── setup.py              # Package setup
├── .env.example          # Environment template
└── .gitignore            # Git ignore rules
```

## 🧪 Test Profiles

Three personas are available in `data/processed/test_profiles.json`:

| Persona | Sector | Self-Assessed | Expected |
|---------|--------|--------------|----------|
| **Amine** (tech, Tunis) | Tech | Fundraising | Structuration (overconfident) |
| **Fatima** (agri-food, Sfax) | Agri-food | Validation | Validation (accurate) |
| **Omar** (artisan, Kebili) | Artisanat | Ideation | Structuration (underestimating) |

## ✨ Features (Planned)

### Feature 1 — Adaptive Diagnostic Engine
- Dynamic branching questionnaire (3 paths: tech/agri-food/artisanat)
- 6-stage maturity classifier (Ideation → Growth)
- Perception-reality gap detection
- Prioritized blocker taxonomy

### Feature 2 — Multi-Dimensional Scoring
- 5 composite scores: Market, Commercial Offer, Innovation, Scalability, Green
- Weighted sub-criteria with documented thresholds
- Floor constraints (e.g., zero validation → Market capped at 40%)
- Anomaly detection (contradictory responses)
- Plain-language justifications

### Feature 3 — RAG Roadmap & Resources
- Semantic search over 49+ Tunisian programs via ChromaDB
- Gap-resource linkage (blocker → matching program)
- Timed action plan (immediate → long-term)
- French/Arabic language support

## 📊 Current Status

| Component | Status |
|-----------|--------|
| Directory structure | ✅ Created |
| KB validation (`scripts/kb_validator_transformer.py`) | ✅ 49 items validated |
| ChromaDB ingestion (`scripts/kb_ingestion_pipeline.py`) | ✅ 49 programs embedded |
| SQLite storage | ✅ 49 programs + 334 stage links + 316 blocker links |
| Pydantic models | ✅ 4 schemas (Profile, Diagnostic, Scoring, Roadmap) |
| Config | ✅ Centralized (`src/config.py`) |
| Test profiles | ✅ 3 personas (`data/processed/test_profiles.json`) |
| Dependencies | ✅ Installed |
| README | ✅ This file |

## 👥 Team

AINS Hackathon 2026 — Intelligent Entrepreneurial Orientation Engine
