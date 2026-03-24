# helpers.py - JSON flattening functions for SportRadar NHL API responses
# Each function takes raw JSON (dict) and returns a polars DataFrame.

import polars as pl


def flatten_teams(data: dict) -> pl.DataFrame:
    """Flatten the league hierarchy response into a teams DataFrame.

    Args:
        data: Raw JSON from /league/hierarchy.json

    Returns:
        pl.DataFrame: One row per team with columns:
            id, name, market, alias, founded, conference_id,
            conference_name, division_id, division_name
    """
    rows = []
    for conference in data.get("league", {}).get("conferences", []):
        for division in conference.get("divisions", []):
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
    return pl.DataFrame(rows)


def flatten_roster(data: dict) -> pl.DataFrame:
    """Flatten the team profile response into a roster DataFrame.

    Args:
        data: Raw JSON from /teams/{team_id}/profile.json

    Returns:
        pl.DataFrame: One row per player with columns:
            id, full_name, first_name, last_name, jersey_number,
            primary_position, birth_date, birth_city, birth_country,
            height, weight, shoots_catches, team_id, team_name
    """
    team = data.get("team", {})
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
            "shoots_catches": player.get("shoots_catches"),
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


def flatten_boxscore(data: dict) -> pl.DataFrame:
    """Flatten the game boxscore response into a periods DataFrame.

    Args:
        data: Raw JSON from /games/{game_id}/boxscore.json

    Returns:
        pl.DataFrame: One row per period with columns:
            game_id, period_number, period_type,
            home_team_id, home_team_name, home_points,
            away_team_id, away_team_name, away_points
    """
    game = data.get("game", {})
    game_id = game.get("id")
    home = game.get("home", {})
    away = game.get("away", {})
    rows = []
    for period in game.get("scoring", []):
        rows.append({
            "game_id": game_id,
            "period_number": period.get("number"),
            "period_type": period.get("type"),
            "home_team_id": home.get("id"),
            "home_team_name": home.get("name"),
            "home_points": period.get("home_scoring", {}).get("points"),
            "away_team_id": away.get("id"),
            "away_team_name": away.get("name"),
            "away_points": period.get("away_scoring", {}).get("points"),
        })
    return pl.DataFrame(rows)


def flatten_game_summary(data: dict) -> pl.DataFrame:
    """Flatten the game summary response into a player stats DataFrame.

    Args:
        data: Raw JSON from /games/{game_id}/summary.json

    Returns:
        pl.DataFrame: One row per player with columns:
            game_id, team_id, team_name, player_id, full_name,
            position, goals, assists, points, plus_minus,
            shots, penalty_minutes, time_on_ice
    """
    game = data.get("game", {})
    game_id = game.get("id")
    rows = []
    for team_key in ("home", "away"):
        team = game.get(team_key, {})
        team_id = team.get("id")
        team_name = team.get("name")
        for player in team.get("players", []):
            stats = player.get("statistics", {})
            rows.append({
                "game_id": game_id,
                "team_id": team_id,
                "team_name": team_name,
                "player_id": player.get("id"),
                "full_name": player.get("full_name"),
                "position": player.get("primary_position"),
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
    """Flatten the play-by-play response into an events DataFrame.

    Args:
        data: Raw JSON from /games/{game_id}/pbp.json

    Returns:
        pl.DataFrame: One row per event with columns:
            game_id, period_number, event_id, event_type,
            clock, description, player_id, player_name, team_id
    """
    game = data.get("game", {})
    game_id = game.get("id")
    rows = []
    for period in game.get("periods", []):
        period_number = period.get("number")
        for event in period.get("events", []):
            player = event.get("attribution", {})
            rows.append({
                "game_id": game_id,
                "period_number": period_number,
                "event_id": event.get("id"),
                "event_type": event.get("event_type"),
                "clock": event.get("clock"),
                "description": event.get("description"),
                "player_id": player.get("id"),
                "player_name": player.get("full_name"),
                "team_id": player.get("team_id"),
            })
    return pl.DataFrame(rows)


def flatten_player_profile(data: dict) -> pl.DataFrame:
    """Flatten the player profile response into a career stats DataFrame.

    Args:
        data: Raw JSON from /players/{player_id}/profile.json

    Returns:
        pl.DataFrame: One row per season with columns:
            player_id, full_name, primary_position, season_year,
            season_type, team_id, team_name, games_played,
            goals, assists, points, plus_minus, shots, penalty_minutes
    """
    player_id = data.get("id")
    full_name = data.get("full_name")
    position = data.get("primary_position")
    rows = []
    for season in data.get("seasons", []):
        season_year = season.get("year")
        season_type = season.get("type")
        for team in season.get("teams", []):
            totals = team.get("totals", {}).get("statistics", {})
            rows.append({
                "player_id": player_id,
                "full_name": full_name,
                "primary_position": position,
                "season_year": season_year,
                "season_type": season_type,
                "team_id": team.get("id"),
                "team_name": team.get("name"),
                "games_played": totals.get("games_played"),
                "goals": totals.get("goals"),
                "assists": totals.get("assists"),
                "points": totals.get("points"),
                "plus_minus": totals.get("plus_minus"),
                "shots": totals.get("shots"),
                "penalty_minutes": totals.get("penalty_minutes"),
            })
    return pl.DataFrame(rows)


def flatten_player_season_stats(data: dict) -> pl.DataFrame:
    """Flatten the team season stats response into a player stats DataFrame.

    Args:
        data: Raw JSON from /seasons/{year}/{type}/teams/{team_id}/statistics.json

    Returns:
        pl.DataFrame: One row per player with columns:
            team_id, team_name, player_id, full_name, primary_position,
            games_played, goals, assists, points, plus_minus,
            shots, penalty_minutes
    """
    team = data.get("team", {})
    team_id = team.get("id")
    team_name = team.get("name")
    rows = []
    for player in team.get("players", []):
        stats = player.get("statistics", {})
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
