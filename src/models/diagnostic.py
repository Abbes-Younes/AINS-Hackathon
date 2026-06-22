"""
Diagnostic Result Data Models
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any


class PerceptionGap(BaseModel):
    """Perception-reality gap between self-assessed and system-assessed stage"""
    gap_type: str = Field(..., description="Type of gap: OVER_ESTIMATION, UNDER_ESTIMATION, ACCURATE")
    claimed_stage: str = Field(..., description="Stage self-assessed by entrepreneur")
    actual_stage: str = Field(..., description="Stage assigned by system")
    gap_severity: str = Field(..., description="Severity of gap: NONE, MILD, MODERATE, SEVERE")
    explanation: str = Field(..., description="Human-readable explanation of the gap")


class Blocker(BaseModel):
    """Identified blocker to entrepreneurial progress"""
    name: str = Field(..., description="Blocker name/identifier")
    description: str = Field(..., description="General description of the blocker")
    domain: str = Field(..., description="Domain: financial, legal, market, technical, organisational, etc.")
    priority: str = Field(..., description="Priority level: high, medium, low")
    affected_stages: List[str] = Field(default_factory=list, description="Stages this blocker affects")
    explanation: str = Field(..., description="Personalized explanation of how this blocker applies")


class DiagnosticResult(BaseModel):
    """Complete diagnostic assessment result"""
    assigned_stage: str = Field(..., description="Assigned maturity stage")
    confidence_score: float = Field(..., ge=0.0, le=1.0, description="Confidence in classification (0.0-1.0)")
    perception_gap: Optional[PerceptionGap] = Field(None, description="Perception-reality gap if present")
    key_blockers: List[Blocker] = Field(default_factory=list, description="Top priority blockers")
    evidence_trace: List[str] = Field(default_factory=list, description="Data points that influenced classification")
    plain_language_summary: str = Field(..., description="Human-readable summary of diagnostic findings")