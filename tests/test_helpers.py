# tests/test_helpers.py - Tests for JSON flattening helpers

import pytest
import polars as pl

from slapyshot.helpers import (
    flatten_teams,
    flatten_roster,
    flatten_daily_schedule,
    flatten_season_schedule,
    flatten_boxscore,
    flatten_game_summary,
    flatten_play_by_play,
    flatten_player_profile,
    flatten_player_season_stats,
)


# ---------------------------------------------------------------------------
# Shared mock payloads
# ---------------------------------------------------------------------------

MOCK_TEAMS_DATA = {
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

MOCK_ROSTER_DATA = {
    "team": {
        "id": "team-1",
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
                "jersey_number": "11",
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

MOCK_SCHEDULE_DATA = {
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

GAME_ID = "game-abc-123"

MOCK_BOXSCORE_DATA = {
    "game": {
        "id": GAME_ID,
        "home": {"id": "team-1", "name": "Bruins"},
        "away": {"id": "team-2", "name": "Sabres"},
        "scoring": [
            {"number": 1, "type": "period", "home_scoring": {"points": 2}, "away_scoring": {"points": 0}},
            {"number": 2, "type": "period", "home_scoring": {"points": 1}, "away_scoring": {"points": 1}},
            {"number": 3, "type": "period", "home_scoring": {"points": 0}, "away_scoring": {"points": 2}},
        ],
    }
}

MOCK_SUMMARY_DATA = {
    "game": {
        "id": GAME_ID,
        "home": {
            "id": "team-1",
            "name": "Bruins",
            "players": [
                {
                    "id": "player-1",
                    "full_name": "Alice Smith",
                    "primary_position": "C",
                    "statistics": {
                        "goals": 2,
                        "assists": 1,
                        "points": 3,
                        "plus_minus": 2,
                        "shots": 5,
                        "penalty_minutes": 0,
                        "time_on_ice": "20:14",
                    },
                }
            ],
        },
        "away": {
            "id": "team-2",
            "name": "Sabres",
            "players": [
                {
                    "id": "player-2",
                    "full_name": "Bob Jones",
                    "primary_position": "G",
                    "statistics": {
                        "goals": 0,
                        "assists": 0,
                        "points": 0,
                        "plus_minus": -2,
                        "shots": 0,
                        "penalty_minutes": 4,
                        "time_on_ice": "60:00",
                    },
                }
            ],
        },
    }
}

MOCK_PBP_DATA = {
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
                        "attribution": {"id": "player-1", "full_name": "Alice Smith", "team_id": "team-1"},
                    },
                    {
                        "id": "evt-2",
                        "event_type": "goal",
                        "clock": "14:22",
                        "description": "Goal by Alice Smith",
                        "attribution": {"id": "player-1", "full_name": "Alice Smith", "team_id": "team-1"},
                    },
                ],
            },
            {
                "number": 2,
                "events": [
                    {
                        "id": "evt-3",
                        "event_type": "shot",
                        "clock": "09:45",
                        "description": "Shot by Bob Jones",
                        "attribution": {"id": "player-2", "full_name": "Bob Jones", "team_id": "team-2"},
                    },
                ],
            },
        ],
    }
}

