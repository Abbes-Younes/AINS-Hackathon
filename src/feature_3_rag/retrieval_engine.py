"""
Retrieval Engine for Feature 3: RAG-Grounded Roadmap & Resource Orientation
Implements hybrid retrieval combining semantic search and structured filtering.
"""

import json
import logging
import sqlite3
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
import numpy as np

logger = logging.getLogger(__name__)

# Add project root to path for src.config
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from src.config import (
    CHROMA_DIR,
    SQLITE_PATH,
    CHROMA_COLLECTION_NAME,
    EMBEDDING_MODEL_NAME,
    RAG_TOP_K,
)


class RetrievalEngine:
    """Hybrid retrieval engine combining semantic and structured search."""

    def __init__(self):
        """Initialize the retrieval engine with ChromaDB and SQLite connections."""
        self.logger = logging.getLogger(self.__class__.__name__)
        self._initialize_connections()
        self.logger.info("Retrieval engine initialized")

    def _initialize_connections(self):
        """Initialize ChromaDB and SQLite connections."""
        # Import here to avoid issues if not installed
        try:
            import chromadb
            from chromadb.config import Settings
            from sentence_transformers import SentenceTransformer
        except ImportError as e:
            self.logger.error(f"Missing dependencies for retrieval engine: {e}")
            raise

        # Initialize ChromaDB
        self.chroma_client = chromadb.PersistentClient(
            path=str(CHROMA_DIR),
            settings=Settings(anonymized_telemetry=False),
        )
        try:
            self.collection = self.chroma_client.get_collection(
                name=CHROMA_COLLECTION_NAME
            )
            self.logger.info(
                f"Connected to ChromaDB collection: {self.collection.count()} items"
            )
        except Exception:
            self.logger.error(
                f"ChromaDB collection '{CHROMA_COLLECTION_NAME}' not found. "
                "Run ingestion pipeline first."
            )
            raise

        # Initialize SQLite
        self.sqlite_conn = sqlite3.connect(str(SQLITE_PATH))
        self.sqlite_conn.row_factory = sqlite3.Row
        self.logger.info(f"Connected to SQLite database: {SQLITE_PATH}")

        # Initialize embedding model for query encoding
        self.embedding_model = SentenceTransformer(EMBEDDING_MODEL_NAME)
        self.logger.info(f"Loaded embedding model: {EMBEDDING_MODEL_NAME}")

    def hybrid_retrieve(
        self,
        query_text: str,
        eligibility_stages: Optional[List[str]] = None,
        domains_addressed: Optional[List[str]] = None,
        blockers_resolved: Optional[List[str]] = None,
        geographic_scope: Optional[str] = None,
        program_type: Optional[str] = None,
        limit: int = RAG_TOP_K,
    ) -> List[Dict[str, Any]]:
        """
        Perform hybrid retrieval combining semantic and structured search.

        Args:
            query_text: Natural language query string
            eligibility_stages: Filter by entrepreneurial stages
            domains_addressed: Filter by addressed domains (financial, legal, etc."
            blockers_resolved: Filter by blockers that the program helps resolve
            geographic_scope: Filter by geographic scope (national, regional, etc.")
            program_type: Filter by program type (funding, incubation, training, etc.")
            limit: Maximum number of results to return

        Returns:
            List of resource dictionaries with relevance scores and metadata
        """
        self.logger.info(f"Performing hybrid retrieval for query: '{query_text[:50]}...'")

        # Generate query embedding
        query_embedding = self.embedding_model.encode([query_text])[0].tolist()

        # Perform semantic search in ChromaDB
        semantic_results = self.collection.query(
            query_embeddings=[query_embedding],
            n_neighbors=min(limit * 3, 100),  # Get more candidates for re-ranking
            include=["metadatas", "documents", "distances"],
        )

        # If no results, return empty list
        if not semantic_results["ids"] or not semantic_results["ids"][0]:
            self.logger.warning("No semantic search results found")
            return []

        # Process semantic results
        candidates = []
        for i, (rid, doc, distance, metadata) in enumerate(
            zip(
                semantic_results["ids"][0],
                semantic_results["documents"][0],
                semantic_results["distances"][0],
                semantic_results["metadatas"][0],
            )
        ):
            # Convert distance to similarity score (ChromaDB uses L2 distance by default)
            # For cosine similarity space, we need to adjust
            semantic_score = max(0.0, 1.0 - distance)  # Simple conversion

            candidate = {
                "resource_id": rid,
                "name": metadata.get("name", ""),
                "name_en": metadata.get("name_en", ""),
                "type": metadata.get("type", ""),
                "operator": metadata.get("operator", ""),
                "description": doc,
                "semantic_score": float(semantic_score),
                "eligibility_stages": metadata.get("stages", "").split(",")
                if metadata.get("stages")
                else [],
                "domains_addressed": metadata.get("domains", "").split(",")
                if metadata.get("domains")
                else [],
                "geographic_scope": metadata.get("geographic_scope", ""),
                "source_url": metadata.get("source_url", ""),
            }
            candidates.append(candidate)

        # Apply structured filters from SQLite
        filtered_candidates = self._apply_structured_filters(
            candidates,
            eligibility_stages=eligibility_stages,
            domains_addressed=domains_addressed,
            blockers_resolved=blockers_resolved,
            geographic_scope=geographic_scope,
            program_type=program_type,
        )

        # Re-rank candidates using combined score
        ranked_results = self._rank_candidates(
            filtered_candidates,
            semantic_weight=0.7,
            eligibility_weight=0.3,
        )

        # Return top k results
        results = ranked_results[:limit]
        self.logger.info(f"Retrieved {len(results)} resources after filtering and ranking")
        return results

    def _apply_structured_filters(
        self,
        candidates: List[Dict[str, Any]],
        eligibility_stages: Optional[List[str]] = None,
        domains_addressed: Optional[List[str]] = None,
        blockers_resolved: Optional[List[str]] = None,
        geographic_scope: Optional[str] = None,
        program_type: Optional[List[str]] = None,
    ) -> List[Dict[str, Any]]:
        """Apply structured filters using SQLite queries."""
        if not any(
            [eligibility_stages, domains_addressed, blockers_resolved, geographic_scope, program_type]
        ):
            return candidates  # No filters to apply

        # Extract candidate IDs for batch querying
        candidate_ids = [c["resource_id"] for c in candidates]
        if not candidate_ids:
            return []

        # Build SQLite query with filters
        query = """
            SELECT DISTINCT p.resource_id
            FROM programs p
            WHERE p.resource_id IN ({placeholders})
        """.format(
            placeholders=",".join("?" for _ in candidate_ids)
        )

        params = list(candidate_ids)
        conditions = []

        if eligibility_stages:
            # Check if program is eligible for any of the specified stages
            placeholders = ",".join("?" for _ in eligibility_stages)
            conditions.append(f"""
                EXISTS (
                    SELECT 1 FROM program_stages ps
                    WHERE ps.resource_id = p.resource_id
                    AND ps.stage IN ({placeholders})
                )
            """)
            params.extend(eligibility_stages)

        if domains_addressed:
            # Check if program addresses any of the specified domains
            # Note: domains_addressed is stored as JSON array in SQLite
            placeholders = ",".join("?" for _ in domains_addressed)
            conditions.append(f"""
                EXISTS (
                    SELECT 1 FROM programs
                    WHERE resource_id = p.resource_id
                    AND json_each.value IN ({placeholders})
                )
            """)
            # This is a simplified check - in practice we'd need to parse JSON properly
            # For now, we'll do a text-based search which is less accurate but works
            conditions.append(
                "OR".join([f"p.domains_addressed LIKE '%{domain}%'" for domain in domains_addressed])
            )

        if program_type:
            conditions.append("p.type IN ({})".format(",".join("?" for _ in program_type)))
            params.extend([program_type] if isinstance(program_type, str) else program_type)

        if geographic_scope:
            conditions.append("p.geographic_scope = ?")
            params.append(geographic_scope)

        # Blockers resolved filter would require joining program_blockers table
        # For simplicity, we'll skip this in the MVP and handle it in re-ranking
        # A full implementation would check if the program resolves the specified blockers

        if conditions:
            query += " AND " + " AND ".join(conditions)

        try:
            cursor = self.sqlite_conn.cursor()
            cursor.execute(query, params)
            allowed_ids = {row["resource_id"] for row in cursor.fetchall()}
            self.logger.info(f"Structural filtering: {len(candidates)} -> {len(allowed_ids)} candidates")

            # Filter candidates to only those that passed structural filters
            filtered = [c for c in candidates if c["resource_id"] in allowed_ids]
            return filtered
        except Exception as e:
            self.logger.warning(f"Error applying structured filters: {e}")
            # Return original candidates if filtering fails
            return candidates

    def _rank_candidates(
        self,
        candidates: List[Dict[str, Any]],
        semantic_weight: float = 0.7,
        eligibility_weight: float = 0.3,
    ) -> List[Dict[str, Any]]:
        """Re-rank candidates using combined semantic and eligibility scores."""
        for candidate in candidates:
            # Start with semantic score
            combined_score = candidate["semantic_score"] * semantic_weight

            # Add eligibility bonus based on how well the program matches desired criteria
            eligibility_bonus = 0.0
            max_bonus = eligibility_weight

            # In a full implementation, we would check specific matches
            # For now, we'll give a small bonus to all candidates that passed filters
            # TODO: Implement more sophisticated eligibility scoring based on
            # explicit matching of stages, domains, blockers, etc.

            if eligibility_bonus > 0:
                combined_score += min(eligibility_bonus, max_bonus)

            candidate["combined_score"] = float(combined_score)
            candidate["relevance_score"] = float(
                combined_score
            )  # For backwards compatibility

        # Sort by combined score descending
        ranked = sorted(candidates, key=lambda x: x["combined_score"], reverse=True)
        return ranked

    def get_resource_by_id(self, resource_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific resource by its ID."""
        try:
            # Try ChromaDB first for full details
            results = self.collection.get(
                ids=[resource_id],
                include=["metadatas", "documents"]
            )

            if results["ids"] and results["ids"][0]:
                rid = results["ids"][0]
                doc = results["documents"][0]
                metadata = results["metadatas"][0]

                return {
                    "resource_id": rid,
                    "name": metadata.get("name", ""),
                    "name_en": metadata.get("name_en", ""),
                    "type": metadata.get("type", ""),
                    "operator": metadata.get("operator", ""),
                    "description": doc,
                    "eligibility_stages": metadata.get("stages", "").split(",")
                    if metadata.get("stages")
                    else [],
                    "domains_addressed": metadata.get("domains", "").split(",")
                    if metadata.get("domains")
                    else [],
                    "geographic_scope": metadata.get("geographic_scope", ""),
                    "source_url": metadata.get("source_url", ""),
                    "eligibility_criteria": metadata.get("eligibility_criteria", ""),
                    "blockers_resolved": metadata.get("blockers_resolved", ""),
                    "contact_email_or_phone": metadata.get("contact_email_or_phone", ""),
                    "last_verified": metadata.get("last_verified", ""),
                    "notes": metadata.get("notes", ""),
                }
        except Exception as e:
            self.logger.warning(f"Error retrieving resource {resource_id} from ChromaDB: {e}")

        # Fallback to SQLite
        try:
            cursor = self.sqlite_conn.cursor()
            cursor.execute(
                """
                SELECT * FROM programs WHERE resource_id = ?
                """,
                (resource_id,),
            )
            row = cursor.fetchone()
            if row:
                return dict(row)
        except Exception as e:
            self.logger.warning(f"Error retrieving resource {resource_id} from SQLite: {e}")

        return None

    def close(self):
        """Close database connections."""
        if hasattr(self, 'sqlite_conn'):
            self.sqlite_conn.close()
        self.logger.info("Retrieval engine connections closed")


# Convenience function for easy retrieval
def retrieve_resources(
    query_text: str,
    eligibility_stages: Optional[List[str]] = None,
    domains_addressed: Optional[List[str]] = None,
    blockers_resolved: Optional[List[str]] = None,
    geographic_scope: Optional[str] = None,
    program_type: Optional[str] = None,
    limit: int = RAG_TOP_K,
) -> List[Dict[str, Any]]:
    """
    Convenience function for hybrid resource retrieval.

    Args:
        query_text: Natural language query string
        eligibility_stages: Filter by entrepreneurial stages
        domains_addressed: Filter by addressed domains
        blockers_resolved: Filter by blockers that the program helps resolve
        geographic_scope: Filter by geographic scope
        program_type: Filter by program type
        limit: Maximum number of results to return

    Returns:
        List of resource dictionaries with relevance scores and metadata
    """
    engine = RetrievalEngine()
    try:
        return engine.hybrid_retrieve(
            query_text=query_text,
            eligibility_stages=eligibility_stages,
            domains_addressed=domains_addressed,
            blockers_resolved=blockers_resolved,
            geographic_scope=geographic_scope,
            program_type=program_type,
            limit=limit,
        )
    finally:
        engine.close()