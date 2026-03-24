# endpoints/schedule.py - Game Schedules

import polars as pl
from ..helpers import flatten_daily_schedule, flatten_season_schedule

_VALID_SEASON_TYPES = ("PRE", "REG", "PST")


class ScheduleEndpoint:
    """Endpoints related to NHL game schedules.

    Access via the NHLClient:
        >>> client.schedule.get_daily_schedule(2026, 3, 23)
        >>> client.schedule.get_season_schedule(2025, "REG")
    """

    def __init__(self, client):
        self._client = client

    def get_daily_schedule(self, year: int, month: int, day: int) -> pl.DataFrame:
        """Get the schedule for a specific date.

        Returns all games taking place on the given day including
        venue, broadcast, and team info.

        Args:
            year: Four digit year (e.g. 2026)
            month: Month as an integer (e.g. 3)
            day: Day as an integer (e.g. 23)

        Returns:
            pl.DataFrame: One row per game with columns:
                id, status, scheduled, home_team_id, home_team_name,
                home_team_alias, away_team_id, away_team_name,
                away_team_alias, venue_id, venue_name

        Example:
            >>> schedule = client.schedule.get_daily_schedule(2026, 3, 23)
            >>> print(schedule.select(["home_team_name", "away_team_name", "status"]))
        """
        month_str = str(month).zfill(2)
        day_str = str(day).zfill(2)
        data = self._client._get(f"/games/{year}/{month_str}/{day_str}/schedule.json")
        return flatten_daily_schedule(data)

    def get_season_schedule(self, season_year: int, season_type: str) -> pl.DataFrame:
        """Get the full schedule for an entire season.

        Note: season_year is the *starting* year of the season.
        For example, the 2025-26 season uses season_year=2025.

        Args:
            season_year: The starting year of the season (e.g. 2025 for 2025-26)
            season_type: One of 'PRE' (preseason), 'REG' (regular season),
                         or 'PST' (postseason/playoffs)

        Returns:
            pl.DataFrame: One row per game with columns:
                id, status, scheduled, home_team_id, home_team_name,
                home_team_alias, away_team_id, away_team_name,
                away_team_alias, venue_id, venue_name

        Example:
            >>> schedule = client.schedule.get_season_schedule(2025, "REG")
            >>> print(f"Total games: {len(schedule)}")
            >>> print(schedule.filter(pl.col("home_team_name") == "Avalanche"))

        Raises:
            ValueError: If season_type is not one of PRE, REG, or PST.
        """
        season_type = season_type.upper()
        if season_type not in _VALID_SEASON_TYPES:
            raise ValueError(
                f"Invalid season_type '{season_type}'. "
                f"Must be one of: {_VALID_SEASON_TYPES}"
            )
        data = self._client._get(f"/games/{season_year}/{season_type}/schedule.json")
        return flatten_season_schedule(data)