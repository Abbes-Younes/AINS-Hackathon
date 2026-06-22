"""
Test suite for Feature 3: RAG-Grounded Roadmap & Resource Orientation
"""

import pytest
from typing import Dict, List, Any
from unittest.mock import Mock, patch

from src.models.diagnostic import DiagnosticResult, PerceptionGap
from src.models.scoring import ScoreResult, CompositeScore, Anomaly
from src.models.roadmap import ResourceOrientation, RoadmapAction, RoadmapMilestone
from src.feature_3_rag.roadmap_generator import RoadmapGenerator
from src.feature_3_rag.query_generator import QueryGenerator
from src.feature_3_rag.conversational_layer import ConversationalLayer


class TestRoadmapGenerator:
    """Test the roadmap generator functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.generator = RoadmapGenerator()

        # Sample diagnostic result
        self.diagnostic_result = DiagnosticResult(
            project_id="test-project-1",
            assigned_stage="validation",
            perception_gap=PerceptionGap(
                gap_type="OVER_ESTIMATION",
                gap_severity="MEDIUM",
                claimed_stage="structuration",
                actual_stage="validation",
                description="Overestimation of readiness"
            ),
            key_blockers=[
                {"name": "Limited market validation", "description": "Need more customer interviews"},
                {"name": "Undefined business model", "description": "Need to clarify revenue streams"}
            ],
            evidence_trace=["customer_interview_1", "market_research_1"]
        )

        # Sample scoring result
        self.scoring_result = ScoreResult(
            project_id="test-project-1",
            overall_score=45.0,
            percentages={
                "market": 30.0,
                "commercial_offer": 50.0,
                "innovation": 60.0,
                "scalability": 40.0,
                "green": 55.0
            },
            composites={
                "market": CompositeScore(
                    label="Market",
                    overall_score=30.0,
                    percentage=30.0,
                    floor_applied=False
                ),
                "commercial_offer": CompositeScore(
                    label="Commercial Offer",
                    overall_score=50.0,
                    percentage=50.0,
                    floor_applied=False
                )
            },
            anomalies=[
                Anomaly(
                    description="Inconsistent market validation claims",
                    criteria_pair="market_validation, customer_interviews",
                    severity="MEDIUM"
                )
            ],
            priorities=["Improve market validation through customer interviews"],
            executive_summary="Primary gap in market validation"
        )

        # Sample resources
        self.sample_resources = [
            {
                "resource_id": "res-001",
                "name": "Customer Discovery Workshop",
                "operator": "APII",
                "type": "training",
                "description": "Workshop on customer discovery techniques",
                "source_url": "https://example.com/workshop",
                "eligibility_criteria": ["early-stage startups"],
                "eligibility_stages": ["validation", "structuration"]
            },
            {
                "resource_id": "res-002",
                "name": "Business Model Canvas Training",
                "operator": "Tunisie Innovation",
                "type": "training",
                "description": "Learn to build and test business models",
                "source_url": "https://example.com/bmc",
                "eligibility_criteria": ["pre-revenue startups"],
                "eligibility_stages": ["validation", "structuration", "fundraising"]
            }
        ]

    def test_generate_roadmap_basic(self):
        """Test basic roadmap generation."""
        roadmap = self.generator.generate_roadmap(
            diagnostic_result=self.diagnostic_result,
            score_result=self.scoring_result,
            resources=self.sample_resources
        )

        assert isinstance(roadmap, ResourceOrientation)
        assert len(roadmap.roadmap) > 0
        assert len(roadmap.milestones) > 0
        assert roadmap.estimated_timeline_months > 0
        assert roadmap.executive_summary is not None
        assert roadmap.next_steps_summary is not None

    def test_generate_actions_from_diagnostic(self):
        """Test action generation from diagnostic findings."""
        actions = self.generator._generate_actions_from_diagnostic(
            diagnostic_result=self.diagnostic_result,
            score_result=self.scoring_result,
            resources=self.sample_resources
        )

        # Should have actions for perception gap and blockers
        assert len(actions) >= 2

        # Check for perception gap action
        gap_actions = [a for a in actions if "Perception gap" in a.action_text]
        assert len(gap_actions) >= 1

        # Check for blocker actions
        blocker_actions = [a for a in actions if "Address blocker:" in a.action_text]
        assert len(blocker_actions) >= 2

    def test_generate_actions_from_scoring(self):
        """Test action generation from scoring findings."""
        actions = self.generator._generate_actions_from_scoring(
            diagnostic_result=self.diagnostic_result,
            score_result=self.scoring_result,
            resources=self.sample_resources
        )

        # Should have actions for low scores and anomalies
        assert len(actions) >= 2

        # Check for low score action (market score is 30% < 50%)
        low_score_actions = [a for a in actions if "Improve your market" in a.action_text]
        assert len(low_score_actions) >= 1

        # Check for anomaly action
        anomaly_actions = [a for a in actions if "Address inconsistency:" in a.action_text]
        assert len(anomaly_actions) >= 1

    def test_remove_duplicate_actions(self):
        """Test duplicate action removal."""
        # Create duplicate actions
        action1 = RoadmapAction(
            id="test-1",
            time_horizon="immediate",
            action_text="Test action",
            rationale="Test rationale",
            estimated_effort="medium",
            estimated_impact="medium"
        )

        action2 = RoadmapAction(
            id="test-2",
            time_horizon="immediate",
            action_text="Test action",  # Same text as action1
            rationale="Different rationale",
            estimated_effort="low",
            estimated_impact="high"
        )

        actions = [action1, action2]
        unique_actions = self.generator._remove_duplicate_actions(actions)

        # Should only have one action
        assert len(unique_actions) == 1
        assert unique_actions[0].action_text == "Test action"

    def test_sequence_actions(self):
        """Test action sequencing."""
        # Create actions with different horizons
        actions = [
            RoadmapAction(
                id="test-1",
                time_horizon="long_term",
                action_text="Long term action",
                rationale="Test",
                estimated_effort="low",
                estimated_impact="low"
            ),
            RoadmapAction(
                id="test-2",
                time_horizon="immediate",
                action_text="Immediate action",
                rationale="Test",
                estimated_effort="high",
                estimated_impact="high"
            ),
            RoadmapAction(
                id="test-3",
                time_horizon="short_term",
                action_text="Short term action",
                rationale="Test",
                estimated_effort="medium",
                estimated_impact="medium"
            )
        ]

        sequenced = self.generator._sequence_actions(actions)

        # Should be ordered: immediate, short_term, long_term
        assert len(sequenced) == 3
        assert sequenced[0].time_horizon == "immediate"
        assert sequenced[1].time_horizon == "short_term"
        assert sequenced[2].time_horizon == "long_term"

    def test_group_actions_by_horizon(self):
        """Test grouping actions by time horizon."""
        actions = [
            RoadmapAction(
                id="test-1",
                time_horizon="immediate",
                action_text="Immediate action",
                rationale="Test",
                estimated_effort="high",
                estimated_impact="high"
            ),
            RoadmapAction(
                id="test-2",
                time_horizon="immediate",
                action_text="Another immediate action",
                rationale="Test",
                estimated_effort="high",
                estimated_impact="high"
            ),
            RoadmapAction(
                id="test-3",
                time_horizon="short_term",
                action_text="Short term action",
                rationale="Test",
                estimated_effort="medium",
                estimated_impact="medium"
            )
        ]

        grouped = self.generator._group_actions_by_horizon(actions)

        assert len(grouped["immediate"]) == 2
        assert len(grouped["short_term"]) == 1
        assert len(grouped["medium_term"]) == 0
        assert len(grouped["long_term"]) == 0

    def test_get_target_stage_for_horizon(self):
        """Test target stage calculation."""
        # Test immediate horizon (should stay at same stage or progress slightly)
        target = self.generator._get_target_stage_for_horizon("immediate", "validation")
        assert target == "validation"  # Immediate horizon stays at current stage

        # Test short-term horizon (should progress one stage)
        target = self.generator._get_target_stage_for_horizon("short_term", "validation")
        assert target == "structuration"

        # Test medium-term horizon (should progress two stages)
        target = self.generator._get_target_stage_for_horizon("medium_term", "validation")
        assert target == "fundraising"

        # Test long-term horizon (should progress three stages)
        target = self.generator._get_target_stage_for_horizon("long_term", "validation")
        assert target == "launch_planning"

    def test_calculate_estimated_timeline(self):
        """Test timeline calculation."""
        # Create milestones for different horizons
        milestones = [
            RoadmapMilestone(
                title="Immediate",
                description="Immediate actions",
                actions=[
                    RoadmapAction(
                        id="test-1",
                        time_horizon="immediate",
                        action_text="Test action",
                        rationale="Test",
                        estimated_effort="high",
                        estimated_impact="high"
                    )
                ],
                target_stage="validation"
            ),
            RoadmapMilestone(
                title="Short-term",
                description="Short-term actions",
                actions=[
                    RoadmapAction(
                        id="test-2",
                        time_horizon="short_term",
                        action_text="Test action",
                        rationale="Test",
                        estimated_effort="medium",
                        estimated_impact="medium"
                    )
                ],
                target_stage="structuration"
            )
        ]

        timeline = self.generator._calculate_estimated_timeline(milestones)
        # Should be 3 months (short-term horizon)
        assert timeline == 3

    def test_generate_executive_summary(self):
        """Test executive summary generation."""
        milestones = [
            RoadmapMilestone(
                title="Immediate",
                description="Immediate actions",
                actions=[
                    RoadmapAction(
                        id="test-1",
                        time_horizon="immediate",
                        action_text="Test action",
                        rationale="Test",
                        estimated_effort="high",
                        estimated_impact="high"
                    )
                ],
                target_stage="validation"
            )
        ]

        summary = self.generator._generate_executive_summary(
            diagnostic_result=self.diagnostic_result,
            score_result=self.scoring_result,
            milestones=milestones
        )

        assert isinstance(summary, str)
        assert len(summary) > 0
        assert "validation" in summary  # Should mention the stage
        assert "market" in summary.lower()  # Should mention the weakest dimension

    def test_generate_next_steps_summary(self):
        """Test next steps summary generation."""
        milestones = [
            RoadmapMilestone(
                title="Immediate",
                description="Immediate actions",
                actions=[
                    RoadmapAction(
                        id="test-1",
                        time_horizon="immediate",
                        action_text="First immediate action",
                        rationale="Test",
                        estimated_effort="high",
                        estimated_impact="high"
                    ),
                    RoadmapAction(
                        id="test-2",
                        time_horizon="immediate",
                        action_text="Second immediate action",
                        rationale="Test",
                        estimated_effort="high",
                        estimated_impact="high"
                    ),
                    RoadmapAction(
                        id="test-3",
                        time_horizon="immediate",
                        action_text="Third immediate action",
                        rationale="Test",
                        estimated_effort="high",
                        estimated_impact="high"
                    )
                ],
                target_stage="validation"
            )
        ]

        summary = self.generator._generate_next_steps_summary(milestones)

        assert isinstance(summary, str)
        assert "First immediate action" in summary
        assert "Second immediate action" in summary
        assert "Third immediate action" in summary


class TestQueryGenerator:
    """Test the query generator functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.generator = QueryGenerator()

        # Sample diagnostic result
        self.diagnostic_result = DiagnosticResult(
            project_id="test-project-1",
            assigned_stage="validation",
            perception_gap=PerceptionGap(
                gap_type="OVER_ESTIMATION",
                gap_severity="MEDIUM",
                claimed_stage="structuration",
                actual_stage="validation",
                description="Overestimation of readiness"
            ),
            key_blockers=[
                {"name": "Limited market validation", "description": "Need more customer interviews"},
                {"name": "Undefined business model", "description": "Need to clarify revenue streams"}
            ]
        )

        # Sample scoring result
        self.scoring_result = ScoreResult(
            project_id="test-project-1",
            overall_score=45.0,
            percentages={
                "market": 30.0,
                "commercial_offer": 50.0,
                "innovation": 60.0,
                "scalability": 40.0,
                "green": 55.0
            },
            composites={
                "market": CompositeScore(
                    label="Market",
                    overall_score=30.0,
                    percentage=30.0,
                    floor_applied=False
                )
            },
            anomalies=[
                Anomaly(
                    description="Inconsistent market validation claims",
                    criteria_pair="market_validation, customer_interviews",
                    severity="MEDIUM"
                )
            ],
            priorities=["Improve market validation through customer interviews"],
            executive_summary="Primary gap in market validation"
        )

    def test_generate_query(self):
        """Test query generation."""
        query_string, structured_filters = self.generator.generate_query(
            diagnostic_result=self.diagnostic_result,
            score_result=self.scoring_result
        )

        assert isinstance(query_string, str)
        assert len(query_string) > 0
        assert isinstance(structured_filters, dict)

        # Should contain stage information
        assert "validation" in query_string

        # Should contain gap information
        assert "overconfident" in query_string or "OVER_ESTIMATION" in query_string

        # Should contain blocker information
        assert "market validation" in query_string or "business model" in query_string

        # Should contain score information
        assert "market" in query_string

        # Should contain structured filters
        assert "eligibility_stages" in structured_filters
        assert "domains_addressed" in structured_filters
        assert "blockers_resolved" in structured_filters


