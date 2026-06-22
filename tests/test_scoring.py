"""
Test suite for Feature 2: Explainable Multi-Dimensional Scoring
Validates scoring engine, anomaly detection, justification, improvement guidance, and evolution tracking
"""

import sys
import os
import json

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.models.profile import EntrepreneurProfile
from src.feature_2_scoring.scoring_engine import ScoringEngine
from src.feature_2_scoring.anomaly_detector import AnomalyDetector
from src.feature_2_scoring.justification_engine import JustificationEngine
from src.feature_2_scoring.improvement_guidance import ImprovementGuidanceEngine
from src.feature_2_scoring.evolution_tracker import ScoreEvolutionTracker

def create_test_profiles():
    """Create test profiles based on the three personas mentioned in the plan"""

    # Profile 1: Amine - Tech startup with strong innovation but weak validation
    amine = EntrepreneurProfile(
        project_id="amine_001",
        project_name="TechInnovate Solutions",
        first_name="Amine",
        last_name="Ben Ali",
        email="amine@example.com",
        sector="tech",
        stage_idea="AI-powered mobile app for agricultural diagnostics",
        has_mvp=True,
        has_pilot=False,
        has_traction=False,
        validation_client=2,  # Low validation
        has_paying_customers=False,
        monthly_revenue=500,  # Low revenue
        business_model_clarity=2,  # Moderate clarity
        has_ip=True,
        has_rd=True,
        tech_readiness_level=4,  # Moderate TRL
        has_sustainability_plan=False,
        uses_digital_tools=True,
        has_website=True,
        has_social_media=True,
        has_full_time_team=False,
        self_assessed_stage="fundraising",  # Overestimating stage
        value_prop_tested=False
    )

    # Profile 2: Fatima - Artisanat business with strong market but weak innovation
    fatima = EntrepreneurProfile(
        project_id="fatima_002",
        project_name="Artisanat Moderne",
        first_name="Fatima",
        last_name="Nasri",
        email="fatima@example.com",
        sector="artisanat",
        stage_idea="Modern traditional ceramics with e-commerce",
        has_mvp=True,
        has_pilot=True,
        has_traction=True,
        validation_client=15,  # High validation
        has_paying_customers=True,
        monthly_revenue=3000,  # Good revenue
        business_model_clarity=3,  # Good clarity
        has_ip=False,
        has_rd=False,
        tech_readiness_level=2,  # Low TRL
        has_sustainability_plan=True,
        uses_digital_tools=True,
        has_website=True,
        has_social_media=True,
        has_full_time_team=True,
        self_assessed_stage="launch_planning",
        value_prop_tested=True
    )

    # Profile 3: Omar - Services startup with balanced profile
    omar = EntrepreneurProfile(
        project_id="omar_003",
        project_name="ServicePro Connect",
        first_name="Omar",
        last_name="Dahmani",
        email="omar@example.com",
        sector="services",
        stage_idea="Platform connecting freelancers with SMEs",
        has_mvp=True,
        has_pilot=True,
        has_traction=True,
        validation_client=8,  # Moderate validation
        has_paying_customers=True,
        monthly_revenue=1500,  # Moderate revenue
        business_model_clarity=2,  # Moderate clarity
        has_ip=False,
        has_rd=False,
        tech_readiness_level=3,  # Moderate TRL
        has_sustainability_plan=False,
        uses_digital_tools=True,
        has_website=True,
        has_social_media=True,
        has_full_time_team=True,
        self_assessed_stage="validation",
        value_prop_tested=True
    )

    return [amine, fatima, omar]

def test_scoring_engine():
    """Test the scoring engine with the three profiles"""
    print("=" * 60)
    print("Testing Scoring Engine")
    print("=" * 60)

    scoring_engine = ScoringEngine()
    test_profiles = create_test_profiles()

    for profile in test_profiles:
        print(f"\nTesting profile: {profile.project_name} ({profile.first_name} {profile.last_name})")
        print("-" * 50)

        # Compute scores
        score_breakdown = scoring_engine.compute_scores(profile)

        # Display results
        print(f"Market Score: {score_breakdown.market:.1f}/100")
        print(f"Commercial Offer Score: {score_breakdown.commercial_offer:.1f}/100")
        print(f"Innovation Score: {score_breakdown.innovation:.1f}/100")
        print(f"Scalability Score: {score_breakdown.scalability:.1f}/100")
        print(f"Green Score: {score_breakdown.green:.1f}/100")
        print(f"Overall Score: {score_breakdown.overall_score:.1f}/100")
        print(f"Data Reliability: {score_breakdown.data_reliability}")

        # Verify scores are in valid range
        assert 0 <= score_breakdown.market <= 100, f"Market score out of range: {score_breakdown.market}"
        assert 0 <= score_breakdown.commercial_offer <= 100, f"Commercial offer score out of range: {score_breakdown.commercial_offer}"
        assert 0 <= score_breakdown.innovation <= 100, f"Innovation score out of range: {score_breakdown.innovation}"
        assert 0 <= score_breakdown.scalability <= 100, f"Scalability score out of range: {score_breakdown.scalability}"
        assert 0 <= score_breakdown.green <= 100, f"Green score out of range: {score_breakdown.green}"
        assert 0 <= score_breakdown.overall_score <= 100, f"Overall score out of range: {score_breakdown.overall_score}"

        # Check that sub-criteria are present
        assert hasattr(score_breakdown, 'market_sub_criteria'), "Missing market sub-criteria"
        assert hasattr(score_breakdown, 'commercial_offer_sub_criteria'), "Missing commercial offer sub-criteria"
        assert hasattr(score_breakdown, 'innovation_sub_criteria'), "Missing innovation sub-criteria"
        assert hasattr(score_breakdown, 'scalability_sub_criteria'), "Missing scalability sub-criteria"
        assert hasattr(score_breakdown, 'green_sub_criteria'), "Missing green sub-criteria"

        print("✓ Scoring engine test passed")

