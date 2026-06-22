"""
Diagnostic Synthesis Module
Combines classification, gap detection, and blocker identification into final diagnostic result
"""

from typing import Dict, Any, Optional
import logging

from src.models.profile import EntrepreneurProfile
from src.models.diagnostic import DiagnosticResult
from src.engine.classifier import MaturityClassifier, ClassificationResult
from src.engine.gap_detector import GapDetector, GapAnalysis
from src.engine.blocker_identifier import BlockerIdentifier, Blocker

logger = logging.getLogger(__name__)


class DiagnosticSynthesizer:
    """Synthesizes diagnostic components into final result"""

    def __init__(self):
        """Initialize synthesizer with required components"""
        self.classifier = MaturityClassifier()
        self.gap_detector = GapDetector()
        self.blocker_identifier = BlockerIdentifier()
        logger.info("Diagnostic synthesizer initialized")

    def synthesize_diagnostic(self, profile: EntrepreneurProfile) -> DiagnosticResult:
        """
        Create complete diagnostic result from entrepreneur profile

        Args:
            profile: EntrepreneurProfile to analyze

        Returns:
            DiagnosticResult containing all diagnostic information
        """
        logger.info(f"Synthesizing diagnostic for project: {profile.project_name}")

        # Step 1: Classify maturity stage
        classification_result = self.classifier.classify(profile)
        logger.debug(f"Classification: {classification_result.assigned_stage} "
                    f"(confidence: {classification_result.confidence_score:.2f})")

        # Step 2: Detect perception-reality gap
        gap_analysis = self.gap_detector.detect_gap(profile, classification_result)
        logger.debug(f"Gap analysis: {gap_analysis.gap_type} "
                    f"(severity: {gap_analysis.gap_severity})")

        # Step 3: Identify and prioritize blockers
        blockers = self.blocker_identifier.identify_blockers(
            profile,
            gap_analysis=gap_analysis,
            assigned_stage=gap_analysis.actual_stage
        )
        logger.debug(f"Identified {len(blockers)} blockers")

        # Step 4: Generate plain-language summary (using LLM in real implementation)
        # For now, we'll create a structured summary
        plain_language_summary = self._generate_plain_language_summary(
            profile, classification_result, gap_analysis, blockers
        )

        # Step 5: Create final diagnostic result
        diagnostic_result = DiagnosticResult(
            assigned_stage=gap_analysis.actual_stage,
            confidence_score=min(classification_result.confidence_score, gap_analysis.confidence),
            perception_gap=self._gap_analysis_to_perception_gap(gap_analysis),
            key_blockers=self._blockers_to_diagnostic_format(blockers[:5]),  # Top 5 blockers
            evidence_trace=classification_result.evidence_trace,
            plain_language_summary=plain_language_summary
        )

        logger.info(f"Diagnostic synthesis complete: {diagnostic_result.assigned_stage}")
        return diagnostic_result

    def _gap_analysis_to_perception_gap(self, gap_analysis: GapAnalysis) -> Optional[Dict[str, Any]]:
        """Convert gap analysis to perception gap format"""
        if gap_analysis.gap_type == "ACCURATE" and gap_analysis.gap_severity == "NONE":
            return None  # No significant gap to report

        return {
            "gap_type": gap_analysis.gap_type,
            "claimed_stage": gap_analysis.claimed_stage,
            "actual_stage": gap_analysis.actual_stage,
            "gap_severity": gap_analysis.gap_severity,
            "explanation": gap_analysis.explanation
        }

    def _blockers_to_diagnostic_format(self, blockers: List[Blocker]) -> List[Dict[str, Any]]:
        """Convert blocker objects to diagnostic format"""
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

    def _generate_plain_language_summary(self, profile: EntrepreneurProfile,
                                       classification_result: ClassificationResult,
                                       gap_analysis: GapAnalysis,
                                       blockers: List[Blocker]) -> str:
        """
        Generate plain-language summary of diagnostic results
        In a real implementation, this would use an LLM with structured prompt
        """
        stage_names_fr = {
            "ideation": "idéation",
            "market_validation": "validation du marché",
            "structuration": "structuration",
            "fundraising": "recherche de financement",
            "launch_planning": "planification du lancement",
            "growth": "croissance"
        }

        stage_fr = stage_names_fr.get(gap_analysis.actual_stage, gap_analysis.actual_stage)

        # Start with basic assessment
        summary_parts = [
            f"Notre analyse classe votre projet au stade de {stage_fr}. ",
            f"Ce classement est basé sur {len(classification_result.evidence_trace)} éléments clés de votre profil."
        ]

        # Add gap information if present
        if gap_analysis.gap_type != "ACCURATE" or gap_analysis.gap_severity != "NONE":
            if gap_analysis.gap_type == "OVERESTIMATION":
                summary_parts.append(
                    f"Vous vous auto-évaluez au stade de {gap_analysis.claimed_stage}, "
                    f"mais notre analyse suggère que vous pourriez bénéficier de renforcer certains aspects "
                    f"avant d'atteindre ce stade."
                )
            else:  # UNDERESTIMATION
                summary_parts.append(
                    f"Vous vous auto-évaluez au stade de {gap_analysis.claimed_stage}, "
                    f"mais notre analyse révèle que vous avez déjà accompli des progrès qui vous placent "
                    f"avantageusement au stade de {stage_fr}."
                )
        else:
            summary_parts.append(
                f"Votre auto-évaluation ({gap_analysis.claimed_stage}) correspond précisément à notre analyse."
            )

        # Add blocker information if any
        if blockers:
            high_priority_blockers = [b for b in blockers if b.priority == "high"]
            if high_priority_blockers:
                summary_parts.append(
                    f"Nous avons identifié {len(high_priority_blockers)} point(s) de blocage prioritaire(s) "
                    f"qui nécessitent votre attention immédiate pour progresser vers le stade suivant."
                )
            elif len(blockers) > 0:
                summary_parts.append(
                    f"Nous avons identifié {len(blockers)} domaine(s) d'amélioration qui, une fois adressés, "
                    f"renforceront votre position au stade de {stage_fr}."
                )

        # Add encouragement and next steps
        summary_parts.append(
            f"Cette analyse vous donne une base solide pour planifier vos prochaines étapes estratégiques. "
            f"En vous concentrant sur les domaines identifiés, vous pourrez accélérer votre progression entrepreneuriale."
        )

        return " ".join(summary_parts)