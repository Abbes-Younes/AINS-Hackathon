"""
Pydantic models for the diagnostic engine output.
"""

from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class BlockerItem(BaseModel):
    """A single blocker identified during the diagnostic."""

    category: str = Field(..., description="Blocker category")
    description: str = Field(..., description="Human-readable description of the blocker")
    severity: str = Field("medium", description="Severity: critical, high, medium, low")
    evidence: str = Field("", description="Evidence from questionnaire responses")
    priority: int = Field(1, ge=1, le=10, description="Priority ranking (1=most critical)")


class StageGap(BaseModel):
    """Gap between self-assessed stage and system-assigned stage."""

    self_assessed: Optional[str] = Field(None, description="Stage the entrepreneur claimed")
    system_assigned: str = Field(..., description="Stage assigned by the diagnostic engine")
    gap_description: str = Field("", description="Explanation of the gap")
    gap_severity: str = Field("none", description="Severity: none, mild, moderate, severe")
    overestimation: bool = Field(False, description="If entrepreneur overestimated their stage")


class DiagnosticResult(BaseModel):
    """Complete output from the diagnostic engine."""

    # ── Classification ───────────────────────────────────────────────────────
    assigned_stage: str = Field(..., description="Stage assigned by the classifier")
    stage_confidence: float = Field(0.0, ge=0.0, le=1.0, description="Confidence in the assigned stage")
    stage_probabilities: Dict[str, float] = Field(
        default_factory=dict,
        description="Probability distribution across all stages"
    )

    # ── Evidence Trace ───────────────────────────────────────────────────────
    evidence_trace: List[str] = Field(
        default_factory=list,
        description="Evidence snippets that support the assigned stage"
    )
    key_factors: List[str] = Field(
        default_factory=list,
        description="Factors that most influenced the classification"
    )

    # ── Gaps & Blockers ──────────────────────────────────────────────────────
    perception_gap: Optional[StageGap] = Field(None, description="Perception-reality gap analysis")
    blockers: List[BlockerItem] = Field(default_factory=list, description="Prioritized list of blockers")
    blocker_summary: str = Field("", description="Natural language summary of main blockers")

    # ── Anomalies ────────────────────────────────────────────────────────────
    anomalies_detected: List[str] = Field(default_factory=list, description="Any contradictions or anomalies found")
    data_quality_score: float = Field(1.0, ge=0.0, le=1.0, description="Quality/consistency of provided data")

    # ── Metadata ─────────────────────────────────────────────────────────────
    questionnaire_version: str = Field("1.0.0", description="Version of the questionnaire used")
    questions_asked: int = Field(0, description="Number of questions asked during diagnostic")
