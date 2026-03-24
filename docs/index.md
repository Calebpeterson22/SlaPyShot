# SlaPyShot

**A clean Python wrapper for the SportRadar NHL API.**

SlaPyShot turns raw SportRadar JSON into tidy [Polars](https://pola.rs) DataFrames with one line of code. No wrestling with nested dicts, no manual pagination, no rate-limit headaches — just hockey data, ready to analyze.

```python
from slapyshot import NHLClient

client = NHLClient()

# Get every NHL team
teams = client.teams.get_all_teams()

# Today's schedule
schedule = client.schedule.get_daily_schedule(2026, 3, 23)

# Live boxscore
boxscore = client.games.get_game_boxscore(game_id)

# Player career stats
profile = client.players.get_player_profile(player_id)
```

---

## Why SlaPyShot?

| Feature | Detail |
|---|---|
| **Polars-native** | Every endpoint returns a `pl.DataFrame` — filter, sort, join with zero boilerplate |
| **Rate limiting built in** | Automatic 1-second delay between calls keeps you inside the free tier |
| **Simple auth** | Drop your API key in a `.env` file and forget about it |
| **Typed & documented** | Every method has full docstrings with column descriptions and examples |

---

## Installation

```bash
pip install slapyshot
```

Or with `uv`:

```bash
uv pip install slapyshot
```

---

## Quick Setup

1. Get a free API key from [SportRadar](https://developer.sportradar.com/)
2. Add it to a `.env` file in your project root:

```bash
SPORTRADAR_API_KEY=your_key_here
```

3. Start querying:

```python
from slapyshot import NHLClient
client = NHLClient()
print(client.teams.get_all_teams())
```

---

## What's Available

<div class="grid cards" markdown>

-   :fontawesome-solid-users: **Teams & Rosters**

    ---

    Get all 32 NHL teams with conference and division info, or pull the full roster for any team.

    [:octicons-arrow-right-24: Teams vignette](vignettes/teams.md)

-   :fontawesome-solid-calendar: **Schedules**

    ---

    Fetch the schedule for any single day or pull the full season schedule at once.

    [:octicons-arrow-right-24: Schedules vignette](vignettes/schedules.md)

-   :fontawesome-solid-hockey-puck: **Game Data**

    ---

    Boxscores, player summaries, and full play-by-play for any game.

    [:octicons-arrow-right-24: Game data vignette](vignettes/games.md)

-   :fontawesome-solid-chart-line: **Player Stats**

    ---

    Career profiles and full team season statistics for any player or team.

    [:octicons-arrow-right-24: Player stats vignette](vignettes/players.md)

</div>