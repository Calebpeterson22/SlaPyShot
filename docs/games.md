# Game Data

This vignette covers the three game-level endpoints: boxscores, game summaries, and play-by-play. All three require a `game_id`, which you get from the [schedule endpoints](schedules.md).

---

## Setup

```python
from slapyshot import NHLClient
import polars as pl

client = NHLClient()

# Get a game ID from today's schedule
schedule = client.schedule.get_daily_schedule(2026, 3, 23)
game_id = schedule["id"][0]
```

---

## Boxscore

`get_game_boxscore()` returns the score broken down by period. This is the lightest of the three game endpoints — use it for scoreboards and quick score checks.

```python
boxscore = client.games.get_game_boxscore(game_id)
print(boxscore)
```

**Columns returned:** `game_id`, `period_number`, `period_type`, `home_team_id`, `home_team_name`, `home_points`, `away_team_id`, `away_team_name`, `away_points`

### Show the score by period

```python
print(
    boxscore.select([
        "period_number", "home_team_name", "home_points",
        "away_team_name", "away_points"
    ])
)
```

### Calculate final score

```python
final_home = boxscore["home_points"].sum()
final_away = boxscore["away_points"].sum()

home_name = boxscore["home_team_name"][0]
away_name = boxscore["away_team_name"][0]

print(f"{home_name} {final_home} — {away_name} {final_away}")
```

---

## Game Summary

`get_game_summary()` returns individual player stats for both teams. Use this when you want richer data beyond just the score.

```python
summary = client.games.get_game_summary(game_id)
print(summary)
```

**Columns returned:** `game_id`, `team_id`, `team_name`, `player_id`, `full_name`, `position`, `goals`, `assists`, `points`, `plus_minus`, `shots`, `penalty_minutes`, `time_on_ice`

### Top scorers in the game

```python
top_scorers = (
    summary
    .sort("points", descending=True)
    .select(["full_name", "team_name", "goals", "assists", "points"])
    .head(10)
)
print(top_scorers)
```

### Filter by team

```python
home_team = summary["team_name"][0]
home_players = summary.filter(pl.col("team_name") == home_team)
print(home_players.sort("points", descending=True))
```

### Find players with a point

```python
scorers = summary.filter(pl.col("points") > 0)
print(scorers.select(["full_name", "team_name", "goals", "assists", "points"]))
```

### Players with penalty minutes

```python
penalties = (
    summary
    .filter(pl.col("penalty_minutes") > 0)
    .select(["full_name", "team_name", "penalty_minutes"])
    .sort("penalty_minutes", descending=True)
)
print(penalties)
```

---

## Play-by-Play

`get_game_play_by_play()` returns every event in the game — faceoffs, shots, goals, penalties, and more. This is the heaviest endpoint, but it gives you the most granular data.

```python
pbp = client.games.get_game_play_by_play(game_id)
print(f"Total events: {len(pbp)}")
```

**Columns returned:** `game_id`, `period_number`, `event_id`, `event_type`, `clock`, `description`, `player_id`, `player_name`, `team_id`

### See all event types

```python
print(pbp["event_type"].unique().sort())
```

### Filter for goals only

```python
goals = pbp.filter(pl.col("event_type") == "goal")
print(goals.select(["period_number", "clock", "player_name", "description"]))
```

### All events in the third period

```python
third = pbp.filter(pl.col("period_number") == 3)
print(third)
```

### Shot attempts by team

```python
shots = (
    pbp
    .filter(pl.col("event_type").is_in(["shot", "goal"]))
    .group_by("team_id")
    .agg(pl.len().alias("shot_attempts"))
    .sort("shot_attempts", descending=True)
)
print(shots)
```

### Timeline of goals

```python
goals_timeline = (
    pbp
    .filter(pl.col("event_type") == "goal")
    .select(["period_number", "clock", "player_name", "team_id", "description"])
    .sort(["period_number", "clock"], descending=[False, True])
)
print(goals_timeline)
```

!!! tip "Use play-by-play sparingly on the free tier"
    Play-by-play responses are large but still count as a single API call. To stay within your 1,000/month quota during development, test with boxscore or summary first, then switch to play-by-play when you need the full event log.

---

## Choosing the Right Endpoint

| Endpoint | Use when you want... |
|---|---|
| `get_game_boxscore()` | Final score, score by period |
| `get_game_summary()` | Individual player stats, top scorers |
| `get_game_play_by_play()` | Every event, shot maps, goal timelines |