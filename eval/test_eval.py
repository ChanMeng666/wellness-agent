"""Evaluation script for Wellness Agent."""

import pathlib

import dotenv
from google.adk.evaluation.agent_evaluator import AgentEvaluator
import pytest


@pytest.fixture(scope="session", autouse=True)
def load_env():
    """Load environment variables for tests."""
    dotenv.load_dotenv()


def test_basic():
    """Test the agent's basic ability on common examples."""
    AgentEvaluator.evaluate(
        "wellness_agent",
        str(pathlib.Path(__file__).parent / "data"),
        num_runs=1,
    )


if __name__ == "__main__":
    test_basic() 