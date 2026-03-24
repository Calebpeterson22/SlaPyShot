# tests/test_games.py - Tests for GamesEndpoint

import pytest
from unittest.mock import patch, MagicMock
import polars as pl

from slapyshot import NHLClient


GAME_ID = "abc-123-game-id"

# ---------------------------------------------------------------------------
# Shared mock API payloads
# ---------------------------------------------------------------------------

MOCK_SUMMARY_RESPONSE = {
    "game": {
        "id": GAME_ID,
        "home": {
            "id": "home-team-id",
            "name": "Home Team",
            "players": [
                {
                    "id": "player-1",
                    "full_name": "Alice Smith",
                    "primary_position": "C",
                    "statistics": {
                        "goals": 1,
                        "assists": 2,
                        "points": 3,
                        "plus_minus": 1,
                        "shots": 4,
                        "penalty_minutes": 0,
                        "time_on_ice": "18:32",
                    },
                }
            ],
        },
        "away": {
            "id": "away-team-id",
            "name": "Away Team",
            "players": [
                {
                    "id": "player-2",
                    "full_name": "Bob Jones",
                    "primary_position": "LW",
                    "statistics": {
                        "goals": 0,
                        "assists": 1,
                        "points": 1,
                        "plus_minus": -1,
                        "shots": 2,
                        "penalty_minutes": 2,
                        "time_on_ice": "14:10",
                    },
                }
            ],
        },
    }
}

MOCK_BOXSCORE_RESPONSE = {
    "game": {
        "id": GAME_ID,
        "home": {"id": "home-team-id", "name": "Home Team"},
        "away": {"id": "away-team-id", "name": "Away Team"},
        "scoring": [
            {
                "number": 1,
                "type": "period",
                "home_scoring": {"points": 2},
                "away_scoring": {"points": 1},
            },
            {
                "number": 2,
                "type": "period",
                "home_scoring": {"points": 1},
                "away_scoring": {"points": 0},
            },
            {
                "number": 3,
                "type": "period",
                "home_scoring": {"points": 0},
                "away_scoring": {"points": 2},
            },
        ],
    }
}

MOCK_PBP_RESPONSE = {
    "game": {
        "id": GAME_ID,
        "periods": [
            {
                "number": 1,
                "events": [
                    {
                        "id": "evt-1",
                        "event_type": "faceoff",
                        "clock": "20:00",
                        "description": "Faceoff at center ice",
                        "attribution": {
                            "id": "player-1",
                            "full_name": "Alice Smith",
                            "team_id": "home-team-id",
                        },
                    },
                    {
                        "id": "evt-2",
                        "event_type": "goal",
                        "clock": "12:34",
                        "description": "Goal by Alice Smith",
                        "attribution": {
                            "id": "player-1",
                            "full_name": "Alice Smith",
                            "team_id": "home-team-id",
                        },
                    },
                ],
            },
            {
                "number": 2,
                "events": [
                    {
                        "id": "evt-3",
                        "event_type": "shot",
                        "clock": "08:15",
                        "description": "Shot by Bob Jones",
                        "attribution": {
                            "id": "player-2",
                            "full_name": "Bob Jones",
                            "team_id": "away-team-id",
                        },
                    },
                ],
            },
        ],
    }
}


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def client():
    return NHLClient(api_key="test-api-key")


def make_mock_get(payload):
    """Return a patch-ready mock that returns the given payload from _get."""
    mock = MagicMock()
    mock.return_value = payload
    return mock


# ---------------------------------------------------------------------------
# get_game_summary tests
# ---------------------------------------------------------------------------

