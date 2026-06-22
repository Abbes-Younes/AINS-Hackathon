"""
Conversational Layer for Feature 3: RAG-Grounded Roadmap & Resource Orientation
Provides grounded conversational assistance constrained to reference diagnostic data, scores, and KB resources.
"""

import logging
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path

# Add project root to path for importing models and services
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from src.models.diagnostic import DiagnosticResult
from src.models.scoring import ScoreResult
from src.models.roadmap import ResourceOrientation
from src.feature_3_rag.retrieval_engine import RetrievalEngine
from src.feature_3_rag.query_generator import QueryGenerator

logger = logging.getLogger(__name__)


class ConversationalLayer:
    """Provides grounded conversational assistance for entrepreneurs."""

    def __init__(self):
        """Initialize the conversational layer."""
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.info("Conversational layer initialized")

        # Initialize subcomponents
        self.query_generator = QueryGenerator()
        self.retrieval_engine = RetrievalEngine()

    def generate_response(
        self,
        user_query: str,
        diagnostic_result: DiagnosticResult,
        score_result: ScoreResult,
        roadmap: Optional[ResourceOrientation] = None,
    ) -> Tuple[str, List[Dict[str, Any]]]:
        """
        Generate a grounded response to user query based on diagnostic data and knowledge base.

        Args:
            user_query: The user's question or request
            diagnostic_result: Diagnostic output from Feature 1
            score_result: Scoring output from Feature 2
            roadmap: Optional pre-generated roadmap for context

        Returns:
            Tuple of (response_text, sources_used) where sources_used are KB resources referenced
        """
        self.logger.info(f"Generating grounded response for query: '{user_query[:50]}...'")

        # Generate query and retrieve relevant resources
        query_string, structured_filters = self.query_generator.generate_query(
            diagnostic_result=diagnostic_result,
            score_result=score_result,
        )

        # Enhance query with user intent
        enhanced_query = f"{user_query} {query_string}"

        # Retrieve relevant resources
        resources = self.retrieval_engine.hybrid_retrieve(
            query_text=enhanced_query,
            eligibility_stages=structured_filters.get("eligibility_stages"),
            domains_addressed=structured_filters.get("domains_addressed"),
            blockers_resolved=structured_filters.get("blockers_resolved"),
            limit=5,  # Top 5 resources for grounding
        )

        # Generate grounded response
        response_text = self._create_grounded_response(
            user_query=user_query,
            diagnostic_result=diagnostic_result,
            score_result=score_result,
            roadmap=roadmap,
            resources=resources,
        )

        # Validate response is sufficiently grounded
        if not self._is_response_grounded(response_text, diagnostic_result, score_result, resources):
            # Fallback to structured response if not grounded enough
            response_text = self._generate_fallback_response(
                diagnostic_result=diagnostic_result,
                score_result=score_result,
                roadmap=roadmap,
            )

        self.logger.info(f"Generated response with {len(resources)} sources")
        return response_text, resources

    def _create_grounded_response(
        self,
        user_query: str,
        diagnostic_result: DiagnosticResult,
        score_result: ScoreResult,
        roadmap: Optional[ResourceOrientation],
        resources: List[Dict[str, Any]],
    ) -> str:
        """Create a response grounded in diagnostic data, scores, and KB resources."""
        # Start with acknowledgment of user query
        response_parts = []

        # Add diagnostic context
        stage = diagnostic_result.assigned_stage
        response_parts.append(f"Based on your {stage}-stage diagnosis:")

        # Add perception gap info if relevant
        if diagnostic_result.perception_gap:
            gap = diagnostic_result.perception_gap
            if gap.gap_type == "OVER_ESTIMATION":
                response_parts.append(f"You perceive yourself at {gap.claimed_stage} stage, but evidence suggests {gap.actual_stage} stage.")
            elif gap.gap_type == "UNDER_ESTIMATION":
                response_parts.append(f"You perceive yourself at {gap.claimed_stage} stage, but evidence suggests {gap.actual_stage} stage.")

        # Add score context if relevant to query
        if score_result.composites:
            # Find lowest scoring dimension
            if score_result.composites:
                weakest = min(score_result.composites.items(), key=lambda x: x[1].percentage)
                response_parts.append(f"Your {weakest[1].label.lower()} score is {weakest[1].percentage:.0f}/100, indicating this is a key area for development.")

        # Add blocker context if relevant
        if diagnostic_result.key_blockers:
            blocker_names = []
            for blocker in diagnostic_result.key_blockers[:2]:  # Top 2 blockers
                if isinstance(blocker, dict):
                    blocker_names.append(blocker.get("name", ""))
                else:
                    blocker_names.append(str(blocker))
            if blocker_names:
                response_parts.append(f"Key blockers identified: {', '.join(blocker_names)}.")

        # Add resource recommendations if available
        if resources:
            response_parts.append("\nRecommended resources:")
            for i, resource in enumerate(resources[:3], 1):  # Top 3 resources
                name = resource.get("name", "Unknown")
                operator = resource.get("operator", "Unknown")
                relevance = resource.get("relevance_score", 0.0)
                response_parts.append(
                    f"{i}. {name} by {operator} (relevance: {relevance:.0%}) - "
                    f"{resource.get('description', '')[:100]}..."
                )

        # Add roadmap guidance if available
        if roadmap and roadmap.milestones:
            immediate_milestone = next((m for m in roadmap.milestones if m.title == "Immediate"), None)
            if immediate_milestone and immediate_milestone.actions:
                action_texts = [a.action_text for a in immediate_milestone.actions[:2]]  # Top 2 immediate actions
                response_parts.append(f"\nImmediate next steps: {'; '.join(action_texts)}.")

        # Add grounding statement
        response_parts.append("\nThis guidance is grounded in your diagnostic assessment, scoring results, and verified Tunisian entrepreneurship resources.")

        return " ".join(response_parts)

    def _is_response_grounded(
        self,
        response: str,
        diagnostic_result: DiagnosticResult,
        score_result: ScoreResult,
        resources: List[Dict[str, Any]],
    ) -> bool:
        """Check if response is sufficiently grounded in diagnostic data, scores, or KB resources."""
        # Simple heuristic: response should contain specific references to user's data
        grounded_indicators = 0

        # Check for stage reference
        if diagnostic_result.assigned_stage.lower() in response.lower():
            grounded_indicators += 1

        # Check for dimension references from scores
        if score_result.composites:
            for dim_key in score_result.composites.keys():
                if dim_key.replace('_', ' ') in response.lower():
                    grounded_indicators += 1
                    break  # Only need one dimension reference

        # Check for blocker references
        if diagnostic_result.key_blockers:
            for blocker in diagnostic_result.key_blockers:
                blocker_name = blocker.get("name", "") if isinstance(blocker, dict) else str(blocker)
                if blocker_name.lower() in response.lower():
                    grounded_indicators += 1
                    break  # Only need one blocker reference

        # Check for resource references
        for resource in resources:
            resource_name = resource.get("name", "").lower()
            if resource_name and resource_name in response.lower():
                grounded_indicators += 1
                break  # Only need one resource reference

        # Require at least 2 grounded indicators for sufficient grounding
        return grounded_indicators >= 2

    def _generate_fallback_response(
        self,
        diagnostic_result: DiagnosticResult,
        score_result: ScoreResult,
        roadmap: Optional[ResourceOrientation],
    ) -> str:
        """Generate a fallback response when grounded response is not sufficient."""
        response_parts = [
            "Based on your entrepreneurial assessment:",
            f"- Current stage: {diagnostic_result.assigned_stage}",
        ]

        if diagnostic_result.perception_gap:
            gap = diagnostic_result.perception_gap
            response_parts.append(
                f"- Perception gap: You see yourself at {gap.claimed_stage}, "
                f"but evidence places you at {gap.actual_stage}"
            )

        if score_result.composites:
            weakest = min(score_result.composites.items(), key=lambda x: x[1].percentage)
            response_parts.append(
                f"- Primary development area: {weakest[1].label.lower()} "
                f"({weakest[1].percentage:.0f}/100)"
            )

        if diagnostic_result.key_blockers:
            blocker_names = []
            for blocker in diagnostic_result.key_blockers[:3]:
                blocker_name = blocker.get("name", "") if isinstance(blocker, dict) else str(blocker)
                if blocker_name:
                    blocker_names.append(blocker_name)
            if blocker_names:
                response_parts.append(f"- Key blockers: {', '.join(blocker_names)}")

        response_parts.append(
            "\nFor specific resource recommendations and action steps, "
            "please refer to your personalized roadmap or ask more specific questions "
            "about your stage, scores, or identified blockers."
        )

        return " ".join(response_parts)

    def close(self):
        """Close database connections."""
        if hasattr(self, 'retrieval_engine'):
            self.retrieval_engine.close()
        self.logger.info("Conversational layer connections closed")