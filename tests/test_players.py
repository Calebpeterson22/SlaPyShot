# tests/test_players.py - Tests for PlayersEndpoint

import pytest
from unittest.mock import patch
import polars as pl

from slapyshot import NHLClient


PLAYER_ID = "player-uuid-123"
TEAM_ID = "team-uuid-456"

# ---------------------------------------------------------------------------
# Shared mock API payloads
# ---------------------------------------------------------------------------

MOCK_PLAYER_PROFILE_RESPONSE = {
    "id": PLAYER_ID,
    "full_name": "Alice Smith",
    "primary_position": "C",
    "seasons": [
        {
            "year": 2025,
            "type": "REG",
            "teams": [
                {
                    "id": TEAM_ID,
                    "name": "Bruins",
                    "totals": {
                        "statistics": {
                            "games_played": 72,
                            "goals": 30,
                            "assists": 40,
                            "points": 70,
                            "plus_minus": 15,
                            "shots": 200,
                            "penalty_minutes": 18,
                        }
                    },
                }
            ],
        },
        {
            "year": 2024,
            "type": "REG",
            "teams": [
                {
                    "id": TEAM_ID,
                    "name": "Bruins",
                    "totals": {
                        "statistics": {
                            "games_played": 68,
                            "goals": 25,
                            "assists": 35,
                            "points": 60,
                            "plus_minus": 10,
                            "shots": 180,
                            "penalty_minutes": 12,
                        }
                    },
                }
            ],
        },
    ],
}