class TestGetGameSummary:

    def test_returns_dataframe(self, client):
        with patch.object(client, "_get", return_value=MOCK_SUMMARY_RESPONSE):
            result = client.games.get_game_summary(GAME_ID)
        assert isinstance(result, pl.DataFrame)

    def test_calls_correct_endpoint(self, client):
        with patch.object(client, "_get", return_value=MOCK_SUMMARY_RESPONSE) as mock_get:
            client.games.get_game_summary(GAME_ID)
        mock_get.assert_called_once_with(f"/games/{GAME_ID}/summary.json")

    def test_has_expected_columns(self, client):
        with patch.object(client, "_get", return_value=MOCK_SUMMARY_RESPONSE):
            result = client.games.get_game_summary(GAME_ID)
        expected_columns = {
            "game_id", "team_id", "team_name", "player_id", "full_name",
            "position", "goals", "assists", "points", "plus_minus",
            "shots", "penalty_minutes", "time_on_ice",
        }
        assert expected_columns.issubset(set(result.columns))

    def test_returns_one_row_per_player(self, client):
        with patch.object(client, "_get", return_value=MOCK_SUMMARY_RESPONSE):
            result = client.games.get_game_summary(GAME_ID)
        # Mock has 1 home player + 1 away player
        assert len(result) == 2

    def test_includes_both_teams(self, client):
        with patch.object(client, "_get", return_value=MOCK_SUMMARY_RESPONSE):
            result = client.games.get_game_summary(GAME_ID)
        team_names = result["team_name"].to_list()
        assert "Home Team" in team_names
        assert "Away Team" in team_names

    def test_game_id_populated(self, client):
        with patch.object(client, "_get", return_value=MOCK_SUMMARY_RESPONSE):
            result = client.games.get_game_summary(GAME_ID)
        assert all(gid == GAME_ID for gid in result["game_id"].to_list())

    def test_player_stats_values(self, client):
        with patch.object(client, "_get", return_value=MOCK_SUMMARY_RESPONSE):
            result = client.games.get_game_summary(GAME_ID)
        alice = result.filter(pl.col("full_name") == "Alice Smith")
        assert alice["goals"][0] == 1
        assert alice["assists"][0] == 2
        assert alice["points"][0] == 3
        assert alice["time_on_ice"][0] == "18:32"

    def test_empty_response_returns_empty_dataframe(self, client):
        empty = {"game": {"id": GAME_ID, "home": {"id": "h", "name": "H", "players": []}, "away": {"id": "a", "name": "A", "players": []}}}
        with patch.object(client, "_get", return_value=empty):
            result = client.games.get_game_summary(GAME_ID)
        assert len(result) == 0


# ---------------------------------------------------------------------------
# get_game_boxscore tests
# ---------------------------------------------------------------------------

class TestGetGameBoxscore:

    def test_returns_dataframe(self, client):
        with patch.object(client, "_get", return_value=MOCK_BOXSCORE_RESPONSE):
            result = client.games.get_game_boxscore(GAME_ID)
        assert isinstance(result, pl.DataFrame)

    def test_calls_correct_endpoint(self, client):
        with patch.object(client, "_get", return_value=MOCK_BOXSCORE_RESPONSE) as mock_get:
            client.games.get_game_boxscore(GAME_ID)
        mock_get.assert_called_once_with(f"/games/{GAME_ID}/boxscore.json")

    def test_has_expected_columns(self, client):
        with patch.object(client, "_get", return_value=MOCK_BOXSCORE_RESPONSE):
            result = client.games.get_game_boxscore(GAME_ID)
        expected_columns = {
            "game_id", "period_number", "period_type",
            "home_team_id", "home_team_name", "home_points",
            "away_team_id", "away_team_name", "away_points",
        }
        assert expected_columns.issubset(set(result.columns))

    def test_returns_one_row_per_period(self, client):
        with patch.object(client, "_get", return_value=MOCK_BOXSCORE_RESPONSE):
            result = client.games.get_game_boxscore(GAME_ID)
        # Mock has 3 periods
        assert len(result) == 3

    def test_period_numbers_are_correct(self, client):
        with patch.object(client, "_get", return_value=MOCK_BOXSCORE_RESPONSE):
            result = client.games.get_game_boxscore(GAME_ID)
        assert result["period_number"].to_list() == [1, 2, 3]

    def test_score_values(self, client):
        with patch.object(client, "_get", return_value=MOCK_BOXSCORE_RESPONSE):
            result = client.games.get_game_boxscore(GAME_ID)
        period_1 = result.filter(pl.col("period_number") == 1)
        assert period_1["home_points"][0] == 2
        assert period_1["away_points"][0] == 1

    def test_game_id_populated(self, client):
        with patch.object(client, "_get", return_value=MOCK_BOXSCORE_RESPONSE):
            result = client.games.get_game_boxscore(GAME_ID)
        assert all(gid == GAME_ID for gid in result["game_id"].to_list())

    def test_empty_scoring_returns_empty_dataframe(self, client):
        empty = {"game": {"id": GAME_ID, "home": {"id": "h", "name": "H"}, "away": {"id": "a", "name": "A"}, "scoring": []}}
        with patch.object(client, "_get", return_value=empty):
            result = client.games.get_game_boxscore(GAME_ID)
        assert len(result) == 0


