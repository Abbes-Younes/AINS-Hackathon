"""
Scoring Engine for Feature 2: Explainable Multi-Dimensional Scoring
Computes 5 composite scores with sub-criteria decomposition from entrepreneur profiles
"""

import yaml
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path
import logging

from src.models.profile import EntrepreneurProfile
from src.models.diagnostic import DiagnosticResult
from src.models.scoring import ScoreResult, CompositeScore, SubCriterion, Anomaly

logger = logging.getLogger(__name__)


class ScoringEngine:
    """Computes explainable multi-dimensional scores for entrepreneur profiles"""

    def __init__(self, scoring_config_path: Optional[str] = None):
        """
        Initialize the scoring engine with configuration

        Args:
            scoring_config_path: Path to the scoring configuration YAML file
        """
        if scoring_config_path is None:
            # Default to the scoring config in the same directory
            scoring_config_path = Path(__file__).parent / "scoring_config.yml"

        self.scoring_config = self._load_scoring_config(scoring_config_path)
        logger.info("Scoring engine initialized with configuration")

    def _load_scoring_config(self, path: Path) -> Dict[str, Any]:
        """Load scoring configuration from YAML file"""
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except Exception as e:
            logger.error(f"Failed to load scoring config from {path}: {e}")
            raise

    def compute_scores(self, profile: EntrepreneurProfile,
                      diagnostic_result: Optional[DiagnosticResult] = None) -> ScoreResult:
        """
        Compute all 5 composite scores with sub-criteria breakdown

        Args:
            profile: EntrepreneurProfile containing questionnaire responses
            diagnostic_result: Optional DiagnosticResult from Feature 1

        Returns:
            ScoreResult with all composite scores, sub-criteria, and metadata
        """
        logger.info(f"Computing scores for project: {profile.project_name}")

        # Initialize result containers
        composites = {}
        anomalies = []

        # Compute each composite score
        for dimension_key in self.scoring_config:
            if dimension_key == "FLOOR_CONSTRAINTS":
                continue  # Skip floor constraints section

            dimension_config = self.scoring_config[dimension_key]
            composite_score, dimension_anomalies = self._compute_composite_score(
                profile, dimension_key, dimension_config
            )
            composites[dimension_key] = composite_score
            anomalies.extend(dimension_anomalies)

        # Calculate overall score (weighted average of composites)
        overall_score, overall_percentage = self._calculate_overall_score(composites)

        # Identify strongest and weakest dimensions
        strongest_dimension, weakest_dimension = self._identify_extremes(composites)

        # Generate improvement priorities
        priorities = self._generate_improvement_priorities(composites)

        # Generate executive summary
        executive_summary = self._generate_executive_summary(
            profile, composites, strongest_dimension, weakest_dimension, priorities
        )

        # Calculate data reliability based on profile completeness
        data_reliability = self._calculate_data_reliability(profile)

        # Create and return the final score result
        score_result = ScoreResult(
            composites=composites,
            overall_score=overall_score,
            overall_percentage=overall_percentage,
            anomalies=anomalies,
            data_reliability=data_reliability,
            strongest_dimension=strongest_dimension,
            weakest_dimension=weakest_dimension,
            priorities=priorities,
            executive_summary=executive_summary
        )

        logger.info(f"Scoring complete. Overall score: {overall_percentage:.1f}%")
        return score_result

    def _compute_composite_score(self, profile: EntrepreneurProfile,
                               dimension_key: str,
                               dimension_config: Dict[str, Any]) -> Tuple[CompositeScore, List[Anomaly]]:
        """
        Compute a single composite score with its sub-criteria

        Args:
            profile: EntrepreneurProfile
            dimension_key: Key identifying the dimension (e.g., 'market')
            dimension_config: Configuration for this dimension

        Returns:
            Tuple of (CompositeScore, List of anomalies found in this dimension)
        """
        label = dimension_config.get("label", dimension_key)
        sub_criteria_config = dimension_config.get("sub_criteria", {})

        sub_criteria = []
        total_weighted_score = 0.0
        total_weight = 0.0
        anomalies = []

        # Process each sub-criterion
        for sub_criterion_key, sub_config in sub_criteria_config.items():
            sub_criterion = self._compute_sub_criterion(
                profile, sub_criterion_key, sub_config
            )
            sub_criteria.append(sub_criterion)

            # Add to weighted score calculation
            weight = sub_config.get("weight", 0.0)
            # Convert points to normalized score (0-1)
            max_points = self._get_max_points(sub_config)
            normalized_value = sub_criterion.value if max_points > 0 else 0.0
            total_weighted_score += normalized_value * weight
            total_weight += weight

        # Apply floor constraints if any
        floor_applied, floor_reason = self._apply_floor_constraints(
            profile, dimension_key, sub_criteria, total_weighted_score, total_weight
        )

        # Calculate final composite score (0-1 scale)
        if total_weight > 0:
            raw_score = total_weighted_score / total_weight
        else:
            raw_score = 0.0

        # Apply floor constraint if applicable
        final_score = raw_score
        if floor_applied:
            final_score = min(final_score, floor_reason.get("max_score", 1.0) if isinstance(floor_reason, dict) else 0.4)

        # Ensure score is within bounds
        final_score = max(0.0, min(1.0, final_score))

        # Create the composite score object
        composite_score = CompositeScore(
            dimension=dimension_key,
            label=label,
            overall_score=final_score,
            percentage=final_score * 100.0,
            sub_criteria=sub_criteria,
            justification="",  # Will be filled by justification engine
            floor_applied=floor_applied,
            floor_reason=str(floor_reason) if floor_reason else None
        )

        return composite_score, anomalies

    def _compute_sub_criterion(self, profile: EntrepreneurProfile,
                             sub_criterion_key: str,
                             sub_config: Dict[str, Any]) -> SubCriterion:
        """
        Compute a single sub-criterion score from profile data

        Args:
            profile: EntrepreneurProfile
            sub_criterion_key: Key identifying the sub-criterion
            sub_config: Configuration for this sub-criterion

        Returns:
            SubCriterion with computed score and metadata
        """
        label = sub_config.get("label", sub_criterion_key)
        levels = sub_config.get("levels", {})
        weight = sub_config.get("weight", 0.0)

        # Map profile data to sub-criterion level
        level_achieved, points_earned, evidence = self._map_profile_to_level(
            profile, sub_criterion_key, levels
        )

        # Calculate normalized score (0-1)
        max_points = self._get_max_points(sub_config)
        normalized_value = points_earned / max_points if max_points > 0 else 0.0

        # Generate improvement suggestion
        improvement_suggestion = self._generate_improvement_suggestion(
            sub_criterion_key, label, level_achieved, levels, profile
        )

        return SubCriterion(
            name=sub_criterion_key,
            label=label,
            value=normalized_value,
            weight=weight,
            evidence=evidence,
            improvement_suggestion=improvement_suggestion
        )

    def _map_profile_to_level(self, profile: EntrepreneurProfile,
                            sub_criterion_key: str,
                            levels: Dict[int, Dict[str, Any]]) -> Tuple[int, int, str]:
        """
        Map profile data to a specific level for a sub-criterion

        Args:
            profile: EntrepreneurProfile
            sub_criterion_key: Key identifying the sub-criterion
            levels: Dictionary of level configurations

        Returns:
            Tuple of (level_achieved, points_earned, evidence_description)
        """
        # Define mapping logic for each sub-criterion
        # This is where we connect profile fields to scoring criteria

        if sub_criterion_key == "addressable_market_size":
            # Based on sector, location, and urban/rural classification
            # This would need enhancement with actual market sizing logic
            if profile.sector == "tech" and profile.is_urban and profile.location == "Tunis":
                return 4, 25, "Tech startup in Tunis targeting national market"
            elif profile.sector in ["agri-food", "artisanat"] and not profile.is_urban:
                return 1, 6, "Local rural business with limited market reach"
            else:
                return 2, 12, "Regional market with moderate potential"

        elif sub_criterion_key == "competitive_landscape":
            # Based on validation evidence and business model clarity
            validation_level = profile.validation_client
            if validation_level >= 8:
                return 4, 20, "Strong validation with detailed competitive analysis"
            elif validation_level >= 5:
                return 3, 12, "Moderate validation with basic competitive understanding"
            elif validation_level >= 2:
                return 2, 8, "Some validation with limited competitive analysis"
            else:
                return 0, 0, "No validation evidence for competitive analysis"

        elif sub_criterion_key == "customer_validation_evidence":
            # Directly from validation_client field (0-10 scale)
            validation_score = profile.validation_client
            if validation_score >= 9:
                return 4, 35, f"Validation score: {validation_score}/10 - strong customer validation"
            elif validation_score >= 7:
                return 3, 20, f"Validation score: {validation_score}/10 - good customer validation"
            elif validation_score >= 4:
                return 2, 10, f"Validation score: {validation_score}/10 - moderate customer validation"
            elif validation_score >= 1:
                return 1, 4, f"Validation score: {validation_score}/10 - basic customer validation"
            else:
                return 0, 0, f"Validation score: {validation_score}/10 - no customer validation"

        elif sub_criterion_key == "revenue_model_clarity":
            # Based on business_model_clarity field (0-10 scale)
            clarity_score = profile.business_model_clarity
            if clarity_score >= 8:
                return 4, 20, f"Business model clarity: {clarity_score}/10 - clear and documented"
            elif clarity_score >= 6:
                return 3, 14, f"Business model clarity: {clarity_score}/10 - documented and validated"
            elif clarity_score >= 4:
                return 2, 8, f"Business model clarity: {clarity_score}/10 - tested with customers"
            elif clarity_score >= 2:
                return 1, 4, f"Business model clarity: {clarity_score}/10 - basic idea"
            else:
                return 0, 0, f"Business model clarity: {clarity_score}/10 - undefined model"

        elif sub_criterion_key == "value_proposition_clarity":
            # Based on business_model_clarity and validation evidence
            avg_score = (profile.business_model_clarity + profile.validation_client) / 2
            if avg_score >= 8:
                return 4, 20, f"Average clarity/validation: {avg_score:.1f} - clear value proposition"
            elif avg_score >= 6:
                return 3, 12, f"Average clarity/validation: {avg_score:.1f} - validated value prop"
            elif avg_score >= 4:
                return 2, 8, f"Average clarity/validation: {avg_score:.1f} - tested value prop"
            elif avg_score >= 2:
                return 1, 4, f"Average clarity/validation: {avg_score:.1f} - basic value prop idea"
            else:
                return 0, 0, f"Average clarity/validation: {avg_score:.1f} - undefined value prop"

        elif sub_criterion_key == "differentiation":
            # Based on tech readiness and IP/R&D indicators
            innovation_indicators = []
            if profile.has_ip:
                innovation_indicators.append("has IP")
            if profile.has_rd:
                innovation_indicators.append("has R&D")
            if profile.tech_readiness_level >= 6:
                innovation_indicators.append("high TRL")

            if len(innovation_indicators) >= 3:
                return 4, 20, f"Strong differentiation: {', '.join(innovation_indicators)}"
            elif len(innovation_indicators) >= 2:
                return 3, 12, f"Moderate differentiation: {', '.join(innovation_indicators)}"
            elif len(innovation_indicators) >= 1:
                return 2, 8, f"Some differentiation: {', '.join(innovation_indicators)}"
            else:
                return 0, 0, "No clear differentiation indicators"

        elif sub_criterion_key == "product_service_maturity":
            # Based on MVP status and validation
            if profile.has_mvp and profile.has_pilot and profile.validation_client >= 7:
                return 4, 20, "Mature product with MVP, pilot, and strong validation"
            elif profile.has_mvp and profile.validation_client >= 4:
                return 3, 12, "Functional product with MVP and moderate validation"
            elif profile.has_mvp:
                return 2, 8, "Basic MVP but limited validation"
            else:
                return 0, 0, "No MVP or prototype developed"

        elif sub_criterion_key == "pricing_strategy":
            # This would need to be inferred from business model or revenue model
            # For now, use business model clarity as proxy
            clarity_score = profile.business_model_clarity
            if clarity_score >= 8:
                return 4, 20, f"Clear business model ({clarity_score}/10) suggests defined pricing"
            elif clarity_score >= 6:
                return 3, 12, f"Documented business model ({clarity_score}/10) suggests pricing strategy"
            elif clarity_score >= 4:
                return 2, 8, f"Tested business model ({clarity_score}/10) suggests pricing tested"
            elif clarity_score >= 2:
                return 1, 4, f"Basic business model ({clarity_score}/10) suggests pricing idea"
            else:
                return 0, 0, f"Undefined business model ({clarity_score}/10) - no pricing strategy"

        elif sub_criterion_key == "offer_need_alignment":
            # Based on validation evidence and problem-solution fit
            validation_score = profile.validation_client
            if validation_score >= 8:
                return 4, 20, f"Strong validation ({validation_score}/10) indicates good problem-solution fit"
            elif validation_score >= 5:
                return 3, 12, f"Moderate validation ({validation_score}/10) suggests some fit"
            elif validation_score >= 2:
                return 2, 8, f"Limited validation ({validation_score}/10) indicates uncertain fit"
            else:
                return 0, 0, f"Minimal validation ({validation_score}/10) - unclear problem-solution fit"

        # Innovation dimension sub-criteria
        elif sub_criterion_key == "local_novelty":
            # Based on sector novelty and local context
            if profile.sector == "tech" and profile.has_rd:
                return 4, 25, "Tech startup with R&D - likely innovative locally"
            elif profile.sector == "agri-food" and profile.has_sustainability_plan:
                return 3, 18, "Agri-food with sustainability plan - some local novelty"
            elif profile.has_ip:
                return 2, 12, "Has IP - indicates novelty"
            else:
                return 1, 6, "Standard local business model"

        elif sub_criterion_key == "technology_intensity":
            # Based on tech readiness level and digital tools
            trl_score = profile.tech_readiness_level
            digital_score = sum([profile.has_website, profile.has_social_media, profile.uses_digital_tools])
            if trl_score >= 7 and digital_score >= 2:
                return 4, 20, f"High TRL ({trl_score}) and digital tools - high tech intensity"
            elif trl_score >= 5 and digital_score >= 1:
                return 3, 12, f"Moderate TRL ({trl_score}) and some digital - moderate tech intensity"
            elif trl_score >= 3:
                return 2, 8, f"Basic TRL ({trl_score}) - low to moderate tech intensity"
            else:
                return 0, 0, f"Low TRL ({trl_score}) and limited digital - low tech intensity"

        elif sub_criterion_key == "barrier_to_entry":
            # Based on IP protection and technical complexity
            barriers = []
            if profile.has_ip:
                barriers.append("IP protection")
            if profile.tech_readiness_level >= 6:
                barriers.append("High technical complexity")
            if profile.has_rd:
                barriers.append("R&D capabilities")

            if len(barriers) >= 3:
                return 4, 20, f"Strong barriers: {', '.join(barriers)}"
            elif len(barriers) >= 2:
                return 3, 12, f"Moderate barriers: {', '.join(barriers)}"
            elif len(barriers) >= 1:
                return 2, 8, f"Some barrier: {', '.join(barriers)}"
            else:
                return 0, 0, "Low barriers to entry"

        elif sub_criterion_key == "departure_from_existing":
            # Based on innovation indicators and sector
            innovation_score = sum([
                1 if profile.has_ip else 0,
                1 if profile.has_rd else 0,
                1 if profile.tech_readiness_level >= 5 else 0,
                1 if profile.has_sustainability_plan else 0
            ])
            if innovation_score >= 4:
                return 4, 12, "High innovation indicators - significant departure"
            elif innovation_score >= 3:
                return 3, 9, "Good innovation indicators - substantial departure"
            elif innovation_score >= 2:
                return 2, 6, "Some innovation indicators - notable departure"
            elif innovation_score >= 1:
                return 1, 3, "Minimal innovation indicators - slight departure"
            else:
                return 0, 0, "No innovation indicators - very similar to existing"

        elif sub_criterion_key == "ip_protection":
            # Directly from IP and RD fields
            if profile.has_ip:
                return 4, 20, "Has intellectual property protection"
            elif profile.has_rd:
                return 2, 8, "Has R&D activities - potential for IP"
            else:
                return 0, 0, "No IP or R&D activities"

        # Scalability dimension sub-criteria
        elif sub_criterion_key == "replicability_without_linear_cost":
            # Based on business model and digitalization
            digital_score = sum([profile.has_website, profile.has_social_media, profile.uses_digital_tools])
            if profile.has_website and profile.uses_digital_tools and profile.sector == "tech":
                return 4, 25, "Digital tech business - highly replicable"
            elif profile.has_website or profile.uses_digital_tools:
                return 3, 18, "Some digitalization - moderately replicable"
            elif profile.sector in ["tech", "services"]:
                return 2, 12, "Service/tech business - somewhat replicable"
            else:
                return 1, 6, "Physical product business - limited replicability"

        elif sub_criterion_key == "manual_dependency":
            # Inverse scoring: less manual = higher score
            automation_indicators = sum([
                profile.uses_digital_tools,
                profile.has_website,
                profile.has_social_media
            ])
            if automation_indicators >= 3:
                return 4, 20, "Highly digital - low manual dependency"
            elif automation_indicators >= 2:
                return 3, 12, "Moderately digital - moderate manual dependency"
            elif automation_indicators >= 1:
                return 2, 8, "Some digital tools - moderate to high manual dependency"
            else:
                return 0, 0, "Low digitalization - high manual dependency"

        elif sub_criterion_key == "deployment_cost_structure":
            # Based on sector and technology requirements
            if profile.sector == "tech" and not profile.has_rd:
                return 4, 20, "Pure software tech - low deployment costs"
            elif profile.sector == "tech" and profile.has_rd:
                return 3, 12, "Tech with R&D - moderate deployment costs"
            elif profile.sector == "services":
                return 2, 8, "Service business - moderate deployment costs"
            else:
                return 0, 0, "Physical/product business - high deployment costs"

        elif sub_criterion_key == "geographic_addressability":
            # Based on location, urban/rural, and sector
            if profile.is_urban and profile.location == "Tunis" and profile.sector == "tech":
                return 4, 12, "Urban tech in Tunis - national/international addressable"
            elif profile.is_urban and profile.sector in ["tech", "services"]:
                return 3, 9, "Urban service/tech - regionally addressable"
            elif not profile.is_urban:
                return 1, 3, "Rural business - locally addressable"
            else:
                return 2, 6, "Mixed urban/rural - moderately addressable"

        elif sub_criterion_key == "automation_potential":
            # Based on sector and digital tool usage
            if profile.sector == "tech" and profile.uses_digital_tools:
                return 4, 20, "Tech business using digital tools - high automation potential"
            elif profile.sector == "tech":
                return 3, 12, "Tech business - moderate automation potential"
            elif profile.uses_digital_tools:
                return 2, 8, "Uses digital tools - some automation potential"
            else:
                return 0, 0, "Low tech/digital usage - limited automation potential"

        # Green dimension sub-criteria
        elif sub_criterion_key == "environmental_impact_assessment":
            # Based on sustainability plan and social impact
            if profile.has_sustainability_plan and profile.has_social_impact:
                return 4, 20, "Has both sustainability and social impact plans"
            elif profile.has_sustainability_plan:
                return 3, 12, "Has sustainability plan - environmental assessment done"
            elif profile.has_social_impact:
                return 2, 8, "Has social impact - some environmental consideration"
            else:
                return 0, 0, "No sustainability or social impact plans"

        elif sub_criterion_key == "sdg_alignment":
            # Based on sustainability and social impact indicators
            sgd_indicators = sum([
                1 if profile.has_sustainability_plan else 0,
                1 if profile.has_social_impact else 0,
                1 if profile.has_rd else 0  # R&D can align with SDGs
            ])
            if sgd_indicators >= 3:
                return 4, 20, "Strong SDG alignment indicators"
            elif sgd_indicators >= 2:
                return 3, 12, "Moderate SDG alignment indicators"
            elif sgd_indicators >= 1:
                return 2, 8, "Some SDG alignment indicators"
            else:
                return 0, 0, "Minimal SDG alignment indicators"

        elif sub_criterion_key == "resource_efficiency":
            # Based on sector and operational hints
            if profile.sector == "tech" and profile.uses_digital_tools:
                return 4, 20, "Tech with digital tools - likely resource efficient"
            elif profile.has_sustainability_plan:
                return 3, 12, "Has sustainability plan - likely resource efficient"
            elif profile.sector == "services":
                return 2, 8, "Service business - moderate resource efficiency"
            else:
                return 0, 0, "Physical business - uncertain resource efficiency"

        elif sub_criterion_key == "circular_economy_practices":
            # Based on sustainability plan specifics
            if profile.has_sustainability_plan:
                # Would need more specific data, using plan as proxy
                return 3, 12, "Has sustainability plan - likely includes circular practices"
            else:
                return 0, 0, "No sustainability plan - unlikely circular practices"

        elif sub_criterion_key == "carbon_footprint_awareness":
            # Based on sustainability plan and digital awareness
            if profile.has_sustainability_plan and profile.uses_digital_tools:
                return 4, 10, "Has sustainability plan and uses digital tools - carbon awareness likely"
            elif profile.has_sustainability_plan:
                return 2, 4, "Has sustainability plan - some carbon awareness"
            elif profile.uses_digital_tools:
                return 1, 2, "Uses digital tools - basic carbon awareness"
            else:
                return 0, 0, "No sustainability plan or digital tools - low carbon awareness"

        elif sub_criterion_key == "sustainable_sourcing":
            # Based on sector and sustainability
            if profile.sector == "agri-food" and profile.has_sustainability_plan:
                return 4, 10, "Agri-food with sustainability plan - likely sustainable sourcing"
            elif profile.has_sustainability_plan:
                return 2, 4, "Has sustainability plan - possibly sustainable sourcing"
            else:
                return 0, 0, "No sustainability plan - uncertain sustainable sourcing"

        else:
            # Unknown sub-criterion - return default
            logger.warning(f"Unknown sub-criterion: {sub_criterion_key}")
            return 0, 0, f"No mapping defined for {sub_criterion_key}"

    def _get_max_points(self, sub_config: Dict[str, Any]) -> int:
        """Get the maximum points possible for a sub-criterion"""
        levels = sub_config.get("levels", {})
        if not levels:
            return 1
        return max(level.get("points", 0) for level in levels.values())

    def _apply_floor_constraints(self, profile: EntrepreneurProfile,
                               dimension_key: str,
                               sub_criteria: List[SubCriterion],
                               raw_score: float,
                               total_weight: float) -> Tuple[bool, Any]:
        """
        Apply floor constraints to a dimension score

        Args:
            profile: EntrepreneurProfile
            dimension_key: Key identifying the dimension
            sub_criteria: List of sub-criteria for this dimension
            raw_score: Raw computed score (0-1 scale)
            total_weight: Total weight of sub-criteria

        Returns:
            Tuple of (floor_applied, floor_reason_or_max_score)
        """
        floor_constraints = self.scoring_config.get("FLOOR_CONSTRAINTS", {})
        if dimension_key not in floor_constraints:
            return False, None

        constraint_key, max_raw_score = floor_constraints[dimension_key]

        # Find the sub-criterion that corresponds to this constraint
        constraint_sub_criterion = None
        for sub_criterion in sub_criteria:
            if sub_criterion.name == constraint_key:
                constraint_sub_criterion = sub_criterion
                break

        if constraint_sub_criterion is None:
            logger.warning(f"Floor constraint key {constraint_key} not found in sub-criteria for {dimension_key}")
            return False, None

        # Check if the constraint sub-criterion is at level 0 (minimum points)
        max_points = self._get_max_points(
            next(config for key, config in self.scoring_config[dimension_key].get("sub_criteria", {}).items()
                 if key == constraint_key)
        )
        min_normalized_score = 0.0  # Level 0 always has 0 points

        if constraint_sub_criterion.value <= min_normalized_score + 0.001:  # Essentially zero
            # Apply floor constraint
            max_final_score = max_raw_score / 100.0  # Convert from points to 0-1 scale
            return True, {"max_score": max_final_score, "reason": f"Floor constraint: {constraint_key} = 0"}

        return False, None

    def _calculate_overall_score(self, composites: Dict[str, CompositeScore]) -> Tuple[float, float]:
        """
        Calculate overall score as weighted average of composite scores

        Args:
            composites: Dictionary of composite scores

        Returns:
            Tuple of (overall_score_0_to_1, overall_percentage)
        """
        # For now, use equal weighting - could be enhanced with stage-based weights
        total_score = 0.0
        count = 0

        for composite in composites.values():
            total_score += composite.overall_score
            count += 1

        if count > 0:
            overall_score = total_score / count
        else:
            overall_score = 0.0

        overall_percentage = overall_score * 100.0
        return overall_score, overall_percentage

    def _identify_extremes(self, composites: Dict[str, CompositeScore]) -> Tuple[Optional[str], Optional[str]]:
        """
        Identify strongest and weakest dimensions

        Args:
            composites: Dictionary of composite scores

        Returns:
            Tuple of (strongest_dimension_key, weakest_dimension_key)
        """
        if not composites:
            return None, None

        strongest_key = max(composites.keys(), key=lambda k: composites[k].overall_score)
        weakest_key = min(composites.keys(), key=lambda k: composites[k].overall_score)

        return strongest_key, weakest_key

    def _generate_improvement_priorities(self, composites: Dict[str, CompositeScore]) -> List[str]:
        """
        Generate improvement priorities based on weakest sub-criteria

        Args:
            composites: Dictionary of composite scores

        Returns:
            List of priority improvement areas
        """
        priorities = []

        # For each dimension, find the sub-criterion with lowest score
        for dimension_key, composite in composites.items():
            if not composite.sub_criteria:
                continue

            # Find sub-criterion with lowest value
            worst_sub = min(composite.sub_criteria, key=lambda sc: sc.value)
            if worst_sub.value < 0.5:  # Only prioritize if score is below 50%
                priorities.append(f"{composite.label}: {worst_sub.label}")

        # Sort by severity (lowest score first)
        priorities.sort(key=lambda p: float(p.split(": ")[1].split()[0]) if ": " in p and p.split(": ")[1].split()[0].replace('.', '', 1).isdigit() else 1.0)

        return priorities[:5]  # Return top 5 priorities

    def _generate_executive_summary(self, profile: EntrepreneurProfile,
                                  composites: Dict[str, CompositeScore],
                                  strongest_dimension: Optional[str],
                                  weakest_dimension: Optional[str],
                                  priorities: List[str]) -> str:
        """
        Generate a one-paragraph executive summary of the scoring results

        Args:
            profile: EntrepreneurProfile
            composites: Dictionary of composite scores
            strongest_dimension: Key of strongest dimension
            weakest_dimension: Key of weakest dimension
            priorities: List of improvement priorities

        Returns:
            Executive summary string
        """
        if not composites:
            return "Unable to generate scoring summary due to insufficient data."

        # Calculate overall score
        overall_score = sum(c.overall_score for c in composites.values()) / len(composites)
        overall_percentage = overall_score * 100.0

        # Get dimension labels
        strongest_label = composites[strongest_dimension].label if strongest_dimension and strongest_dimension in composites else "N/A"
        weakest_label = composites[weakest_dimension].label if weakest_dimension and weakest_dimension in composites else "N/A"

        summary = f"L'entreprise {profile.project_name} obtient un score global de {overall_percentage:.0f}%. "
        summary += f"Son domaine le plus fort est {strongest_label}, tandis que {weakest_label} représente la principale amélioration. "

        if priorities:
            summary += f"Les priorités d'action sont : {'; '.join(priorities[:3])}."
        else:
            summary += "Les performances sont équilibrées across all dimensions."

        return summary

    def _calculate_data_reliability(self, profile: EntrepreneurProfile) -> float:
        """
        Calculate data reliability based on profile completeness

        Args:
            profile: EntrepreneurProfile

        Returns:
            Reliability score (0.0 to 1.0)
        """
        # Count how many key fields have been populated
        key_fields = [
            'has_idea', 'has_validation_interviews', 'has_mvp', 'has_business_model',
            'business_model_clarity', 'has_legal_form', 'team_size', 'has_full_time_team',
            'monthly_revenue', 'has_paying_customers', 'validation_client',
            'validation_surveys', 'validation_expert', 'has_pilot', 'has_traction',
            'is_seeking_funding', 'has_incubation', 'has_state_aid',
            'has_ip', 'has_rd', 'tech_readiness_level',
            'has_website', 'has_social_media', 'uses_digital_tools'
        ]

        populated_count = 0
        total_count = len(key_fields)

        for field in key_fields:
            value = getattr(profile, field, None)
            if value is not None and value != False and value != 0 and value != "":
                # For boolean fields, True counts as populated
                # For numeric fields, non-zero counts as populated
                # For string fields, non-empty counts as populated
                if isinstance(value, bool):
                    if value:
                        populated_count += 1
                elif isinstance(value, (int, float)):
                    if value != 0:
                        populated_count += 1
                elif isinstance(value, str):
                    if value != "":
                        populated_count += 1
                else:
                    populated_count += 1

        reliability = populated_count / total_count if total_count > 0 else 0.0
        return reliability

    def _generate_improvement_suggestion(self, sub_criterion_key: str, label: str,
                                       level_achieved: int, levels: Dict[int, Dict[str, Any]],
                                       profile: EntrepreneurProfile) -> str:
        """
        Generate improvement suggestion for a sub-criterion

        Args:
            sub_criterion_key: Key identifying the sub-criterion
            label: Human-readable label
            level_achieved: Level currently achieved (0-4)
            levels: Dictionary of level configurations
            profile: EntrepreneurProfile

        Returns:
            Improvement suggestion string
        """
        if level_achieved >= 4:  # Already at max level
            return "Niveau maximum atteint - maintenir cette performance"

        # Get next level information
        next_level = level_achieved + 1
        if next_level in levels:
            next_level_info = levels[next_level]
            next_level_label = next_level_info.get("label", f"Niveau {next_level}")
            return f"Atteindre le niveau suivant : {next_level_label}"
        else:
            # Try to get the highest level
            max_level = max(levels.keys()) if levels else 4
            if max_level in levels:
                max_level_info = levels[max_level]
                max_level_label = max_level_info.get("label", f"Niveau {max_level}")
                return f"Améliorer pour atteindre : {max_level_label}"
            else:
                return f"Améliorer {label} pour augmenter le score"