MOCK_SEASON_STATS_RESPONSE = {
    "team": {
        "id": TEAM_ID,
        "name": "Bruins",
        "players": [
            {
                "id": "player-1",
                "full_name": "Alice Smith",
                "primary_position": "C",
                "statistics": {
                    "games_played": 72,
                    "goals": 30,
                    "assists": 40,
                    "points": 70,
                    "plus_minus": 15,
                    "shots": 200,
                    "penalty_minutes": 18,
                },
            },
            {
                "id": "player-2",
                "full_name": "Bob Jones",
                "primary_position": "G",
                "statistics": {
                    "games_played": 55,
                    "goals": 0,
                    "assists": 2,
                    "points": 2,
                    "plus_minus": 0,
                    "shots": 0,
                    "penalty_minutes": 4,
                },
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


# ---------------------------------------------------------------------------
# get_player_profile tests
# ---------------------------------------------------------------------------

class TestGetPlayerProfile:

    def test_returns_dataframe(self, client):
        with patch.object(client, "_get", return_value=MOCK_PLAYER_PROFILE_RESPONSE):
            result = client.players.get_player_profile(PLAYER_ID)
        assert isinstance(result, pl.DataFrame)

    def test_calls_correct_endpoint(self, client):
        with patch.object(client, "_get", return_value=MOCK_PLAYER_PROFILE_RESPONSE) as mock_get:
            client.players.get_player_profile(PLAYER_ID)
        mock_get.assert_called_once_with(f"/players/{PLAYER_ID}/profile.json")

    def test_has_expected_columns(self, client):
        with patch.object(client, "_get", return_value=MOCK_PLAYER_PROFILE_RESPONSE):
            result = client.players.get_player_profile(PLAYER_ID)
        expected = {
            "player_id", "full_name", "primary_position", "season_year",
            "season_type", "team_id", "team_name", "games_played",
            "goals", "assists", "points", "plus_minus", "shots", "penalty_minutes",
        }
        assert expected.issubset(set(result.columns))

    def test_returns_one_row_per_season(self, client):
        with patch.object(client, "_get", return_value=MOCK_PLAYER_PROFILE_RESPONSE):
            result = client.players.get_player_profile(PLAYER_ID)
        assert len(result) == 2

    def test_season_years_correct(self, client):
        with patch.object(client, "_get", return_value=MOCK_PLAYER_PROFILE_RESPONSE):
            result = client.players.get_player_profile(PLAYER_ID)
        assert set(result["season_year"].to_list()) == {2024, 2025}

    def test_stat_values_correct(self, client):
        with patch.object(client, "_get", return_value=MOCK_PLAYER_PROFILE_RESPONSE):
            result = client.players.get_player_profile(PLAYER_ID)
        season_2025 = result.filter(pl.col("season_year") == 2025)
        assert season_2025["goals"][0] == 30
        assert season_2025["points"][0] == 70
        assert season_2025["games_played"][0] == 72

    def test_player_fields_populated(self, client):
        with patch.object(client, "_get", return_value=MOCK_PLAYER_PROFILE_RESPONSE):
            result = client.players.get_player_profile(PLAYER_ID)
        assert all(pid == PLAYER_ID for pid in result["player_id"].to_list())
        assert all(fn == "Alice Smith" for fn in result["full_name"].to_list())

    def test_empty_seasons_returns_empty_dataframe(self, client):
        empty = {"id": PLAYER_ID, "full_name": "Alice Smith", "primary_position": "C", "seasons": []}
        with patch.object(client, "_get", return_value=empty):
            result = client.players.get_player_profile(PLAYER_ID)
        assert len(result) == 0


# ---------------------------------------------------------------------------
# get_player_season_stats tests
# ---------------------------------------------------------------------------

class TestGetPlayerSeasonStats:

    def test_returns_dataframe(self, client):
        with patch.object(client, "_get", return_value=MOCK_SEASON_STATS_RESPONSE):
            result = client.players.get_player_season_stats(2025, "REG", TEAM_ID)
        assert isinstance(result, pl.DataFrame)

    def test_calls_correct_endpoint(self, client):
        with patch.object(client, "_get", return_value=MOCK_SEASON_STATS_RESPONSE) as mock_get:
            client.players.get_player_season_stats(2025, "REG", TEAM_ID)
        mock_get.assert_called_once_with(f"/seasons/2025/REG/teams/{TEAM_ID}/statistics.json")

    def test_has_expected_columns(self, client):
        with patch.object(client, "_get", return_value=MOCK_SEASON_STATS_RESPONSE):
            result = client.players.get_player_season_stats(2025, "REG", TEAM_ID)
        expected = {
            "team_id", "team_name", "player_id", "full_name", "primary_position",
            "games_played", "goals", "assists", "points", "plus_minus",
            "shots", "penalty_minutes",
        }
        assert expected.issubset(set(result.columns))

    def test_returns_one_row_per_player(self, client):
        with patch.object(client, "_get", return_value=MOCK_SEASON_STATS_RESPONSE):
            result = client.players.get_player_season_stats(2025, "REG", TEAM_ID)
        assert len(result) == 2

    def test_stat_values_correct(self, client):
        with patch.object(client, "_get", return_value=MOCK_SEASON_STATS_RESPONSE):
            result = client.players.get_player_season_stats(2025, "REG", TEAM_ID)
        alice = result.filter(pl.col("player_id") == "player-1")
        assert alice["goals"][0] == 30
        assert alice["assists"][0] == 40
        assert alice["points"][0] == 70

    def test_team_fields_populated(self, client):
        with patch.object(client, "_get", return_value=MOCK_SEASON_STATS_RESPONSE):
            result = client.players.get_player_season_stats(2025, "REG", TEAM_ID)
        assert all(tid == TEAM_ID for tid in result["team_id"].to_list())
        assert all(tn == "Bruins" for tn in result["team_name"].to_list())

    def test_accepts_all_valid_season_types(self, client):
        for season_type in ("PRE", "REG", "PST"):
            with patch.object(client, "_get", return_value=MOCK_SEASON_STATS_RESPONSE):
                result = client.players.get_player_season_stats(2025, season_type, TEAM_ID)
            assert isinstance(result, pl.DataFrame)

    def test_season_type_is_case_insensitive(self, client):
        with patch.object(client, "_get", return_value=MOCK_SEASON_STATS_RESPONSE) as mock_get:
            client.players.get_player_season_stats(2025, "reg", TEAM_ID)
        # Should normalize to uppercase in the URL
        mock_get.assert_called_once_with(f"/seasons/2025/REG/teams/{TEAM_ID}/statistics.json")

    def test_raises_on_invalid_season_type(self, client):
        with pytest.raises(ValueError, match="Invalid season_type"):
            client.players.get_player_season_stats(2025, "INVALID", TEAM_ID)

    def test_raises_on_lowercase_invalid_season_type(self, client):
        with pytest.raises(ValueError, match="Invalid season_type"):
            client.players.get_player_season_stats(2025, "xyz", TEAM_ID)

    def test_empty_players_returns_empty_dataframe(self, client):
        empty = {"team": {"id": TEAM_ID, "name": "Bruins", "players": []}}
        with patch.object(client, "_get", return_value=empty):
            result = client.players.get_player_season_stats(2025, "REG", TEAM_ID)
        assert len(result) == 0