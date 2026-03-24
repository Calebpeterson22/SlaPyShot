from slapyshot import *
# tests/test_client.py - Tests for NHLClient

import time
import pytest
from unittest.mock import patch, MagicMock
from dotenv import load_dotenv
import os

from slapyshot import NHLClient

load_dotenv()


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def client():
    """Create a real NHLClient for the test session.

    Fails immediately with a clear message if the API key is not set,
    rather than producing confusing errors downstream.
    """
    api_key = os.getenv("SPORTRADAR_API_KEY")
    assert api_key, (
        "\n\nSPORTRADAR_API_KEY is not set.\n"
        "Add it to your .env file before running tests:\n\n"
        "    SPORTRADAR_API_KEY=your_key_here\n"
    )
    return NHLClient()


# ---------------------------------------------------------------------------
# Initialization tests
# ---------------------------------------------------------------------------

def test_client_loads_api_key_from_env(client):
    """Client should load the API key from the environment variable."""
    assert client.api_key is not None
    assert len(client.api_key) > 0


def test_client_defaults_to_trial_access_level(client):
    """Client should default to trial access level."""
    assert client.access_level == "trial"


def test_client_builds_correct_base_url_for_trial(client):
    """Client should build the correct base URL for trial access."""
    assert client.base_url == "https://api.sportradar.com/nhl/trial/v7/en"


def test_client_builds_correct_base_url_for_production():
    """Client should build the correct base URL for production access."""
    api_key = os.getenv("SPORTRADAR_API_KEY")
    prod_client = NHLClient(api_key=api_key, access_level="production")
    assert prod_client.base_url == "https://api.sportradar.com/nhl/production/v7/en"


def test_client_raises_on_missing_api_key(monkeypatch):
    """Client should raise a clear ValueError when no API key is provided."""
    monkeypatch.delenv("SPORTRADAR_API_KEY", raising=False)
    with pytest.raises(ValueError, match="SPORTRADAR_API_KEY"):
        NHLClient(api_key=None)


def test_client_raises_on_invalid_access_level():
    """Client should raise a clear ValueError for invalid access levels."""
    api_key = os.getenv("SPORTRADAR_API_KEY")
    with pytest.raises(ValueError, match="Invalid access_level"):
        NHLClient(api_key=api_key, access_level="premium")


def test_client_accepts_valid_access_levels():
    """Client should accept both 'trial' and 'production' access levels."""
    api_key = os.getenv("SPORTRADAR_API_KEY")
    for level in ("trial", "production"):
        c = NHLClient(api_key=api_key, access_level=level)
        assert c.access_level == level


# ---------------------------------------------------------------------------
# Endpoint attachment tests
# ---------------------------------------------------------------------------

def test_client_has_teams_endpoint(client):
    """Client should have a teams endpoint attached."""
    assert hasattr(client, "teams")


def test_client_has_schedule_endpoint(client):
    """Client should have a schedule endpoint attached."""
    assert hasattr(client, "schedule")


def test_client_has_games_endpoint(client):
    """Client should have a games endpoint attached."""
    assert hasattr(client, "games")


def test_client_has_players_endpoint(client):
    """Client should have a players endpoint attached."""
    assert hasattr(client, "players")


# ---------------------------------------------------------------------------
# Rate limiting tests
# ---------------------------------------------------------------------------

def test_rate_limiting_waits_between_calls(client):
    """Client should wait at least 1 second between consecutive API calls."""
    mock_response = MagicMock()
    mock_response.raise_for_status.return_value = None
    mock_response.json.return_value = {"conferences": []}

    with patch("slapyshot.client.requests.get", return_value=mock_response):
        start = time.time()
        client.teams.get_all_teams()
        client.teams.get_all_teams()
        elapsed = time.time() - start

    assert elapsed >= 1.0, (
        f"Expected at least 1.0s between calls due to rate limiting, "
        f"but only {elapsed:.2f}s elapsed."
    )


def test_rate_limit_delay_is_configurable():
    """Client should respect a custom rate_limit_delay value."""
    api_key = os.getenv("SPORTRADAR_API_KEY")
    slow_client = NHLClient(api_key=api_key, rate_limit_delay=2.0)
    assert slow_client.rate_limit_delay == 2.0


def test_rate_limiting_respects_custom_delay():
    """A client with a 2 second delay should wait at least 2 seconds between calls."""
    api_key = os.getenv("SPORTRADAR_API_KEY")
    slow_client = NHLClient(api_key=api_key, rate_limit_delay=2.0)

    mock_response = MagicMock()
    mock_response.raise_for_status.return_value = None
    mock_response.json.return_value = {"conferences": []}

    with patch("slapyshot.client.requests.get", return_value=mock_response):
        start = time.time()
        slow_client.teams.get_all_teams()
        slow_client.teams.get_all_teams()
        elapsed = time.time() - start

    assert elapsed >= 2.0, (
        f"Expected at least 2.0s between calls for custom rate limit, "
        f"but only {elapsed:.2f}s elapsed."
    )