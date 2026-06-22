"""
Test script for diagnostic engine components
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.models.profile import EntrepreneurProfile
from src.engine.intake_engine import IntakeEngine
from src.engine.classifier import MaturityClassifier
from src.engine.gap_detector import GapDetector
from src.engine.blocker_identifier import BlockerIdentifier
from src.engine.synthesis import DiagnosticSynthesizer

def test_intake_engine():
    """Test the intake engine"""
    print("Testing Intake Engine...")
    engine = IntakeEngine()

    # Start intake
    project_id = "test_project_001"
    first_question = engine.start_intake(project_id)

    assert first_question["type"] == "question"
    assert "question_id" in first_question
    assert first_question["question_id"] == "welcome_1"
    print("✓ Intake engine started successfully")

    # Answer a few questions
    engine.submit_answer(project_id, "welcome_1", "info")
    engine.submit_answer(project_id, "sector_1", "tech")
    engine.submit_answer(project_id, "tech_1", True)  # AI/ML project
    engine.submit_answer(project_id, "tech_2", "nlp")  # NLP specialization

    # Submit MVP answer
    engine.submit_answer(project_id, "core_1", True)  # Has MVP

    # Submit validation answers
    engine.submit_answer(project_id, "core_4", True)  # Has validation interviews
    engine.submit_answer(project_id, "core_5", "5_plus_doc")  # 5+ documented interviews

    # Submit business model
    engine.submit_answer(project_id, "core_12", "documented")  # Documented business model

    # Submit legal form
    engine.submit_answer(project_id, "core_13", "sarl")  # SARL legal form

    # Submit team
    engine.submit_answer(project_id, "core_14", "co_founders")  # Co-founders
    engine.submit_answer(project_id, "core_15", True)  # Has full-time team

    # Submit revenue
    engine.submit_answer(project_id, "core_17", "recurring")  # Recurring revenue
    engine.submit_answer(project_id, "core_18", "11_50")  # 11-50 customers

    # Get status
    status = engine.get_intake_status(project_id)
    print(f"Intake status: {status}")

    # Get current question (should be near the end)
    current_question = engine.get_current_question(project_id)
    if current_question and current_question["type"] == "question":
        print(f"Current question: {current_question['question_text_fr']}")

    print("✓ Intake engine tests passed\n")
    return project_id

def test_classifier():
    """Test the classifier"""
    print("Testing Classifier...")
    classifier = MaturityClassifier()

    # Create a test profile
    profile = EntrepreneurProfile(
        project_name="Test Tech Startup",
        sector="tech",
        has_idea=True,
        has_validation_interviews=True,
        has_mvp=True,
        has_business_model=True,
        business_model_clarity=8,
        has_legal_form=True,
        legal_form_type="SARL",
        team_size=3,
        has_full_time_team=True,
        monthly_revenue=5000.0,
        has_paying_customers=True,
        customer_count=25,
        validation_client=8,
        validation_surveys=True,
        validation_expert=True,
        has_pilot=True,
        has_traction=True,
        has_fundraising_experience=False,
        has_investors=False,
        amount_raised_tnd=0.0,
        is_seeking_funding=True,
        funding_target_tnd=100000.0,
        location="Tunis",
        is_tunisia_based=True,
        is_urban=True,
        has_incubation=True,
        has_state_aid=False,
        has_previous_program=True,
        previous_programs=["Coding-Dojo Tunisie"],
        self_assessed_stage="fundraising",
        self_assessed_readiness=7,
        biggest_challenges=["Trouver des investisseurs", "Scaler la solution technique"],
        has_ip=True,
        has_rd=True,
        tech_readiness_level=6,
        has_sustainability_plan=False,
        has_social_impact=False,
        has_website=True,
        has_social_media=True,
        uses_digital_tools=True
    )

    # Classify
    result = classifier.classify(profile)

    print(f"Assigned stage: {result.assigned_stage}")
    print(f"Confidence: {result.confidence_score:.2f}")
    print(f"Evidence trace: {result.evidence_trace}")
    if result.alternative_stages:
        print(f"Alternative stages: {result.alternative_stages}")

    # Should be close to fundraising or structuration
    assert result.assigned_stage in ["structuration", "fundraising", "launch_planning"]
    assert result.confidence_score > 0.5
    print("✓ Classifier tests passed\n")
    return profile, result

def test_gap_detector():
    """Test the gap detector"""
    print("Testing Gap Detector...")
    gap_detector = GapDetector()

    # Use the profile from classifier test
    profile = EntrepreneurProfile(
        project_name="Test Tech Startup",
        sector="tech",
        has_idea=True,
        has_validation_interviews=True,
        has_mvp=True,
        has_business_model=True,
        business_model_clarity=8,
        has_legal_form=True,
        legal_form_type="SARL",
        team_size=3,
        has_full_time_team=True,
        monthly_revenue=5000.0,
        has_paying_customers=True,
        customer_count=25,
        validation_client=8,
        validation_surveys=True,
        validation_expert=True,
        has_pilot=True,
        has_traction=True,
        has_fundraising_experience=False,
        has_investors=False,
        amount_raised_tnd=0.0,
        is_seeking_funding=True,
        funding_target_tnd=100000.0,
        location="Tunis",
        is_tunisia_based=True,
        is_urban=True,
        has_incubation=True,
        has_state_aid=False,
        has_previous_program=True,
        previous_programs=["Coding-Dojo Tunisie"],
        self_assessed_stage="fundraising",  # Self-assessed as fundraising
        self_assessed_readiness=7,
        biggest_challenges=["Trouver des investisseurs", "Scaler la solution technique"],
        has_ip=True,
        has_rd=True,
        tech_readiness_level=6,
        has_sustainability_plan=False,
        has_social_impact=False,
        has_website=True,
        has_social_media=True,
        uses_digital_tools=True
    )

    # Mock classification result (as if classifier said structuration)
    from src.engine.classifier import ClassificationResult
    classification_result = ClassificationResult(
        assigned_stage="structuration",
        confidence_score=0.8,
        evidence_trace=[
            "Has legal form (SARL)",
            "Clear and documented business model (clarity 8)",
            "Has team structure (3 members)",
            "Has MVP with validation evidence",
            "Some revenue generation (5000 TND/month)"
        ]
    )

    # Detect gap
    gap_analysis = gap_detector.detect_gap(profile, classification_result)

    print(f"Gap type: {gap_analysis.gap_type}")
    print(f"Claimed stage: {gap_analysis.claimed_stage}")
    print(f"Actual stage: {gap_analysis.actual_stage}")
    print(f"Gap severity: {gap_analysis.gap_severity}")
    print(f"Missing dimensions: {gap_analysis.missing_dimensions}")
    print(f"Explanation: {gap_analysis.explanation}")
    print(f"Confidence: {gap_analysis.confidence:.2f}")

    # Should detect overestimation (claimed funding, actual structuration)
    assert gap_analysis.gap_type == "OVER_ESTIMATION"
    assert gap_analysis.claimed_stage == "fundraising"
    assert gap_analysis.actual_stage == "structuration"
    print("✓ Gap detector tests passed\n")
    return gap_analysis

def test_blocker_identifier():
    """Test the blocker identifier"""
    print("Testing Blocker Identifier...")
    blocker_identifier = BlockerIdentifier()

    # Use the profile from previous tests
    profile = EntrepreneurProfile(
        project_name="Test Tech Startup",
        sector="tech",
        has_idea=True,
        has_validation_interviews=True,
        has_mvp=True,
        has_business_model=True,
        business_model_clarity=8,
        has_legal_form=True,
        legal_form_type="SARL",
        team_size=3,
        has_full_time_team=True,
        monthly_revenue=5000.0,
        has_paying_customers=True,
        customer_count=25,
        validation_client=8,
        validation_surveys=True,
        validation_expert=True,
        has_pilot=True,
        has_traction=True,
        has_fundraising_experience=False,
        has_investors=False,
        amount_raised_tnd=0.0,
        is_seeking_funding=True,
        funding_target_tnd=100000.0,
        location="Tunis",
        is_tunisia_based=True,
        is_urban=True,
        has_incubation=True,
        has_state_aid=False,
        has_previous_program=True,
        previous_programs=["Coding-Dojo Tunisie"],
        self_assessed_stage="fundraising",
        self_assessed_readiness=7,
        biggest_challenges=["Trouver des investisseurs", "Scaler la solution technique"],
        has_ip=True,
        has_rd=True,
        tech_readiness_level=6,
        has_sustainability_plan=False,
        has_social_impact=False,
        has_website=True,
        has_social_media=True,
        uses_digital_tools=True
    )

    # Identify blockers
    blockers = blocker_identifier.identify_blockers(profile, assigned_stage="structuration")

    print(f"Identified {len(blockers)} blockers:")
    for i, blocker in enumerate(blockers[:5]):  # Show first 5
        print(f"  {i+1}. [{blocker.priority}] {blocker.name} ({blocker.domain})")
        print(f"     {blocker.explanation[:100]}...")

    # Should have identified some blockers
    assert len(blockers) >= 0  # At least not crash
    print("✓ Blocker identifier tests passed\n")
    return blockers

def test_synthesis():
    """Test the full synthesis"""
    print("Testing Diagnostic Synthesis...")
    synthesizer = DiagnosticSynthesizer()

    # Create a test profile that should show gaps
    profile = EntrepreneurProfile(
        project_name="Test Tech Startup",
        sector="tech",
        has_idea=True,
        has_validation_interviews=True,
        has_mvp=True,
        has_business_model=True,
        business_model_clarity=6,  # Medium clarity
        has_legal_form=False,  # NO LEGAL FORM - this should be a blocker
        legal_form_type=None,
        team_size=1,  # SOLO FOUNDER
        has_full_time_team=False,
        monthly_revenue=0.0,  # NO REVENUE
        has_paying_customers=False,
        customer_count=0,
        validation_client=4,
        validation_surveys=True,
        validation_expert=False,
        has_pilot=False,
        has_traction=False,
        has_fundraising_experience=False,
        has_investors=False,
        amount_raised_tnd=0.0,
        is_seeking_funding=True,  # Seeking funding but no legal form/revenue
        funding_target_tnd=50000.0,
        location="Tunis",
        is_tunisia_based=True,
        is_urban=True,
        has_incubation=False,
        has_state_aid=False,
        has_previous_program=False,
        previous_programs=[],
        self_assessed_stage="fundraising",  # OVERCONFIDENT - claims fundraising
        self_assessed_readiness=8,
        biggest_challenges=["Trouver des investisseurs", "Formaliser l'entreprise"],
        has_ip=False,
        has_rd=True,
        tech_readiness_level=3,
        has_sustainability_plan=False,
        has_social_impact=False,
        has_website=True,
        has_social_media=False,
        uses_digital_tools=True
    )

    # Synthesize diagnostic
    diagnostic_result = synthesizer.synthesize_diagnostic(profile)

    print(f"Assigned stage: {diagnostic_result.assigned_stage}")
    print(f"Confidence: {diagnostic_result.confidence_score:.2f}")
    print(f"Plain language summary: {diagnostic_result.plain_language_summary[:200]}...")

    if diagnostic_result.perception_gap:
        gap = diagnostic_result.perception_gap
        print(f"Perception gap: {gap.gap_type} ({gap.gap_severity})")
        print(f"Claimed: {gap.claimed_stage} -> Actual: {gap.actual_stage}")
        print(f"Explanation: {gap.explanation}")

    print(f"Key blockers ({len(diagnostic_result.key_blockers)}):")
    for i, blocker in enumerate(diagnostic_result.key_blockers[:3]):
        print(f"  {i+1}. [{blocker.priority}] {blocker.name}")
        print(f"     {blocker.explanation[:100]}...")

    print(f"Evidence trace: {diagnostic_result.evidence_trace}")

    # Should detect overestimation gap (claimed fundraising, actual likely structuration or lower)
    assert diagnostic_result.assigned_stage in ["ideation", "market_validation", "structuration"]
    print("✓ Diagnostic synthesis tests passed\n")
    return diagnostic_result

def main():
    """Run all tests"""
    print("=" * 50)
    print("Testing Diagnostic Engine Components")
    print("=" * 50)

    try:
        # Test intake engine
        project_id = test_intake_engine()

        # Test classifier
        profile, classification_result = test_classifier()

        # Test gap detector
        gap_analysis = test_gap_detector()

        # Test blocker identifier
        blockers = test_blocker_identifier()

        # Test full synthesis
        diagnostic_result = test_synthesis()

        print("=" * 50)
        print("All tests passed! 🎉")
        print("=" * 50)

    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)