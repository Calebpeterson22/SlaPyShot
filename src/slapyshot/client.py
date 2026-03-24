# client.py - Core NHLClient class
# Handles API key loading, base URL, and rate limiting

import os
import time
import requests
from dotenv import load_dotenv

from .endpoints.teams import TeamsEndpoint
from .endpoints.schedule import ScheduleEndpoint
from .endpoints.games import GamesEndpoint
from .endpoints.players import PlayersEndpoint

load_dotenv()

_VALID_ACCESS_LEVELS = ("trial", "production")


class NHLClient:
    """Main client for interacting with the SportRadar NHL API.

    Loads the API key from the SPORTRADAR_API_KEY environment variable.
    Enforces a 1 second delay between requests to respect free tier rate limits.

    Args:
        api_key: Your SportRadar API key. If not provided, loads from the
                 SPORTRADAR_API_KEY environment variable or .env file.
        access_level: Either "trial" (default, free tier) or "production".
        rate_limit_delay: Seconds to wait between requests. Defaults to 1.0
                          to stay within the free tier limit of 1 call/second.

    Example:
        >>> # Free tier (default)
        >>> client = NHLClient()

        >>> # Production tier
        >>> client = NHLClient(access_level="production")

        >>> client.teams.get_all_teams()
    """

    def __init__(
        self,
        api_key: str = None,
        access_level: str = "trial",
        rate_limit_delay: float = 1.0,
    ):
        self.api_key = api_key or os.getenv("SPORTRADAR_API_KEY")
        if not self.api_key:
            raise ValueError(
                "No API key found. Set SPORTRADAR_API_KEY in your .env file "
                "or pass it directly as api_key='your_key'."
            )

        if access_level not in _VALID_ACCESS_LEVELS:
            raise ValueError(
                f"Invalid access_level '{access_level}'. "
                f"Must be one of: {_VALID_ACCESS_LEVELS}"
            )

        self.access_level = access_level
        self.base_url = f"https://api.sportradar.com/nhl/{access_level}/v7/en"
        self.rate_limit_delay = rate_limit_delay
        self._last_call_time = 0.0

        # Endpoint groups
        self.teams = TeamsEndpoint(self)
        self.schedule = ScheduleEndpoint(self)
        self.games = GamesEndpoint(self)
        self.players = PlayersEndpoint(self)

    def _get(self, path: str, params: dict = None) -> dict:
        """Internal method to make a rate-limited GET request.

        Args:
            path: The API endpoint path (e.g. '/teams/{team_id}/profile.json')
            params: Optional query parameters

        Returns:
            Parsed JSON response as a dictionary
        """
        # Rate limiting - wait if needed before making the call
        elapsed = time.time() - self._last_call_time
        if elapsed < self.rate_limit_delay:
            time.sleep(self.rate_limit_delay - elapsed)

        url = f"{self.base_url}{path}"
        query_params = {"api_key": self.api_key}
        if params:
            query_params.update(params)

        response = requests.get(url, params=query_params)
        self._last_call_time = time.time()

        response.raise_for_status()
        return response.json()