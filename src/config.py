"""
Central configuration for the Intelligent Entrepreneurial Orientation Engine.
All paths, model names, thresholds, and constants are defined here.
"""

import os
from pathlib import Path
from typing import Dict, List, Tuple

# ── Project Root ──────────────────────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# ── Data Paths ────────────────────────────────────────────────────────────────
DATA_DIR = PROJECT_ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"
CHROMA_DIR = DATA_DIR / "chroma"
SQLITE_DIR = DATA_DIR / "sqlite"
SQLITE_PATH = SQLITE_DIR / "engine.db"

# KB file paths
KB_RAW_PATH = RAW_DIR / "kb_raw.json"
KB_CLEAN_PATH = PROCESSED_DIR / "kb_clean.json"
KB_FLAGGED_PATH = PROCESSED_DIR / "kb_flagged.json"
KB_SUMMARY_PATH = PROCESSED_DIR / "kb_summary.csv"

# Test profiles
TEST_PROFILES_PATH = PROCESSED_DIR / "test_profiles.json"

# ── Embedding Model ──────────────────────────────────────────────────────────
# Multilingual model supporting French, Arabic, and English
EMBEDDING_MODEL_NAME = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
EMBEDDING_DIMENSION = 384

# ── ChromaDB Settings ────────────────────────────────────────────────────────
CHROMA_COLLECTION_NAME = "tunisian_programs"
CHROMA_N_RESULTS = 5  # Default number of results to retrieve

# ── Stage Taxonomy ───────────────────────────────────────────────────────────
STAGES: List[str] = [
    "ideation",
    "validation",
    "structuration",
    "fundraising",
    "launch_planning",
    "growth",
]

STAGE_LABELS: Dict[str, str] = {
    "ideation": "Idéation",
    "validation": "Validation",
    "structuration": "Structuration",
    "fundraising": "Levée de fonds",
    "launch_planning": "Plan de lancement",
    "growth": "Croissance",
}

STAGE_LABELS_EN: Dict[str, str] = {
    "ideation": "Ideation",
    "validation": "Validation",
    "structuration": "Structuration",
    "fundraising": "Fundraising",
    "launch_planning": "Launch Planning",
    "growth": "Growth",
}

# Stage transition thresholds (0.0 – 1.0)
# Minimum confidence required to assign a stage
STAGE_CONFIDENCE_THRESHOLD = 0.35

# ── Scoring Configuration ────────────────────────────────────────────────────
SCORE_DIMENSIONS: List[str] = [
    "market",
    "commercial_offer",
    "innovation",
    "scalability",
    "green",
]

SCORE_DIMENSION_LABELS: Dict[str, str] = {
    "market": "Marché",
    "commercial_offer": "Offre Commerciale",
    "innovation": "Innovation",
    "scalability": "Scalabilité",
    "green": "Green / Impact Environnemental",
}

# Floor constraints: if a critical criterion is 0, cap the dimension score
FLOOR_CONSTRAINTS: Dict[str, Tuple[str, float]] = {
    "market": ("validation_client", 0.4),
    "commercial_offer": ("business_model_clarity", 0.4),
}

# ── Diagnostic Engine Settings ───────────────────────────────────────────────
QUESTIONNAIRE_VERSION = "1.0.0"
MAX_QUESTIONS = 25  # Maximum questions before branching ends
MIN_QUESTIONS = 8  # Minimum questions before classifying

# ── RAG / Roadmap Settings ───────────────────────────────────────────────────
RAG_TOP_K = 3  # Number of KB resources to retrieve per gap
ROADMAP_TIME_HORIZONS: List[str] = ["immediate", "short_term", "medium_term", "long_term"]
ROADMAP_MAX_ACTIONS = 12

# ── Anomaly Detection Settings ───────────────────────────────────────────────
ANOMALY_CONTRADICTION_THRESHOLD = 0.7  # High similarity between contradictory answers

# ── Supported Languages ──────────────────────────────────────────────────────
SUPPORTED_LANGUAGES: List[str] = ["fr", "en", "ar"]
DEFAULT_LANGUAGE = "fr"
