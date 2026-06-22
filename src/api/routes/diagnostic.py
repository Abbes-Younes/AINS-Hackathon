"""
Diagnostic API Endpoints
Handles intake, classification, gap detection, and diagnostic results
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Dict, Any, Optional
import uuid
import logging

from src.models.profile import EntrepreneurProfile
from src.engine.intake_engine import IntakeEngine
from src.engine.synthesis import DiagnosticSynthesizer

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/diagnostic", tags=["diagnostic"])

# Initialize engines (in production, these would be dependency injected or singleton)
intake_engine = IntakeEngine()
diagnostic_synthesizer = DiagnosticSynthesizer()

# In-memory storage for profiles (in production, use database)
profiles: Dict[str, EntrepreneurProfile] = {}


class IntakeStartResponse(BaseModel):
    project_id: str
    question_id: str
    question_text_fr: str
    question_text_ar: str
    input_type: str
    options: list = []
    message: str


class IntakeAnswerRequest(BaseModel):
    project_id: str
    question_id: str
    answer: Any


class IntakeAnswerResponse(BaseModel):
    type: str  # "question" or "completion"
    question_id: Optional[str] = None
    question_text_fr: Optional[str] = None
    question_text_ar: Optional[str] = None
    input_type: Optional[str] = None
    options: list = []
    message_fr: Optional[str] = None
    message_ar: Optional[str] = None
    profile_data: Optional[Dict[str, Any]] = None


class DiagnosticResponse(BaseModel):
    project_id: str
    assigned_stage: str
    confidence_score: float
    perception_gap: Optional[Dict[str, Any]] = None
    key_blockers: List[Dict[str, Any]]
    evidence_trace: List[str]
    plain_language_summary: str


@router.post("/start", response_model=IntakeStartResponse)
async def start_diagnostic():
    """
    Start a new diagnostic intake session
    Returns the first question to ask the user
    """
    # Generate unique project ID
    project_id = str(uuid.uuid4())

    # Start intake session
    try:
        first_question = intake_engine.start_intake(project_id)

        return IntakeStartResponse(
            project_id=project_id,
            question_id=first_question["question_id"],
            question_text_fr=first_question["question_text_fr"],
            question_text_ar=first_question["question_text_ar"],
            input_type=first_question["input_type"],
            options=first_question.get("options", []),
            message="Intake session started successfully"
        )
    except Exception as e:
        logger.error(f"Failed to start intake session: {e}")
        raise HTTPException(status_code=500, detail="Failed to start diagnostic session")


@router.post("/answer", response_model=IntakeAnswerResponse)
async def submit_intake_answer(request: IntakeAnswerRequest):
    """
    Submit an answer to the current question and get the next question or completion
    """
    try:
        result = intake_engine.submit_answer(
            request.project_id,
            request.question_id,
            request.answer
        )

        if result["type"] == "completion":
            # Store the completed profile
            profile_data = result["profile_data"]
            profile = EntrepreneurProfile(**profile_data)
            profiles[request.project_id] = profile

            return IntakeAnswerResponse(
                type="completion",
                message_fr=result["message_fr"],
                message_ar=result["message_ar"],
                profile_data=profile_data
            )
        else:
            # Return next question
            return IntakeAnswerResponse(
                type="question",
                question_id=result["question_id"],
                question_text_fr=result["question_text_fr"],
                question_text_ar=result["question_text_ar"],
                input_type=result["input_type"],
                options=result.get("options", []),
                message_fr=result["question_text_fr"],  # For compatibility
                message_ar=result["question_text_ar"]
            )

    except ValueError as e:
        logger.error(f"Invalid intake request: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to process intake answer: {e}")
        raise HTTPException(status_code=500, detail="Failed to process answer")


@router.get("/{project_id}", response_model=DiagnosticResponse)
async def get_diagnostic(project_id: str):
    """
    Get complete diagnostic result for a project
    """
    if project_id not in profiles:
        raise HTTPException(status_code=404, detail="Project not found")

    profile = profiles[project_id]

    try:
        diagnostic_result = diagnostic_synthesizer.synthesize_diagnostic(profile)
        return diagnostic_result
    except Exception as e:
        logger.error(f"Failed to synthesize diagnostic for project {project_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate diagnostic")


@router.post("/{project_id}/classify")
async def classify_profile(project_id: str):
    """
    Run classification on a complete profile (alternative endpoint)
    """
    if project_id not in profiles:
        raise HTTPException(status_code=404, detail="Project not found")

    profile = profiles[project_id]

    try:
        classifier = diagnostic_synthesizer.classifier
        classification_result = classifier.classify(profile)

        return {
            "project_id": project_id,
            "assigned_stage": classification_result.assigned_stage,
            "confidence_score": classification_result.confidence_score,
            "evidence_trace": classification_result.evidence_trace,
            "alternative_stages": classification_result.alternative_stages
        }
    except Exception as e:
        logger.error(f"Failed to classify profile {project_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to classify profile")


@router.get("/{project_id}/gaps")
async def get_gap_analysis(project_id: str):
    """
    Get gap analysis for a project
    """
    if project_id not in profiles:
        raise HTTPException(status_code=404, detail="Project not found")

    profile = profiles[project_id]

    try:
        # First classify to get baseline
        classifier = diagnostic_synthesizer.classifier
        classification_result = classifier.classify(profile)

        # Then detect gap
        gap_detector = diagnostic_synthesizer.gap_detector
        gap_analysis = gap_detector.detect_gap(profile, classification_result)

        return {
            "project_id": project_id,
            "gap_type": gap_analysis.gap_type,
            "claimed_stage": gap_analysis.claimed_stage,
            "actual_stage": gap_analysis.actual_stage,
            "gap_severity": gap_analysis.gap_severity,
            "missing_dimensions": gap_analysis.missing_dimensions,
            "explanation": gap_analysis.explanation,
            "confidence": gap_analysis.confidence
        }
    except Exception as e:
        logger.error(f"Failed to analyze gap for project {project_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to analyze gap")


@router.get("/{project_id}/blockers")
async def get_blockers(project_id: str):
    """
    Get identified and prioritized blockers for a project
    """
    if project_id not in profiles:
        raise HTTPException(status_code=404, detail="Project not found")

    profile = profiles[project_id]

    try:
        blocker_identifier = diagnostic_synthesizer.blocker_identifier
        blockers = blocker_identifier.identify_blockers(profile)

        # Convert to diagnostic format
        blocker_dicts = []
        for blocker in blockers:
            blocker_dicts.append({
                "name": blocker.name,
                "description": blocker.description,
                "domain": blocker.domain,
                "priority": blocker.priority,
                "explanation": blocker.explanation
            })

        return {
            "project_id": project_id,
            "blockers": blocker_dicts,
            "count": len(blockers)
        }
    except Exception as e:
        logger.error(f"Failed to identify blockers for project {project_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to identify blockers")