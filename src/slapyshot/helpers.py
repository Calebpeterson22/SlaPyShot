# helpers.py - JSON flattening functions for SportRadar NHL API responses
# Each function takes raw JSON (dict) and returns a polars DataFrame.

import polars as pl


def flatten_teams(data: dict) -> pl.DataFrame:
    """Flatten the league hierarchy response into a teams DataFrame."""
    rows = []

    # Conferences are at the top level
    for conference in data.get("conferences", []):
        # Some conferences may have divisions
        divisions = conference.get("divisions", [])
        if divisions:
            for division in divisions:
                for team in division.get("teams", []):
                    rows.append({
                        "id": team.get("id"),
                        "name": team.get("name"),
                        "market": team.get("market"),
                        "alias": team.get("alias"),
                        "founded": team.get("founded"),
                        "conference_id": conference.get("id"),
                        "conference_name": conference.get("name"),
                        "division_id": division.get("id"),
                        "division_name": division.get("name"),
                    })
        else:
            # No divisions, teams directly under conference
            for team in conference.get("teams", []):
                rows.append({
                    "id": team.get("id"),
                    "name": team.get("name"),
                    "market": team.get("market"),
                    "alias": team.get("alias"),
                    "founded": team.get("founded"),
                    "conference_id": conference.get("id"),
                    "conference_name": conference.get("name"),
                    "division_id": None,
                    "division_name": None,
                })

    return pl.DataFrame(rows)


def flatten_roster(data: dict) -> pl.DataFrame:
    """Flatten team roster / profile response into a DataFrame."""
    # Some responses wrap under "team", some are top-level
    team = data.get("team", data)  

    team_id = team.get("id")
    team_name = team.get("name")

    rows = []

    for player in team.get("players", []):
        rows.append({
            "id": player.get("id"),
            "full_name": player.get("full_name"),
            "first_name": player.get("first_name"),
            "last_name": player.get("last_name"),
            "jersey_number": player.get("jersey_number"),
            "primary_position": player.get("primary_position"),
            "birth_date": player.get("birth_date"),
            "birth_city": player.get("birth_city"),
            "birth_country": player.get("birth_country"),
            "height": player.get("height"),
            "weight": player.get("weight"),
            "handedness": player.get("handedness"),
            "team_id": team_id,
            "team_name": team_name,
        })

    return pl.DataFrame(rows)


def flatten_daily_schedule(data: dict) -> pl.DataFrame:
    """Flatten the daily schedule response into a games DataFrame.

    Args:
        data: Raw JSON from /games/{year}/{month}/{day}/schedule.json

    Returns:
        pl.DataFrame: One row per game with columns:
            id, status, scheduled, home_team_id, home_team_name,
            home_team_alias, away_team_id, away_team_name, away_team_alias,
            venue_id, venue_name
    """
    rows = []
    for game in data.get("games", []):
        home = game.get("home", {})
        away = game.get("away", {})
        venue = game.get("venue", {})
        rows.append({
            "id": game.get("id"),
            "status": game.get("status"),
            "scheduled": game.get("scheduled"),
            "home_team_id": home.get("id"),
            "home_team_name": home.get("name"),
            "home_team_alias": home.get("alias"),
            "away_team_id": away.get("id"),
            "away_team_name": away.get("name"),
            "away_team_alias": away.get("alias"),
            "venue_id": venue.get("id"),
            "venue_name": venue.get("name"),
        })
    return pl.DataFrame(rows)


def flatten_season_schedule(data: dict) -> pl.DataFrame:
    """Flatten the season schedule response into a games DataFrame.

    Args:
        data: Raw JSON from /games/{season_year}/{season_type}/schedule.json

    Returns:
        pl.DataFrame: One row per game with columns:
            id, status, scheduled, home_team_id, home_team_name,
            home_team_alias, away_team_id, away_team_name, away_team_alias,
            venue_id, venue_name
    """
    # Season schedule has the same game shape as daily schedule
    return flatten_daily_schedule(data)


import polars as pl

import polars as pl

