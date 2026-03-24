# endpoints/games.py - Live Game Data

import polars as pl
from ..helpers import flatten_game_summary, flatten_boxscore, flatten_play_by_play


class GamesEndpoint:
    """Endpoints related to NHL live and historical game data.

    All endpoints require a game_id. Get game IDs from the schedule endpoints:
        >>> schedule = client.schedule.get_daily_schedule(2026, 3, 23)
        >>> game_id = schedule["id"][0]

    Then use it here:
        >>> client.games.get_game_summary(game_id)
        >>> client.games.get_game_boxscore(game_id)
        >>> client.games.get_game_play_by_play(game_id)
    """

    def __init__(self, client):
        self._client = client

    def get_game_summary(self, game_id: str) -> pl.DataFrame:
        """Get a rich summary for a specific game including detailed stats.

        Returns one row per player with their individual game statistics.
        Use this when you want richer data beyond just the score.

        Args:
            game_id: The SportRadar UUID for the game.
                     Get this from client.schedule.get_daily_schedule()
                     or client.schedule.get_season_schedule().

        Returns:
            pl.DataFrame: One row per player with columns:
                game_id, team_id, team_name, player_id, full_name,
                position, goals, assists, points, plus_minus,
                shots, penalty_minutes, time_on_ice

        Example:
            >>> schedule = client.schedule.get_daily_schedule(2026, 3, 23)
            >>> game_id = schedule["id"][0]
            >>> summary = client.games.get_game_summary(game_id)
            >>> print(summary.sort("points", descending=True))
        """
        data = self._client._get(f"/games/{game_id}/summary.json")
        return flatten_game_summary(data)

    def get_game_boxscore(self, game_id: str) -> pl.DataFrame:
        """Get the boxscore for a specific game.

        Returns one row per period with home and away scores.
        Lighter than get_game_summary() — use this for scoreboards
        and high-level score tracking.

        Args:
            game_id: The SportRadar UUID for the game.
                     Get this from client.schedule.get_daily_schedule()
                     or client.schedule.get_season_schedule().

        Returns:
            pl.DataFrame: One row per period with columns:
                game_id, period_number, period_type,
                home_team_id, home_team_name, home_points,
                away_team_id, away_team_name, away_points

        Example:
            >>> boxscore = client.games.get_game_boxscore(game_id)
            >>> print(boxscore.select(["period_number", "home_points", "away_points"]))
        """
        data = self._client._get(f"/games/{game_id}/boxscore.json")
        return flatten_boxscore(data)

    def get_game_play_by_play(self, game_id: str) -> pl.DataFrame:
        """Get play-by-play data for a specific game.

        Returns one row per event with detailed information on every
        possession, faceoff, shot, and goal in the game.

        Note: This is the heaviest endpoint — use sparingly on the free
        tier as it counts as one API call but returns a large payload.

        Args:
            game_id: The SportRadar UUID for the game.
                     Get this from client.schedule.get_daily_schedule()
                     or client.schedule.get_season_schedule().

        Returns:
            pl.DataFrame: One row per event with columns:
                game_id, period_number, event_id, event_type,
                clock, description, player_id, player_name, team_id

        Example:
            >>> pbp = client.games.get_game_play_by_play(game_id)
            >>> print(pbp.filter(pl.col("event_type") == "goal"))
        """
        data = self._client._get(f"/games/{game_id}/pbp.json")
        return flatten_play_by_play(data)