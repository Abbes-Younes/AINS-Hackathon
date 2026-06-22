"""
Roadmap Generator for Feature 3: RAG-Grounded Roadmap & Resource Orientation
Generates personalized, sequenced action plans based on diagnostic and scoring data.
"""

import logging
from typing import Dict, List, Any, Optional
from pathlib import Path

# Add project root to path for importing models
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from src.models.diagnostic import DiagnosticResult
from src.models.scoring import ScoreResult
from src.models.roadmap import RoadmapAction, RoadmapMilestone, ResourceOrientation

logger = logging.getLogger(__name__)


class RoadmapGenerator:
    """Generates personalized, sequenced action plans for entrepreneurs."""

    def __init__(self):
        """Initialize the roadmap generator."""
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.info("Roadmap generator initialized")

        # Define time horizons with concrete durations
        self.time_horizons = {
            "immediate": {
                "name": "Immediate",
                "description": "Critical actions to resolve blockers and gather essential evidence (0-30 days)",
                "days": 30,
            },
            "short_term": {
                "name": "Short-term",
                "description": "Foundational steps to build legitimacy and prepare for growth (1-3 months)",
                "days": 90,
            },
            "medium_term": {
                "name": "Medium-term",
                "description": "Growth levers, financing access, and market expansion (3-12 months)",
                "days": 365,
            },
            "long_term": {
                "name": "Long-term",
                "description": "Consolidation, diversification, and exit planning (12+ months)",
                "days": 730,  # Approximate 2 years
            }
        }

    def generate_roadmap(
        self,
        diagnostic_result: DiagnosticResult,
        score_result: ScoreResult,
        resources: Optional[List[Dict[str, Any]]] = None,
    ) -> ResourceOrientation:
        """
        Generate a personalized roadmap based on diagnostic and scoring data.

        Args:
            diagnostic_result: Diagnostic output from Feature 1
            score_result: Scoring output from Feature 2
            resources: Optional pre-fetched KB resources for grounding actions

        Returns:
            ResourceOrientation containing the personalized roadmap and related information
        """
        self.logger.info("Generating personalized roadmap")

        # Generate actions based on diagnostic findings
        actions = self._generate_actions_from_diagnostic(diagnostic_result, score_result, resources)

        # Generate actions based on scoring findings
        actions.extend(self._generate_actions_from_scoring(diagnostic_result, score_result, resources))

        # Remove duplicates and sequence actions
        unique_actions = self._remove_duplicate_actions(actions)
        sequenced_actions = self._sequence_actions(unique_actions)

        # Group actions by time horizon
        actions_by_horizon = self._group_actions_by_horizon(sequenced_actions)

        # Create milestones
        milestones = []
        for horizon_key, horizon_actions in actions_by_horizon.items():
            horizon_info = self.time_horizons[horizon_key]
            milestone = RoadmapMilestone(
                title=horizon_info["name"],
                description=horizon_info["description"],
                actions=horizon_actions,
                target_stage=self._get_target_stage_for_horizon(horizon_key, diagnostic_result.assigned_stage),
            )
            milestones.append(milestone)

        # Flatten actions for backward compatibility
        all_actions = []
        for milestone in milestones:
            all_actions.extend(milestone.actions)

        # Calculate estimated timeline
        estimated_months = self._calculate_estimated_timeline(milestones)

        # Determine which blockers have linked resources
        blockers_addressed = self._get_blockers_with_resources(diagnostic_result, resources or [])
        all_blocker_names = [b.get("name", str(b)) for b in diagnostic_result.key_blockers or []]
        unaddressed_blockers = [b for b in all_blocker_names if b not in blockers_addressed]

        # Create ResourceOrientation object
        orientation = ResourceOrientation(
            resources=resources or [],
            resources_by_type=self._group_resources_by_type(resources or []),
            total_resources_found=len(resources or []),
            roadmap=all_actions,
            milestones=milestones,
            estimated_timeline_months=estimated_months,
            blockers_addressed=blockers_addressed,
            unaddressed_blockers=unaddressed_blockers,
            executive_summary=self._generate_executive_summary(diagnostic_result, score_result, milestones),
            next_steps_summary=self._generate_next_steps_summary(milestones),
        )

        self.logger.info(f"Generated roadmap with {len(all_actions)} actions across {len(milestones)} milestones")
        return orientation

    def _generate_actions_from_diagnostic(
        self,
        diagnostic_result: DiagnosticResult,
        score_result: ScoreResult,
        resources: Optional[List[Dict[str, Any]]],
    ) -> List[RoadmapAction]:
        """Generate roadmap actions based on diagnostic findings."""
        actions = []

        # Actions for perception-reality gaps
        if diagnostic_result.perception_gap:
            gap = diagnostic_result.perception_gap
            if gap.gap_type == "OVER_ESTIMATION":
                actions.append(self._create_action(
                    id=f"gap_overestimation_{diagnostic_result.project_id}",
                    text="Ground your self-assessment with structured customer validation and market research",
                    rationale="Overestimating readiness can lead to premature resource allocation and missed learning opportunities",
                    horizon="immediate",
                    linked_blocker=f"Perception gap: {gap.claimed_stage} vs {gap.actual_stage}",
                    linked_dimension="market",
                    resources=resources,
                ))
            elif gap.gap_type == "UNDER_ESTIMATION":
                actions.append(self._create_action(
                    id=f"gap_underestimation_{diagnostic_result.project_id}",
                    text="Build confidence through skill development and mentorship programs",
                    rationale="Underestimating readiness can prevent entrepreneurs from pursuing appropriate opportunities",
                    horizon="immediate",
                    linked_blocker=f"Perception gap: {gap.claimed_stage} vs {gap.actual_stage}",
                    linked_dimension="commercial_offer",
                    resources=resources,
                ))

        # Actions for blockers
        for blocker in diagnostic_result.key_blockers or []:
            if isinstance(blocker, dict):
                blocker_name = blocker.get("name", "")
                blocker_description = blocker.get("description", "")
            else:
                blocker_name = str(blocker)
                blocker_description = ""

            if blocker_name:
                action_id = f"blocker_{hash(blocker_name)}_{diagnostic_result.project_id}"
                actions.append(self._create_action(
                    id=action_id,
                    text=f"Address blocker: {blocker_name}",
                    rationale=f"Resolving this blocker is essential for progressing to the next maturity stage",
                    horizon="immediate",
                    linked_blocker=blocker_name,
                    resources=resources,
                ))

        return actions

    def _generate_actions_from_scoring(
        self,
        diagnostic_result: DiagnosticResult,
        score_result: ScoreResult,
        resources: Optional[List[Dict[str, Any]]],
    ) -> List[RoadmapAction]:
        """Generate roadmap actions based on scoring findings."""
        actions = []

        # Actions for low-scoring dimensions
        if score_result.composites:
            for dim_key, composite in score_result.composites.items():
                if composite.percentage < 50:  # Below average
                    actions.append(self._create_action(
                        id=f"low_score_{dim_key}_{diagnostic_result.project_id}",
                        text=f"Improve your {composite.label.lower()} through targeted learning and practice",
                        rationale=f"Strengthening {composite.label.lower()} will increase your overall competitiveness and readiness",
                        horizon="short_term",
                        linked_dimension=dim_key,
                        resources=resources,
                    ))

        # Actions for anomalies
        for anomaly in score_result.anomalies or []:
            actions.append(self._create_action(
                id=f"anomaly_{hash(anomaly.description)}_{diagnostic_result.project_id}",
                text=f"Address inconsistency: {anomaly.description}",
                rationale="Resolving inconsistencies in your self-assessment improves credibility with investors and support programs",
                horizon="immediate",
                linked_anomaly=anomaly.description,
                resources=resources,
            ))

        return actions

    def _create_action(
        self,
        id: str,
        text: str,
        rationale: str,
        horizon: str,
        linked_blocker: Optional[str] = None,
        linked_dimension: Optional[str] = None,
        linked_anomaly: Optional[str] = None,
        resources: Optional[List[Dict[str, Any]]] = None,
    ) -> RoadmapAction:
        """Create a RoadmapAction object."""
        # Filter resources to those relevant to this action (simplified)
        relevant_resources = []
        if resources:
            # In a full implementation, we would do proper matching
            # For now, we'll just include all resources as potentially relevant
            relevant_resources = [
                {
                    "kb_id": r.get("resource_id", ""),
                    "title": r.get("name", ""),
                    "organization": r.get("operator", ""),
                    "program_type": r.get("type", ""),
                    "eligibility": r.get("eligibility_criteria", ""),
                    "url": r.get("source_url", ""),
                    "relevance_score": 0.8,  # Placeholder
                    "relevance_reason": "Matched to action based on diagnostic findings",
                }
                for r in resources[:3]  # Limit to top 3 for simplicity
            ]

        # Determine effort and impact based on horizon (simplified)
        effort_map = {
            "immediate": "high",
            "short_term": "medium",
            "medium_term": "medium",
            "long_term": "low",
        }
        impact_map = {
            "immediate": "high",
            "short_term": "high",
            "medium_term": "medium",
            "long_term": "medium",
        }

        return RoadmapAction(
            id=id,
            time_horizon=horizon,
            action_text=text,
            rationale=rationale,
            linked_blocker=linked_blocker,
            linked_dimension=linked_dimension,
            linked_sub_criterion=None,  # Would be populated in full implementation
            resources=relevant_resources,
            estimated_effort=effort_map.get(horizon, "medium"),
            estimated_impact=impact_map.get(horizon, "medium"),
        )

    def _remove_duplicate_actions(self, actions: List[RoadmapAction]) -> List[RoadmapAction]:
        """Remove duplicate actions based on action text."""
        seen_texts = set()
        unique_actions = []
        for action in actions:
            if action.action_text not in seen_texts:
                seen_texts.add(action.action_text)
                unique_actions.append(action)
        return unique_actions

    def _sequence_actions(self, actions: List[RoadmapAction]) -> List[RoadmapAction]:
        """Sequence actions based on dependencies and logical order."""
        # Define priority order for time horizons
        horizon_priority = {
            "immediate": 0,
            "short_term": 1,
            "medium_term": 2,
            "long_term": 3,
        }

        # Sort by time horizon priority, then by action text for consistency
        return sorted(
            actions,
            key=lambda a: (
                horizon_priority.get(a.time_horizon, 999),
                a.action_text
            )
        )

    def _group_actions_by_horizon(self, actions: List[RoadmapAction]) -> Dict[str, List[RoadmapAction]]:
        """Group actions by their time horizon."""
        grouped = {horizon: [] for horizon in self.time_horizons.keys()}
        for action in actions:
            horizon = action.time_horizon
            if horizon in grouped:
                grouped[horizon].append(action)
        return grouped

    def _get_target_stage_for_horizon(
        self,
        horizon_key: str,
        current_stage: str
    ) -> str:
        """Get the target maturity stage for a given time horizon."""
        # Define stage progression
        stage_progression = [
            "ideation",
            "validation",
            "structuration",
            "fundraising",
            "launch_planning",
            "growth"
        ]

        try:
            current_index = stage_progression.index(current_stage)
        except ValueError:
            current_index = 0  # Default to ideation if stage not found

        # Target stage based on horizon
        horizon_offsets = {
            "immediate": 0,      # Stay at current stage or resolve blockers to progress
            "short_term": 1,     # Progress to next stage
            "medium_term": 2,    # Progress two stages ahead
            "long_term": 3,      # Progress three stages ahead
        }

        offset = horizon_offsets.get(horizon_key, 0)
        target_index = min(current_index + offset, len(stage_progression) - 1)
        return stage_progression[target_index]

    def _calculate_estimated_timeline(self, milestones: List[RoadmapMilestone]) -> int:
        """Calculate estimated timeline in months."""
        if not milestones:
            return 0

        # Use the horizon with actions that extends furthest in the future
        horizon_months = {
            "immediate": 1,    # ~1 month
            "short_term": 3,   # ~3 months
            "medium_term": 12, # ~12 months
            "long_term": 24,   # ~24 months
        }

        max_months = 0
        for milestone in milestones:
            # Find which horizon this milestone belongs to based on title
            for horizon_key, horizon_info in self.time_horizons.items():
                if horizon_info["name"] == milestone.title:
                    months = horizon_months.get(horizon_key, 0)
                    max_months = max(max_months, months)
                    break

        return max_months

    def _get_blockers_with_resources(
        self,
        diagnostic_result: DiagnosticResult,
        resources: List[Dict[str, Any]],
    ) -> List[str]:
        """Determine which blockers have linked resources."""
        # Simplified implementation - in reality, we'd check specific resource-blocker mappings
        blocker_names = []
        for blocker in diagnostic_result.key_blockers or []:
            if isinstance(blocker, dict):
                name = blocker.get("name", "")
            else:
                name = str(blocker)
            if name:
                blocker_names.append(name)

        # For now, assume blockers Have resources if we have any resources
        # In a full implementation, we would check specific linkages
        if resources and blocker_names:
            return blocker_names[:min(len(blocker_names), len(resources))]
        return []

    def _group_resources_by_type(self, resources: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """Group resources by program type."""
        grouped = {}
        for resource in resources:
            res_type = resource.get("type", "unknown")
            if res_type not in grouped:
                grouped[res_type] = []
            grouped[res_type].append(resource)
        return grouped

    def _generate_executive_summary(
        self,
        diagnostic_result: DiagnosticResult,
        score_result: ScoreResult,
        milestones: List[RoadmapMilestone]
    ) -> str:
        """Generate an executive summary of the roadmap."""
        stage = diagnostic_result.assigned_stage
        gap_info = ""
        if diagnostic_result.perception_gap:
            gap = diagnostic_result.perception_gap
            gap_info = f"You perceive yourself at {gap.claimed_stage} stage, but our assessment places you at {gap.actual_stage} stage."

        weakness = ""
        if score_result.composites:
            weakest_dim = min(score_result.composites.items(), key=lambda x: x[1].percentage)
            weakness = f"Your {weakest_dim[1].label.lower()} score ({weakest_dim[1].percentage:.0f}/100) is your primary area for development."

        action_count = sum(len(m.actions) for m in milestones)
        horizon_count = len(milestones)

        summary = f"Based on your {stage} stage diagnosis, {gap_info} {weakness} "
        summary += f"This personalized roadmap includes {action_count} specific actions organized across {horizon_count} time horizons "
        summary += "to help you progress toward your entrepreneurial goals."
        return summary.strip()

    def _generate_next_steps_summary(self, milestones: List[RoadmapMilestone]) -> str:
        """Generate a summary of immediate next steps."""
        if not milestones or not milestones[0].actions:
            return "Complete your diagnostic assessment to begin building your personalized roadmap."

        immediate_actions = milestones[0].actions[:3]  # First 3 immediate actions
        if not immediate_actions:
            return "Review your full roadmap for recommended actions."

        action_texts = [a.action_text for a in immediate_actions]
        if len(action_texts) == 1:
            return f"Next step: {action_texts[0]}."
        elif len(action_texts) == 2:
            return f"Next steps: {action_texts[0]} and {action_texts[1]}."
        else:
            return f"Next steps: {action_texts[0]}, {action_texts[1]}, and {action_texts[2]}."