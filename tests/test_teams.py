# tests/test_teams.py - Tests for TeamsEndpoint

import pytest
from unittest.mock import patch
import polars as pl

from slapyshot import NHLClient


TEAM_ID = "team-uuid-123"

# ---------------------------------------------------------------------------
# Shared mock API payloads
# ---------------------------------------------------------------------------

MOCK_HIERARCHY_RESPONSE = {
    "league": {
        "conferences": [
            {
                "id": "conf-1",
                "name": "Eastern",
                "divisions": [
                    {
                        "id": "div-1",
                        "name": "Atlantic",
                        "teams": [
                            {"id": "team-1", "name": "Bruins", "market": "Boston", "alias": "BOS", "founded": 1924},
                            {"id": "team-2", "name": "Sabres", "market": "Buffalo", "alias": "BUF", "founded": 1970},
                        ],
                    }
                ],
            },
            {
                "id": "conf-2",
                "name": "Western",
                "divisions": [
                    {
                        "id": "div-2",
                        "name": "Central",
                        "teams": [
                            {"id": "team-3", "name": "Blackhawks", "market": "Chicago", "alias": "CHI", "founded": 1926},
                        ],
                    }
                ],
            },
        ]
    }
}

MOCK_ROSTER_RESPONSE = {
    "team": {
        "id": TEAM_ID,
        "name": "Bruins",
        "players": [
            {
                "id": "player-1",
                "full_name": "Alice Smith",
                "first_name": "Alice",
                "last_name": "Smith",
                "jersey_number": "37",
                "primary_position": "C",
                "birth_date": "1995-04-12",
                "birth_city": "Toronto",
                "birth_country": "CAN",
                "height": 73,
                "weight": 195,
                "shoots_catches": "L",
            },
            {
                "id": "player-2",
                "full_name": "Bob Jones",
                "first_name": "Bob",
                "last_name": "Jones",
                "jersey_number": "30",
                "primary_position": "G",
                "birth_date": "1993-08-22",
                "birth_city": "Montreal",
                "birth_country": "CAN",
                "height": 75,
                "weight": 210,
                "shoots_catches": "R",
            },
        ],
    }
}

EXPECTED_ROSTER_COLUMNS = {
    "id", "full_name", "first_name", "last_name", "jersey_number",
    "primary_position", "birth_date", "birth_city", "birth_country",
    "height", "weight", "shoots_catches", "team_id", "team_name",
}


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def client():
    return NHLClient(api_key="test-api-key")


# ---------------------------------------------------------------------------
# get_all_teams tests
# ---------------------------------------------------------------------------

class TestGetAllTeams:

    def test_returns_dataframe(self, client):
        with patch.object(client, "_get", return_value=MOCK_HIERARCHY_RESPONSE):
            result = client.teams.get_all_teams()
        assert isinstance(result, pl.DataFrame)

    def test_calls_correct_endpoint(self, client):
        with patch.object(client, "_get", return_value=MOCK_HIERARCHY_RESPONSE) as mock_get:
            client.teams.get_all_teams()
        mock_get.assert_called_once_with("/league/hierarchy.json")

    def test_has_expected_columns(self, client):
        with patch.object(client, "_get", return_value=MOCK_HIERARCHY_RESPONSE):
            result = client.teams.get_all_teams()
        expected = {"id", "name", "market", "alias", "founded", "conference_id", "conference_name", "division_id", "division_name"}
        assert expected.issubset(set(result.columns))

    def test_returns_one_row_per_team(self, client):
        with patch.object(client, "_get", return_value=MOCK_HIERARCHY_RESPONSE):
            result = client.teams.get_all_teams()
        assert len(result) == 3

    def test_team_fields_correct(self, client):
        with patch.object(client, "_get", return_value=MOCK_HIERARCHY_RESPONSE):
            result = client.teams.get_all_teams()
        bruins = result.filter(pl.col("id") == "team-1")
        assert bruins["name"][0] == "Bruins"
        assert bruins["market"][0] == "Boston"
        assert bruins["alias"][0] == "BOS"
        assert bruins["founded"][0] == 1924

    def test_conference_name_propagates_to_teams(self, client):
        with patch.object(client, "_get", return_value=MOCK_HIERARCHY_RESPONSE):
            result = client.teams.get_all_teams()
        eastern = result.filter(pl.col("conference_name") == "Eastern")
        assert len(eastern) == 2

    def test_division_name_propagates_to_teams(self, client):
        with patch.object(client, "_get", return_value=MOCK_HIERARCHY_RESPONSE):
            result = client.teams.get_all_teams()
        atlantic = result.filter(pl.col("division_name") == "Atlantic")
        assert len(atlantic) == 2

    def test_empty_hierarchy_returns_empty_dataframe(self, client):
        with patch.object(client, "_get", return_value={"league": {"conferences": []}}):
            result = client.teams.get_all_teams()
        assert len(result) == 0


# ---------------------------------------------------------------------------
# get_team_profile tests
# ---------------------------------------------------------------------------

