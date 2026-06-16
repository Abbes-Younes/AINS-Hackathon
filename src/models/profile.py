"""
Pydantic model for the entrepreneur's profile.
Captures all inputs needed for diagnostic, scoring, and roadmap generation.
"""

from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class EntrepreneurProfile(BaseModel):
    """Profile of the entrepreneur, built from the adaptive questionnaire."""

    # ── Identity ─────────────────────────────────────────────────────────────
    entrepreneur_name: Optional[str] = Field(None, description="Entrepreneur's name (optional)")
    language: str = Field("fr", description="Preferred language: fr, en, ar")

    # ── Project Info ─────────────────────────────────────────────────────────
    project_name: Optional[str] = Field(None, description="Project/business name")
    sector: Optional[str] = Field(None, description="Sector: tech, agri-food, artisanat, services, social, other")
    sector_other: Optional[str] = Field(None, description="If sector=other, specify")
    project_description: Optional[str] = Field(None, description="Brief description of the project")

    # ── Maturity Indicators ──────────────────────────────────────────────────
    has_idea: bool = Field(False, description="Has a clear business idea")
    has_validation_interviews: bool = Field(False, description="Conducted customer discovery interviews")
    has_mvp: bool = Field(False, description="Has a minimum viable product / prototype")
    has_business_model: bool = Field(False, description="Has a documented business model canvas or lean canvas")
    business_model_clarity: int = Field(0, ge=0, le=10, description="Self-assessed clarity of business model (0–10)")
    has_legal_form: bool = Field(False, description="Has registered a legal entity (e.g., SARL, SRS)")
    legal_form_type: Optional[str] = Field(None, description="Type of legal structure")

    # ── Team & Revenue ──────────────────────────────────────────────────────
    team_size: int = Field(0, ge=0, description="Number of team members")
    has_full_time_team: bool = Field(False, description="Has at least one full-time co-founder")
    monthly_revenue: float = Field(0.0, ge=0.0, description="Monthly revenue in TND")
    has_paying_customers: bool = Field(False, description="Has at least one paying customer")
    customer_count: int = Field(0, ge=0, description="Approximate number of customers")

    # ── Validation ──────────────────────────────────────────────────────────
    validation_client: int = Field(0, ge=0, le=10, description="Level of customer validation (0–10)")
    validation_surveys: bool = Field(False, description="Has conducted surveys or polls")
    validation_expert: bool = Field(False, description="Has sought expert / mentor validation")
    has_pilot: bool = Field(False, description="Has a pilot project or beta test")
    has_traction: bool = Field(False, description="Has evidence of traction (waiting list, LOIs, pre-orders)")

    # ── Fundraising & Investment ──────────────────────────────────────────
    has_fundraising_experience: bool = Field(False, description="Previous fundraising experience")
    has_investors: bool = Field(False, description="Already has investors")
    amount_raised_tnd: float = Field(0.0, ge=0.0, description="Total funds raised in TND")
    is_seeking_funding: bool = Field(False, description="Currently seeking funding")
    funding_target_tnd: float = Field(0.0, ge=0.0, description="Funding target in TND")

    # ── Geography & Ecosystem ───────────────────────────────────────────────
    location: Optional[str] = Field(None, description="Governorate / region in Tunisia")
    is_tunisia_based: bool = Field(True, description="Whether the entrepreneur is based in Tunisia")
    is_urban: bool = Field(True, description="Whether the entrepreneur is in an urban area")

    # ── Accompaniment History ───────────────────────────────────────────────
    has_incubation: bool = Field(False, description="Has been in an incubator/accelerator")
    has_state_aid: bool = Field(False, description="Has received state aid (APII, BFPME, etc.)")
    has_previous_program: bool = Field(False, description="Has participated in an entrepreneurship program")
    previous_programs: List[str] = Field(default_factory=list, description="Previous programs participated in")

    # ── Self-Assessment ─────────────────────────────────────────────────────
    self_assessed_stage: Optional[str] = Field(
        None,
        description="Stage the entrepreneur believes they are at: ideation, validation, structuration, fundraising, launch_planning, growth"
    )
    self_assessed_readiness: int = Field(5, ge=0, le=10, description="Self-assessed readiness score (0–10)")
    biggest_challenges: List[str] = Field(default_factory=list, description="Top challenges as perceived by entrepreneur")

    # ── Innovation & Green ──────────────────────────────────────────────────
    has_ip: bool = Field(False, description="Has intellectual property (patent, trademark)")
    has_rd: bool = Field(False, description="Has formal R&D activities")
    tech_readiness_level: int = Field(0, ge=0, le=9, description="TRL score (0–9)")
    has_sustainability_plan: bool = Field(False, description="Has an environmental sustainability plan")
    has_social_impact: bool = Field(False, description="Has measurable social impact")

    # ── Digital Maturity ────────────────────────────────────────────────────
    has_website: bool = Field(False, description="Has a website or landing page")
    has_social_media: bool = Field(False, description="Has active social media presence")
    uses_digital_tools: bool = Field(False, description="Uses digital tools for operations")
