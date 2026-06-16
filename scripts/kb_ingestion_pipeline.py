#!/usr/bin/env python3
"""
KB Ingestion Pipeline for AINS Hackathon 2026
----------------------------------------------
Loads kb_clean.json, generates embeddings, and populates:
  1. ChromaDB (vector store for semantic search)
  2. SQLite (relational store for structured queries)

Usage:
    python kb_ingestion_pipeline.py
"""

import json
import sqlite3
import sys
from pathlib import Path
from typing import Dict, List, Any

# Add project root to path for src.config (this script is in scripts/)
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.config import (
    KB_CLEAN_PATH,
    CHROMA_DIR,
    SQLITE_PATH,
    CHROMA_COLLECTION_NAME,
    EMBEDDING_MODEL_NAME,
    EMBEDDING_DIMENSION,
)


def load_clean_kb(path: Path) -> List[Dict[str, Any]]:
    """Load validated knowledge base items."""
    if not path.exists():
        print(f"[ERROR] Clean KB not found at {path}")
        print("       Run kb_validator_transformer.py first.")
        sys.exit(1)

    with open(path, "r", encoding="utf-8") as f:
        items = json.load(f)

    print(f"[DATA] Loaded {len(items)} clean KB items from {path}")
    return items


def init_embedding_model(model_name: str):
    """Initialize the sentence-transformers embedding model."""
    from sentence_transformers import SentenceTransformer

    print(f"[MODEL] Loading embedding model: {model_name} ...")
    model = SentenceTransformer(model_name)
    print(f"[MODEL] Model loaded. Dimension: {model.get_embedding_dimension()}")
    return model


def init_chromadb(persist_dir: Path, collection_name: str):
    """Initialize ChromaDB client and get/create the collection."""
    import chromadb
    from chromadb.config import Settings

    persist_dir.mkdir(parents=True, exist_ok=True)

    client = chromadb.PersistentClient(
        path=str(persist_dir),
        settings=Settings(anonymized_telemetry=False),
    )

    # Delete existing collection if it exists (for fresh ingestion)
    try:
        client.delete_collection(collection_name)
        print(f"[CHROMA] Deleted existing collection '{collection_name}'")
    except Exception:
        pass  # Collection doesn't exist yet

    collection = client.create_collection(
        name=collection_name,
        metadata={"hnsw:space": "cosine"},
    )
    print(f"[CHROMA] Created collection '{collection_name}' at {persist_dir}")
    return collection


def init_sqlite(db_path: Path) -> sqlite3.Connection:
    """Initialize SQLite database with the KB schema."""
    db_path.parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.executescript("""
        CREATE TABLE IF NOT EXISTS programs (
            resource_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            name_en TEXT,
            type TEXT NOT NULL,
            operator TEXT NOT NULL,
            description TEXT,
            eligibility_stages TEXT,
            eligibility_criteria TEXT,
            domains_addressed TEXT,
            blockers_resolved TEXT,
            geographic_scope TEXT,
            language TEXT,
            source_url TEXT,
            contact_email_or_phone TEXT,
            last_verified TEXT,
            notes TEXT,
            embedding_text TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS program_stages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            resource_id TEXT NOT NULL,
            stage TEXT NOT NULL,
            FOREIGN KEY (resource_id) REFERENCES programs(resource_id)
        );

        CREATE TABLE IF NOT EXISTS program_blockers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            resource_id TEXT NOT NULL,
            blocker TEXT NOT NULL,
            FOREIGN KEY (resource_id) REFERENCES programs(resource_id)
        );

        CREATE INDEX IF NOT EXISTS idx_program_stage ON program_stages(stage);
        CREATE INDEX IF NOT EXISTS idx_program_blocker ON program_blockers(blocker);
        CREATE INDEX IF NOT EXISTS idx_programs_type ON programs(type);
        CREATE INDEX IF NOT EXISTS idx_programs_operator ON programs(operator);
    """)

    conn.commit()
    print(f"[SQLITE] Database initialized at {db_path}")
    return conn