class TestGetTeamProfile:

    def test_returns_dataframe(self, client):
        with patch.object(client, "_get", return_value=MOCK_ROSTER_RESPONSE):
            result = client.teams.get_team_profile(TEAM_ID)
        assert isinstance(result, pl.DataFrame)

    def test_calls_correct_endpoint(self, client):
        with patch.object(client, "_get", return_value=MOCK_ROSTER_RESPONSE) as mock_get:
            client.teams.get_team_profile(TEAM_ID)
        mock_get.assert_called_once_with(f"/teams/{TEAM_ID}/profile.json")

    def test_has_expected_columns(self, client):
        with patch.object(client, "_get", return_value=MOCK_ROSTER_RESPONSE):
            result = client.teams.get_team_profile(TEAM_ID)
        assert EXPECTED_ROSTER_COLUMNS.issubset(set(result.columns))

    def test_returns_one_row_per_player(self, client):
        with patch.object(client, "_get", return_value=MOCK_ROSTER_RESPONSE):
            result = client.teams.get_team_profile(TEAM_ID)
        assert len(result) == 2

    def test_team_id_and_name_propagate_to_all_players(self, client):
        with patch.object(client, "_get", return_value=MOCK_ROSTER_RESPONSE):
            result = client.teams.get_team_profile(TEAM_ID)
        assert all(tid == TEAM_ID for tid in result["team_id"].to_list())
        assert all(tn == "Bruins" for tn in result["team_name"].to_list())

    def test_player_fields_correct(self, client):
        with patch.object(client, "_get", return_value=MOCK_ROSTER_RESPONSE):
            result = client.teams.get_team_profile(TEAM_ID)
        alice = result.filter(pl.col("id") == "player-1")
        assert alice["full_name"][0] == "Alice Smith"
        assert alice["primary_position"][0] == "C"
        assert alice["shoots_catches"][0] == "L"

    def test_empty_roster_returns_empty_dataframe(self, client):
        empty = {"team": {"id": TEAM_ID, "name": "Bruins", "players": []}}
        with patch.object(client, "_get", return_value=empty):
            result = client.teams.get_team_profile(TEAM_ID)
        assert len(result) == 0


# ---------------------------------------------------------------------------
# get_team_roster tests
# ---------------------------------------------------------------------------

class TestGetTeamRoster:

    def test_returns_dataframe(self, client):
        with patch.object(client, "_get", return_value=MOCK_ROSTER_RESPONSE):
            result = client.teams.get_team_roster(TEAM_ID)
        assert isinstance(result, pl.DataFrame)

    def test_calls_correct_endpoint(self, client):
        with patch.object(client, "_get", return_value=MOCK_ROSTER_RESPONSE) as mock_get:
            client.teams.get_team_roster(TEAM_ID)
        mock_get.assert_called_once_with(f"/teams/{TEAM_ID}/profile.json")

    def test_has_expected_columns(self, client):
        with patch.object(client, "_get", return_value=MOCK_ROSTER_RESPONSE):
            result = client.teams.get_team_roster(TEAM_ID)
        assert EXPECTED_ROSTER_COLUMNS.issubset(set(result.columns))

    def test_returns_one_row_per_player(self, client):
        with patch.object(client, "_get", return_value=MOCK_ROSTER_RESPONSE):
            result = client.teams.get_team_roster(TEAM_ID)
        assert len(result) == 2

    def test_team_id_and_name_propagate_to_all_players(self, client):
        with patch.object(client, "_get", return_value=MOCK_ROSTER_RESPONSE):
            result = client.teams.get_team_roster(TEAM_ID)
        assert all(tid == TEAM_ID for tid in result["team_id"].to_list())
        assert all(tn == "Bruins" for tn in result["team_name"].to_list())

    def test_player_fields_correct(self, client):
        with patch.object(client, "_get", return_value=MOCK_ROSTER_RESPONSE):
            result = client.teams.get_team_roster(TEAM_ID)
        bob = result.filter(pl.col("id") == "player-2")
        assert bob["full_name"][0] == "Bob Jones"
        assert bob["primary_position"][0] == "G"
        assert bob["shoots_catches"][0] == "R"

    def test_empty_roster_returns_empty_dataframe(self, client):
        empty = {"team": {"id": TEAM_ID, "name": "Bruins", "players": []}}
        with patch.object(client, "_get", return_value=empty):
            result = client.teams.get_team_roster(TEAM_ID)
        assert len(result) == 0

    def test_returns_same_result_as_get_team_profile(self, client):
        """get_team_roster and get_team_profile hit the same endpoint and should return identical data."""
        with patch.object(client, "_get", return_value=MOCK_ROSTER_RESPONSE):
            profile = client.teams.get_team_profile(TEAM_ID)
        with patch.object(client, "_get", return_value=MOCK_ROSTER_RESPONSE):
            roster = client.teams.get_team_roster(TEAM_ID)
        assert profile.equals(roster)