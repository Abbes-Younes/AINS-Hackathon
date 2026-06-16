"""
Pydantic models for the multi-dimensional scoring engine output.
"""

from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class SubCriterion(BaseModel):
    """A single sub-criterion within a composite score."""

    name: str = Field(..., description="Unique identifier for the sub-criterion")
    label: str = Field("", description="Human-readable label")
    value: float = Field(0.0, ge=0.0, le=1.0, description="Normalized score (0.0–1.0)")
    weight: float = Field(0.0, ge=0.0, le=1.0, description="Weight within the composite score")
    evidence: str = Field("", description="Evidence from the profile supporting this score")
    improvement_suggestion: str = Field("", description="How to improve this sub-criterion")


class CompositeScore(BaseModel):
    """A single composite score (one of the 5 dimensions)."""

    dimension: str = Field(..., description="Dimension key: market, commercial_offer, innovation, scalability, green")
    label: str = Field(..., description="Human-readable label for the dimension")
    overall_score: float = Field(0.0, ge=0.0, le=1.0, description="Composite score (0.0–1.0)")
    percentage: float = Field(0.0, ge=0.0, le=100.0, description="Score as percentage (0–100)")
    sub_criteria: List[SubCriterion] = Field(default_factory=list, description="Sub-criteria that compose this score")
    justification: str = Field("", description="Plain-language explanation of why this score was assigned")
    floor_applied: bool = Field(False, description="Whether a floor constraint limited this score")
    floor_reason: Optional[str] = Field(None, description="Reason if a floor constraint was applied")


class Anomaly(BaseModel):
    """An anomaly or contradiction detected in the responses."""

    description: str = Field(..., description="What was detected")
    criteria_pair: List[str] = Field(default_factory=list, description="The two criteria that conflict")
    severity: str = Field("low", description="Severity: low, medium, high")


class ScoreResult(BaseModel):
    """Complete output from the scoring engine."""

    # ── Composite Scores ─────────────────────────────────────────────────────
    composites: Dict[str, CompositeScore] = Field(
        default_factory=dict,
        description="5 composite scores keyed by dimension"
    )
    overall_score: float = Field(0.0, ge=0.0, le=1.0, description="Overall weighted score across all dimensions")
    overall_percentage: float = Field(0.0, ge=0.0, le=100.0, description="Overall score as percentage")

    # ── Anomaly Detection ────────────────────────────────────────────────────
    anomalies: List[Anomaly] = Field(default_factory=list, description="Contradictions or anomalies detected")
    data_reliability: float = Field(1.0, ge=0.0, le=1.0, description="Reliability of the score based on data quality")

    # ── Summary ──────────────────────────────────────────────────────────────
    strongest_dimension: Optional[str] = Field(None, description="Dimension with the highest score")
    weakest_dimension: Optional[str] = Field(None, description="Dimension with the lowest score")
    priorities: List[str] = Field(default_factory=list, description="Recommended improvement priorities")
    executive_summary: str = Field("", description="One-paragraph summary of the scoring results")
