# endpoints/teams.py - Teams & Rosters

import polars as pl
from ..helpers import flatten_teams, flatten_roster


class TeamsEndpoint:
    """Endpoints related to NHL teams and rosters.

    Access via the NHLClient:
        >>> client.teams.get_all_teams()
        >>> client.teams.get_team_profile(team_id="4416091c-0f24-11e2-8525-18a905767e44")
        >>> client.teams.get_team_roster(team_id="4416091c-0f24-11e2-8525-18a905767e44")
    """

    def __init__(self, client):
        self._client = client

    def get_all_teams(self) -> pl.DataFrame:
        """Get a list of all NHL teams.

        Returns:
            pl.DataFrame: One row per team with columns:
                id, name, market, alias, founded, conference_id,
                conference_name, division_id, division_name

        Example:
            >>> teams = client.teams.get_all_teams()
            >>> print(teams)
            >>> print(teams["name"])
        """
        data = self._client._get("/league/hierarchy.json")
        return flatten_teams(data)

    def get_team_profile(self, team_id: str) -> pl.DataFrame:
        """Get a profile for a specific team including venue and coach info.

        Note: Returns the same data as get_team_roster() — use whichever
        name makes your code more readable.

        Args:
            team_id: The SportRadar UUID for the team
                     (e.g. "4416091c-0f24-11e2-8525-18a905767e44" for Minnesota Wild).
                     Use get_all_teams() to find team IDs.

        Returns:
            pl.DataFrame: One row per player on the roster with columns:
                id, full_name, first_name, last_name, jersey_number,
                primary_position, birth_date, birth_city, birth_country,
                height, weight, shoots_catches, team_id, team_name

        Example:
            >>> profile = client.teams.get_team_profile("4416091c-0f24-11e2-8525-18a905767e44")
            >>> print(profile.select(["full_name", "primary_position"]))
        """
        data = self._client._get(f"/teams/{team_id}/profile.json")
        return flatten_roster(data)

    def get_team_roster(self, team_id: str) -> pl.DataFrame:
        """Get the current roster for a specific team.

        Note: Returns the same data as get_team_profile() — use whichever
        name makes your code more readable.

        Args:
            team_id: The SportRadar UUID for the team.
                     Use get_all_teams() to find team IDs.

        Returns:
            pl.DataFrame: One row per player on the roster with columns:
                id, full_name, first_name, last_name, jersey_number,
                primary_position, birth_date, birth_city, birth_country,
                height, weight, shoots_catches, team_id, team_name

        Example:
            >>> roster = client.teams.get_team_roster("4416091c-0f24-11e2-8525-18a905767e44")
            >>> print(roster.filter(pl.col("primary_position") == "G"))
        """
        data = self._client._get(f"/teams/{team_id}/profile.json")
        return flatten_roster(data)