# ---------------------------------------------------------------------------
# get_game_play_by_play tests
# ---------------------------------------------------------------------------

class TestGetGamePlayByPlay:

    def test_returns_dataframe(self, client):
        with patch.object(client, "_get", return_value=MOCK_PBP_RESPONSE):
            result = client.games.get_game_play_by_play(GAME_ID)
        assert isinstance(result, pl.DataFrame)

    def test_calls_correct_endpoint(self, client):
        with patch.object(client, "_get", return_value=MOCK_PBP_RESPONSE) as mock_get:
            client.games.get_game_play_by_play(GAME_ID)
        mock_get.assert_called_once_with(f"/games/{GAME_ID}/pbp.json")

    def test_has_expected_columns(self, client):
        with patch.object(client, "_get", return_value=MOCK_PBP_RESPONSE):
            result = client.games.get_game_play_by_play(GAME_ID)
        expected_columns = {
            "game_id", "period_number", "event_id", "event_type",
            "clock", "description", "player_id", "player_name", "team_id",
        }
        assert expected_columns.issubset(set(result.columns))

    def test_returns_one_row_per_event(self, client):
        with patch.object(client, "_get", return_value=MOCK_PBP_RESPONSE):
            result = client.games.get_game_play_by_play(GAME_ID)
        # Mock has 2 events in period 1 + 1 event in period 2
        assert len(result) == 3

    def test_period_numbers_assigned_correctly(self, client):
        with patch.object(client, "_get", return_value=MOCK_PBP_RESPONSE):
            result = client.games.get_game_play_by_play(GAME_ID)
        assert result["period_number"].to_list() == [1, 1, 2]

    def test_event_types_present(self, client):
        with patch.object(client, "_get", return_value=MOCK_PBP_RESPONSE):
            result = client.games.get_game_play_by_play(GAME_ID)
        event_types = result["event_type"].to_list()
        assert "faceoff" in event_types
        assert "goal" in event_types
        assert "shot" in event_types

    def test_can_filter_goals(self, client):
        with patch.object(client, "_get", return_value=MOCK_PBP_RESPONSE):
            result = client.games.get_game_play_by_play(GAME_ID)
        goals = result.filter(pl.col("event_type") == "goal")
        assert len(goals) == 1
        assert goals["player_name"][0] == "Alice Smith"

    def test_game_id_populated(self, client):
        with patch.object(client, "_get", return_value=MOCK_PBP_RESPONSE):
            result = client.games.get_game_play_by_play(GAME_ID)
        assert all(gid == GAME_ID for gid in result["game_id"].to_list())

    def test_empty_periods_returns_empty_dataframe(self, client):
        empty = {"game": {"id": GAME_ID, "periods": []}}
        with patch.object(client, "_get", return_value=empty):
            result = client.games.get_game_play_by_play(GAME_ID)
        assert len(result) == 0