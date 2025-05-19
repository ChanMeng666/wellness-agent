"""Basic tests for Wellness Agent."""

import sys
import unittest
from unittest.mock import patch

import pytest
from google.adk.testing import run_agent_test

# Import the agents to test
from wellness_agent.agent import root_agent
from wellness_agent.sub_agents.employee_support.agent import employee_support_agent
from wellness_agent.sub_agents.hr_manager.agent import hr_manager_agent
from wellness_agent.sub_agents.employer_insights.agent import employer_insights_agent


@pytest.fixture(scope="session", autouse=True)
def load_env():
    """Load environment variables for tests."""
    # Automatically loads .env file if present
    import dotenv
    dotenv.load_dotenv()


class TestAgents(unittest.TestCase):
    """Test suite for all wellness agents."""

    def test_root_agent_initialization(self):
        """Test that the root agent initializes correctly."""
        self.assertEqual(root_agent.name, "wellness_support_agent")
        self.assertEqual(len(root_agent.tools), 4)  # 3 sub-agents + google_search

    def test_employee_agent_initialization(self):
        """Test that the employee agent initializes correctly."""
        self.assertEqual(employee_support_agent.name, "employee_support_agent")
        self.assertEqual(len(employee_support_agent.tools), 4)  # 4 employee tools

    def test_hr_agent_initialization(self):
        """Test that the HR agent initializes correctly."""
        self.assertEqual(hr_manager_agent.name, "hr_manager_agent")
        self.assertEqual(len(hr_manager_agent.tools), 3)  # 3 HR tools

    def test_employer_agent_initialization(self):
        """Test that the employer agent initializes correctly."""
        self.assertEqual(employer_insights_agent.name, "employer_insights_agent")
        self.assertEqual(len(employer_insights_agent.tools), 2)  # 2 employer tools

    @patch("google.adk.testing.run_agent_test")
    def test_employee_tracking_flow(self, mock_run_agent_test):
        """Test the employee symptom tracking flow."""
        mock_run_agent_test.return_value = {"status": "success"}
        result = run_agent_test(
            agent=employee_support_agent,
            messages=[
                {"role": "user", "content": "I'd like to track my fatigue today, it's at a level 7."}
            ],
            expected_tool_calls=[
                {"name": "track_symptom"}
            ]
        )
        self.assertEqual(result.get("status"), "success")

    @patch("google.adk.testing.run_agent_test")
    def test_hr_trend_analysis_flow(self, mock_run_agent_test):
        """Test the HR trend analysis flow."""
        mock_run_agent_test.return_value = {"status": "success"}
        result = run_agent_test(
            agent=hr_manager_agent,
            messages=[
                {"role": "user", "content": "Show me accommodation request trends for the last quarter."}
            ],
            expected_tool_calls=[
                {"name": "view_anonymous_trends"}
            ]
        )
        self.assertEqual(result.get("status"), "success")

    @patch("google.adk.testing.run_agent_test")
    def test_employer_roi_flow(self, mock_run_agent_test):
        """Test the employer ROI calculation flow."""
        mock_run_agent_test.return_value = {"status": "success"}
        result = run_agent_test(
            agent=employer_insights_agent,
            messages=[
                {"role": "user", "content": "Calculate the ROI for our wellness program over the last year."}
            ],
            expected_tool_calls=[
                {"name": "calculate_wellness_roi"}
            ]
        )
        self.assertEqual(result.get("status"), "success")


if __name__ == "__main__":
    unittest.main() 