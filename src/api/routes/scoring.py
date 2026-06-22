"""
Scoring API Endpoints for Feature 2: Explainable Multi-Dimensional Scoring
REST API for score computation, retrieval, history, anomalies, and improvement guidance
"""

from fastapi import APIRouter, HTTPException, Depends, Path as FastAPIPath
from typing import Dict, Any, List
import logging

from src.models.profile import EntrepreneurProfile
from src.models.scoring import (
    ScoreBreakdown, Justification, ImprovementGuidance,
    Anomaly, ScoreEvolution
)
from src.feature_2_scoring.scoring_engine import ScoringEngine
from src.feature_2_scoring.justification_engine import JustificationEngine
from src.feature_2_scoring.improvement_guidance import ImprovementGuidanceEngine
from src.feature_2_scoring.evolution_tracker import ScoreEvolutionTracker
from src.feature_2_scoring.anomaly_detector import AnomalyDetector
from src.api.dependencies import get_current_user

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/scoring", tags=["scoring"])

# Initialize components (in production, these would be dependency injected)
scoring_engine = ScoringEngine()
justification_engine = JustificationEngine(scoring_engine)
improvement_engine = ImprovementGuidanceEngine(scoring_engine)
evolution_tracker = ScoreEvolutionTracker()
anomaly_detector = AnomalyDetector()


@router.post("/compute/{project_id}", response_model=ScoreBreakdown)
async def compute_scores(
    project_id: str = FastAPIPath(..., description="Unique identifier for the entrepreneur/project"),
    profile: EntrepreneurProfile = None
):
    """
    Compute scores for an entrepreneur profile

    Args:
        project_id: Unique identifier for the entrepreneur/project
        profile: EntrepreneurProfile containing the data to score

    Returns:
        ScoreBreakdown with all composite scores and sub-criteria
    """
    try:
        if profile is None:
            raise HTTPException(status_code=400, detail="Profile data is required")

        # Set project ID in profile if not already set
        if not profile.project_id:
            profile.project_id = project_id

        # Compute scores
        score_breakdown = scoring_engine.compute_scores(profile)

        # Save snapshot for evolution tracking
        evolution_tracker.save_score_snapshot(project_id, profile, score_breakdown)

        logger.info(f"Computed scores for project {project_id}")
        return score_breakdown

    except Exception as e:
        logger.error(f"Error computing scores for project {project_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Error computing scores: {str(e)}")


@router.get("/{project_id}", response_model=ScoreBreakdown)
async def get_scores(
    project_id: str = FastAPIPath(..., description="Unique identifier for the entrepreneur/project")
):
    """
    Get current scores for an entrepreneur/project

    Args:
        project_id: Unique identifier for the entrepreneur/project

    Returns:
        ScoreBreakdown with all composite scores and sub-criteria
    """
    try:
        # Get latest score from evolution tracker
        latest = evolution_tracker.get_latest_score(project_id)

        if not latest:
            raise HTTPException(status_code=404, detail=f"No scores found for project {project_id}")

        # Reconstruct ScoreBreakdown from database record
        # In a full implementation, we would store the complete ScoreBreakdown
        # For now, we'll reconstruct what we can
        score_breakdown = ScoreBreakdown(
            market=latest["market_score"],
            commercial_offer=latest["commercial_offer_score"],
            innovation=latest["innovation_score"],
            scalability=latest["scalability_score"],
            green=latest["green_score"],
            overall_score=latest["overall_score"],
            data_reliability=latest["data_reliability"],
            # Sub-criteria would need to be parsed from JSON
            market_sub_criteria=json.loads(latest["market_sub_criteria"]) if latest["market_sub_criteria"] else {},
            commercial_offer_sub_criteria=json.loads(latest["commercial_offer_sub_criteria"]) if latest["commercial_offer_sub_criteria"] else {},
            innovation_sub_criteria=json.loads(latest["innovation_sub_criteria"]) if latest["innovation_sub_criteria"] else {},
            scalability_sub_criteria=json.loads(latest["scalability_sub_criteria"]) if latest["scalability_sub_criteria"] else {},
            green_sub_criteria=json.loads(latest["green_sub_criteria"]) if latest["green_sub_criteria"] else {}
        )

        return score_breakdown

    except json.JSONDecodeError as e:
        logger.error(f"Error parsing JSON in score data for project {project_id}: {e}")
        raise HTTPException(status_code=500, detail="Error parsing score data")
    except Exception as e:
        logger.error(f"Error retrieving scores for project {project_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Error retrieving scores: {str(e)}")