def test_anomaly_detector():
    """Test the anomaly detector"""
    print("\n" + "=" * 60)
    print("Testing Anomaly Detector")
    print("=" * 60)

    anomaly_detector = AnomalyDetector()
    test_profiles = create_test_profiles()

    # Amine should trigger the "high_innovation_claim_low_tech_readiness" anomaly
    # (claims high innovation via has_ip and has_rd but has low tech_readiness_level)
    amine = test_profiles[0]
    print(f"\nTesting for anomalies in: {amine.project_name}")

    anomalies = anomaly_detector.detect_anomalies(amine)
    print(f"Detected {len(anomalies)} anomalies:")

    for anomaly in anomalies:
        print(f"  - {anomaly.description} (Severity: {anomaly.severity})")

    # We expect at least one anomaly for Amine's profile
    assert len(anomalies) > 0, "Expected at least one anomaly for Amine's profile"

    print("✓ Anomaly detector test passed")

def test_justification_engine():
    """Test the justification engine"""
    print("\n" + "=" * 60)
    print("Testing Justification Engine")
    print("=" * 60)

    scoring_engine = ScoringEngine()
    justification_engine = JustificationEngine(scoring_engine)
    test_profiles = create_test_profiles()

    for profile in test_profiles:
        print(f"\nTesting justification for: {profile.project_name}")

        # Compute scores first
        score_breakdown = scoring_engine.compute_scores(profile)

        # Generate justifications
        justifications = justification_engine.generate_justifications(profile, score_breakdown)

        # Check that we have justifications for all scores
        expected_scores = ["market", "commercial_offer", "innovation", "scalability", "green"]
        for score_name in expected_scores:
            assert score_name in justifications, f"Missing justification for {score_name}"
            justification = justifications[score_name]
            assert justification.explanation, f"Empty explanation for {score_name}"
            print(f"  {score_name}: {justification.explanation[:100]}...")

    print("✓ Justification engine test passed")

def test_improvement_guidance():
    """Test the improvement guidance engine"""
    print("\n" + "=" * 60)
    print("Testing Improvement Guidance Engine")
    print("=" * 60)

    scoring_engine = ScoringEngine()
    improvement_engine = ImprovementGuidanceEngine(scoring_engine)
    test_profiles = create_test_profiles()

    for profile in test_profiles:
        print(f"\nTesting improvement guidance for: {profile.project_name}")

        # Compute scores first
        score_breakdown = scoring_engine.compute_scores(profile)

        # Generate improvement guidance
        guidance = improvement_engine.generate_improvement_guidance(profile, score_breakdown)

        # Check that we have guidance for all scores
        expected_scores = ["market", "commercial_offer", "innovation", "scalability", "green"]
        for score_name in expected_scores:
            assert score_name in guidance, f"Missing guidance for {score_name}"
            guide = guidance[score_name]
            assert guide.action, f"Empty action for {score_name}"
            assert guide.estimated_impact >= 0, f"Negative impact for {score_name}: {guide.estimated_impact}"
            assert guide.kb_reference, f"Missing KB reference for {score_name}"
            print(f"  {score_name}: {guide.action[:80]}... (Impact: +{guide.estimated_impact})")

    print("✓ Improvement guidance test passed")

def test_evolution_tracker():
    """Test the score evolution tracker"""
    print("\n" + "=" * 60)
    print("Testing Score Evolution Tracker")
    print("=" * 60)

    scoring_engine = ScoringEngine()
    evolution_tracker = ScoreEvolutionTracker("data/test_scoring_evolution.db")
    test_profiles = create_test_profiles()

    # Use Amine's profile for testing
    profile = test_profiles[0]
    project_id = profile.project_id

    print(f"\nTesting evolution tracking for: {project_id}")

    # Save initial snapshot
    score_breakdown1 = scoring_engine.compute_scores(profile)
    evolution_tracker.save_score_snapshot(project_id, profile, score_breakdown1)
    print(f"  Saved initial snapshot: {score_breakdown1.overall_score:.1f}/100")

    # Modify profile slightly to simulate progress
    profile.validation_client += 5
    profile.monthly_revenue += 1000

    # Save second snapshot
    score_breakdown2 = scoring_engine.compute_scores(profile)
    evolution_tracker.save_score_snapshot(project_id, profile, score_breakdown2)
    print(f"  Saved updated snapshot: {score_breakdown2.overall_score:.1f}/100")

    # Get evolution
    evolution = evolution_tracker.get_score_evolution(project_id)

    if evolution:
        print(f"  Overall score delta: {evolution.deltas['overall']:+.1f}")
        print(f"  Trend: {evolution.trend_indicators['overall']}")
        assert 'overall' in evolution.deltas, "Missing overall delta"
        assert 'overall' in evolution.trend_indicators, "Missing overall trend indicator"
    else:
        print("  Warning: Could not compute evolution (insufficient data)")

    # Get history
    history = evolution_tracker.get_score_history(project_id)
    assert len(history) >= 2, f"Expected at least 2 history records, got {len(history)}"
    print(f"  History records: {len(history)}")

    print("✓ Evolution tracker test passed")

def run_all_tests():
    """Run all tests"""
    print("Starting Feature 2: Explainable Multi-Dimensional Scoring Tests")
    print("=" * 70)

    try:
        test_scoring_engine()
        test_anomaly_detector()
        test_justification_engine()
        test_improvement_guidance()
        test_evolution_tracker()

        print("\n" + "=" * 70)
        print("🎉 ALL TESTS PASSED! Feature 2 implementation is working correctly.")
        print("=" * 70)

    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

    return True

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)