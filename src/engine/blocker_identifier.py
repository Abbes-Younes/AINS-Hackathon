"""
Blocker Identification Module
Identifies and prioritizes blockers based on entrepreneur profile and maturity stage
"""

from typing import Dict, Any, List, Optional, Tuple
import yaml
from pathlib import Path
import logging

from src.models.profile import EntrepreneurProfile
from src.models.diagnostic import Blocker
from src.engine.gap_detector import GapAnalysis

logger = logging.getLogger(__name__)


class BlockerIdentifier:
    """Identifies and prioritizes blockers for entrepreneur profiles"""

    def __init__(self, blocker_taxonomy_path: Optional[str] = None):
        """
        Initialize blocker identifier with taxonomy

        Args:
            blocker_taxonomy_path: Path to blocker taxonomy YAML file
        """
        if blocker_taxonomy_path is None:
            # Default to the blocker taxonomy in the same directory
            blocker_taxonomy_path = Path(__file__).parent / "blocker_taxonomy.yml"

        self.blocker_taxonomy = self._load_blocker_taxonomy(blocker_taxonomy_path)
        logger.info(f"Loaded {len(self.blocker_taxonomy)} blockers from taxonomy")

    def _load_blocker_taxonomy(self, path: Path) -> List[Dict[str, Any]]:
        """Load blocker taxonomy from YAML file"""
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
                return data.get('blockers', [])
        except Exception as e:
            logger.error(f"Failed to load blocker taxonomy from {path}: {e}")
            # Return empty list as fallback
            return []

    def identify_blockers(self, profile: EntrepreneurProfile,
                        gap_analysis: Optional[GapAnalysis] = None,
                        assigned_stage: Optional[str] = None) -> List[Blocker]:
        """
        Identify blockers based on profile and current/potential stage

        Args:
            profile: EntrepreneurProfile to analyze
            gap_analysis: Optional gap analysis result
            assigned_stage: Currently assigned maturity stage (if known)

        Returns:
            List of prioritized blocker objects
        """
        # Determine stage to check blockers for
        if assigned_stage is None:
            if gap_analysis:
                # Use the actual (system-assessed) stage for blocker identification
                assigned_stage = gap_analysis.actual_stage
            else:
                # Fallback to self-assessed stage or ideation
                assigned_stage = getattr(profile, 'self_assessed_stage', 'ideation')

        logger.info(f"Identifying blockers for stage: {assigned_stage}")

        applicable_blockers = []

        # Check each blocker in taxonomy
        for blocker_data in self.blocker_taxonomy:
            if self._is_blocker_applicable(blocker_data, profile, assigned_stage):
                blocker = self._create_blocker_object(blocker_data, profile)
                if blocker:
                    applicable_blockers.append(blocker)

        # Prioritize blockers
        prioritized_blockers = self._prioritize_blockers(applicable_blockers, profile, assigned_stage)

        logger.info(f"Identified {len(prioritized_blockers)} applicable blockers")
        return prioritized_blockers

    def _is_blocker_applicable(self, blocker_data: Dict[str, Any],
                             profile: EntrepreneurProfile,
                             assigned_stage: str) -> bool:
        """
        Check if a blocker is applicable to the given profile and stage

        Args:
            blocker_data: Blocker definition from taxonomy
            profile: EntrepreneurProfile to check
            assigned_stage: Current maturity stage

        Returns:
            True if blocker applies, False otherwise
        """
        # Check if blocker affects the current stage
        affected_stages = blocker_data.get('affected_stages', [])
        if assigned_stage not in affected_stages:
            return False

        # Check domain-specific conditions
        domain = blocker_data.get('domain', '')
        if not self._check_domain_conditions(domain, profile, blocker_data):
            return False

        # Check any specific conditions mentioned in the blocker
        if not self._check_specific_conditions(blocker_data, profile):
            return False

        return True

    def _check_domain_conditions(self, domain: str, profile: EntrepreneurProfile,
                               blocker_data: Dict[str, Any]) -> bool:
        """Check domain-specific conditions for blocker applicability"""
        if domain == "financial":
            return self._check_financial_conditions(profile, blocker_data)
        elif domain == "legal":
            return self._check_legal_conditions(profile, blocker_data)
        elif domain == "market":
            return self._check_market_conditions(profile, blocker_data)
        elif domain == "technical":
            return self._check_technical_conditions(profile, blocker_data)
        elif domain == "organisational":
            return self._check_organizational_conditions(profile, blocker_data)
        elif domain == "sustainability":
            return self._check_sustainability_conditions(profile, blocker_data)
        elif domain == "social_impact":
            return self._check_social_impact_conditions(profile, blocker_data)
        elif domain == "digital":
            return self._check_digital_conditions(profile, blocker_data)
        elif domain == "regulatory":
            return self._check_regulatory_conditions(profile, blocker_data)
        elif domain == "personal":
            return self._check_personal_conditions(profile, blocker_data)
        elif domain == "support":
            return self._check_support_conditions(profile, blocker_data)
        elif domain == "network":
            return self._check_network_conditions(profile, blocker_data)
        else:
            # For unknown domains, assume applicable if stage matches
            logger.debug(f"Unknown domain {domain}, assuming applicable")
            return True

    def _check_financial_conditions(self, profile: EntrepreneurProfile,
                                  blocker_data: Dict[str, Any]) -> bool:
        """Check financial-specific conditions"""
        blocker_name = blocker_data.get('name', '')

        if "No paying customers" in blocker_name:
            return profile.has_paying_customers == False and profile.monthly_revenue == 0
        elif "Insufficient revenue traction" in blocker_name:
            # Check if revenue is present but insufficient for growth
            return (profile.has_paying_customers == True and
                   profile.monthly_revenue > 0 and
                   profile.monthly_revenue < 1000)  # Arbitrary threshold
        elif "No clear business model" in blocker_name:
            return getattr(profile, 'business_model_clarity', 0) < 4
        elif "Insufficient funding runway" in blocker_name:
            # Simplified check - would need expense data in reality
            return profile.monthly_revenue < 500 and profile.is_seeking_funding == True

        return True  # Default to applicable if we can't determine

    def _check_legal_conditions(self, profile: EntrepreneurProfile,
                              blocker_data: Dict[str, Any]) -> bool:
        """Check legal-specific conditions"""
        blocker_name = blocker_data.get('name', '')

        if "No legal structure" in blocker_name:
            return profile.has_legal_form == False
        elif "Inappropriate legal structure" in blocker_name:
            # Simplified - would need more detailed logic
            return profile.has_legal_form == True  # Has some structure, might be inappropriate
        elif "Intellectual property not protected" in blocker_name:
            return profile.has_ip == False and profile.has_rd == True

        return True

    def _check_market_conditions(self, profile: EntrepreneurProfile,
                               blocker_data: Dict[str, Any]) -> bool:
        """Check market-specific conditions"""
        blocker_name = blocker_data.get('name', '')

        if "No customer validation evidence" in blocker_name:
            return (profile.has_validation_interviews == False and
                   profile.has_pilot == False and
                   getattr(profile, 'validation_surveys_conducted', False) == False)
        elif "Insufficient market research" in blocker_name:
            return getattr(profile, 'market_research_conducted', False) == False
        elif "Weak competitive differentiation" in blocker_name:
            # Simplified check
            return getattr(profile, 'competitive_differentiation_weak', False) == True
        elif "Undefined target market" in blocker_name:
            return getattr(profile, 'target_market_defined', False) == False

        return True

    def _check_technical_conditions(self, profile: EntrepreneurProfile,
                                  blocker_data: Dict[str, Any]) -> bool:
        """Check technical-specific conditions"""
        blocker_name = blocker_data.get('name', '')

        if "No functional MVP/prototype" in blocker_name:
            return profile.has_mvp == False
        elif "Technical feasibility unproven" in blocker_name:
            return profile.has_mvp == False and profile.has_validation_interviews == False
        elif "Technology stack not scalable" in blocker_name:
            return getattr(profile, 'tech_scalable', False) == False

        return True

    def _check_organizational_conditions(self, profile: EntrepreneurProfile,
                                       blocker_data: Dict[str, Any]) -> bool:
        """Check organizational-specific conditions"""
        blocker_name = blocker_data.get('name', '')

        if "Solo founder with no team" in blocker_name:
            return profile.team_size <= 1
        elif "Missing key skills in team" in blocker_name:
            # Simplified check
            return getattr(profile, 'team_has_skill_gaps', False) == True
        elif "Inadequate operational processes" in blocker_name:
            return getattr(profile, 'has_formal_processes', False) == False
        elif "No clear leadership structure" in blocker_name:
            return getattr(profile, 'clear_leadership_structure', False) == False

        return True

    def _check_sustainability_conditions(self, profile: EntrepreneurProfile,
                                       blocker_data: Dict[str, Any]) -> bool:
        """Check sustainability-specific conditions"""
        blocker_name = blocker_data.get('name', '')

        if "No sustainability plan" in blocker_name:
            return getattr(profile, 'has_sustainability_plan', False) == False
        elif "Social impact not measured" in blocker_name:
            return getattr(profile, 'social_impact_measured', False) == False

        return True

    def _check_digital_conditions(self, profile: EntrepreneurProfile,
                                blocker_data: Dict[str, Any]) -> bool:
        """Check digital-specific conditions"""
        blocker_name = blocker_data.get('name', '')

        if "Limited digital presence" in blocker_name:
            return (getattr(profile, 'has_website', False) == False and
                   getattr(profile, 'has_social_media', False) == False)
        elif "No e-commerce capability" in blocker_name:
            return getattr(profile, 'has_ecommerce_capability', False) == False

        return True

    def _check_regulatory_conditions(self, profile: EntrepreneurProfile,
                                   blocker_data: Dict[str, Any]) -> bool:
        """Check regulatory-specific conditions"""
        blocker_name = blocker_data.get('name', '')

        if "Insufficient food safety certifications" in blocker_name:
            return getattr(profile, 'food_safety_certified', False) == False
        elif "Missing required licenses or permits" in blocker_name:
            return getattr(profile, 'has_required_permits', False) == False

        return True

    def _check_personal_conditions(self, profile: EntrepreneurProfile,
                                 blocker_data: Dict[str, Any]) -> bool:
        """Check personal-specific conditions"""
        blocker_name = blocker_data.get('name', '')

        if "Founder burnout risk" in blocker_name:
            # Simplified - would need more detailed assessment
            return getattr(profile, 'founder_working_hours', 0) > 60
        elif "Work-life imbalance" in blocker_name:
            return getattr(profile, 'work_life_balance_poor', False) == True
        elif "Lack of mentor or advisor" in blocker_name:
            return getattr(profile, 'has_mentor_or_advisor', False) == False

        return True

    def _check_support_conditions(self, profile: EntrepreneurProfile,
                                blocker_data: Dict[str, Any]) -> bool:
        """Check support-specific conditions"""
        blocker_name = blocker_data.get('name', '')

        if "Limited professional network" in blocker_name:
            return getattr(profile, 'professional_network_strong', False) == False

        return True

    def _check_network_conditions(self, profile: EntrepreneurProfile,
                                blocker_data: Dict[str, Any]) -> bool:
        """Check network-specific conditions"""
        # For network domain, we'll use the same as support for now
        return self._check_support_conditions(profile, blocker_data)

    def _check_specific_conditions(self, blocker_data: Dict[str, Any],
                                 profile: EntrepreneurProfile) -> bool:
        """Check any specific conditions mentioned in blocker data"""
        # This could be extended to handle custom condition expressions
        # For now, return True (no specific conditions beyond domain checks)
        return True

    def _create_blocker_object(self, blocker_data: Dict[str, Any],
                             profile: EntrepreneurProfile) -> Optional[Blocker]:
        """
        Create a Blocker object from blocker data and profile

        Args:
            blocker_data: Blocker definition from taxonomy
            profile: EntrepreneurProfile for context

        Returns:
            Blocker object or None if creation fails
        """
        try:
            # Generate specific explanation based on profile
            explanation = self._generate_blocker_explanation(blocker_data, profile)

            blocker = Blocker(
                name=blocker_data['name'],
                description=blocker_data['description'],
                domain=blocker_data['domain'],
                priority=blocker_data['priority'],
                affected_stages=blocker_data.get('affected_stages', []),
                explanation=explanation
            )

            return blocker

        except Exception as e:
            logger.warning(f"Failed to create blocker object for {blocker_data.get('name', 'unknown')}: {e}")
            return None

    def _generate_blocker_explanation(self, blocker_data: Dict[str, Any],
                                    profile: EntrepreneurProfile) -> str:
        """Generate personalized explanation for why this blocker applies"""
        base_explanation = blocker_data.get('description', '')
        blocker_name = blocker_data.get('name', '')

        # Add profile-specific details
        details = []

        if "No paying customers" in blocker_name:
            details.append(f"Revenu mensuel actuel: {profile.monthly_revenue} TND")
        elif "No legal structure" in blocker_name:
            legal_form = getattr(profile, 'legal_form_type', 'Non défini')
            details.append(f"Statut juridique actuel: {legal_form}")
        elif "No customer validation evidence" in blocker_name:
            validation_count = getattr(profile, 'validation_client_count', 0)
            details.append(f"Nombre de clients validés: {validation_count}")
        elif "No functional MVP/prototype" in blocker_name:
            has_mvp = getattr(profile, 'has_mvp', False)
            details.append(f"MVP développé: {'Oui' if has_mvp else 'Non'}")
        elif "Solo founder with no team" in blocker_name:
            team_size = getattr(profile, 'team_size', 0)
            details.append(f"Taille de l'équipe: {team_size} personne(s)")

        if details:
            detail_text = " Détails: " + "; ".join(details)
            return base_explanation + detail_text
        else:
            return base_explanation

    def _prioritize_blockers(self, blockers: List[Blocker],
                           profile: EntrepreneurProfile,
                           assigned_stage: str) -> List[Blocker]:
        """
        Prioritize blockers based on impact and urgency

        Args:
            blockers: List of identified blockers
            profile: EntrepreneurProfile
            assigned_stage: Current maturity stage

        Returns:
            List of blockers sorted by priority
        """
        # Define priority weights
        priority_weights = {
            "high": 3,
            "medium": 2,
            "low": 1
        }

        # Define stage order for transition impact calculation
        stage_order = ["ideation", "market_validation", "structuration",
                      "fundraising", "launch_planning", "growth"]

        try:
            current_stage_idx = stage_order.index(assigned_stage)
        except ValueError:
            current_stage_idx = 0  # Default to ideation

        def blocker_score(blocker: Blocker) -> float:
            score = 0.0

            # Base priority score (higher is better for sorting)
            priority_weight = priority_weights.get(blocker.priority.lower(), 1)
            score += priority_weight * 10  # Weight priority heavily

            # Bonus for blockers that affect stage transitions (more critical)
            if getattr(blocker, 'blocks_stage_transition', False):
                score += 5

            # Additional penalty for blockers affecting immediate next stage
            # Blockers that prevent progression to the next logical stage are more urgent
            next_stage_idx = min(current_stage_idx + 1, len(stage_order) - 1)
            if next_stage_idx < len(stage_order):
                next_stage = stage_order[next_stage_idx]
                if next_stage in blocker.affected_stages:
                    score += 3  # Extra urgency for next-stage blockers

            return score

        # Sort by score descending (highest priority first)
        sorted_blockers = sorted(blockers, key=blocker_score, reverse=True)
        return sorted_blockers

    def blocker_list_to Diagnostic_format(self, blockers: List[Blocker]) -> List[Dict[str, Any]]:
        """
        Convert blocker objects to format suitable for diagnostic output

        Args:
            blockers: List of Blocker objects

        Returns:
            List of dictionaries suitable for inclusion in DiagnosticResult
        """
        return [
            {
                "name": blocker.name,
                "description": blocker.description,
                "domain": blocker.domain,
                "priority": blocker.priority,
                "explanation": blocker.explanation
            }
            for blocker in blockers
        ]