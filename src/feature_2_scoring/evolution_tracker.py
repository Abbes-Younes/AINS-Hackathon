"""
Score Evolution Tracker for Feature 2: Explainable Multi-Dimensional Scoring
Tracks score history and calculates deltas over time
"""

import json
import logging
import sqlite3
from datetime import datetime
from typing import Dict, Any, List, Optional
from pathlib import Path

from src.models.profile import EntrepreneurProfile
from src.models.scoring import ScoreBreakdown, ScoreEvolution
from src.feature_2_scoring.scoring_engine import ScoringEngine

logger = logging.getLogger(__name__)


class ScoreEvolutionTracker:
    """Tracks score evolution over time and calculates deltas"""

    def __init__(self, db_path: str = "data/scoring_evolution.db"):
        """Initialize the evolution tracker with SQLite database"""
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_database()
        logger.info(f"Score evolution tracker initialized with database: {self.db_path}")

    def _init_database(self):
        """Initialize the SQLite database for score tracking"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS score_snapshots (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    project_id TEXT NOT NULL,
                    timestamp DATETIME NOT NULL,
                    market_score REAL,
                    commercial_offer_score REAL,
                    innovation_score REAL,
                    scalability_score REAL,
                    green_score REAL,
                    market_sub_criteria TEXT,  -- JSON
                    commercial_offer_sub_criteria TEXT,  -- JSON
                    innovation_sub_criteria TEXT,  -- JSON
                    scalability_sub_criteria TEXT,  -- JSON
                    green_sub_criteria TEXT,  -- JSON
                    overall_score REAL,
                    data_reliability TEXT
                )
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_project_timestamp
                ON score_snapshots(project_id, timestamp)
            """)
            conn.commit()

    def save_score_snapshot(
        self,
        project_id: str,
        profile: EntrepreneurProfile,
        score_breakdown: ScoreBreakdown
    ) -> None:
        """
        Save a score snapshot to the database

        Args:
            project_id: Unique identifier for the entrepreneur/project
            profile: EntrepreneurProfile used for scoring
            score_breakdown: ScoreBreakdown containing all scores
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT INTO score_snapshots (
                        project_id, timestamp, market_score, commercial_offer_score,
                        innovation_score, scalability_score, green_score,
                        market_sub_criteria, commercial_offer_sub_criteria,
                        innovation_sub_criteria, scalability_sub_criteria,
                        green_sub_criteria, overall_score, data_reliability
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    project_id,
                    datetime.now().isoformat(),
                    score_breakdown.market,
                    score_breakdown.commercial_offer,
                    score_breakdown.innovation,
                    score_breakdown.scalability,
                    score_breakdown.green,
                    json.dumps(score_breakdown.market_sub_criteria),
                    json.dumps(score_breakdown.commercial_offer_sub_criteria),
                    json.dumps(score_breakdown.innovation_sub_criteria),
                    json.dumps(score_breakdown.scalability_sub_criteria),
                    json.dumps(score_breakdown.green_sub_criteria),
                    score_breakdown.overall_score,
                    score_breakdown.data_reliability
                ))
                conn.commit()
            logger.debug(f"Saved score snapshot for project {project_id}")
        except Exception as e:
            logger.error(f"Error saving score snapshot: {e}")

    def get_score_evolution(
        self,
        project_id: str,
        limit: int = 10
    ) -> Optional[ScoreEvolution]:
        """
        Get score evolution for a project

        Args:
            project_id: Unique identifier for the entrepreneur/project
            limit: Maximum number of snapshots to retrieve

        Returns:
            ScoreEvolution object with deltas and trends, or None if insufficient data
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.execute("""
                    SELECT * FROM score_snapshots
                    WHERE project_id = ?
                    ORDER BY timestamp DESC
                    LIMIT ?
                """, (project_id, limit))

                rows = cursor.fetchall()

                if len(rows) < 2:
                    logger.warning(f"Insufficient data for evolution tracking: {len(rows)} snapshots for project {project_id}")
                    return None

                # Get current and previous snapshots
                current = dict(rows[0])
                previous = dict(rows[1])

                # Calculate deltas
                deltas = {
                    "market": current["market_score"] - previous["market_score"],
                    "commercial_offer": current["commercial_offer_score"] - previous["commercial_offer_score"],
                    "innovation": current["innovation_score"] - previous["innovation_score"],
                    "scalability": current["scalability_score"] - previous["scalability_score"],
                    "green": current["green_score"] - previous["green_score"],
                    "overall": current["overall_score"] - previous["overall_score"]
                }

                # Get changed sub-criteria (simplified - in practice would compare JSON)
                changed_sub_criteria = self._get_changed_sub_criteria(current, previous)

                # Generate trend indicators
                trend_indicators = {
                    k: "up" if v > 0.5 else "down" if v < -0.5 else "stable"
                    for k, v in deltas.items()
                }

                return ScoreEvolution(
                    project_id=project_id,
                    timestamp=current["timestamp"],
                    previous_timestamp=previous["timestamp"],
                    deltas=deltas,
                    changed_sub_criteria=changed_sub_criteria,
                    trend_indicators=trend_indicators
                )

        except Exception as e:
            logger.error(f"Error getting score evolution: {e}")
            return None

    def _get_changed_sub_criteria(
        self,
        current: Dict[str, Any],
        previous: Dict[str, Any]
    ) -> List[str]:
        """Identify which sub-criteria have changed significantly"""
        changed = []
        score_areas = ["market", "commercial_offer", "innovation", "scalability", "green"]

        for area in score_areas:
            current_key = f"{area}_sub_criteria"
            previous_key = f"{area}_sub_criteria"

            try:
                current_val = json.loads(current[current_key]) if current[current_key] else {}
                previous_val = json.loads(previous[previous_key]) if previous[previous_key] else {}

                # Check for significant changes (> 2 points difference)
                for criterion_id in set(current_val.keys()) | set(previous_val.keys()):
                    current_score = current_val.get(criterion_id, 0)
                    previous_score = previous_val.get(criterion_id, 0)

                    if abs(current_score - previous_score) > 2.0:
                        changed.append(f"{area}.{criterion_id}")

            except (json.JSONDecodeError, KeyError) as e:
                logger.warning(f"Error parsing sub-criteria for {area}: {e}")

        return changed

    def get_score_history(
        self,
        project_id: str,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Get full score history for a project

        Args:
            project_id: Unique identifier for the entrepreneur/project
            limit: Maximum number of records to retrieve

        Returns:
            List of score snapshots ordered by timestamp (oldest first)
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.execute("""
                    SELECT * FROM score_snapshots
                    WHERE project_id = ?
                    ORDER BY timestamp ASC
                    LIMIT ?
                """, (project_id, limit))

                rows = cursor.fetchall()
                return [dict(row) for row in rows]

        except Exception as e:
            logger.error(f"Error getting score history: {e}")
            return []

    def get_latest_score(
        self,
        project_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get the latest score snapshot for a project

        Args:
            project_id: Unique identifier for the entrepreneur/project

        Returns:
            Latest score snapshot or None if no data
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.execute("""
                    SELECT * FROM score_snapshots
                    WHERE project_id = ?
                    ORDER BY timestamp DESC
                    LIMIT 1
                """, (project_id,))

                row = cursor.fetchone()
                return dict(row) if row else None

        except Exception as e:
            logger.error(f"Error getting latest score: {e}")
            return None