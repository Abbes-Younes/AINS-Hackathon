"""
API Routes for Feature 3: RAG-Grounded Roadmap & Resource Orientation
Handles roadmap generation, resource search, and grounded conversational assistance.
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, List, Any, Optional
from pathlib import Path
import sys

# Add project root to path for importing models and services
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from src.models.diagnostic import DiagnosticResult
from src.models.scoring import ScoreResult
from src.models.roadmap import ResourceOrientation
from src.feature_3_rag.roadmap_generator import RoadmapGenerator
from src.feature_3_rag.query_generator import QueryGenerator
from src.feature_3_rag.retrieval_engine import retrieve_resources
from src.feature_3_rag.conversational_layer import ConversationalLayer
from src.api.routes.diagnostic import get_diagnostic_result
from src.api.routes.scoring import get_scoring_result

# Initialize router
router = APIRouter(prefix="/roadmap", tags=["roadmap"])

# Initialize services
roadmap_generator = RoadmapGenerator()
query_generator = QueryGenerator()
conversational_layer = ConversationalLayer()


@router.post("/generate/{project_id}", response_model=ResourceOrientation)
async def generate_roadmap(project_id: str):
    """
    Generate a personalized roadmap based on current diagnostic and scoring data.

    Args:
        project_id: Unique identifier for the entrepreneur's project

    Returns:
        ResourceOrientation containing the personalized roadmap
    """
    try:
        # Get diagnostic and scoring results
        diagnostic_result = await get_diagnostic_result(project_id)
        score_result = await get_scoring_result(project_id)

        if not diagnostic_result:
            raise HTTPException(status_code=404, detail=f"Diagnostic result not found for project {project_id}")

        if not score_result:
            raise HTTPException(status_code=404, detail=f"Scoring result not found for project {project_id}")

        # Generate roadmap
        roadmap = roadmap_generator.generate_roadmap(
            diagnostic_result=diagnostic_result,
            score_result=score_result,
        )

        return roadmap

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate roadmap: {str(e)}")


@router.get("/{project_id}", response_model=ResourceOrientation)
async def get_roadmap(project_id: str):
    """
    Get the current roadmap for a project.

    Args:
        project_id: Unique identifier for the entrepreneur's project

    Returns:
        ResourceOrientation containing the current roadmap
    """
    # For now, we'll regenerate on each request
    # In a full implementation, this would be cached/stored
    return await generate_roadmap(project_id)


@router.get("/resources/search")
async def search_resources(
    q: str,
    project_id: Optional[str] = None,
    limit: int = 10
):
    """
    Search the knowledge base for resources.

    Args:
        q: Search query
        project_id: Optional project ID to contextualize search with diagnostic data
        limit: Maximum number of results to return

    Returns:
        List of resources with relevance scores
    """
    try:
        diagnostic_result = None
        score_result = None

        # If project_id provided, get diagnostic and scoring data for contextual search
        if project_id:
            diagnostic_result = await get_diagnostic_result(project_id)
            score_result = await get_scoring_result(project_id)

        # Generate query and filters if we have diagnostic/scoring data
        if diagnostic_result and score_result:
            query_string, structured_filters = query_generator.generate_query(
                diagnostic_result=diagnostic_result,
                score_result=score_result,
            )
            # Enhance the user query with contextual information
            enhanced_query = f"{q} {query_string}"

            resources = retrieve_resources(
                query_text=enhanced_query,
                eligibility_stages=structured_filters.get("eligibility_stages"),
                domains_addressed=structured_filters.get("domains_addressed"),
                blockers_resolved=structured_filters.get("blockers_resolved"),
                limit=limit,
            )
        else:
            # Simple search without contextual filtering
            resources = retrieve_resources(
                query_text=q,
                limit=limit,
            )

        return {
            "query": q,
            "results": resources,
            "total": len(resources)
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to search resources: {str(e)}")


@router.get("/resources/{resource_id}")
async def get_resource(resource_id: str):
    """
    Get detailed information about a specific resource.

    Args:
        resource_id: Unique identifier for the resource

    Returns:
        Resource details with full metadata
    """
    try:
        from src.feature_3_rag.retrieval_engine import RetrievalEngine

        engine = RetrievalEngine()
        try:
            resource = engine.get_resource_by_id(resource_id)
            if not resource:
                raise HTTPException(status_code=404, detail=f"Resource {resource_id} not found")
            return resource
        finally:
            engine.close()

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve resource: {str(e)}")


@router.post("/assistant/ask")
async def ask_assistant(
    project_id: str,
    question: str
):
    """
    Ask the grounded conversational assistant a question.

    Args:
        project_id: Unique identifier for the entrepreneur's project
        question: The user's question

    Returns:
        Assistant response grounded in diagnostic data, scores, and KB resources
    """
    try:
        # Get diagnostic and scoring results
        diagnostic_result = await get_diagnostic_result(project_id)
        score_result = await get_scoring_result(project_id)

        if not diagnostic_result:
            raise HTTPException(status_code=404, detail=f"Diagnostic result not found for project {project_id}")

        if not score_result:
            raise HTTPException(status_code=404, detail=f"Scoring result not found for project {project_id}")

        # Get roadmap for context (optional)
        roadmap = None
        try:
            roadmap = await generate_roadmap(project_id)
        except Exception:
            # Continue without roadmap if generation fails
            pass

        # Generate grounded response
        response, sources = conversational_layer.generate_response(
            user_query=question,
            diagnostic_result=diagnostic_result,
            score_result=score_result,
            roadmap=roadmap,
        )

        return {
            "question": question,
            "response": response,
            "sources": sources,
            "grounded": len(sources) > 0
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate assistant response: {str(e)}")


@router.get("/dashboard/{project_id}")
async def get_dashboard(project_id: str):
    """
    Get complete dashboard state for Mon Parcours view.

    Args:
        project_id: Unique identifier for the entrepreneur's project

    Returns:
        Complete dashboard state including diagnostics, scores, roadmap, and resources
    """
    try:
        # Get diagnostic and scoring results
        diagnostic_result = await get_diagnostic_result(project_id)
        score_result = await get_scoring_result(project_id)

        if not diagnostic_result:
            raise HTTPException(status_code=404, detail=f"Diagnostic result not found for project {project_id}")

        if not score_result:
            raise HTTPException(status_code=404, detail=f"Scoring result not found for project {project_id}")

        # Generate roadmap
        roadmap = await generate_roadmap(project_id)

        # Get recommended resources (top 5)
        query_string, structured_filters = query_generator.generate_query(
            diagnostic_result=diagnostic_result,
            score_result=score_result,
        )
        resources = retrieve_resources(
            query_text=query_string,
            eligibility_stages=structured_filters.get("eligibility_stages"),
            domains_addressed=structured_filters.get("domains_addressed"),
            blockers_resolved=structured_filters.get("blockers_resolved"),
            limit=5,
        )

        # Build dashboard response
        dashboard = {
            "project_id": project_id,
            "diagnostic": {
                "stage": diagnostic_result.assigned_stage,
                "confidence": getattr(diagnostic_result, 'confidence', None),
                "perception_gap": diagnostic_result.perception_gap.dict() if diagnostic_result.perception_gap else None,
                "key_blockers": diagnostic_result.key_blockers,
                "evidence_trace": diagnostic_result.evidence_trace,
            },
            "scoring": {
                "overall_score": score_result.overall_score,
                "composites": {k: v.dict() for k, v in score_result.composites.items()} if score_result.composites else {},
                "anomalies": [a.dict() for a in score_result.anomalies] if score_result.anomalies else [],
                "priorities": score_result.priorities,
                "executive_summary": score_result.executive_summary,
            },
            "roadmap": roadmap.dict(),
            "recommended_resources": resources,
            "dashboard_metadata": {
                "last_updated": None,  # Would be timestamp in full implementation
                "version": "1.0",
            }
        }

        return dashboard

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate dashboard: {str(e)}")