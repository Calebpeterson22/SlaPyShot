# tests/test_schedule.py - Tests for ScheduleEndpoint

import pytest
from unittest.mock import patch
import polars as pl

from slapyshot import NHLClient


# ---------------------------------------------------------------------------
# Shared mock API payloads
# ---------------------------------------------------------------------------

MOCK_SCHEDULE_RESPONSE = {
    "games": [
        {
            "id": "game-1",
            "status": "closed",
            "scheduled": "2026-03-23T19:00:00+00:00",
            "home": {"id": "team-1", "name": "Bruins", "alias": "BOS"},
            "away": {"id": "team-2", "name": "Sabres", "alias": "BUF"},
            "venue": {"id": "venue-1", "name": "TD Garden"},
        },
        {
            "id": "game-2",
            "status": "scheduled",
            "scheduled": "2026-03-23T22:00:00+00:00",
            "home": {"id": "team-3", "name": "Blackhawks", "alias": "CHI"},
            "away": {"id": "team-4", "name": "Blues", "alias": "STL"},
            "venue": {"id": "venue-2", "name": "United Center"},
        },
    ]
}

EXPECTED_COLUMNS = {
    "id", "status", "scheduled",
    "home_team_id", "home_team_name", "home_team_alias",
    "away_team_id", "away_team_name", "away_team_alias",
    "venue_id", "venue_name",
}


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def client():
    return NHLClient(api_key="test-api-key")


# ---------------------------------------------------------------------------
# get_daily_schedule tests
# ---------------------------------------------------------------------------

class TestGetDailySchedule:

    def test_returns_dataframe(self, client):
        with patch.object(client, "_get", return_value=MOCK_SCHEDULE_RESPONSE):
            result = client.schedule.get_daily_schedule(2026, 3, 23)
        assert isinstance(result, pl.DataFrame)

    def test_calls_correct_endpoint(self, client):
        with patch.object(client, "_get", return_value=MOCK_SCHEDULE_RESPONSE) as mock_get:
            client.schedule.get_daily_schedule(2026, 3, 23)
        mock_get.assert_called_once_with("/games/2026/03/23/schedule.json")

    def test_single_digit_month_and_day_are_zero_padded(self, client):
        with patch.object(client, "_get", return_value=MOCK_SCHEDULE_RESPONSE) as mock_get:
            client.schedule.get_daily_schedule(2026, 1, 5)
        mock_get.assert_called_once_with("/games/2026/01/05/schedule.json")

    def test_double_digit_month_and_day_not_padded(self, client):
        with patch.object(client, "_get", return_value=MOCK_SCHEDULE_RESPONSE) as mock_get:
            client.schedule.get_daily_schedule(2026, 11, 23)
        mock_get.assert_called_once_with("/games/2026/11/23/schedule.json")

    def test_has_expected_columns(self, client):
        with patch.object(client, "_get", return_value=MOCK_SCHEDULE_RESPONSE):
            result = client.schedule.get_daily_schedule(2026, 3, 23)
        assert EXPECTED_COLUMNS.issubset(set(result.columns))

    def test_returns_one_row_per_game(self, client):
        with patch.object(client, "_get", return_value=MOCK_SCHEDULE_RESPONSE):
            result = client.schedule.get_daily_schedule(2026, 3, 23)
        assert len(result) == 2

    def test_home_and_away_fields_correct(self, client):
        with patch.object(client, "_get", return_value=MOCK_SCHEDULE_RESPONSE):
            result = client.schedule.get_daily_schedule(2026, 3, 23)
        game = result.filter(pl.col("id") == "game-1")
        assert game["home_team_name"][0] == "Bruins"
        assert game["home_team_alias"][0] == "BOS"
        assert game["away_team_name"][0] == "Sabres"
        assert game["away_team_alias"][0] == "BUF"

    def test_venue_fields_correct(self, client):
        with patch.object(client, "_get", return_value=MOCK_SCHEDULE_RESPONSE):
            result = client.schedule.get_daily_schedule(2026, 3, 23)
        game = result.filter(pl.col("id") == "game-1")
        assert game["venue_name"][0] == "TD Garden"

    def test_status_field_correct(self, client):
        with patch.object(client, "_get", return_value=MOCK_SCHEDULE_RESPONSE):
            result = client.schedule.get_daily_schedule(2026, 3, 23)
        assert "closed" in result["status"].to_list()
        assert "scheduled" in result["status"].to_list()

    def test_empty_games_returns_empty_dataframe(self, client):
        with patch.object(client, "_get", return_value={"games": []}):
            result = client.schedule.get_daily_schedule(2026, 3, 23)
        assert len(result) == 0


# ---------------------------------------------------------------------------
# get_season_schedule tests
# ---------------------------------------------------------------------------

class TestGetSeasonSchedule:

    def test_returns_dataframe(self, client):
        with patch.object(client, "_get", return_value=MOCK_SCHEDULE_RESPONSE):
            result = client.schedule.get_season_schedule(2025, "REG")
        assert isinstance(result, pl.DataFrame)

    def test_calls_correct_endpoint(self, client):
        with patch.object(client, "_get", return_value=MOCK_SCHEDULE_RESPONSE) as mock_get:
            client.schedule.get_season_schedule(2025, "REG")
        mock_get.assert_called_once_with("/games/2025/REG/schedule.json")

    def test_has_expected_columns(self, client):
        with patch.object(client, "_get", return_value=MOCK_SCHEDULE_RESPONSE):
            result = client.schedule.get_season_schedule(2025, "REG")
        assert EXPECTED_COLUMNS.issubset(set(result.columns))

    def test_returns_one_row_per_game(self, client):
        with patch.object(client, "_get", return_value=MOCK_SCHEDULE_RESPONSE):
            result = client.schedule.get_season_schedule(2025, "REG")
        assert len(result) == 2

    def test_accepts_all_valid_season_types(self, client):
        for season_type in ("PRE", "REG", "PST"):
            with patch.object(client, "_get", return_value=MOCK_SCHEDULE_RESPONSE) as mock_get:
                result = client.schedule.get_season_schedule(2025, season_type)
            assert isinstance(result, pl.DataFrame)
            mock_get.assert_called_once_with(f"/games/2025/{season_type}/schedule.json")

    def test_season_type_is_case_insensitive(self, client):
        with patch.object(client, "_get", return_value=MOCK_SCHEDULE_RESPONSE) as mock_get:
            client.schedule.get_season_schedule(2025, "reg")
        mock_get.assert_called_once_with("/games/2025/REG/schedule.json")

    def test_raises_on_invalid_season_type(self, client):
        with pytest.raises(ValueError, match="Invalid season_type"):
            client.schedule.get_season_schedule(2025, "INVALID")

    def test_raises_on_lowercase_invalid_season_type(self, client):
        with pytest.raises(ValueError, match="Invalid season_type"):
            client.schedule.get_season_schedule(2025, "xyz")

    def test_home_and_away_fields_correct(self, client):
        with patch.object(client, "_get", return_value=MOCK_SCHEDULE_RESPONSE):
            result = client.schedule.get_season_schedule(2025, "REG")
        game = result.filter(pl.col("id") == "game-2")
        assert game["home_team_name"][0] == "Blackhawks"
        assert game["away_team_name"][0] == "Blues"

    def test_empty_games_returns_empty_dataframe(self, client):
        with patch.object(client, "_get", return_value={"games": []}):
            result = client.schedule.get_season_schedule(2025, "REG")
        assert len(result) == 0