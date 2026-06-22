"""
Improvement Guidance for Feature 2: Explainable Multi-Dimensional Scoring
Identifies highest-leverage gaps and suggests concrete actions
"""

import logging
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path

from src.models.profile import EntrepreneurProfile
from src.models.scoring import ImprovementGuidance, ScoreBreakdown
from src.feature_2_scoring.scoring_engine import ScoringEngine

logger = logging.getLogger(__name__)


class ImprovementGuidanceEngine:
    """Identifies highest-leverage gaps and suggests concrete improvement actions"""

    def __init__(self, scoring_engine: ScoringEngine):
        """Initialize the improvement guidance engine"""
        self.scoring_engine = scoring_engine
        logger.info("Improvement guidance engine initialized")

    def generate_improvement_guidance(
        self,
        profile: EntrepreneurProfile,
        score_breakdown: ScoreBreakdown
    ) -> Dict[str, ImprovementGuidance]:
        """
        Generate improvement guidance for each composite score

        Args:
            profile: EntrepreneurProfile used for scoring
            score_breakdown: ScoreBreakdown containing all scores and sub-criteria

        Returns:
            Dictionary mapping score names to their improvement guidance
        """
        logger.info("Generating improvement guidance for all scores")
        guidance = {}

        # Generate guidance for each composite score
        for score_name in ["market", "commercial_offer", "innovation", "scalability", "green"]:
            guidance_item = self._generate_score_guidance(profile, score_name, score_breakdown)
            guidance[score_name] = guidance_item

        return guidance

    def _generate_score_guidance(
        self,
        profile: EntrepreneurProfile,
        score_name: str,
        score_breakdown: ScoreBreakdown
    ) -> ImprovementGuidance:
        """
        Generate improvement guidance for a specific composite score

        Args:
            profile: EntrepreneurProfile
            score_name: Name of the score (market, commercial_offer, etc.)
            score_breakdown: Complete score breakdown

        Returns:
            ImprovementGuidance object with action, impact, and KB reference
        """
        # Get current score and sub-criteria
        current_score = getattr(score_breakdown, score_name)
        sub_criteria = getattr(score_breakdown, f"{score_name}_sub_criteria", {})
        max_possible = self._get_max_possible_score(score_name)

        # If no sub-criteria, return default guidance
        if not sub_criteria:
            return ImprovementGuidance(
                action="Complete the entrepreneurial profile to enable detailed analysis.",
                estimated_impact=max_possible - current_score,
                kb_reference="general_onboarding"
            )

        # Find the sub-criterion with the biggest gap (lowest score relative to max)
        biggest_gap = None
        biggest_gap_score = float('inf')
        biggest_gap_max = 0

        for criterion_id, criterion_score in sub_criteria.items():
            criterion_max = self._get_criterion_max_score(score_name, criterion_id)
            gap = criterion_max - criterion_score

            if gap > (biggest_gap_max - biggest_gap_score if biggest_gap else float('inf')):
                biggest_gap = criterion_id
                biggest_gap_score = criterion_score
                biggest_gap_max = criterion_max

        # Calculate estimated impact if this gap is closed
        estimated_impact = biggest_gap_max - biggest_gap_score if biggest_gap else 0

        # Generate concrete action linked to knowledge base
        action = self._generate_concrete_action(profile, score_name, biggest_gap)

        # Get knowledge base reference
        kb_reference = self._get_kb_reference(score_name, biggest_gap)

        return ImprovementGuidance(
            action=action,
            estimated_impact=round(estimated_impact, 1),
            kb_reference=kb_reference
        )

    def _get_max_possible_score(self, score_name: str) -> float:
        """Get maximum possible score for a composite"""
        max_scores = {
            "market": 100.0,
            "commercial_offer": 100.0,
            "innovation": 100.0,
            "scalability": 100.0,
            "green": 100.0
        }
        return max_scores.get(score_name, 100.0)

    def _get_criterion_max_score(self, score_name: str, criterion_id: str) -> float:
        """Get maximum possible score for a specific criterion"""
        # Extract max points from scoring config (simplified)
        criterion_points = {
            "market": {
                "addressable_market_size": 25.0,
                "competitive_landscape": 20.0,
                "customer_validation_evidence": 35.0,
                "revenue_model_clarity": 20.0
            },
            "commercial_offer": {
                "value_proposition_clarity": 20.0,
                "differentiation": 20.0,
                "product_service_maturity": 20.0,
                "pricing_strategy": 20.0,
                "offer_need_alignment": 20.0
            },
            "innovation": {
                "local_novelty": 25.0,
                "technology_intensity": 20.0,
                "barrier_to_entry": 20.0,
                "departure_from_existing": 15.0,
                "ip_protection": 20.0
            },
            "scalability": {
                "replicability_without_linear_cost": 25.0,
                "manual_dependency": 20.0,
                "deployment_cost_structure": 20.0,
                "geographic_addressability": 15.0,
                "automation_potential": 20.0
            },
            "green": {
                "environmental_impact_assessment": 20.0,
                "sdg_alignment": 20.0,
                "resource_efficiency": 20.0,
                "circular_economy_practices": 20.0,
                "carbon_footprint_awareness": 10.0,
                "sustainable_sourcing": 10.0
            }
        }

        return criterion_points.get(score_name, {}).get(criterion_id, 20.0)

    def _generate_concrete_action(
        self,
        profile: EntrepreneurProfile,
        score_name: str,
        criterion_id: Optional[str]
    ) -> str:
        """Generate a concrete action based on profile and gap"""
        if not criterion_id:
            return "Complete more sections of your entrepreneurial profile to enable specific guidance."

        actions_map = {
            "market": {
                "addressable_market_size": "Réalisez une étude de marché quantifiant votre marché adresseable et son potentiel de croissance à 3-5 ans.",
                "competitive_landscape": "Documentez une analyse concurrentielle détaillant vos principaux concurrents, leurs forces/faiblesses et votre positionnement différentiel.",
                "customer_validation_evidence": "Organisez et documentez des entretiens structurés avec au moins 10 utilisateurs potentiels ou obtenez des lettres d'intention signées.",
                "revenue_model_clarity": "Testez votre modèle de revenus avec des clients pilotes et documentez les résultats montrant une volonté de payer."
            },
            "commercial_offer": {
                "value_proposition_clarity": "Formulez clairement votre proposition de valeur en une phrase et testez-là avec 20 clients cible pour valider sa compréhension et son appeal.",
                "differentiation": "Identifiez 3 facteurs qui vous différencient de manière sostenible de vos 3 principaux concurrents et documentez les preuves de ces avantages.",
                "product_service_maturity": "Développez un prototype fonctionnel ou MVP de votre solution et testez-le avec au moins 15 utilisateurs pour obtenir des retours quantifiables.",
                "pricing_strategy": "Expérimentez avec 3 modèles de tarification différents auprès de votre marché cible et mesurez le taux de conversion et la valeur client sur la durée (LTV).",
                "offer_need_alignment": "Conduisez une enquête de satisfaction auprès de vos 20 premiers clients et utilisez les retours pour améliorer l'alignement offre-besoin."
            },
            "innovation": {
                "local_novelty": "Étudiez 5 solutions similaires disponibles localement et documentez en quoi votre approche apporte une nouveauté significative ou une amélioration substantielle.",
                "technology_intensity": "Identifiez une technologie émergente pertinente pour votre secteur et élaborez un plan d'intégration progressif sur les 6 prochains mois.",
                "barrier_to_entry": "Consultez un avocat spécialisé en propriété intellectuelle pour évaluer quels aspects de votre innovation peuvent être protégés et comment.",
                "departure_from_existing": "Organisez un atelier avec 10 utilisateurs potentiels pour comparer votre solution aux alternatives existantes et quantifier la valeur ajoutée perçue.",
                "ip_protection": "Déposez une demande de protection provisoire (brevet, dessin industriel, ou droit d'auteur) pour l'aspect le plus innovant de votre solution."
            },
            "scalability": {
                "replicability_without_linear_cost": "Standardisez votre processus de production/service pour réduire de 30% le coût unitaire lorsque vous doublez votre volume.",
                "manual_dependency": "Automatisez une tâche manuelle répétitive consommant plus de 5 heures par semaine et documentez les procédures résultantes.",
                "deployment_cost_structure": "Négociez avec vos fournisseurs principaux pour réduire de 20% vos coûts de déploiement ou identifiez des alternatives plus économiques.",
                "geographic_addressability": "Élaborer un plan d'expansion géographique progressif commençant par une ville pilote dans un gouvernorat voisin.",
                "automation_potential": "Cartographiez vos processus opérationnels et identifiez 3 opportunités d'automatisation avec un ROI estimé supérieur à 12 mois."
            },
            "green": {
                "environmental_impact_assessment": "Réalisez une évaluation préliminaire de votre impact environnemental sur les domaines de consommation d'énergie, production de déchets et utilisation d'eau.",
                "sdg_alignment": "Identifiez 2 Objectifs de Développement Durable pertinents pour votre secteur et définissez des indicateurs mesurables de votre contribution à chacun.",
                "resource_efficiency": "Mesurez votre taux d'utilisation des matières premières et identifiez une opportunité de réduction de gaspillage de 15%.",
                "circular_economy_practices": "Mettez en place un système de récupération et de réutilisation pour au moins un flux de déchets ou de sous-produit de votre processus.",
                "carbon_footprint_awareness": "Mesurez votre empreinte carbone de base (scope 1 et 2) en utilisant une méthodologie reconnue et fixez un objectif de réduction de 10% sur 12 mois.",
                "sustainable_sourcing": "Évaluez vos 5 principaux fournisseurs selon des critères environnementaux et sociaux et augmentez la proportion de ceux meeting vos standards de 30%."
            }
        }

        if score_name in actions_map and criterion_id in actions_map[score_name]:
            return actions_map[score_name][criterion_id]
        return f"Améliorez votre performance sur le critère {criterion_id} lié au domaine {score_name}."

    def _get_kb_reference(self, score_name: str, criterion_id: Optional[str]) -> str:
        """Get knowledge base reference for the improvement action"""
        kb_map = {
            "market": {
                "addressable_market_size": "kb/market_analysis_bfpme",
                "competitive_landscape": "kb/competitive_analysis_template",
                "customer_validation_evidence": "kb/customer_interview_guide",
                "revenue_model_clarity": "kb/business_model_canvas"
            },
            "commercial_offer": {
                "value_proposition_clarity": "kb/value_prop_canvas",
                "differentiation": "kb/differentiation_framework",
                "product_service_maturity": "kb/mvp_development_guide",
                "pricing_strategy": "kb/pricing_strategy_toolkit",
                "offer_need_alignment": "kb/product_market_fit_survey"
            },
            "innovation": {
                "local_novelty": "kb/innovation_assessment_toolkit",
                "technology_intensity": "kb/tech_trends_sector_specific",
                "barrier_to_entry": "kb/ip_protection_guide_tn",
                "departure_from_existing": "kb/blue_ocean_strategy_intro",
                "ip_protection": "kb/ip_filing_process_tunisia"
            },
            "scalability": {
                "replicability_without_linear_cost": "kb/operations_scale_readiness",
                "manual_dependency": "kb/process_automation_guide",
                "deployment_cost_structure": "kb/cost_optimization_sme",
                "geographic_addressability": "kb/geographic_expansion_framework",
                "automation_potential": "kb/automation_opportunity_assessment"
            },
            "green": {
                "environmental_impact_assessment": "kb/environmental_impact_assessment_sme",
                "sdg_alignment": "kb/sdg_business_integration_guide",
                "resource_efficiency": "kb/resource_efficiency_manufacturing",
                "circular_economy_practices": "kb/circular_economy_business_models",
                "carbon_footprint_awareness": "kb/carbon_footprint_measurement_sme",
                "sustainable_sourcing": "kb/sustainable_sourcing_checklist"
            }
        }

        if score_name in kb_map and criterion_id in kb_map[score_name]:
            return kb_map[score_name][criterion_id]
        return "kb/general_entrepreneurship"