MOCK_PLAYER_PROFILE_DATA = {
    "id": "player-1",
    "full_name": "Alice Smith",
    "primary_position": "C",
    "seasons": [
        {
            "year": 2025,
            "type": "REG",
            "teams": [
                {
                    "id": "team-1",
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
                    "id": "team-1",
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

MOCK_PLAYER_SEASON_STATS_DATA = {
    "team": {
        "id": "team-1",
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
# flatten_teams
# ---------------------------------------------------------------------------

class TestFlattenTeams:

    def test_returns_dataframe(self):
        assert isinstance(flatten_teams(MOCK_TEAMS_DATA), pl.DataFrame)

    def test_returns_one_row_per_team(self):
        result = flatten_teams(MOCK_TEAMS_DATA)
        assert len(result) == 3

    def test_has_expected_columns(self):
        result = flatten_teams(MOCK_TEAMS_DATA)
        expected = {"id", "name", "market", "alias", "founded", "conference_id", "conference_name", "division_id", "division_name"}
        assert expected.issubset(set(result.columns))

    def test_conference_name_propagates_to_all_teams(self):
        result = flatten_teams(MOCK_TEAMS_DATA)
        eastern_teams = result.filter(pl.col("conference_name") == "Eastern")
        assert len(eastern_teams) == 2

    def test_division_name_propagates_to_teams(self):
        result = flatten_teams(MOCK_TEAMS_DATA)
        atlantic_teams = result.filter(pl.col("division_name") == "Atlantic")
        assert len(atlantic_teams) == 2

    def test_team_fields_correct(self):
        result = flatten_teams(MOCK_TEAMS_DATA)
        bruins = result.filter(pl.col("id") == "team-1")
        assert bruins["name"][0] == "Bruins"
        assert bruins["market"][0] == "Boston"
        assert bruins["alias"][0] == "BOS"
        assert bruins["founded"][0] == 1924

    def test_empty_conferences_returns_empty_dataframe(self):
        result = flatten_teams({"league": {"conferences": []}})
        assert len(result) == 0

    def test_missing_league_key_returns_empty_dataframe(self):
        result = flatten_teams({})
        assert len(result) == 0


# ---------------------------------------------------------------------------
# flatten_roster
# ---------------------------------------------------------------------------

class TestFlattenRoster:

    def test_returns_dataframe(self):
        assert isinstance(flatten_roster(MOCK_ROSTER_DATA), pl.DataFrame)

    def test_returns_one_row_per_player(self):
        result = flatten_roster(MOCK_ROSTER_DATA)
        assert len(result) == 2

    def test_has_expected_columns(self):
        result = flatten_roster(MOCK_ROSTER_DATA)
        expected = {
            "id", "full_name", "first_name", "last_name", "jersey_number",
            "primary_position", "birth_date", "birth_city", "birth_country",
            "height", "weight", "shoots_catches", "team_id", "team_name",
        }
        assert expected.issubset(set(result.columns))

    def test_team_id_and_name_propagate_to_all_players(self):
        result = flatten_roster(MOCK_ROSTER_DATA)
        assert all(tid == "team-1" for tid in result["team_id"].to_list())
        assert all(tn == "Bruins" for tn in result["team_name"].to_list())

    def test_player_fields_correct(self):
        result = flatten_roster(MOCK_ROSTER_DATA)
        alice = result.filter(pl.col("id") == "player-1")
        assert alice["full_name"][0] == "Alice Smith"
        assert alice["primary_position"][0] == "C"
        assert alice["shoots_catches"][0] == "L"

    def test_empty_players_returns_empty_dataframe(self):
        result = flatten_roster({"team": {"id": "t", "name": "T", "players": []}})
        assert len(result) == 0


# ---------------------------------------------------------------------------
# flatten_daily_schedule
# ---------------------------------------------------------------------------

class TestFlattenDailySchedule:

    def test_returns_dataframe(self):
        assert isinstance(flatten_daily_schedule(MOCK_SCHEDULE_DATA), pl.DataFrame)

    def test_returns_one_row_per_game(self):
        result = flatten_daily_schedule(MOCK_SCHEDULE_DATA)
        assert len(result) == 2

    def test_has_expected_columns(self):
        result = flatten_daily_schedule(MOCK_SCHEDULE_DATA)
        expected = {
            "id", "status", "scheduled",
            "home_team_id", "home_team_name", "home_team_alias",
            "away_team_id", "away_team_name", "away_team_alias",
            "venue_id", "venue_name",
        }
        assert expected.issubset(set(result.columns))

    def test_home_and_away_fields_correct(self):
        result = flatten_daily_schedule(MOCK_SCHEDULE_DATA)
        game = result.filter(pl.col("id") == "game-1")
        assert game["home_team_name"][0] == "Bruins"
        assert game["away_team_name"][0] == "Sabres"
        assert game["home_team_alias"][0] == "BOS"
        assert game["away_team_alias"][0] == "BUF"

    def test_venue_fields_correct(self):
        result = flatten_daily_schedule(MOCK_SCHEDULE_DATA)
        game = result.filter(pl.col("id") == "game-1")
        assert game["venue_name"][0] == "TD Garden"

    def test_empty_games_returns_empty_dataframe(self):
        result = flatten_daily_schedule({"games": []})
        assert len(result) == 0


# ---------------------------------------------------------------------------
# flatten_season_schedule
# ---------------------------------------------------------------------------

class TestFlattenSeasonSchedule:

    def test_returns_same_shape_as_daily_schedule(self):
        daily = flatten_daily_schedule(MOCK_SCHEDULE_DATA)
        season = flatten_season_schedule(MOCK_SCHEDULE_DATA)
        assert daily.shape == season.shape
        assert daily.columns == season.columns


# ---------------------------------------------------------------------------
# flatten_boxscore
# ---------------------------------------------------------------------------

class TestFlattenBoxscore:

    def test_returns_dataframe(self):
        assert isinstance(flatten_boxscore(MOCK_BOXSCORE_DATA), pl.DataFrame)

    def test_returns_one_row_per_period(self):
        result = flatten_boxscore(MOCK_BOXSCORE_DATA)
        assert len(result) == 3

    def test_has_expected_columns(self):
        result = flatten_boxscore(MOCK_BOXSCORE_DATA)
        expected = {
            "game_id", "period_number", "period_type",
            "home_team_id", "home_team_name", "home_points",
            "away_team_id", "away_team_name", "away_points",
        }
        assert expected.issubset(set(result.columns))

    def test_game_id_populated(self):
        result = flatten_boxscore(MOCK_BOXSCORE_DATA)
        assert all(gid == GAME_ID for gid in result["game_id"].to_list())

    def test_period_numbers_correct(self):
        result = flatten_boxscore(MOCK_BOXSCORE_DATA)
        assert result["period_number"].to_list() == [1, 2, 3]

    def test_score_values_correct(self):
        result = flatten_boxscore(MOCK_BOXSCORE_DATA)
        p1 = result.filter(pl.col("period_number") == 1)
        assert p1["home_points"][0] == 2
        assert p1["away_points"][0] == 0

    def test_home_and_away_team_names_correct(self):
        result = flatten_boxscore(MOCK_BOXSCORE_DATA)
        assert result["home_team_name"][0] == "Bruins"
        assert result["away_team_name"][0] == "Sabres"

    def test_empty_scoring_returns_empty_dataframe(self):
        empty = {"game": {"id": GAME_ID, "home": {"id": "h", "name": "H"}, "away": {"id": "a", "name": "A"}, "scoring": []}}
        result = flatten_boxscore(empty)
        assert len(result) == 0


# ---------------------------------------------------------------------------
# flatten_game_summary
# ---------------------------------------------------------------------------

class TestFlattenGameSummary:

    def test_returns_dataframe(self):
        assert isinstance(flatten_game_summary(MOCK_SUMMARY_DATA), pl.DataFrame)

    def test_returns_one_row_per_player(self):
        result = flatten_game_summary(MOCK_SUMMARY_DATA)
        assert len(result) == 2

    def test_has_expected_columns(self):
        result = flatten_game_summary(MOCK_SUMMARY_DATA)
        expected = {
            "game_id", "team_id", "team_name", "player_id", "full_name",
            "position", "goals", "assists", "points", "plus_minus",
            "shots", "penalty_minutes", "time_on_ice",
        }
        assert expected.issubset(set(result.columns))

    def test_game_id_populated(self):
        result = flatten_game_summary(MOCK_SUMMARY_DATA)
        assert all(gid == GAME_ID for gid in result["game_id"].to_list())

    def test_includes_both_home_and_away_players(self):
        result = flatten_game_summary(MOCK_SUMMARY_DATA)
        team_names = result["team_name"].to_list()
        assert "Bruins" in team_names
        assert "Sabres" in team_names

    def test_stat_values_correct(self):
        result = flatten_game_summary(MOCK_SUMMARY_DATA)
        alice = result.filter(pl.col("player_id") == "player-1")
        assert alice["goals"][0] == 2
        assert alice["assists"][0] == 1
        assert alice["points"][0] == 3
        assert alice["plus_minus"][0] == 2
        assert alice["time_on_ice"][0] == "20:14"

    def test_home_team_id_correct(self):
        result = flatten_game_summary(MOCK_SUMMARY_DATA)
        alice = result.filter(pl.col("player_id") == "player-1")
        assert alice["team_id"][0] == "team-1"

    def test_away_team_id_correct(self):
        result = flatten_game_summary(MOCK_SUMMARY_DATA)
        bob = result.filter(pl.col("player_id") == "player-2")
        assert bob["team_id"][0] == "team-2"

    def test_empty_players_returns_empty_dataframe(self):
        empty = {"game": {"id": GAME_ID, "home": {"id": "h", "name": "H", "players": []}, "away": {"id": "a", "name": "A", "players": []}}}
        result = flatten_game_summary(empty)
        assert len(result) == 0


# ---------------------------------------------------------------------------
# flatten_play_by_play
# ---------------------------------------------------------------------------

class TestFlattenPlayByPlay:

    def test_returns_dataframe(self):
        assert isinstance(flatten_play_by_play(MOCK_PBP_DATA), pl.DataFrame)

    def test_returns_one_row_per_event(self):
        result = flatten_play_by_play(MOCK_PBP_DATA)
        assert len(result) == 3

    def test_has_expected_columns(self):
        result = flatten_play_by_play(MOCK_PBP_DATA)
        expected = {
            "game_id", "period_number", "event_id", "event_type",
            "clock", "description", "player_id", "player_name", "team_id",
        }
        assert expected.issubset(set(result.columns))

    def test_game_id_populated(self):
        result = flatten_play_by_play(MOCK_PBP_DATA)
        assert all(gid == GAME_ID for gid in result["game_id"].to_list())

    def test_period_numbers_assigned_correctly(self):
        result = flatten_play_by_play(MOCK_PBP_DATA)
        assert result["period_number"].to_list() == [1, 1, 2]

    def test_event_types_correct(self):
        result = flatten_play_by_play(MOCK_PBP_DATA)
        assert result["event_type"].to_list() == ["faceoff", "goal", "shot"]

    def test_can_filter_by_event_type(self):
        result = flatten_play_by_play(MOCK_PBP_DATA)
        goals = result.filter(pl.col("event_type") == "goal")
        assert len(goals) == 1
        assert goals["player_name"][0] == "Alice Smith"
        assert goals["team_id"][0] == "team-1"

    def test_attribution_fields_correct(self):
        result = flatten_play_by_play(MOCK_PBP_DATA)
        evt = result.filter(pl.col("event_id") == "evt-3")
        assert evt["player_name"][0] == "Bob Jones"
        assert evt["team_id"][0] == "team-2"

    def test_clock_values_preserved(self):
        result = flatten_play_by_play(MOCK_PBP_DATA)
        assert result["clock"][0] == "20:00"

    def test_empty_periods_returns_empty_dataframe(self):
        result = flatten_play_by_play({"game": {"id": GAME_ID, "periods": []}})
        assert len(result) == 0

    def test_period_with_no_events_produces_no_rows(self):
        data = {"game": {"id": GAME_ID, "periods": [{"number": 1, "events": []}]}}
        result = flatten_play_by_play(data)
        assert len(result) == 0


# ---------------------------------------------------------------------------
# flatten_player_profile
# ---------------------------------------------------------------------------

class TestFlattenPlayerProfile:

    def test_returns_dataframe(self):
        assert isinstance(flatten_player_profile(MOCK_PLAYER_PROFILE_DATA), pl.DataFrame)

    def test_returns_one_row_per_season(self):
        result = flatten_player_profile(MOCK_PLAYER_PROFILE_DATA)
        assert len(result) == 2

    def test_has_expected_columns(self):
        result = flatten_player_profile(MOCK_PLAYER_PROFILE_DATA)
        expected = {
            "player_id", "full_name", "primary_position", "season_year",
            "season_type", "team_id", "team_name", "games_played",
            "goals", "assists", "points", "plus_minus", "shots", "penalty_minutes",
        }
        assert expected.issubset(set(result.columns))

    def test_player_fields_propagate_to_all_rows(self):
        result = flatten_player_profile(MOCK_PLAYER_PROFILE_DATA)
        assert all(pid == "player-1" for pid in result["player_id"].to_list())
        assert all(fn == "Alice Smith" for fn in result["full_name"].to_list())
        assert all(pos == "C" for pos in result["primary_position"].to_list())

    def test_season_years_correct(self):
        result = flatten_player_profile(MOCK_PLAYER_PROFILE_DATA)
        assert set(result["season_year"].to_list()) == {2024, 2025}

    def test_stat_values_correct(self):
        result = flatten_player_profile(MOCK_PLAYER_PROFILE_DATA)
        season_2025 = result.filter(pl.col("season_year") == 2025)
        assert season_2025["goals"][0] == 30
        assert season_2025["points"][0] == 70
        assert season_2025["games_played"][0] == 72

    def test_empty_seasons_returns_empty_dataframe(self):
        data = {"id": "p1", "full_name": "Alice Smith", "primary_position": "C", "seasons": []}
        result = flatten_player_profile(data)
        assert len(result) == 0


# ---------------------------------------------------------------------------
# flatten_player_season_stats
# ---------------------------------------------------------------------------

class TestFlattenPlayerSeasonStats:

    def test_returns_dataframe(self):
        assert isinstance(flatten_player_season_stats(MOCK_PLAYER_SEASON_STATS_DATA), pl.DataFrame)

    def test_returns_one_row_per_player(self):
        result = flatten_player_season_stats(MOCK_PLAYER_SEASON_STATS_DATA)
        assert len(result) == 2

    def test_has_expected_columns(self):
        result = flatten_player_season_stats(MOCK_PLAYER_SEASON_STATS_DATA)
        expected = {
            "team_id", "team_name", "player_id", "full_name", "primary_position",
            "games_played", "goals", "assists", "points", "plus_minus",
            "shots", "penalty_minutes",
        }
        assert expected.issubset(set(result.columns))

    def test_team_fields_propagate_to_all_players(self):
        result = flatten_player_season_stats(MOCK_PLAYER_SEASON_STATS_DATA)
        assert all(tid == "team-1" for tid in result["team_id"].to_list())
        assert all(tn == "Bruins" for tn in result["team_name"].to_list())

    def test_stat_values_correct(self):
        result = flatten_player_season_stats(MOCK_PLAYER_SEASON_STATS_DATA)
        alice = result.filter(pl.col("player_id") == "player-1")
        assert alice["goals"][0] == 30
        assert alice["assists"][0] == 40
        assert alice["games_played"][0] == 72

    def test_empty_players_returns_empty_dataframe(self):
        data = {"team": {"id": "team-1", "name": "Bruins", "players": []}}
        result = flatten_player_season_stats(data)
        assert len(result) == 0