class TestConversationalLayer:
    """Test the conversational layer functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.layer = ConversationalLayer()

        # Sample diagnostic result
        self.diagnostic_result = DiagnosticResult(
            project_id="test-project-1",
            assigned_stage="validation",
            perception_gap=PerceptionGap(
                gap_type="OVER_ESTIMATION",
                gap_severity="MEDIUM",
                claimed_stage="structuration",
                actual_stage="validation",
                description="Overestimation of readiness"
            ),
            key_blockers=[
                {"name": "Limited market validation", "description": "Need more customer interviews"}
            ]
        )

        # Sample scoring result
        self.scoring_result = ScoreResult(
            project_id="test-project-1",
            overall_score=45.0,
            percentages={
                "market": 30.0,
                "commercial_offer": 50.0,
                "innovation": 60.0,
                "scalability": 40.0,
                "green": 55.0
            },
            composites={
                "market": CompositeScore(
                    label="Market",
                    overall_score=30.0,
                    percentage=30.0,
                    floor_applied=False
                )
            },
            priorities=["Improve market validation through customer interviews"],
            executive_summary="Primary gap in market validation"
        )

    @patch('src.feature_3_rag.conversational_layer.RetrievalEngine')
    def test_generate_response(self, mock_retrieval_engine):
        """Test response generation."""
        # Mock the retrieval engine
        mock_instance = Mock()
        mock_instance.hybrid_retrieve.return_value = [
            {
                "resource_id": "res-001",
                "name": "Customer Discovery Workshop",
                "operator": "APII",
                "type": "training",
                "description": "Workshop on customer discovery techniques",
                "relevance_score": 0.85,
                "source_url": "https://example.com/workshop"
            }
        ]
        mock_retrieval_engine.return_value = mock_instance

        # Test response generation
        response, sources = self.layer.generate_response(
            user_query="How can I improve my market validation?",
            diagnostic_result=self.diagnostic_result,
            score_result=self.scoring_result
        )

        assert isinstance(response, str)
        assert len(response) > 0
        assert isinstance(sources, list)
        assert len(sources) == 1
        assert sources[0]["name"] == "Customer Discovery Workshop"

        # Check that response is grounded
        assert "validation" in response  # Should mention the stage
        assert "market" in response.lower()  # Should mention market validation
        assert "Customer Discovery Workshop" in response  # Should mention the resource

    def test_is_response_grounded(self):
        """Test grounding validation."""
        # Well-grounded response
        grounded_response = "Based on your validation-stage diagnosis and low market score (30/100), you should attend the Customer Discovery Workshop by APII to improve market validation."
        is_grounded = self.layer._is_response_grounded(
            grounded_response,
            self.diagnostic_result,
            self.scoring_result,
            [{"name": "Customer Discovery Workshop"}]
        )
        assert is_grounded == True

        # Poorly grounded response
        poor_response = "You should generally work on improving your skills and attend workshops to become a better entrepreneur."
        is_grounded = self.layer._is_response_grounded(
            poor_response,
            self.diagnostic_result,
            self.scoring_result,
            [{"name": "Customer Discovery Workshop"}]
        )
        assert is_grounded == False  # Lacks specific references to user's data

    def test_generate_fallback_response(self):
        """Test fallback response generation."""
        response = self.layer._generate_fallback_response(
            diagnostic_result=self.diagnostic_result,
            score_result=self.scoring_result,
            roadmap=None
        )

        assert isinstance(response, str)
        assert len(response) > 0
        assert "validation" in response  # Should mention the stage
        assert "market" in response.lower()  # Should mention the weakest dimension
        assert "Limited market validation" in response  # Should mention the blocker


if __name__ == "__main__":
    pytest.main([__file__])