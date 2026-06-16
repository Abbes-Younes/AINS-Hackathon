"""
Pydantic models for the RAG-grounded roadmap and resource orientation output.
"""

from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class Resource(BaseModel):
    """A program or resource from the knowledge base."""

    kb_id: str = Field(..., description="ID of the KB entry")
    title: str = Field(..., description="Title of the program")
    organization: str = Field("", description="Organization offering the program")
    program_type: str = Field("", description="Type: funding, incubation, training, mentoring, competition, etc.")
    eligibility: str = Field("", description="Eligibility criteria summary")
    url: str = Field("", description="Official URL for the program")
    relevance_score: float = Field(0.0, ge=0.0, le=1.0, description="Cosine similarity relevance score")
    relevance_reason: str = Field("", description="Why this resource matches the entrepreneur's profile")


class RoadmapAction(BaseModel):
    """A single action item in the entrepreneur's roadmap."""

    id: str = Field(..., description="Unique action identifier")
    time_horizon: str = Field(..., description="Time horizon: immediate, short_term, medium_term, long_term")
    action_text: str = Field(..., description="What the entrepreneur should do")
    rationale: str = Field("", description="Why this action is important")
    linked_blocker: Optional[str] = Field(None, description="Blocker from diagnostic that this action addresses")
    linked_dimension: Optional[str] = Field(None, description="Scoring dimension this action targets")
    linked_sub_criterion: Optional[str] = Field(None, description="Sub-criterion this action aims to improve")
    resources: List[Resource] = Field(default_factory=list, description="KB resources supporting this action")
    estimated_effort: str = Field("medium", description="Effort: low, medium, high")
    estimated_impact: str = Field("medium", description="Impact: low, medium, high")


class RoadmapMilestone(BaseModel):
    """A milestone grouping multiple actions."""

    title: str = Field(..., description="Milestone title")
    description: str = Field("", description="What this milestone represents")
    actions: List[RoadmapAction] = Field(default_factory=list, description="Actions grouped under this milestone")
    target_stage: str = Field("", description="The stage this milestone targets")


class ResourceOrientation(BaseModel):
    """Complete output from the RAG resource orientation engine."""

    # ── Retrieved Resources ──────────────────────────────────────────────────
    resources: List[Resource] = Field(default_factory=list, description="All recommended resources")
    resources_by_type: Dict[str, List[Resource]] = Field(
        default_factory=dict,
        description="Resources grouped by type (funding, incubation, training, etc.)"
    )
    total_resources_found: int = Field(0, description="Total number of distinct resources found")

    # ── Action Plan ──────────────────────────────────────────────────────────
    roadmap: List[RoadmapAction] = Field(default_factory=list, description="Ordered list of actions")
    milestones: List[RoadmapMilestone] = Field(default_factory=list, description="Milestones that group actions")
    estimated_timeline_months: int = Field(0, description="Estimated timeline for the full roadmap in months")

    # ── Gap-Resource Linkage ─────────────────────────────────────────────────
    blockers_addressed: List[str] = Field(
        default_factory=list,
        description="Blockers from diagnostic that have linked resources"
    )
    unaddressed_blockers: List[str] = Field(
        default_factory=list,
        description="Blockers with no linked resources yet"
    )

    # ── Summary ──────────────────────────────────────────────────────────────
    executive_summary: str = Field("", description="Natural language summary of the roadmap and resources")
    next_steps_summary: str = Field("", description="What to do immediately")