@router.get("/{project_id}/history", response_model=List[ScoreEvolution])
async def get_score_history(
    project_id: str = FastAPIPath(..., description="Unique identifier for the entrepreneur/project"),
    limit: int = 10
):
    """
    Get score evolution history for an entrepreneur/project

    Args:
        project_id: Unique identifier for the entrepreneur/project
        limit: Maximum number of evolution points to return

    Returns:
        List of ScoreEvolution objects showing changes over time
    """
    try:
        # Get raw history
        history_records = evolution_tracker.get_score_history(project_id, limit * 2)  # Get extra for pairing

        if len(history_records) < 2:
            return []  # Not enough data for evolution

        # Calculate evolutions between consecutive records
        evolutions = []
        for i in range(len(history_records) - 1):
            current = history_records[i + 1]  # Newer record
            previous = history_records[i]     # Older record

            # Calculate deltas
            deltas = {
                "market": current["market_score"] - previous["market_score"],
                "commercial_offer": current["commercial_offer_score"] - previous["commercial_offer_score"],
                "innovation": current["innovation_score"] - previous["innovation_score"],
                "scalability": current["scalability_score"] - previous["scalability_score"],
                "green": current["green_score"] - previous["green_score"],
                "overall": current["overall_score"] - previous["overall_score"]
            }

            # Get changed sub-criteria (simplified)
            changed_sub_criteria = []  # Would be calculated similar to evolution tracker

            # Generate trend indicators
            trend_indicators = {
                k: "up" if v > 0.5 else "down" if v < -0.5 else "stable"
                for k, v in deltas.items()
            }

            evolution = ScoreEvolution(
                project_id=project_id,
                timestamp=current["timestamp"],
                previous_timestamp=previous["timestamp"],
                deltas=deltas,
                changed_sub_criteria=changed_sub_criteria,
                trend_indicators=trend_indicators
            )
            evolutions.append(evolution)

        # Return most recent evolutions first
        return evolutions[-limit:][::-1]

    except Exception as e:
        logger.error(f"Error getting score history for project {project_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting score history: {str(e)}")


@router.get("/{project_id}/anomalies", response_model=List[Anomaly])
async def get_anomalies(
    project_id: str = FastAPIPath(..., description="Unique identifier for the entrepreneur/project")
):
    """
    Get detected anomalies for an entrepreneur/profile

    Args:
        project_id: Unique identifier for the entrepreneur/project

    Returns:
        List of Anomaly objects representing contradictory signals
    """
    try:
        # We would need to retrieve the profile to detect anomalies
        # For this implementation, we'll return a placeholder
        # In a full implementation, we'd retrieve the profile from storage

        # Placeholder - in reality, we'd fetch the profile and run anomaly detection
        logger.info(f"Getting anomalies for project {project_id}")
        return []  # Return empty list for now

    except Exception as e:
        logger.error(f"Error getting anomalies for project {project_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting anomalies: {str(e)}")


@router.get("/{project_id}/improvements", response_model=Dict[str, ImprovementGuidance])
async def get_improvement_guidance(
    project_id: str = FastAPIPath(..., description="Unique identifier for the entrepreneur/project")
):
    """
    Get highest-leverage improvement guidance for each score

    Args:
        project_id: Unique identifier for the entrepreneur/project

    Returns:
        Dictionary mapping score names to their improvement guidance
    """
    try:
        # We would need the profile and score breakdown to generate guidance
        # For this implementation, we'll return placeholder guidance
        # In a full implementation, we'd retrieve the profile and scores from storage

        logger.info(f"Getting improvement guidance for project {project_id}")

        # Return placeholder guidance
        return {
            "market": ImprovementGuidance(
                action="Complete more market validation activities to improve your market score.",
                estimated_impact=15.0,
                kb_reference="kb/market_validation_guide"
            ),
            "commercial_offer": ImprovementGuidance(
                action="Clarify and test your value proposition with target customers.",
                estimated_impact=12.0,
                kb_reference="kb/value_prop_validation"
            ),
            "innovation": ImprovementGuidance(
                action="Document your technological innovations and consider IP protection.",
                estimated_impact=10.0,
                kb_reference="kb/innovation_documentation"
            ),
            "scalability": ImprovementGuidance(
                action="Identify opportunities to reduce manual dependency in your operations.",
                estimated_impact=13.0,
                kb_reference="kb/operations_automation"
            ),
            "green": ImprovementGuidance(
                action="Evaluate your environmental impact and develop a sustainability plan.",
                estimated_impact=8.0,
                kb_reference="kb/sustainability_assessment"
            )
        }

    except Exception as e:
        logger.error(f"Error getting improvement guidance for project {project_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting improvement guidance: {str(e)}")


# Import json for JSON parsing in get_scores endpoint
import json