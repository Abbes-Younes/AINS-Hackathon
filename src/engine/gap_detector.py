"""
Gap Detection Module
Detects perception-reality gaps between self-assessed and system-assessed stages
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass
import logging

from src.models.profile import EntrepreneurProfile
from src.models.diagnostic import DiagnosticResult, PerceptionGap, GapType
from src.engine.classifier import ClassificationResult

logger = logging.getLogger(__name__)


@dataclass
class GapAnalysis:
    """Result of gap analysis"""
    gap_type: GapType  # OVER_ESTIMATION, UNDER_ESTIMATION, ACCURATE
    claimed_stage: str
    actual_stage: str
    gap_severity: str  # NONE, MILD, MODERATE, SEVERE
    missing_dimensions: List[str]
    explanation: str
    confidence: float


class GapDetector:
    """Detects gaps between self-assessed and system-assessed maturity stages"""

    def __init__(self):
        """Initialize gap detector with stage prerequisites and severity thresholds"""
        # Define prerequisites for each stage (what's needed to be at that stage)
        self.stage_prerequisites = {
            "ideation": [
                "has_idea",
                # No specific prerequisites beyond having an idea
            ],
            "market_validation": [
                "has_validation_interviews",
                "has_mvp",
                "market_research_conducted"
            ],
            "structuration": [
                "has_legal_form",
                "has_business_model_clarity",  # business_model_clarity >= 4
                "team_size",  # team_size >= 2
                "has_mvp"  # Should have MVP by this stage
            ],
            "fundraising": [
                "has_paying_customers",
                "has_business_model_clarity",  # business_model_clarity >= 5
                "is_seeking_funding",
                "has_validation_evidence"  # pilot, surveys, LOIs, etc.
            ],
            "launch_planning": [
                "has_validated_business_model",  # business_model validated with customers
                "has_revenue_traction",  # monthly_revenue >= 1000
                "has_go_to_market_strategy",
                "has_operational_readiness"
            ],
            "growth": [
                "has_consistent_revenue",  # monthly_revenue >= 2000
                "has_profitable_operations",
                "has_scalable_operations",
                "has_team_scaling"  # team_size >= 8
            ]
        }

        # Define what constitutes strong evidence for each prerequisite
        self.prerequisite_checks = {
            "has_idea": lambda p: p.has_idea == True,
            "has_validation_interviews": lambda p: p.has_validation_interviews == True,
            "has_mvp": lambda p: p.has_mvp == True,
            "market_research_conducted": lambda p: getattr(p, 'market_research_conducted', False) == True,
            "has_legal_form": lambda p: p.has_legal_form == True,
            "has_business_model_clarity": lambda p: getattr(p, 'business_model_clarity', 0) >= 4,
            "team_size": lambda p: p.team_size >= 2,
            "has_paying_customers": lambda p: p.has_paying_customers == True,
            "is_seeking_funding": lambda p: p.is_seeking_funding == True,
            "has_validation_evidence": lambda p: (p.has_pilot == True or
                                                getattr(p, 'validation_surveys_conducted', False) == True or
                                                getattr(p, 'signed_lois', 0) > 0),
            "has_validated_business_model": lambda p: getattr(p, 'business_model_clarity', 0) >= 5,
            "has_revenue_traction": lambda p: p.monthly_revenue >= 1000,
            "has_go_to_market_strategy": lambda p: getattr(p, 'has_go_to_market_strategy', False) == True,
            "has_operational_readiness": lambda p: (p.team_size >= 3 and
                                                  p.has_legal_form == True and
                                                  getattr(p, 'has_standard_operating_procedures', False) == True),
            "has_consistent_revenue": lambda p: p.monthly_revenue >= 2000,
            "has_profitable_operations": lambda p: p.monthly_revenue >= 3000 and p.monthly_revenue > 0,
            "has_scalable_operations": lambda p: (p.team_size >= 5 and
                                              getattr(p, 'has_automated_processes', False) == True),
            "has_team_scaling": lambda p: p.team_size >= 8,
            "has_expansion_plans": lambda p: getattr(p, 'has_expansion_plans', False) == True
        }

        # Define severity thresholds based on number of missing prerequisites
        self.severity_thresholds = {
            0: "NONE",
            1: "MILD",
            2: "MODERATE",
            3: "SEVERE"
        }

    def detect_gap(self, profile: EntrepreneurProfile, classification_result: ClassificationResult) -> GapAnalysis:
        """
        Detect perception-reality gap

        Args:
            profile: EntrepreneurProfile containing self-assessed stage
            classification_result: Result from maturity classifier

        Returns:
            GapAnalysis object
        """
        # Get self-assessed stage from profile
        claimed_stage = getattr(profile, 'self_assessed_stage', '').lower()
        if not claimed_stage:
            # Default to ideation if not self-assessed
            claimed_stage = "ideation"
            logger.warning("No self-assessed stage found, defaulting to ideation")

        actual_stage = classification_result.assigned_stage.lower()

        logger.info(f"Detecting gap: claimed={claimed_stage}, actual={actual_stage}")

        # If stages match, check for accurate self-assessment
        if claimed_stage == actual_stage:
            return self._analyze_accurate_self_assessment(profile, claimed_stage, classification_result)

        # Determine gap type
        gap_type = self._determine_gap_type(claimed_stage, actual_stage, profile, classification_result)

        # Identify missing dimensions/prerequisites
        missing_dimensions = self._identify_missing_dimensions(profile, claimed_stage, actual_stage)

        # Determine gap severity
        gap_severity = self._determine_gap_severity(len(missing_dimensions), claimed_stage, actual_stage)

        # Generate explanation
        explanation = self._generate_explanation(claimed_stage, actual_stage, missing_dimensions, gap_type, profile)

        # Calculate confidence based on classification confidence and gap clarity
        confidence = self._calculate_gap_confidence(classification_result, gap_severity, claimed_stage, actual_stage)

        return GapAnalysis(
            gap_type=gap_type,
            claimed_stage=claimed_stage,
            actual_stage=actual_stage,
            gap_severity=gap_severity,
            missing_dimensions=missing_dimensions,
            explanation=explanation,
            confidence=confidence
        )

    def _determine_gap_type(self, claimed_stage: str, actual_stage: str,
                          profile: EntrepreneurProfile,
                          classification_result: ClassificationResult) -> str:
        """Determine if gap is over-estimation, under-estimation, or accurate"""
        stage_order = ["ideation", "market_validation", "structuration",
                      "fundraising", "launch_planning", "growth"]

        try:
            claimed_index = stage_order.index(claimed_stage)
            actual_index = stage_order.index(actual_stage)
        except ValueError:
            # If stage not found, default to over-estimation (safer assumption)
            logger.warning(f"Unknown stage in gap detection: claimed={claimed_stage}, actual={actual_stage}")
            return GapType.OVER_ESTIMATION.value

        if claimed_index > actual_index:
            # Claimed stage is higher than actual = over-estimation
            return GapType.OVER_ESTIMATION.value
        elif claimed_index < actual_index:
            # Claimed stage is lower than actual = under-estimation
            return GapType.UNDER_ESTIMATION.value
        else:
            # Same stage - should have been caught earlier
            return GapType.ACCURATE.value

    def _identify_missing_dimensions(self, profile: EntrepreneurProfile,
                                   claimed_stage: str, actual_stage: str) -> List[str]:
        """Identify which prerequisites are missing for the claimed stage"""
        missing = []

        # Get prerequisites for the claimed stage (what they think they have)
        claimed_prereqs = self.stage_prerequisites.get(claimed_stage, [])

        # Check which prerequisites are actually missing
        for prereq in claimed_prereqs:
            if prereq in self.prerequisite_checks:
                try:
                    if not self.prerequisite_checks[prereq](profile):
                        missing.append(prereq)
                except Exception as e:
                    logger.warning(f"Error checking prerequisite {prereq}: {e}")
                    # If we can't check it, assume it's missing for safety
                    missing.append(prereq)
            else:
                # Handle special cases or direct attribute checks
                if not self._check_direct_attribute(profile, prereq):
                    missing.append(prereq)

        return missing

    def _check_direct_attribute(self, profile: EntrepreneurProfile, attribute_name: str) -> bool:
        """Check direct attribute on profile"""
        # Map common attribute names to profile fields
        attribute_map = {
            "has_idea": "has_idea",
            "has_validation_interviews": "has_validation_interviews",
            "has_mvp": "has_mvp",
            "has_legal_form": "has_legal_form",
            "has_paying_customers": "has_paying_customers",
            "is_seeking_funding": "is_seeking_funding",
            "team_size": "team_size",
            "monthly_revenue": "monthly_revenue",
            "has_incubation": "has_incubation",
            "has_state_aid": "has_state_aid",
            "has_previous_program": "has_previous_program",
            "has_ip": "has_ip",
            "has_rd": "has_rd",
            "tech_readiness_level": "tech_readiness_level",
            "has_sustainability_plan": "has_sustainability_plan",
            "has_social_impact": "has_social_impact",
            "has_website": "has_website",
            "has_social_media": "has_social_media",
            "uses_digital_tools": "uses_digital_tools"
        }

        if attribute_name in attribute_map:
            field_name = attribute_map[attribute_name]
            return getattr(profile, field_name, False) == True
        elif attribute_name == "business_model_clarity":
            # Special handling for scaled field
            return getattr(profile, 'business_model_clarity', 0) >= 4
        elif attribute_name == "has_business_model_clarity":
            return getattr(profile, 'business_model_clarity', 0) >= 4
        else:
            # For attributes we don't have special handling for, return True optimistically
            # This avoids flagging gaps due to missing data rather than actual gaps
            logger.debug(f"No check defined for attribute: {attribute_name}, assuming present")
            return True

    def _analyze_accurate_self_assessment(self, profile: EntrepreneurProfile,
                                        stage: str,
                                        classification_result: ClassificationResult) -> GapAnalysis:
        """Analyze when self-assessment matches system assessment"""
        # Even when stages match, there might be partial gaps or strengths/weaknesses

        # Check how firmly they're in this stage vs. borderline
        missing_for_claimed = self._identify_missing_dimensions(profile, stage, stage)

        if len(missing_for_claimed) == 0:
            # Truly accurate - has all prerequisites for claimed stage
            gap_type = GapType.ACCURATE
            gap_severity = "NONE"
            missing_dimensions = []
            explanation = f"Votre auto-évaluation ({stage}) correspond précisément à notre analyse. Vous remplissez tous les prérequis pour ce stade."
        else:
            # Borderline case - meets stage but missing some elements
            gap_type = GapType.ACCURATE  # Still accurate overall
            gap_severity = self._determine_gap_severity(len(missing_for_claimed), stage, stage)
            missing_dimensions = missing_for_claimed
            explanation = f"Votre auto-évaluation ({stage}) correspond à notre analyse, mais vous manquez encore de certains éléments pour être pleinement confirmé à ce stade."

        confidence = min(classification_result.confidence_score + 0.1, 1.0)  # Boost confidence for agreement

        return GapAnalysis(
            gap_type=gap_type.value,
            claimed_stage=stage,
            actual_stage=stage,
            gap_severity=gap_severity,
            missing_dimensions=missing_dimensions,
            explanation=explanation,
            confidence=confidence
        )

    def _determine_gap_severity(self, missing_count: int, claimed_stage: str, actual_stage: str) -> str:
        """Determine gap severity based on number of missing prerequisites"""
        # Adjust thresholds based on stage transition difficulty
        base_thresholds = self.severity_thresholds.copy()

        # Some stage transitions are more significant than others
        stage_order = ["ideation", "market_validation", "structuration",
                      "fundraising", "launch_planning", "growth"]

        try:
            claimed_idx = stage_order.index(claimed_stage)
            actual_idx = stage_order.index(actual_stage)
            stage_diff = abs(claimed_idx - actual_idx)
        except ValueError:
            stage_diff = 1  # Default assumption

        # Increase severity for larger stage jumps
        severity_levels = ["NONE", "MILD", "MODERATE", "SEVERE"]
        base_severity_idx = min(missing_count, len(severity_levels) - 1)

        # Adjust for stage difference
        adjusted_idx = min(base_severity_idx + stage_diff - 1, len(severity_levels) - 1)
        if adjusted_idx < 0:
            adjusted_idx = 0

        return severity_levels[adjusted_idx]

    def _generate_explanation(self, claimed_stage: str, actual_stage: str,
                          missing_dimensions: List[str], gap_type: str,
                          profile: EntrepreneurProfile) -> str:
        """Generate human-readable explanation of the gap"""
        stage_names_fr = {
            "ideation": "idéation",
            "market_validation": "validation du marché",
            "structuration": "structuration",
            "fundraising": "recherche de financement",
            "launch_planning": "planification du lancement",
            "growth": "croissance"
        }

        stage_names_ar = {
            "ideation": "الidea",
            "market_validation": "validation سوق",
            "structuration": "التنظيم",
            "fundraising": "بحث عن تمويل",
            "launch_planning": "تخطيط الإطلاق",
            "growth": "النمو"
        }

        claimed_fr = stage_names_fr.get(claimed_stage, claimed_stage)
        actual_fr = stage_names_fr.get(actual_stage, actual_stage)
        claimed_ar = stage_names_ar.get(claimed_stage, claimed_stage)
        actual_ar = stage_names_ar.get(actual_stage, actual_stage)

        if gap_type == GapType.OVER_ESTIMATION.value:
            explanation_fr = f"Vous vous auto-évaluez au stade de {claimed_fr}, mais notre analyse vous place au stade de {actual_fr}. "
            explanation_ar = f"أنت تقيم نفسك في مرحلة {claimed_ar}, لكن تحليلنا يضعك في مرحلة {actual_ar}. "
        else:  # UNDER_ESTIMATION
            explanation_fr = f"Vous vous auto-évaluez au stade de {claimed_fr}, mais notre analyse vous place au stade de {actual_fr}. "
            explanation_ar = f"أنت تقيم نفسك في مرحلة {claimed_ar}, لكن تحليلنا يضعك في مرحلة {actual_ar}. "

        if missing_dimensions:
            # Translate missing dimensions to readable format
            missing_names_fr = {
                "has_idea": "une idée claire",
                "has_validation_interviews": "des entretiens de validation avec des clients",
                "has_mvp": "un produit minimum viable (MVP)",
                "market_research_conducted": "des recherches de marché",
                "has_legal_form": "un statut juridique établi",
                "has_business_model_clarity": "un modèle économique clair et documenté",
                "team_size": "une équipe constituée",
                "has_paying_customers": "des clients payants générant des revenus",
                "is_seeking_funding": "une recherche active de financement externe",
                "has_validation_evidence": "des preuves de validation solides (pilots, sondages, LOI)",
                "has_go_to_market_strategy": "une stratégie de mise sur le marché",
                "has_revenue_traction": "une traction des revenus",
                "has_operational_readiness": "une préparation opérationnelle",
                "has_consistent_revenue": "des revenus stables et récurrents",
                "has_profitable_operations": "des opérations rentables",
                "has_scalable_operations": "des opérations scalables",
                "has_team_scaling": "une équipe en croissance pour répondre à la demande",
                "has_expansion_plans": "des plans d'expansion de marché"
            }

            missing_names_ar = {
                "has_idea": "فكرة واضحة",
                "has_validation_interviews": "مقابلات تحقق مع عملاء",
                "has_mvp": "منتج أدنى قابل للتطبيق",
                "market_research_conducted": "أبحاث سوق",
                "has_legal_form": "وضع قانوني establecido",
                "has_business_model_clarity": "نموذج اقتصادي واضح وموثق",
                "team_size": "فريق مكون",
                "has_paying_customers": "عملاء مدفوعين يحققون إيرادات",
                "is_seeking_funding": "بحث actif عن تمويل خارجي",
                "has_validation_evidence": "أدلة تحقق قوية (طيارين، استطلاعات، خطابات نوايا)",
                "has_go_to_market_strategy": "استراتيجية دخول السوق",
                "has_revenue_traction": "جرّ إيرادات",
                "has_operational_readiness": "stعداد تشغيلي",
                "has_consistent_revenue": "إيرادات مستقرة ومتكررة",
                "has_profitable_operations": "عمليات رابحة",
                "has_scalable_operations": "عمليات قابلة للتطوير",
                "has_team_scaling": "فريق في نمو لمواجهة الطلب",
                "has_expansion_plans": "خطط توسع سوقي"
            }

            missing_fr = [missing_names_fr.get(d, d) for d in missing_dimensions[:3]]  # Show first 3
            missing_ar = [missing_names_ar.get(d, d) for d in missing_dimensions[:3]]

            if gap_type == GapType.OVER_ESTIMATION.value:
                explanation_fr += f"Il vous manque spécifiquement : {', '.join(missing_fr)}. Ces éléments sont essentiels pour atteindre le stade de {claimed_fr}."
                explanation_ar += f"أنت تفتقر بشكل خاص إلى: {', '.join(missing_ar)}. هذه العناصر أساسية للوصول إلى مرحلة {claimed_ar}."
            else:  # UNDER_ESTIMATION
                explanation_fr += f"Vous possédez en fait : {', '.join(missing_fr)}. Ces éléments avancés vous placent au-delà de votre auto-évaluation de {claimed_fr}."
                explanation_ar += f"أنت في الواقع تمتلك: {', '.join(missing_ar)}. هذه العناصر المتقدمة تضعك oltre تقييمك الذاتي لـ {claimed_ar}."
        else:
            explanation_fr += "L'écart semble principalement basé sur votre perception globale plutôt que sur des manquants spécifiques."
            explanation_ar += "يبدو أن الفارق يعتمد 주로 على إدراكك العام وليس على نواقص محددة."

        # For simplicity, return French version (could be made language-aware)
        return explanation_fr

    def _calculate_gap_confidence(self, classification_result: ClassificationResult,
                                gap_severity: str, claimed_stage: str, actual_stage: str) -> float:
        """Calculate confidence in the gap detection"""
        base_confidence = classification_result.confidence_score

        # Reduce confidence for severe gaps (could indicate data issues)
        severity_penalty = {
            "NONE": 0.0,
            "MILD": 0.05,
            "MODERATE": 0.1,
            "SEVERE": 0.2
        }

        penalty = severity_penalty.get(gap_severity, 0.1)

        # Increase confidence if classification was confident and gap is clear
        clarity_bonus = 0.0
        if classification_result.confidence_score > 0.8:
            clarity_bonus = 0.05  # Bonus for confident classification

        # Bonus if gap involves adjacent stages (more predictable)
        stage_order = ["ideation", "market_validation", "structuration",
                      "fundraising", "launch_planning", "growth"]
        try:
            claimed_idx = stage_order.index(claimed_stage)
            actual_idx = stage_order.index(actual_stage)
            stage_distance = abs(claimed_idx - actual_idx)
            if stage_distance == 1:
                clarity_bonus += 0.05  # Adjacent stages are more reliable
        except ValueError:
            pass  # If we can't determine, don't adjust

        final_confidence = base_confidence - penalty + clarity_bonus
        return max(0.1, min(final_confidence, 1.0))  # Clamp between 0.1 and 1.0

    def gap_analysis_to_diagnostic(self, gap_analysis: GapAnalysis,
                                 profile: EntrepreneurProfile,
                                 classification_result: ClassificationResult) -> DiagnosticResult:
        """
        Convert gap analysis to DiagnosticResult format

        Args:
            gap_analysis: Result from gap detection
            profile: EntrepreneurProfile
            classification_result: Classification result

        Returns:
            DiagnosticResult object
        """
        # Map gap analysis to diagnostic formats
        perception_gap = None
        if gap_analysis.gap_type != GapType.ACCURATE.value or gap_analysis.gap_severity != "NONE":
            perception_gap = PerceptionGap(
                gap_type=gap_analysis.gap_type,
                claimed_stage=gap_analysis.claimed_stage,
                actual_stage=gap_analysis.actual_stage,
                gap_severity=gap_analysis.gap_severity,
                explanation=gap_analysis.explanation
            )

        # Convert missing dimensions to key blockers format
        key_blockers = []
        for dim in gap_analysis.missing_dimensions:
            blocker_desc = self._dimension_to_blocker_description(dim)
            if blocker_desc:
                key_blockers.append(blocker_desc)

        # If no specific blockers identified, add some generic ones based on stage
        if not key_blockers and gap_analysis.gap_type != GapType.ACCURATE.value:
            key_blockers = self._generate_generic_blockers(gap_analysis.actual_stage, profile)

        return DiagnosticResult(
            assigned_stage=gap_analysis.actual_stage,
            confidence_score=min(classification_result.confidence_score, gap_analysis.confidence),
            perception_gap=perception_gap,
            key_blockers=key_blockers[:5],  # Limit to top 5
            evidence_trace=classification_result.evidence_trace
        )

    def _dimension_to_blocker_description(self, dimension: str) -> Optional[str]:
        """Convert a missing dimension to a blocker description"""
        blocker_map = {
            "has_idea": "Manque d'idée de projet clairement définie",
            "has_validation_interviews": "Absence d'entretiens de validation avec des clients potentiels",
            "has_mvp": "Pas de produit minimum viable (MVP) développé",
            "market_research_conducted": "Aucune recherche de marché effectuée",
            "has_legal_form": "Pas de statut juridique établi pour l'entreprise",
            "has_business_model_clarity": "Modèle économique non défini ou peu clair",
            "team_size": "Équipe insuffisante ou absence de co-fondateurs",
            "has_paying_customers": "Absence de clients payants et de revenus",
            "is_seeking_funding": "Pas de recherche active de financement extérieur",
            "has_validation_evidence": "Preuves de validation insuffisantes (pas de pilot, surveys, ou LOI)",
            "has_go_to_market_strategy": "Stratégie de mise sur le marché non définie",
            "has_revenue_traction": "Traction des revenus insuffisante",
            "has_operational_readiness": "Préparation opérationnelle inadéquate",
            "has_consistent_revenue": "Revenus instables ou irréguliers",
            "has_profitable_operations": "Opérations non rentables ou rentabilité non démontrée",
            "has_scalable_operations": "Manque de scalabilité dans les opérations",
            "has_team_scaling": "Équipe non adaptée à la croissance prévue",
            "has_expansion_plans": "Absence de plans d'expansion de marché"
        }

        return blocker_map.get(dimension, f"Manque de: {dimension.replace('_', ' ')}")

    def _generate_generic_blockers(self, stage: str, profile: EntrepreneurProfile) -> List[str]:
        """Generate generic blockers when specific dimensions aren't identified"""
        blockers = []

        stage_blockers = {
            "ideation": [
                "Besoin de clarifier l'idée de projet",
                "Recherche préliminaire de marché nécessaire",
                "Définition de la proposition de valeur initiale"
            ],
            "market_validation": [
                "Réaliser des entretiens de validation avec des clients",
                "Développer un prototype ou MVP de base",
                "Structurer les retours clients pour itération"
            ],
            "structuration": [
                "Établir un statut juridique pour l'entreprise",
                "Formaliser le modèle économique",
                "Constituer une équipe de fondateurs"
            ],
            "fundraising": [
                "Acquérir les premiers clients payants",
                "Développer un modèle économique éprouvé",
                "Préparer des documents de levée de fonds (pitch deck, business plan)"
            ],
            "launch_planning": [
                "Définir une stratégie de mise sur le marché claire",
                "Augmenter la traction des revenus",
                "Mettre en place des processus opérationnels стандарты"
            ],
            "growth": [
                "Optimiser les opérations pour la rentabilité",
                "Développer des processus scalables et automatisés",
                "Étendre l'équipe pour supporter la croissance"
            ]
        }

        return stage_blockers.get(stage, ["Analyser les domaines d'amélioration généraux"])