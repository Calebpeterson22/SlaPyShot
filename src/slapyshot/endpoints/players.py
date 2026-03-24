# endpoints/players.py - Player Stats & Profiles

import polars as pl
from ..helpers import flatten_player_profile, flatten_player_season_stats

_VALID_SEASON_TYPES = ("PRE", "REG", "PST")


class PlayersEndpoint:
    """Endpoints related to NHL player stats and profiles.

    Player IDs are found via the team roster. The recommended workflow is:
        1. Get team ID:   client.teams.get_all_teams()
        2. Get player ID: client.teams.get_team_roster(team_id)
        3. Get player:    client.players.get_player_profile(player_id)

    Example:
        >>> teams = client.teams.get_all_teams()
        >>> team_id = teams["id"][0]
        >>> roster = client.teams.get_team_roster(team_id)
        >>> player_id = roster["id"][0]
        >>> client.players.get_player_profile(player_id)
    """

    def __init__(self, client):
        self._client = client

    def get_player_profile(self, player_id: str) -> pl.DataFrame:
        """Get full profile and career stats for a specific player.

        Returns one row per season with biographical info and stats.
        Season entries are sorted with the most recent team first, so
        you can reliably infer the player's current team from row 0.

        Note: Player IDs never change once assigned, so they are safe
        to store and reuse across sessions.

        Args:
            player_id: The SportRadar UUID for the player.
                       Find player IDs via client.teams.get_team_roster().

        Returns:
            pl.DataFrame: One row per season with columns:
                player_id, full_name, primary_position, season_year,
                season_type, team_id, team_name, games_played,
                goals, assists, points, plus_minus, shots, penalty_minutes

        Example:
            >>> profile = client.players.get_player_profile(
            ...     "433de553-0f24-11e2-8525-18a905767e44"  # Sidney Crosby
            ... )
            >>> print(profile.filter(pl.col("season_type") == "REG"))
            >>> print(profile.sort("season_year", descending=True).head(1))
        """
        data = self._client._get(f"/players/{player_id}/profile.json")
        return flatten_player_profile(data)

    def get_player_season_stats(self, season_year: int, season_type: str, team_id: str) -> pl.DataFrame:
        """Get full season statistics for all players on a specific team.

        Returns one row per player. Use this for leaderboards or comparing
        players across a team.

        Note: season_year is the *starting* year of the season.
        For example, the 2025-26 season uses season_year=2025.

        Args:
            season_year: The starting year of the season (e.g. 2025 for 2025-26)
            season_type: One of 'REG' (regular season) or 'PST' (postseason).
                         Note: 'PRE' (preseason) is not supported for stats.
            team_id: The SportRadar UUID for the team.
                     Find team IDs via client.teams.get_all_teams().

        Returns:
            pl.DataFrame: One row per player with columns:
                team_id, team_name, player_id, full_name, primary_position,
                games_played, goals, assists, points, plus_minus,
                shots, penalty_minutes

        Example:
            >>> stats = client.players.get_player_season_stats(
            ...     season_year=2025,
            ...     season_type="REG",
            ...     team_id="4415ce44-0f24-11e2-8525-18a905767e44"  # Colorado Avalanche
            ... )
            >>> print(stats.sort("points", descending=True))
            >>> print(stats.filter(pl.col("goals") >= 20))

        Raises:
            ValueError: If season_type is not one of PRE, REG, or PST.
        """
        season_type = season_type.upper()
        if season_type not in _VALID_SEASON_TYPES:
            raise ValueError(
                f"Invalid season_type '{season_type}'. "
                f"Must be one of: {_VALID_SEASON_TYPES}"
            )
        data = self._client._get(
            f"/seasons/{season_year}/{season_type}/teams/{team_id}/statistics.json"
        )
        return flatten_player_season_stats(data)