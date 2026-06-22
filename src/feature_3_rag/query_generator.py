"""
Query Generator for Feature 3: RAG-Grounded Roadmap & Resource Orientation
Converts diagnostic and scoring outputs into effective knowledge base search queries.
"""

import logging
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path

# Add project root to path for importing models
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from src.models.diagnostic import DiagnosticResult, PerceptionGap, Blocker
from src.models.scoring import ScoreResult

logger = logging.getLogger(__name__)


class QueryGenerator:
    """Generates effective KB search queries from diagnostic and scoring outputs."""

    def __init__(self):
        """Initialize the query generator."""
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.info("Query generator initialized")

    def generate_query(
        self,
        diagnostic_result: DiagnosticResult,
        score_result: ScoreResult,
    ) -> Tuple[str, Dict[str, Any]]:
        """
        Generate a natural language query and structured filters from diagnostic and scoring data.

        Args:
            diagnostic_result: Diagnostic output from Feature 1
            score_result: Scoring output from Feature 2

        Returns:
            Tuple of (query_string, structured_filters)
        """
        self.logger.info("Generating KB query from diagnostic and scoring data")

        # Extract key information from diagnostic result
        stage_info = self._extract_stage_info(diagnostic_result)
        gap_info = self._extract_gap_info(diagnostic_result)
        blocker_info = self._extract_blocker_info(diagnostic_result)
        evidence_summary = self._extract_evidence_summary(diagnostic_result)

        # Extract key information from score result
        score_info = self._extract_score_info(score_result)
        anomaly_info = self._extract_anomaly_info(score_result)
        improvement_info = self._extract_improvement_info(score_result)

        # Generate query string components
        query_components = []

        # Stage-appropriate terminology
        if stage_info["assigned_stage"]:
            query_components.append(
                f"{stage_info['assigned_stage']}-stage entrepreneur"
            )

        # Sector information (would come from profile, but we'll work with what we have)
        # For now, we'll note that sector info should be available in a full implementation

        # Blocker-focused language
        if blocker_info["primary_blockers"]:
            blocker_text = ", ".join(blocker_info["primary_blockers"][:2])  # Top 2 blockers
            query_components.append(f"needing support with {blocker_text}")

        # Gap-focused language
        if gap_info["has_gap"]:
            if gap_info["gap_type"] == "OVER_ESTIMATION":
                query_components.append(
                    f"overconfident in readiness, needs validation and grounding"
                )
            elif gap_info["gap_type"] == "UNDER_ESTIMATION":
                query_components.append(
                    f"undersells capabilities, needs confidence building and recognition"
                )

        # Score-focused language - weakest dimensions
        if score_info["weakest_dimensions"]:
            weakest = score_info["weakest_dimensions"][0]  # Top weakest
            query_components.append(
                f"seeking to improve {weakest.replace('_', ' ')}"
            )

        # Anomaly-focused language
        if anomaly_info["has_anomalies"]:
            query_components.append(
                "addressing inconsistencies in self-assessment versus evidence"
            )

        # Improvement guidance language
        if improvement_info["primary_guidance"]:
            query_components.append(
                f"looking for {improvement_info['primary_guidance']}"
            )

        # Join components into a coherent query
        if not query_components:
            # Fallback query if no specific information extracted
            query_string = "Tunisian entrepreneurship support program"
        else:
            query_string = " ".join(query_components)

        # Add Tunisia context if not already present
        if "Tunisian" not in query_string and "Tunisia" not in query_string:
            query_string = "Tunisian " + query_string

        self.logger.debug(f"Generated query string: '{query_string}'")

        # Generate structured filters
        structured_filters = self._generate_structured_filters(
            diagnostic_result=diagnostic_result,
            score_result=score_result,
        )

        return query_string, structured_filters

    def _extract_stage_info(self, diagnostic_result: DiagnosticResult) -> Dict[str, Any]:
        """Extract stage-related information from diagnostic result."""
        return {
            "assigned_stage": diagnostic_result.assigned_stage,
            "claimed_stage": (
                diagnostic_result.perception_gap.claimed_stage
                if diagnostic_result.perception_gap
                else None
            ),
            "gap_present": diagnostic_result.perception_gap is not None,
        }

    def _extract_gap_info(self, diagnostic_result: DiagnosticResult) -> Dict[str, Any]:
        """Extract perception-reality gap information."""
        if not diagnostic_result.perception_gap:
            return {
                "has_gap": False,
                "gap_type": None,
                "severity": None,
                "overestimation": None,
            }

        gap = diagnostic_result.perception_gap
        return {
            "has_gap": True,
            "gap_type": gap.gap_type,
            "severity": gap.gap_severity,
            "overestimation": gap.gap_type == "OVER_ESTIMATION",
            "claimed_stage": gap.claimed_stage,
            "actual_stage": gap.actual_stage,
        }

    def _extract_blocker_info(self, diagnostic_result: DiagnosticResult) -> Dict[str, Any]:
        """Extract blocker information."""
        if not diagnostic_result.key_blockers:
            return {
                "blockers": [],
                "primary_blockers": [],
                "blocker_domains": [],
                "high_priority_blockers": [],
            }

        # blockers in DiagnosticResult are list of dicts
        blockers = diagnostic_result.key_blockers

        # Extract blocker names (assuming they have a 'name' field or similar)
        blocker_names = []
        high_priority = []
        for blocker in blockers:
            if isinstance(blocker, dict):
                name = blocker.get("name", str(blocker))
                priority = blocker.get("priority", "medium")
                blocker_names.append(name)
                if priority == "high":
                    high_priority.append(name)
            else:
                blocker_names.append(str(blocker))

        # Extract domains from blocker descriptions (simplified)
        blocker_domains = []
        domain_keywords = {
            "financial": ["funding", "finance", "capital", "investment", "revenue", "cost"],
            "legal": ["legal", "registration", "license", "permit", "compliance", "law"],
            "market": ["market", "customer", "sales", "validation", "traction"],
            "technical": ["technical", "technology", "development", "engineering", "IT"],
            "organisational": ["team", "organization", "management", "structure", "process"],
        }

        for blocker in blockers:
            if isinstance(blocker, dict):
                text = " ".join([
                    str(blocker.get("name", "")),
                    str(blocker.get("description", "")),
                ]).lower()
            else:
                text = str(blocker).lower()

            for domain, keywords in domain_keywords.items():
                if any(keyword in text for keyword in keywords):
                    if domain not in blocker_domains:
                        blocker_domains.append(domain)

        return {
            "blockers": blockers,
            "primary_blockers": blocker_names[:3],  # Top 3 blockers
            "blocker_domains": list(set(blocker_domains)),
            "high_priority_blockers": high_priority,
        }

    def _extract_evidence_summary(self, diagnostic_result: DiagnosticResult) -> Dict[str, Any]:
        """Extract evidence summary from diagnostic result."""
        evidence_trace = diagnostic_result.evidence_trace or []
        return {
            "evidence_trace": evidence_trace,
            "evidence_count": len(evidence_trace),
            "has_sufficient_evidence": len(evidence_trace) >= 3,  # Arbitrary threshold
        }

    def _extract_score_info(self, score_result: ScoreResult) -> Dict[str, Any]:
        """Extract score-related information."""
        if not score_result.composites:
            return {
                "composites": {},
                "weakest_dimensions": [],
                "strongest_dimensions": [],
                "overall_score": 0.0,
            }

        # Extract composite scores
        composites = {}
        for dim_key, composite in score_result.composites.items():
            composites[dim_key] = {
                "score": composite.overall_score,
                "percentage": composite.percentage,
                'label': composite.label,
                'floor_applied': composite.floor_applied,
            }

        # Find weakest and strongest dimensions
        sorted_by_score = sorted(
            composites.items(),
            key=lambda x: x[1]['score']
        )

        weakest_dimensions = [dim for dim, _ in sorted_by_score[:2]]  # Bottom 2
        strongest_dimensions = [dim for dim, _ in sorted_by_score[-2:]]  # Top 2

        return {
            "composites": composites,
            "weakest_dimensions": weakest_dimensions,
            "strongest_dimensions": strongest_dimensions,
            "overall_score": score_result.overall_score,
        }

    def _extract_anomaly_info(self, score_result: ScoreResult) -> Dict[str, Any]:
        """Extract anomaly information."""
        anomalies = score_result.anomalies or []
        return {
            "has_anomalies": len(anomalies) > 0,
            "anomaly_count": len(anomalies),
            "anomalies": [
                {
                    "description": a.description,
                    "criteria_pair": a.criteria_pair,
                    "severity": a.severity,
                }
                for a in anomalies
            ],
            "high_severity_anomalies": [
                a for a in anomalies if getattr(a, 'severity', '') == 'high'
            ],
        }

    def _extract_improvement_info(self, score_result: ScoreResult) -> Dict[str, Any]:
        """Extract improvement guidance information."""
        priorities = score_result.priorities or []
        executive_summary = score_result.executive_summary or ""
        return {
            "priorities": priorities,
            "primary_guidance": priorities[0] if priorities else None,
            "priority_count": len(priorities),
            "executive_summary": executive_summary,
        }

    def _generate_structured_filters(
        self,
        diagnostic_result: DiagnosticResult,
        score_result: ScoreResult,
    ) -> Dict[str, Any]:
        """Generate structured filters for the retrieval engine."""
        filters = {}

        # Stage filter - target appropriate programs for the assigned stage
        # Also consider programs that help reach the next stage if there's a gap
        if diagnostic_result.assigned_stage:
            filters["eligibility_stages"] = [diagnostic_result.assigned_stage]

            # If there's an overestimation gap, also look for programs that address the gap
            if (diagnostic_result.perception_gap and
                diagnostic_result.perception_gap.gap_type == "OVER_ESTIMATION"):
                # Programs that help with validation and grounding
                # This would be more sophisticated in a full implementation
                pass

        # Blocker resolution filter
        if diagnostic_result.key_blockers:
            blocker_list = []
            for blocker in diagnostic_result.key_blockers:
                if isinstance(blocker, dict):
                    name = blocker.get("name", "")
                else:
                    name = str(blocker)
                if name:
                    blocker_list.append(name)
            if blocker_list:
                filters["blockers_resolved"] = blocker_list

        # Domain filter based on weakest scoring areas
        if score_result.composites:
            # Map score dimensions to domains
            dimension_to_domain = {
                "market": ["market"],
                "commercial_offer": ["market", "organisational"],
                "innovation": ["technical"],
                "scalability": ["organisational", "technical"],
                "green": ["financial", "organisational"],  # sustainability often has financial aspects
            }

            weakest_domains = set()
            for dim_key, composite in score_result.composites.items():
                if composite.overall_score < 50:  # Below average score
                    if dim_key in dimension_to_domain:
                        weakest_domains.update(dimension_to_domain[dim_key])

            if weakest_domains:
                filters["domains_addressed"] = list(weakest_domains)

        # Program type filter based on needs
        # This would be more sophisticated in a full implementation
        # For now, we'll leave it empty to allow broader matching

        # Remove empty filters
        filters = {k: v for k, v in filters.items() if v}

        self.logger.debug(f"Generated structured filters: {filters}")
        return filters