def ingest_to_chromadb(
    collection,
    items: List[Dict[str, Any]],
    model,
    batch_size: int = 16,
):
    """Generate embeddings and ingest items into ChromaDB in batches."""
    total = len(items)
    print(f"\n[CHROMA] Ingesting {total} items in batches of {batch_size}...")

    ids = []
    texts = []
    metadatas = []

    for item in items:
        rid = item.get("resource_id", f"item-{len(ids)}")
        embedding_text = item.get("embedding_text", item.get("description", ""))

        # Build metadata dict (exclude long text fields)
        metadata = {
            "name": item.get("name", ""),
            "name_en": item.get("name_en", ""),
            "type": item.get("type", ""),
            "operator": item.get("operator", ""),
            "stages": ",".join(item.get("eligibility_stages", [])),
            "domains": ",".join(item.get("domains_addressed", [])),
            "source_url": item.get("source_url", ""),
            "geographic_scope": item.get("geographic_scope", ""),
        }

        ids.append(rid)
        texts.append(embedding_text)
        metadatas.append(metadata)

    # Process in batches
    for i in range(0, total, batch_size):
        batch_ids = ids[i : i + batch_size]
        batch_texts = texts[i : i + batch_size]
        batch_metadatas = metadatas[i : i + batch_size]

        # Generate embeddings for the batch
        embeddings = model.encode(batch_texts, show_progress_bar=False).tolist()

        # Add to ChromaDB
        collection.add(
            ids=batch_ids,
            embeddings=embeddings,
            documents=batch_texts,
            metadatas=batch_metadatas,
        )

        progress = min(i + batch_size, total)
        print(f"   [{progress}/{total}] Ingested batch {(i // batch_size) + 1}")

    print(f"[CHROMA] Ingestion complete. Collection has {collection.count()} items.")


def ingest_to_sqlite(conn: sqlite3.Connection, items: List[Dict[str, Any]]):
    """Insert items into SQLite tables."""
    cursor = conn.cursor()
    total = len(items)

    print(f"\n[SQLITE] Inserting {total} items...")

    for idx, item in enumerate(items):
        rid = item.get("resource_id", "")

        # Insert into programs table
        cursor.execute(
            """
            INSERT OR REPLACE INTO programs (
                resource_id, name, name_en, type, operator, description,
                eligibility_stages, eligibility_criteria, domains_addressed,
                blockers_resolved, geographic_scope, language, source_url,
                contact_email_or_phone, last_verified, notes, embedding_text
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                rid,
                item.get("name", ""),
                item.get("name_en", ""),
                item.get("type", ""),
                item.get("operator", ""),
                item.get("description", ""),
                json.dumps(item.get("eligibility_stages", []), ensure_ascii=False),
                json.dumps(item.get("eligibility_criteria", []), ensure_ascii=False),
                json.dumps(item.get("domains_addressed", []), ensure_ascii=False),
                json.dumps(item.get("blockers_resolved", []), ensure_ascii=False),
                item.get("geographic_scope", ""),
                item.get("language", ""),
                item.get("source_url", ""),
                item.get("contact_email_or_phone", ""),
                item.get("last_verified", ""),
                item.get("notes", ""),
                item.get("embedding_text", ""),
            ),
        )

        # Insert stages
        for stage in item.get("eligibility_stages", []):
            cursor.execute(
                "INSERT OR IGNORE INTO program_stages (resource_id, stage) VALUES (?, ?)",
                (rid, stage),
            )

        # Insert blockers
        for blocker in item.get("blockers_resolved", []):
            cursor.execute(
                "INSERT OR IGNORE INTO program_blockers (resource_id, blocker) VALUES (?, ?)",
                (rid, blocker),
            )

        if (idx + 1) % 20 == 0 or (idx + 1) == total:
            print(f"   [{idx + 1}/{total}] Inserted into SQLite")

    conn.commit()
    print(f"[SQLITE] Insertion complete.")

    # Verify
    cursor.execute("SELECT COUNT(*) as cnt FROM programs")
    count = cursor.fetchone()["cnt"]
    cursor.execute("SELECT COUNT(*) as cnt FROM program_stages")
    stages_count = cursor.fetchone()["cnt"]
    cursor.execute("SELECT COUNT(*) as cnt FROM program_blockers")
    blockers_count = cursor.fetchone()["cnt"]
    print(f"[SQLITE] Verification: {count} programs, {stages_count} stage links, {blockers_count} blocker links")


def main():
    print("=" * 60)
    print("KB Ingestion Pipeline — AINS Hackathon 2026")
    print("=" * 60)

    # 1. Load clean KB
    items = load_clean_kb(KB_CLEAN_PATH)

    # 2. Initialize embedding model
    model = init_embedding_model(EMBEDDING_MODEL_NAME)

    # 3. Initialize ChromaDB
    collection = init_chromadb(CHROMA_DIR, CHROMA_COLLECTION_NAME)

    # 4. Initialize SQLite
    conn = init_sqlite(SQLITE_PATH)

    # 5. Ingest to ChromaDB
    ingest_to_chromadb(collection, items, model)

    # 6. Ingest to SQLite
    ingest_to_sqlite(conn, items)

    # 7. Cleanup
    conn.close()
    print(f"\n[OK] Ingestion pipeline complete!")
    print(f"    - ChromaDB: {CHROMA_DIR}")
    print(f"    - SQLite:   {SQLITE_PATH}")
    print(f"    - Items:    {len(items)}")


if __name__ == "__main__":
    main()
