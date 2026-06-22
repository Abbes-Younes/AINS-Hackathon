"""
Adaptive Diagnostic Intake Engine
Handles the adaptive questionnaire logic based on decision tree
"""

import yaml
from typing import Dict, Any, Optional, List
from pathlib import import Path
import logging

from src.models.profile import EntrepreneurProfile

logger = logging.getLogger(__name__)


class IntakeEngine:
    """Manages adaptive diagnostic intake session"""

    def __init__(self, decision_tree_path: Optional[str] = None):
        """
        Initialize the intake engine with a decision tree

        Args:
            decision_tree_path: Path to the decision tree YAML file
        """
        if decision_tree_path is None:
            # Default to the decision tree in the same directory
            decision_tree_path = Path(__file__).parent / "decision_tree.yml"

        self.decision_tree = self._load_decision_tree(decision_tree_path)
        self.sessions: Dict[str, Dict[str, Any]] = {}  # project_id -> session state

    def _load_decision_tree(self, path: Path) -> Dict[str, Any]:
        """Load decision tree from YAML file"""
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except Exception as e:
            logger.error(f"Failed to load decision tree from {path}: {e}")
            raise

    def start_intake(self, project_id: str) -> Dict[str, Any]:
        """
        Start a new intake session for a project

        Args:
            project_id: Unique identifier for the project

        Returns:
            First question to ask the user
        """
        # Initialize session state
        self.sessions[project_id] = {
            "current_node": self.decision_tree["start_node"],
            "answers": {},
            "profile_data": {},
            "completed": False
        }

        # Get the first question
        return self._get_current_question(project_id)

    def submit_answer(self, project_id: str, question_id: str, answer: Any) -> Dict[str, Any]:
        """
        Submit an answer and get the next question

        Args:
            project_id: Project identifier
            question_id: ID of the question being answered
            answer: User's answer

        Returns:
            Next question or completion signal
        """
        if project_id not in self.sessions:
            raise ValueError(f"No active intake session for project {project_id}")

        session = self.sessions[project_id]

        # Store the answer
        session["answers"][question_id] = answer

        # Extract profile data from answer
        self._extract_profile_data(session, question_id, answer)

        # Determine next node based on current node and answer
        current_node_key = session["current_node"]
        current_node = self.decision_tree["nodes"][current_node_key]

        # Find matching rule
        next_node_key = None
        for rule in current_node["next_rules"]:
            if self._evaluate_condition(rule["condition"], session):
                next_node_key = rule["next_node"]
                break

        # If no rule matches, try default (always true)
        if next_node_key is None:
            for rule in current_node["next_rules"]:
                if rule["condition"] == "always":
                    next_node_key = rule["next_node"]
                    break

        # Update current node
        session["current_node"] = next_node_key

        # Check if we've reached a terminal node
        next_node = self.decision_tree["nodes"].get(next_node_key)
        if next_node and next_node.get("type") == "terminal":
            session["completed"] = True
            return {
                "type": "completion",
                "message_fr": next_node["question_text_fr"],
                "message_ar": next_node["question_text_ar"],
                "profile_data": session["profile_data"]
            }

        # Return next question
        return self._format_question(next_node_key, session)

    def get_intake_status(self, project_id: str) -> Dict[str, Any]:
        """
        Get current intake status

        Args:
            project_id: Project identifier

        Returns:
            Status information
        """
        if project_id not in self.sessions:
            return {"error": "No active session"}

        session = self.sessions[project_id]
        return {
            "project_id": project_id,
            "completed": session["completed"],
            "current_node": session["current_node"],
            "answers_count": len(session["answers"]),
            "profile_data": session["profile_data"] if session["completed"] else None
        }

    def get_current_question(self, project_id: str) -> Optional[Dict[str, Any]]:
        """
        Get the current question for a project

        Args:
            project_id: Project identifier

        Returns:
            Current question or None if completed/not found
        """
        if project_id not in self.sessions:
            return None

        session = self.sessions[project_id]
        if session["completed"]:
            return None

        return self._get_current_question(project_id)

    def _get_current_question(self, project_id: str) -> Dict[str, Any]:
        """Get formatted current question"""
        session = self.sessions[project_id]
        current_node_key = session["current_node"]
        return self._format_question(current_node_key, session)

    def _format_question(self, node_key: str, session: Dict[str, Any]) -> Dict[str, Any]:
        """Format a question node for output"""
        node = self.decision_tree["nodes"][node_key]

        return {
            "type": "question",
            "question_id": node["question_id"],
            "question_text_fr": node["question_text_fr"],
            "question_text_ar": node["question_text_ar"],
            "input_type": node["input_type"],
            "options": node.get("options", []),
            "context": {
                "answers_so_far": len(session["answers"]),
                "current_node": node_key
            }
        }

    def _extract_profile_data(self, session: Dict[str, Any], question_id: str, answer: Any):
        """Extract profile data from question-answer pairs"""
        # Mapping of question IDs to profile fields and extraction logic
        extraction_map = {
            # Sector questions
            "sector_1": ("sector", lambda x: x),

            # Tech-specific
            "tech_2": ("tech_specialization", lambda x: x),
            "tech_3": ("tech_solution_type", lambda x: x),

            # Agri-food specific
            "agri_food_2": ("agri_food_processing_type", lambda x: x),
            "agri_food_3": ("agri_food_production_type", lambda x: x),

            # Artisanat specific
            "artisanat_1": ("artisanat_type", lambda x: x),

            # Core validation
            "core_1": ("has_mvp", lambda x: x == True),
            "core_2": ("idea_stage_research", lambda x: x == True),
            "core_3": ("market_research_type", lambda x: x),
            "core_4": ("has_validation_interviews", lambda x: x == True),
            "core_5": ("validation_interviews_detail", lambda x: x),
            "core_6": ("mvp_no_validation", lambda x: x == True),
            "core_7": ("mvp_assumptions_type", lambda x: x),
            "core_8": ("seeking_user_feedback", lambda x: x == True),
            "core_9": ("feedback_plan", lambda x: x),
            "core_10": ("has_pilot", lambda x: x == True),
            "core_11": ("pilot_results", lambda x: x),
            "core_12": ("business_model_clarity", lambda x: {"undefined": 0, "draft": 2, "tested": 4, "documented": 6}[x]),
            "core_13": ("legal_form_type", lambda x: x),
            "core_14": ("team_structure", lambda x: x),
            "core_15": ("has_full_time_team", lambda x: x == True),
            "core_16": ("has_part_time_team", lambda x: x == True),
            "core_17": ("revenue_status", lambda x: x),
            "core_18": ("customer_count_range", lambda x: x),
            "core_19": ("is_seeking_funding", lambda x: x == True),
            "core_20": ("has_fundraising_experience", lambda x: x == True),
            "core_21": ("amount_raised_tnd", lambda x: self._convert_funding_amount(x)),
            "core_22": ("funding_target_tnd", lambda x: self._convert_funding_target(x)),
            "core_23": ("not_seeking_funding_reason", lambda x: x),

            # Support history
            "support_1": ("has_incubation", lambda x: x == True),
            "support_2": ("incubation_program_type", lambda x: x),
            "support_3": ("has_state_aid", lambda x: x == True),
            "support_4": ("state_aid_type", lambda x: x),
            "support_5": ("has_previous_program", lambda x: x == True),
            "support_6": ("previous_programs", lambda x: [p.strip() for p in x.split(",")] if x else []),

            # IP/R&D
            "ip_rd_1": ("has_ip_or_rd", lambda x: x == True),
            "ip_rd_2": ("ip_type", lambda x: x),
            "ip_rd_3": ("tech_readiness_level", lambda x: {"trl_1_2": 1, "trl_3_4": 3, "trl_5_6": 5, "trl_7_8": 7, "trl_9": 9}[x]),

            # Sustainability
            "sust_1": ("has_sustainability_plan", lambda x: x == True),
            "sust_2": ("sustainability_type", lambda x: x),

            # Digital presence
            "digital_1": ("has_website_or_social_media", lambda x: x == True),
            "digital_2": ("digital_presence_details", lambda x: x),
        }

        if question_id in extraction_map:
            field_name, extractor = extraction_map[question_id]
            try:
                extracted_value = extractor(answer)
                session["profile_data"][field_name] = extracted_value
            except Exception as e:
                logger.warning(f"Failed to extract data for {question_id}: {e}")
                # Store raw answer as fallback
                session["profile_data"][question_id] = answer

    def _evaluate_condition(self, condition: str, session: Dict[str, Any]) -> bool:
        """Evaluate a condition string against session data"""
        # Simple condition evaluation - in practice, this would be more sophisticated
        if condition == "always":
            return True
        elif condition == "never":
            return False

        # Handle basic equality checks: "selected == 'tech'"
        if " == " in condition:
            left, right = condition.split(" == ", 1)
            left = left.strip()
            right = right.strip().strip("'\"")

            # Handle special cases like "selected"
            if left == "selected":
                # Find the sector question answer
                sector_answer = session["answers"].get("sector_1")
                return sector_answer == right
            elif left == "answer":
                # Find the most recent answer (this is simplified)
                # In a real implementation, we'd track the current question better
                last_question_id = list(session["answers"].keys())[-1] if session["answers"] else None
                if last_question_id:
                    last_answer = session["answers"][last_question_id]
                    return str(last_answer).lower() == right.lower()
                return False
            elif left in session["profile_data"]:
                return session["profile_data"][left] == right
            elif left in session["answers"]:
                return session["answers"][left] == right

        # Handle AND conditions
        if " AND " in condition:
            sub_conditions = condition.split(" AND ")
            return all(self._evaluate_condition(sub_cond.strip(), session) for sub_cond in sub_conditions)

        # Handle OR conditions
        if " OR " in condition:
            sub_conditions = condition.split(" OR ")
            return any(self._evaluate_condition(sub_cond.strip(), session) for sub_cond in sub_conditions)

        # Default to False for unrecognized conditions
        logger.warning(f"Unrecognized condition: {condition}")
        return False

    def _convert_funding_amount(self, amount_range: str) -> int:
        """Convert funding range string to approximate TND amount"""
        mapping = {
            "less_50k": 25000,
            "50_200k": 125000,
            "200_500k": 350000,
            "more_500k": 750000
        }
        return mapping.get(amount_range, 0)

    def _convert_funding_target(self, target_range: str) -> int:
        """Convert funding target range string to approximate TND amount"""
        mapping = {
            "less_100k": 50000,
            "100_500k": 300000,
            "more_500k": 750000,
            "not_sure": 0
        }
        return mapping.get(target_range, 0)

    def build_profile_from_session(self, project_id: str, base_profile: EntrepreneurProfile) -> EntrepreneurProfile:
        """
        Build a complete EntrepreneurProfile from session data

        Args:
            project_id: Project identifier
            base_profile: Base profile to update

        Returns:
            Updated EntrepreneurProfile
        """
        if project_id not in self.sessions:
            raise ValueError(f"No active intake session for project {project_id}")

        session = self.sessions[project_id]
        profile_data = session["profile_data"]

        # Update base profile with collected data
        # This maps our internal field names to the EntrepreneurProfile fields
        field_mapping = {
            # Basic info (would normally come from elsewhere)
            "sector": "sector",
            "tech_specialization": None,  # Store separately if needed
            "tech_solution_type": None,
            "agri_food_processing_type": None,
            "agri_food_production_type": None,
            "artisanat_type": None,

            # Validation and MVP
            "has_mvp": "has_mvp",
            "idea_stage_research": None,  # Internal tracking
            "market_research_type": None,
            "has_validation_interviews": "has_validation_interviews",
            "validation_interviews_detail": None,
            "mvp_no_validation": None,
            "mvp_assumptions_type": None,
            "seeking_user_feedback": None,
            "feedback_plan": None,
            "has_pilot": "has_pilot",
            "pilot_results": None,

            # Business model
            "business_model_clarity": "business_model_clarity",

            # Legal structure
            "legal_form_type": "legal_form_type",

            # Team
            "team_structure": "team_structure",  # Would need to map to team_size/has_full_time_team
            "has_full_time_team": "has_full_time_team",
            "has_part_time_team": None,

            # Financials
            "revenue_status": None,  # Map to monthly_revenue/has_paying_customers
            "customer_count_range": None,  # Map to customer_count
            "is_seeking_funding": "is_seeking_funding",
            "has_fundraising_experience": "has_fundraising_experience",
            "amount_raised_tnd": "amount_raised_tnd",
            "funding_target_tnd": "funding_target_tnd",
            "not_seeking_funding_reason": None,

            # Support history
            "has_incubation": "has_incubation",
            "incubation_program_type": None,
            "has_state_aid": "has_state_aid",
            "state_aid_type": None,
            "has_previous_program": "has_previous_program",
            "previous_programs": "previous_programs",

            # IP/R&D
            "has_ip_or_rd": None,  # Split into has_ip and has_rd
            "ip_type": None,
            "tech_readiness_level": "tech_readiness_level",

            # Sustainability
            "has_sustainability_plan": "has_sustainability_plan",
            "sustainability_type": None,

            # Digital presence
            "has_website_or_social_media": None,  # Split into has_website and has_social_media
            "digital_presence_details": None,
        }

        # Apply mappings
        for internal_field, profile_field in field_mapping.items():
            if internal_field in profile_data and profile_field is not None:
                setattr(base_profile, profile_field, profile_data[internal_field])

        # Handle special mappings that need conversion
        # Revenue status to monthly_revenue and has_paying_customers
        if "revenue_status" in profile_data:
            revenue_status = profile_data["revenue_status"]
            if revenue_status == "none":
                base_profile.monthly_revenue = 0
                base_profile.has_paying_customers = False
                base_profile.customer_count = 0
            elif revenue_status == "first_sales":
                base_profile.monthly_revenue = 100  # Minimal amount
                base_profile.has_paying_customers = True
                base_profile.customer_count = 1
            elif revenue_status == "recurring":
                base_profile.monthly_revenue = 1000  # Example recurring
                base_profile.has_paying_customers = True
                base_profile.customer_count = 10
            elif revenue_status == "profitable":
                base_profile.monthly_revenue = 5000  # Example profitable
                base_profile.has_paying_customers = True
                base_profile.customer_count = 50

        # Customer count range
        if "customer_count_range" in profile_data:
            ccr = profile_data["customer_count_range"]
            if ccr == "zero":
                base_profile.customer_count = 0
            elif ccr == "1_10":
                base_profile.customer_count = 5
            elif ccr == "11_50":
                base_profile.customer_count = 30
            elif ccr == "51_plus":
                base_profile.customer_count = 100

        # IP/R&D split
        if "has_ip_or_rd" in profile_data and profile_data["has_ip_or_rd"]:
            base_profile.has_ip = True
            base_profile.has_rd = True
            # Could refine based on ip_type if needed

        # Digital presence split
        if "has_website_or_social_media" in profile_data and profile_data["has_website_or_social_media"]:
            digital_details = profile_data.get("digital_presence_details", "")
            if "website" in digital_details.lower() or "site web" in digital_details.lower():
                base_profile.has_website = True
            if "social" in digital_details.lower() or "réseaux" in digital_details.lower():
                base_profile.has_social_media = True

        # Set self-assessed stage if we have it (would come from a specific question)
        # For now, we'll leave this to be determined during classification

        return base_profile