def flatten_boxscore(data: dict) -> pl.DataFrame:
    """
    Flatten a SportRadar boxscore JSON into one row per period with home and away scores.
    """
    game = data.get("game", {})
    game_id = game.get("id")
    start_time = game.get("start_time")
    end_time = game.get("end_time")
    total_game_duration = game.get("total_game_duration")

    home_team = game.get("home_team", {})
    away_team = game.get("away_team", {})

    rows = []

    # Collect periods info
    # Assuming each team has the same periods list
    periods = home_team.get("periods", [])

    for period in periods:
        period_number = period.get("number")
        period_type = period.get("type")
        sequence = period.get("sequence")

        # Home points
        home_period_data = next(
            (p for p in home_team.get("periods", []) if p.get("number") == period_number),
            {}
        )
        away_period_data = next(
            (p for p in away_team.get("periods", []) if p.get("number") == period_number),
            {}
        )

        rows.append({
            "game_id": game_id,
            "start_time": start_time,
            "end_time": end_time,
            "total_game_duration": total_game_duration,
            "period_number": period_number,
            "period_type": period_type,
            "sequence": sequence,
            "home_team_id": home_team.get("id"),
            "home_team_name": home_team.get("name"),
            "home_points": home_period_data.get("points"),
            "away_team_id": away_team.get("id"),
            "away_team_name": away_team.get("name"),
            "away_points": away_period_data.get("points"),
        })

    return pl.DataFrame(rows)


def flatten_game_summary(data: dict) -> pl.DataFrame:
    game = data.get("game", {})
    game_id = game.get("id")
    rows = []

    for team in game.get("teams", []):
        team_id = team.get("id")
        team_name = team.get("name")
        for player in team.get("players", []):
            stats = player.get("statistics") or {}
            rows.append({
                "game_id": game_id,
                "team_id": team_id,
                "team_name": team_name,
                "player_id": player.get("id"),
                "full_name": player.get("full_name"),
                "position": player.get("primary_position"),
                "games_played": stats.get("games_played"),
                "goals": stats.get("goals"),
                "assists": stats.get("assists"),
                "points": stats.get("points"),
                "plus_minus": stats.get("plus_minus"),
                "shots": stats.get("shots"),
                "penalty_minutes": stats.get("penalty_minutes"),
                "time_on_ice": stats.get("time_on_ice"),
            })

    return pl.DataFrame(rows)


def flatten_play_by_play(data: dict) -> pl.DataFrame:
    game = data.get("game", {})
    game_id = game.get("id")
    rows = []

    for period in game.get("periods", []):
        period_number = period.get("sequence") or period.get("number")
        for event in period.get("events", []):
            attribution = event.get("attribution") or {}
            rows.append({
                "game_id": game_id,
                "period_number": period_number,
                "event_id": event.get("id"),
                "event_type": event.get("event_type"),
                "clock": event.get("clock"),
                "description": event.get("description"),
                "player_id": attribution.get("id"),
                "player_name": attribution.get("full_name"),
                "team_id": attribution.get("team_id"),
            })

    return pl.DataFrame(rows)

import polars as pl

def flatten_player_profile(data: dict) -> pl.DataFrame:
    """Flatten a player profile into a career stats DataFrame."""
    player_id = data.get("id")
    full_name = data.get("full_name")
    position = data.get("primary_position")
    rows = []

    for season in data.get("seasons", []):
        season_year = season.get("year")
        season_type = season.get("type")
        for team in season.get("teams", []):
            # The stats we want are under statistics -> total
            stats = team.get("statistics", {}).get("total", {})

            if not stats:
                print(f"⚠️ No stats for {full_name} {season_year} {season_type} {team.get('name')}")

            rows.append({
                "player_id": player_id,
                "full_name": full_name,
                "primary_position": position,
                "season_year": season_year,
                "season_type": season_type,
                "team_id": team.get("id"),
                "team_name": team.get("name"),
                "games_played": stats.get("games_played"),
                "goals": stats.get("goals"),
                "assists": stats.get("assists"),
                "points": stats.get("points"),
                "plus_minus": stats.get("plus_minus"),
                "shots": stats.get("shots"),
                "penalty_minutes": stats.get("penalty_minutes"),
            })

    return pl.DataFrame(rows)


def flatten_player_season_stats(data: dict) -> pl.DataFrame:
    """Flatten team season stats into a player stats DataFrame."""
    team = data.get("team", {})
    team_id = team.get("id")
    team_name = team.get("name")
    rows = []

    for player in team.get("players", []):
        # stats are usually under statistics -> total
        stats = player.get("statistics", {}).get("total", {})

        rows.append({
            "team_id": team_id,
            "team_name": team_name,
            "player_id": player.get("id"),
            "full_name": player.get("full_name"),
            "primary_position": player.get("primary_position"),
            "games_played": stats.get("games_played"),
            "goals": stats.get("goals"),
            "assists": stats.get("assists"),
            "points": stats.get("points"),
            "plus_minus": stats.get("plus_minus"),
            "shots": stats.get("shots"),
            "penalty_minutes": stats.get("penalty_minutes"),
        })

    return pl.DataFrame(rows)