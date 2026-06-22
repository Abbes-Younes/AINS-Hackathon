"""
Maturity Stage Classifier
Implements rule-based classification of entrepreneur projects into 6 maturity stages
"""

from typing import Dict, Any, List, Tuple, Optional
from dataclasses import dataclass
import logging

from src.models.profile import EntrepreneurProfile

logger = logging.getLogger(__name__)


@dataclass
class ClassificationResult:
    """Result of maturity stage classification"""
    assigned_stage: str
    confidence_score: float  # 0.0 to 1.0
    evidence_trace: List[str]  # List of data points that influenced the decision
    alternative_stages: Optional[List[Tuple[str, float]]] = None  # (stage, confidence) pairs


class MaturityClassifier:
    """Rule-based classifier for entrepreneurial maturity stages"""

    def __init__(self):
        """Initialize the classifier with stage definitions and rules"""
        self.stages = [
            "ideation",
            "market_validation",
            "structuration",
            "fundraising",
            "launch_planning",
            "growth"
        ]

        # Define classification rules for each stage
        # Each rule is a tuple: (condition_function, weight, evidence_description)
        self.stage_rules = {
            "ideation": [
                (self._has_idea_only, 0.3, "Idea exists but no validation or team"),
                (self._no_validation_no_team, 0.25, "No validation efforts, no team formed"),
                (self._no_mvp_no_revenue, 0.2, "No MVP, no revenue generation"),
                (self._self_assessed_ideation, 0.15, "Self-assessed at ideation stage"),
                (self._early_stage_indicators, 0.1, "Early stage indicators present")
            ],
            "market_validation": [
                (self._has_validation_interviews, 0.25, "Conducted customer validation interviews"),
                (self._has_mvp_no_revenue, 0.2, "Has MVP but no revenue yet"),
                (self._market_research_conducted, 0.15, "Performed market research"),
                (self._has_surveys_or_pilots, 0.15, "Has validation surveys or pilot tests"),
                (self._self_assessed_validation, 0.15, "Self-assessed at validation stage"),
                (self._no_revenue_yet, 0.1, "No revenue generation yet")
            ],
            "structuration": [
                (self._has_legal_form, 0.2, "Has established legal form"),
                (self._has_business_model_clarity, 0.2, "Clear and documented business model"),
                (self._has_team_structure, 0.15, "Has team structure (co-founders or small team)"),
                (self._has_mvp_with_validation, 0.15, "Has MVP with some validation evidence"),
                (self._self_assessed_structuration, 0.1, "Self-assessed at structuration stage"),
                (self._has_some_revenue, 0.1, "Some revenue generation but not primary focus"),
                (self._has_incubation_support, 0.1, "Received incubation or acceleration support")
            ],
            "fundraising": [
                (self._has_paying_customers, 0.2, "Has paying customers generating revenue"),
                (self._has_clear_business_model, 0.15, "Clear, validated business model"),
                (self._seeking_external_funding, 0.15, "Actively seeking external funding"),
                (self._has_pitch_prepared, 0.1, "Pitch deck and fundraising materials prepared"),
                (self._self_assessed_fundraising, 0.1, "Self-assessed at fundraising stage"),
                (self._has_validation_evidence, 0.1, "Strong validation evidence (pilots, LOIs, etc.)"),
                (self._has_incubation_or_accelerator, 0.1, "Participated in incubator/accelerator program")
            ],
            "launch_planning": [
                (self._has_validated_business_model, 0.2, "Business model validated with customers"),
                (self._has_revenue_traction, 0.15, "Showing revenue traction and growth"),
                (self._has_go_to_market_strategy, 0.15, "Has defined go-to-market strategy"),
                (self._has_operational_readiness, 0.1, "Operationally ready for scaling"),
                (self._self_assessed_launch_planning, 0.1, "Self-assessed at launch planning stage"),
                (self._has_built_sales_process, 0.1, "Has established sales and customer acquisition process"),
                (self._has_marketing_plan, 0.1, "Has marketing and promotion plan")
            ],
            "growth": [
                (self._has_consistent_revenue, 0.25, "Consistent, growing revenue stream"),
                (self._has_profitable_operations, 0.2, "Profitable operations or clear path to profitability"),
                (self._has_scalable_operations, 0.15, "Operations show scalability potential"),
                (self._has_market_expansion_plans, 0.1, "Plans for market expansion or geographic growth"),
                (self._self_assessed_growth, 0.1, "Self-assessed at growth stage"),
                (self._has_team_scaling, 0.1, "Team is scaling to meet demand"),
                (self._has_formal_processes, 0.1, "Has formal business processes and procedures")
            ]
        }

    def classify(self, profile: EntrepreneurProfile) -> ClassificationResult:
        """
        Classify entrepreneur profile into a maturity stage

        Args:
            profile: EntrepreneurProfile to classify

        Returns:
            ClassificationResult with stage, confidence, and evidence trace
        """
        logger.info(f"Classifying profile for project: {profile.project_name}")

        # Score each stage
        stage_scores = {}
        all_evidence = {}

        for stage in self.stages:
            score, evidence = self._score_stage(profile, stage)
            stage_scores[stage] = score
            all_evidence[stage] = evidence

        # Find the stage with highest score
        if not stage_scores:
            # Fallback to ideation if no scores
            return ClassificationResult(
                assigned_stage="ideation",
                confidence_score=0.5,
                evidence_trace=["Insufficient data for classification, defaulting to ideation"],
                alternative_stages=[]
            )

        # Get top stage
        sorted_stages = sorted(stage_scores.items(), key=lambda x: x[1], reverse=True)
        top_stage, top_score = sorted_stages[0]

        # Get alternative stages (within 20% of top score)
        alternative_stages = []
        for stage, score in sorted_stages[1:]:
            if score >= top_score * 0.8:  # Within 80% of top score
                alternative_stages.append((stage, score))

        # Normalize confidence score (0-1 range)
        confidence = min(top_score, 1.0)

        # Get evidence trace for the top stage
        evidence_trace = all_evidence.get(top_stage, [])

        logger.info(f"Classification result: {top_stage} (confidence: {confidence:.2f})")
        logger.debug(f"Evidence: {evidence_trace}")

        return ClassificationResult(
            assigned_stage=top_stage,
            confidence_score=confidence,
            evidence_trace=evidence_trace,
            alternative_stages=alternative_stages if alternative_stages else None
        )

    def _score_stage(self, profile: EntrepreneurProfile, stage: str) -> Tuple[float, List[str]]:
        """
        Score how well a profile matches a specific stage

        Args:
            profile: EntrepreneurProfile to score
            stage: Stage to score against

        Returns:
            Tuple of (score, evidence_list)
        """
        if stage not in self.stage_rules:
            return 0.0, []

        total_score = 0.0
        evidence = []

        # Apply each rule for this stage
        for rule_func, weight, evidence_desc in self.stage_rules[stage]:
            try:
                if rule_func(profile):
                    total_score += weight
                    evidence.append(evidence_desc)
            except Exception as e:
                logger.warning(f"Error applying rule {evidence_desc}: {e}")

        return total_score, evidence

    # Rule implementation methods for Ideation stage
    def _has_idea_only(self, profile: EntrepreneurProfile) -> bool:
        """Check if profile shows only an idea with no validation"""
        return (profile.has_idea == True and
                profile.has_validation_interviews == False and
                profile.has_mvp == False and
                profile.team_size == 0)

    def _no_validation_no_team(self, profile: EntrepreneurProfile) -> bool:
        """Check for no validation efforts and no team"""
        return (profile.has_validation_interviews == False and
                profile.has_mvp == False and
                profile.team_size <= 1)

    def _no_mvp_no_revenue(self, profile: EntrepreneurProfile) -> bool:
        """Check for no MVP and no revenue"""
        return (profile.has_mvp == False and
                profile.monthly_revenue == 0)

    def _self_assessed_ideation(self, profile: EntrepreneurProfile) -> bool:
        """Check if self-assessed as ideation"""
        return getattr(profile, 'self_assessed_stage', '') == 'ideation'

    def _early_stage_indicators(self, profile: EntrepreneurProfile) -> bool:
        """Check for general early stage indicators"""
        return (profile.has_idea == True and
                profile.monthly_revenue == 0 and
                profile.team_size <= 2)

    # Rule implementation methods for Market Validation stage
    def _has_validation_interviews(self, profile: EntrepreneurProfile) -> bool:
        """Check for validation interviews"""
        return profile.has_validation_interviews == True

    def _has_mvp_no_revenue(self, profile: EntrepreneurProfile) -> bool:
        """Check for MVP but no revenue (reused)"""
        return (profile.has_mvp == True and
                profile.monthly_revenue == 0)

    def _market_research_conducted(self, profile: EntrepreneurProfile) -> bool:
        """Check if market research was conducted"""
        # This would come from our intake questions
        return hasattr(profile, 'market_research_conducted') and profile.market_research_conducted == True

    def _has_surveys_or_pilots(self, profile: EntrepreneurProfile) -> bool:
        """Check for validation surveys or pilot tests"""
        return (profile.has_pilot == True or
                getattr(profile, 'validation_surveys_conducted', False) == True)

    def _self_assessed_validation(self, profile: EntrepreneurProfile) -> bool:
        """Check if self-assessed as validation"""
        return getattr(profile, 'self_assessed_stage', '') == 'validation'

    def _no_revenue_yet(self, profile: EntrepreneurProfile) -> bool:
        """Check for no revenue yet"""
        return profile.monthly_revenue == 0

    # Rule implementation methods for Structuration stage
    def _has_legal_form(self, profile: EntrepreneurProfile) -> bool:
        """Check for established legal form"""
        return profile.has_legal_form == True

    def _has_business_model_clarity(self, profile: EntrepreneurProfile) -> bool:
        """Check for clear business model"""
        # business_model_clarity is stored as 0-6 scale
        return getattr(profile, 'business_model_clarity', 0) >= 4

    def _has_team_structure(self, profile: EntrepreneurProfile) -> bool:
        """Check for team structure"""
        return profile.team_size >= 2

    def _has_mvp_with_validation(self, profile: EntrepreneurProfile) -> bool:
        """Check for MVP with validation evidence"""
        return (profile.has_mvp == True and
                (profile.has_validation_interviews == True or
                 profile.has_pilot == True))

    def _self_assessed_structuration(self, profile: EntrepreneurProfile) -> bool:
        """Check if self-assessed as structuration"""
        return getattr(profile, 'self_assessed_stage', '') == 'structuration'

    def _has_some_revenue(self, profile: EntrepreneurProfile) -> bool:
        """Check for some revenue generation"""
        return 0 < profile.monthly_revenue < 1000  # Arbitrary threshold

    def _has_incubation_support(self, profile: EntrepreneurProfile) -> bool:
        """Check for incubation/acceleration support"""
        return profile.has_incubation == True

    # Rule implementation methods for Fundraising stage
    def _has_paying_customers(self, profile: EntrepreneurProfile) -> bool:
        """Check for paying customers"""
        return profile.has_paying_customers == True

    def _has_clear_business_model(self, profile: EntrepreneurProfile) -> bool:
        """Check for clear, validated business model"""
        return getattr(profile, 'business_model_clarity', 0) >= 5

    def _seeking_external_funding(self, profile: EntrepreneurProfile) -> bool:
        """Check for actively seeking external funding"""
        return profile.is_seeking_funding == True

    def _has_pitch_prepared(self, profile: EntrepreneurProfile) -> bool:
        """Check for pitch preparation"""
        # This would be inferred from activities
        return (profile.has_fundraising_experience == True or
                getattr(profile, 'pitch_deck_prepared', False) == True)

    def _self_assessed_fundraising(self, profile: EntrepreneurProfile) -> bool:
        """Check if self-assessed as fundraising"""
        return getattr(profile, 'self_assessed_stage', '') == 'fundraising'

    def _has_validation_evidence(self, profile: EntrepreneurProfile) -> bool:
        """Check for strong validation evidence"""
        return (profile.has_pilot == True or
                profile.validation_client_count >= 5 or
                getattr(profile, 'signed_lois', 0) > 0)

    def _has_incubation_or_accelerator(self, profile: EntrepreneurProfile) -> bool:
        """Check for incubator/accelerator participation"""
        return (profile.has_incubation == True or
                getattr(profile, 'has_accelerator_participation', False) == True)

    # Rule implementation methods for Launch Planning stage
    def _has_validated_business_model(self, profile: EntrepreneurProfile) -> bool:
        """Check for validated business model"""
        return getattr(profile, 'business_model_clarity', 0) >= 5

    def _has_revenue_traction(self, profile: EntrepreneurProfile) -> bool:
        """Check for revenue traction"""
        return profile.monthly_revenue >= 1000  # Arbitrary threshold for traction

    def _has_go_to_market_strategy(self, profile: EntrepreneurProfile) -> bool:
        """Check for go-to-market strategy"""
        return getattr(profile, 'has_go_to_market_strategy', False) == True

    def _has_operational_readiness(self, profile: EntrepreneurProfile) -> bool:
        """Check for operational readiness"""
        return (profile.team_size >= 3 and
                profile.has_legal_form == True and
                getattr(profile, 'has_standard_operating_procedures', False) == True)

    def _self_assessed_launch_planning(self, profile: EntrepreneurProfile) -> bool:
        """Check if self-assessed as launch planning"""
        return getattr(profile, 'self_assessed_stage', '') == 'launch_planning'

    def _has_built_sales_process(self, profile: EntrepreneurProfile) -> bool:
        """Check for established sales process"""
        return getattr(profile, 'has_sales_process', False) == True

    def _has_marketing_plan(self, profile: EntrepreneurProfile) -> bool:
        """Check for marketing plan"""
        return getattr(profile, 'has_marketing_plan', False) == True

    # Rule implementation methods for Growth stage
    def _has_consistent_revenue(self, profile: EntrepreneurProfile) -> bool:
        """Check for consistent revenue"""
        return profile.monthly_revenue >= 2000  # Higher threshold for consistent

    def _has_profitable_operations(self, profile: EntrepreneurProfile) -> bool:
        """Check for profitable operations"""
        # Simplified - in reality would need expenses data
        return profile.monthly_revenue >= 3000 and profile.monthly_revenue > 0

    def _has_scalable_operations(self, profile: EntrepreneurProfile) -> bool:
        """Check for scalable operations"""
        return (profile.team_size >= 5 and
                getattr(profile, 'has_automated_processes', False) == True)

    def _has_market_expansion_plans(self, profile: EntrepreneurProfile) -> bool:
        """Check for market expansion plans"""
        return getattr(profile, 'has_expansion_plans', False) == True

    def _self_assessed_growth(self, profile: EntrepreneurProfile) -> bool:
        """Check if self-assessed as growth"""
        return getattr(profile, 'self_assessed_stage', '') == 'growth'

    def _has_team_scaling(self, profile: EntrepreneurProfile) -> bool:
        """Check for team scaling"""
        return profile.team_size >= 8

    def _has_formal_processes(self, profile: EntrepreneurProfile) -> bool:
        """Check for formal business processes"""
        return getattr(profile, 'has_formal_business_processes', False) == True