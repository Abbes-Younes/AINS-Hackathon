"""
Anomaly Detector for Feature 2: Explainable Multi-Dimensional Scoring
Detects contradictory or unsubstantiated signals in entrepreneur profiles
"""

from typing import Dict, Any, List, Tuple
import logging
from pathlib import Path

from src.models.profile import EntrepreneurProfile
from src.models.scoring import Anomaly

logger = logging.getLogger(__name__)


class AnomalyDetector:
    """Detects anomalies and inconsistencies in entrepreneur profile data"""

    def __init__(self):
        """Initialize the anomaly detector with predefined rules"""
        self.anomaly_rules = self._define_anomaly_rules()
        logger.info("Anomaly detector initialized")

    def _define_anomaly_rules(self) -> List[Dict[str, Any]]:
        """
        Define hardcoded consistency rules for anomaly detection

        Returns:
            List of anomaly rule definitions
        """
        return [
            {
                "id": "high_claim_low_validation",
                "description": "Claims high traction but has low validation evidence",
                "condition": lambda p: self._get_traction_claim(p) == "high" and p.validation_client < 3,
                "severity": "high",
                "criteria_pair": ["claimed_traction", "validation_client"],
                "explanation": "Vous prétendez avoir une forte traction mais vos preuves de validation client sont faibles ou inexistantes."
            },
            {
                "id": "high_scalability_claim_manual_dependency",
                "description": "Claims high scalability but reports high manual dependency",
                "condition": lambda p: self._get_scalability_score_from_profile(p) > 0.8 and self._get_manual_dependency_level(p) == "high",
                "severity": "high",
                "criteria_pair": ["scalability_claim", "manual_dependency"],
                "explanation": "Vous prétendez avoir un modèle hautement scalable mais votre activité dépend fortement de processus manuels."
            },
            {
                "id": "fundraising_claim_low_market_score",
                "description": "Self-assessed at fundraising stage but has low market score",
                "condition": lambda p: p.self_assessed_stage == "fundraising" and self._get_market_score_from_profile(p) < 0.4,
                "severity": "high",
                "criteria_pair": ["self_assessed_stage", "market_score"],
                "explanation": "Vous vous auto-évaluez au stade de levée de fonds mais votre score marché est faible (< 40%), ce qui suggère unpreparedness for fundraising."
            },
            {
                "id": "high_innovation_claim_low_tech_readiness",
                "description": "Claims high innovation but has low technology readiness",
                "condition": lambda p: self._get_innovation_claim_from_profile(p) == "high" and p.tech_readiness_level < 3,
                "severity": "medium",
                "criteria_pair": ["innovation_claim", "tech_readiness_level"],
                "explanation": "Vous prétendez avoir une forte innovation mais votre niveau de préparation technologique est faible (TRL < 3)."
            },
            {
                "id": "no_validation_claims_paying_customers",
                "description": "Claims paying customers but has no validation evidence",
                "condition": lambda p: p.has_paying_customers == True and p.validation_client == 0,
                "severity": "high",
                "criteria_pair": ["has_paying_customers", "validation_client"],
                "explanation": "Vous prétendez avoir des clients payants mais aucune preuve de validation client n'est disponible."
            },
            {
                "id": "high_revenue_no_business_model",
                "description": "Reports high revenue but has undefined business model",
                "condition": lambda p: p.monthly_revenue > 5000 and p.business_model_clarity < 3,
                "severity": "medium",
                "criteria_pair": ["monthly_revenue", "business_model_clarity"],
                "explanation": "Vous rapportez des revenus élevés mais votre modèle d'affaires est peu clair ou non documenté."
            },
            {
                "id": "tech_sector_low_digital_presence",
                "description": "Tech sector business but low digital presence",
                "condition": lambda p: p.sector == "tech" and (not p.has_website and not p.uses_digital_tools),
                "severity": "medium",
                "criteria_pair": ["sector", "digital_presence"],
                "explanation": "Vous êtes dans le secteur technologique mais vous avez une faible présence numérique (pas de site web ou d'outils numériques)."
            },
            {
                "id": "claimed_growth_low_revenue",
                "description": "Self-assessed at growth stage but has low or no revenue",
                "condition": lambda p: p.self_assessed_stage == "growth" and p.monthly_revenue < 1000,
                "severity": "high",
                "criteria_pair": ["self_assessed_stage", "monthly_revenue"],
                "explanation": "Vous vous auto-évaluez au stade de croissance mais vos revenus sont faibles ou nuls (< 1000 TND/mois)."
            },
            {
                "id": "innovation_sector_low_ip",
                "description": "Innovation-focused sector but no IP or R&D",
                "condition": lambda p: p.sector == "tech" and not p.has_ip and not p.has_rd,
                "severity": "medium",
                "criteria_pair": ["sector", "ip_rd"],
                "explanation": "Vous êtes dans le secteur tecnologique mais vous n'avez ni propriété intellectuelle ni activités de R&D."
            }
        ]

    def detect_anomalies(self, profile: EntrepreneurProfile) -> List[Anomaly]:
        """
        Detect anomalies in the entrepreneur profile

        Args:
            profile: EntrepreneurProfile to analyze

        Returns:
            List of detected anomalies
        """
        logger.info(f"Detecting anomalies for project: {profile.project_name}")
        anomalies = []

        for rule in self.anomaly_rules:
            try:
                if rule["condition"](profile):
                    anomaly = Anomaly(
                        description=rule["explanation"],
                        criteria_pair=rule["criteria_pair"],
                        severity=rule["severity"]
                    )
                    anomalies.append(anomaly)
                    logger.debug(f"Anomaly detected: {rule['id']} - {rule['explanation']}")
            except Exception as e:
                logger.warning(f"Error evaluating anomaly rule {rule['id']}: {e}")

        logger.info(f"Detected {len(anomalies)} anomalies")
        return anomalies

    # Helper methods for anomaly detection conditions
    def _get_traction_claim(self, profile: EntrepreneurProfile) -> str:
        """Extract traction claim from profile"""
        if profile.has_traction:
            return "high"
        elif profile.has_pilot:
            return "medium"
        elif profile.validation_client >= 5:
            return "medium"
        elif profile.validation_client >= 2:
            return "low"
        else:
            return "none"

    def _get_scalability_score_from_profile(self, profile: EntrepreneurProfile) -> float:
        """Estimate scalability score from profile indicators"""
        score = 0.0
        # Digital business gets points
        if profile.sector == "tech":
            score += 0.3
        if profile.uses_digital_tools:
            score += 0.2
        if profile.has_website:
            score += 0.2
        if not profile.has_full_time_team:  # Less team dependency = more scalable
            score += 0.1
        if profile.monthly_revenue > 0:
            score += 0.2  # Revenue generation indicates scalability
        return min(score, 1.0)

    def _get_manual_dependency_level(self, profile: EntrepreneurProfile) -> str:
        """Determine manual dependency level"""
        automation_score = sum([profile.uses_digital_tools, profile.has_website, profile.has_social_media])
        if automation_score >= 2:
            return "low"
        elif automation_score >= 1:
            return "medium"
        else:
            return "high"

    def _get_market_score_from_profile(self, profile: EntrepreneurProfile) -> float:
        """Estimate market score from profile"""
        # Use validation and revenue as proxies
        validation_score = min(profile.validation_client / 10.0, 1.0)
        revenue_score = min(profile.monthly_revenue / 10000.0, 1.0)  # Normalize to 10k TND
        return (validation_score * 0.6) + (revenue_score * 0.4)

    def _get_innovation_claim_from_profile(self, profile: EntrepreneurProfile) -> str:
        """Estimate innovation claim from profile"""
        innovation_indicators = sum([
            1 if profile.has_ip else 0,
            1 if profile.has_rd else 0,
            1 if profile.tech_readiness_level >= 6 else 0,
            1 if profile.has_sustainability_plan else 0
        ])
        if innovation_indicators >= 3:
            return "high"
        elif innovation_indicators >= 2:
            return "medium"
        elif innovation_indicators >= 1:
            return "low"
        else:
            return "none"
