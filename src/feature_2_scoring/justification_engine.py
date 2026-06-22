"""
Justification Engine for Feature 2: Explainable Multi-Dimensional Scoring
Generates plain-language explanations for scores using LLM with tight constraints
"""

import json
import logging
import os
from typing import Dict, Any, Optional, Tuple
from pathlib import Path

from src.models.profile import EntrepreneurProfile
from src.models.scoring import ScoreBreakdown, Justification
from src.feature_2_scoring.scoring_engine import ScoringEngine

logger = logging.getLogger(__name__)


class JustificationEngine:
    """Generates plain-language justifications for scoring results"""

    def __init__(self, scoring_engine: ScoringEngine):
        """Initialize the justification engine"""
        self.scoring_engine = scoring_engine
        # In a real implementation, this would connect to an LLM service
        # For now, we'll use template-based explanations
        logger.info("Justification engine initialized")

    def generate_justifications(
        self,
        profile: EntrepreneurProfile,
        score_breakdown: ScoreBreakdown
    ) -> Dict[str, Justification]:
        """
        Generate plain-language justifications for each composite score

        Args:
            profile: EntrepreneurProfile used for scoring
            score_breakdown: ScoreBreakdown containing all scores and sub-criteria

        Returns:
            Dictionary mapping score names to their justifications
        """
        logger.info("Generating justifications for all scores")
        justifications = {}

        # Generate justification for each composite score
        for score_name in ["market", "commercial_offer", "innovation", "scalability", "green"]:
            justification = self._generate_score_justification(profile, score_name, score_breakdown)
            justifications[score_name] = justification

        return justifications

    def _generate_score_justification(
        self,
        profile: EntrepreneurProfile,
        score_name: str,
        score_breakdown: ScoreBreakdown
    ) -> Justification:
        """
        Generate justification for a specific composite score

        Args:
            profile: EntrepreneurProfile
            score_name: Name of the score (market, commercial_offer, etc.)
            score_breakdown: Complete score breakdown

        Returns:
            Justification object with explanation and supporting details
        """
        # Get the score details
        score_value = getattr(score_breakdown, score_name)
        sub_criteria = getattr(score_breakdown, f"{score_name}_sub_criteria", {})

        # Find the lowest and highest contributing sub-criteria
        if sub_criteria:
            sorted_criteria = sorted(sub_criteria.items(), key=lambda x: x[1])
            lowest_criterion = sorted_criteria[0] if sorted_criteria else None
            highest_criterion = sorted_criteria[-1] if sorted_criteria else None
        else:
            lowest_criterion = highest_criterion = None

        # Generate explanation based on score value and profile data
        explanation = self._template_based_explanation(
            profile, score_name, score_value, sub_criteria, lowest_criterion, highest_criterion
        )

        # Identify what needs improvement (lowest scoring sub-criterion)
        needs_improvement = lowest_criterion[0] if lowest_criterion else None
        improvement_suggestion = self._get_improvement_suggestion(
            profile, score_name, needs_improvement
        ) if needs_improvement else None

        # Supporting evidence (key data points that influenced the score)
        supporting_evidence = self._get_supporting_evidence(profile, score_name)

        return Justification(
            explanation=explanation,
            needs_improvement=needs_improvement,
            improvement_suggestion=improvement_suggestion,
            supporting_evidence=supporting_evidence
        )

    def _template_based_explanation(
        self,
        profile: EntrepreneurProfile,
        score_name: str,
        score_value: float,
        sub_criteria: Dict[str, float],
        lowest_criterion: Optional[Tuple[str, float]],
        highest_criterion: Optional[Tuple[str, float]]
    ) -> str:
        """
        Generate template-based explanation (placeholder for LLM)
        In production, this would use a tightly constrained LLM prompt
        """
        score_labels = {
            "market": "Marché",
            "commercial_offer": "Offre Commerciale",
            "innovation": "Innovation",
            "scalability": "Scalabilité",
            "green": "Green / Impact Environnemental"
        }

        label = score_labels.get(score_name, score_name)
        score_int = int(round(score_value))

        # Base explanation
        if score_value >= 80:
            quality = "excellent"
        elif score_value >= 60:
            quality = "bonne"
        elif score_value >= 40:
            quality = "modérée"
        else:
            quality = "insuffisante"

        explanation_parts = [
            f"Votre score {label.lower()} est de {score_int}/100, ce qui est considéré comme {quality}."
        ]

        # Add specific details based on strongest/weakest areas
        if highest_criterion and lowest_criterion:
            highest_name, highest_score = highest_criterion
            lowest_name, lowest_score = lowest_criterion

            # Map criterion IDs to readable names
            criterion_names = self._get_criterion_names(score_name)
            highest_readable = criterion_names.get(highest_name, highest_name)
            lowest_readable = criterion_names.get(lowest_name, lowest_name)

            explanation_parts.append(
                f"Votre point fort est {highest_readable} ({int(highest_score)}/20 ou équivalent), "
                f" tandis que {lowest_readable} nécessite une attention particulière ({int(lowest_score)}/20 ou équivalent)."
            )

        # Add concrete example from profile data
        example = self._get_concrete_example(profile, score_name)
        if example:
            explanation_parts.append(example)

        return " ".join(explanation_parts)

    def _get_criterion_names(self, score_name: str) -> Dict[str, str]:
        """Map criterion IDs to readable names"""
        names_map = {
            "market": {
                "addressable_market_size": "taille du marché adresseable",
                "competitive_landscape": "analyse du paysage concurrentiel",
                "customer_validation_evidence": "preuves de validation client",
                "revenue_model_clarity": "clarté du modèle de revenus"
            },
            "commercial_offer": {
                "value_proposition_clarity": "clarté de la proposition de valeur",
                "differentiation": "différenciation par rapport à la concurrence",
                "product_service_maturity": "maturité du produit/service",
                "pricing_strategy": "stratégie de tarification",
                "offer_need_alignment": "alignement offre-besoin"
            },
            "innovation": {
                "local_novelty": "nouveauté dans le contexte local",
                "technology_intensity": "intensité technologique",
                "barrier_to_entry": "barrière à l'entrée pour les concurrents",
                "departure_from_existing": "écart par rapport aux offres existantes",
                "ip_protection": "protection de la propriété intellectuelle"
            },
            "scalability": {
                "replicability_without_linear_cost": "réplicabilité sans augmentation linéaire des coûts",
                "manual_dependency": "dépendance aux processus manuels",
                "deployment_cost_structure": "structure des coûts de déploiement",
                "geographic_addressability": "adressabilité géographique du marché",
                "automation_potential": "potentialité d'automatisation des opérations"
            },
            "green": {
                "environmental_impact_assessment": "évaluation de l'impact environnemental",
                "sdg_alignment": "alignement avec les Objectifs de Développement Durable (ODD)",
                "resource_efficiency": "efficacité de l'utilisation des ressources",
                "circular_economy_practices": "pratiques d'économie circulaire",
                "carbon_footprint_awareness": "conscience de l'empreinte carbone",
                "sustainable_sourcing": "approvisionnement durable"
            }
        }
        return names_map.get(score_name, {})

    def _get_concrete_example(self, profile: EntrepreneurProfile, score_name: str) -> Optional[str]:
        """Get a concrete example from the profile that illustrates the score"""
        examples = []

        if score_name == "market":
            if profile.validation_client == 0:
                examples.append("Vous n'avez actuellement aucun contact documenté avec des clients potentiels pour valider votre idée.")
            elif profile.validation_client >= 10:
                examples.append(f"Vous avez validé votre idée avec {profile.validation_client} clients, ce qui constitue une preuve solide de demande.")
            elif profile.has_paying_customers:
                examples.append("Vous avez déjà des clients payants, ce qui est un indicateur fort de validation du marché.")

        elif score_name == "innovation":
            if profile.has_ip or profile.has_rd:
                examples.append("Vous avez investi dans la propriété intellectuelle ou la R&D, ce qui renforce votre position d'innovation.")
            elif profile.tech_readiness_level >= 6:
                examples.append(f"Votre niveau de préparation technologique (TRL {profile.tech_readiness_level}) indique une avancée significative dans le développement de votre solution.")
            else:
                examples.append("Actuellement, peu d'éléments indiquent une forte innovation technologique ou de propriété intellectuelle dans votre projet.")

        elif score_name == "commercial_offer":
            if profile.business_model_clarity >= 3:
                examples.append("Vous avez un modèle de revenus clairement défini et validé, ce qui renforce votre offre commerciale.")
            elif profile.has_mvp or profile.has_pilot:
                examples.append("Vous avez au moins un prototype ou un produit testé avec des clients, démontrant la maturité de votre offre.")
            else:
                examples.append("Votre offre commerciale serait renforcée par une clarification du modèle de revenus et le développement d'un prototype testable.")

        elif score_name == "scalability":
            if profile.uses_digital_tools and profile.has_website:
                examples.append("Vous utilisez déjà des outils numériques et avez un site web, posant les bases pour une meilleure scalabilité.")
            elif profile.sector == "tech":
                examples.append("Étant dans le secteur technologique, votre modèle a un potentiel intrinsèque de scalabilité qui peut être développé.")
            else:
                examples.append("Actuellement, votre modèle montre une dépendance importante aux processus manuels, limitant sa scalabilité.")

        elif score_name == "green":
            if profile.has_sustainability_plan:
                examples.append("Vous avez déjà un plan de durabilité, ce qui montre votre engagement envers l'impact environnemental.")
            elif profile.sector in ["agri-food", "artisanat"]:
                examples.append("Votre secteur offre des opportunités naturelles pour intégrer des pratiques durables et circulaires.")
            else:
                examples.append("Intégrer une évaluation d'impact environnemental et des pratiques d'économie circulaire pourrait renforcer votre score green.")

        return examples[0] if examples else None

    def _get_improvement_suggestion(
        self,
        profile: EntrepreneurProfile,
        score_name: str,
        criterion_id: Optional[str]
    ) -> Optional[str]:
        """Get specific improvement suggestion for a criterion"""
        suggestions_map = {
            "market": {
                "customer_validation_evidence": "Documentez vos entretiens avec des clients potentiels et cherchez à obtenir des lettres d'intention ou des premiers clients payants.",
                "addressable_market_size": "Réalisez une étude de marché pour mieux quantifier votre marché adresseable et son potentiel de croissance.",
                "competitive_landscape": "Analysez vos concurrents principaux et identifiez vos avantages différentiels durables.",
                "revenue_model_clarity": "Testez différents modèles de revenus avec vos clients potentiels et documentez celui qui fonctionne le mieux."
            },
            "commercial_offer": {
                "value_proposition_clarity": "Testez votre proposition de valeur avec des clients cible et refinez-la basée sur leurs retours.",
                "differentiation": "Identifiez clairement ce qui vous distingue de la concurrence et communiquez-le efficacement.",
                "product_service_maturity": "Développez un produit minimum viable (MVP) et testez-le avec des utilisateurs réels.",
                "pricing_strategy": "Expérimentez différentes stratégies de tarification et mesurez l'acceptation client.",
                "offer_need_alignment": "Validez régulièrement que votre offre répond bien aux besoins exprimés par vos clients."
            },
            "innovation": {
                "local_novelty": "Étudiez les solutions existantes localement et identifiez comment votre approche apporte quelque chose de nouveau.",
                "technology_intensity": "Explorez comment intégrer davantage de technologies pertinentes dans votre solution.",
                "barrier_to_entry": "Considérez des mécanismes de protection comme la propriété intellectuelle ou des partenariats exclusifs.",
                "departure_from_existing": "Pensez à comment votre solution transforme fondamentalement l'approche actuelle du problème.",
                "ip_protection": "Consultez un spécialiste en propriété intellectuelle pour évaluer ce qui peut être protégé dans votre innovation."
            },
            "scalability": {
                "replicability_without_linear_cost": "Standardisez vos processus pour réduire le coût unitaire lorsque vous augmentez la production.",
                "manual_dependency": "Automatisez les tâches répétitives et documentes vos procédures pour réduire la dépendance au travail manuel.",
                "deployment_cost_structure": "Optimisez vos coûts de déploiement en cherchant des solutions plus économiques ou en échelonnant vos investissements.",
                "geographic_addressability": "Étudiez les possibilités d'expansion géographique progressive de votre marché.",
                "automation_potential": "Identifiez les opérations qui pourraient être automatisées et élaborez une feuille de route pour y parvenir."
            },
            "green": {
                "environmental_impact_assessment": "Réalisez une première évaluation de votre impact environnemental, même simplifiée, pour identifier les axes d'amélioration.",
                "sdg_alignment": "Identifiez lesquels des Objectifs de Développement Durable sont pertinents pour votre activité et comment vous pouvez y contribuer.",
                "resource_efficiency": "Analysez votre utilisation des ressources et cherchez des moyens de réduire le gaspillage.",
                "circular_economy_practices": "Intégrez des principes de réduction, réutilisation et recyclage dans votre modèle d'affaires.",
                "carbon_footprint_awareness": "Mesurez votre empreinte carbone de base et fixez-vous des objectifs de réduction réalistes.",
                "sustainable_sourcing": "Évaluez vos fournisseurs actuels et privilégiez ceux ayant des pratiques durables."
            }
        }

        if score_name in suggestions_map and criterion_id in suggestions_map[score_name]:
            return suggestions_map[score_name][criterion_id]
        return None

    def _get_supporting_evidence(self, profile: EntrepreneurProfile, score_name: str) -> List[str]:
        """Get key data points that support the score"""
        evidence = []

        if score_name == "market":
            evidence.append(f"Nombre de clients validés: {profile.validation_client}")
            evidence.append(f"A des clients payants: {profile.has_paying_customers}")
            evidence.append(f"Clarté du modèle de revenus: {profile.business_model_clarity}/4")

        elif score_name == "innovation":
            evidence.append(f"Niveau de préparation technologique (TRL): {profile.tech_readiness_level}")
            evidence.append(f"A de la propriété intellectuelle: {profile.has_ip}")
            evidence.append(f"Fait de la R&D: {profile.has_rd}")
            evidence.append(f"A un plan de durabilité: {profile.has_sustainability_plan}")

        elif score_name == "commercial_offer":
            evidence.append(f"Clarté du modèle de revenus: {profile.business_model_clarity}/4")
            evidence.append(f"A un MVP: {profile.has_mvp}")
            evidence.append(f"A fait un pilote: {profile.has_pilot}")
            evidence.append(f"Valeur proposition testée: {getattr(profile, 'value_prop_tested', False) if hasattr(profile, 'value_prop_tested') else 'Non spécifié'}")

        elif score_name == "scalability":
            evidence.append(f"Secteur: {profile.sector}")
            evidence.append(f"Utilise des outils numériques: {profile.uses_digital_tools}")
            evidence.append(f"A un site web: {profile.has_website}")
            evidence.append(f"A des réseaux sociaux professionnels: {profile.has_social_media}")
            evidence.append(f"Revenus mensuels: {profile.monthly_revenue} TND")

        elif score_name == "green":
            evidence.append(f"A un plan de durabilité: {profile.has_sustainability_plan}")
            evidence.append(f"Secteur: {profile.sector}")
            evidence.append(f"Conscience de l'impact environnemental: {getattr(profile, 'env_impact_awareness', 'Non spécifié') if hasattr(profile, 'env_impact_awareness') else 'Non spécifié'}")

        return evidence