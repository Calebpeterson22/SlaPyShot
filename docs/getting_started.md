# Getting Started

This page walks you through installing SlaPyShot, setting up your API key, and making your first request.

---

## 1. Install SlaPyShot

=== "pip"

    ```bash
    pip install git+https://github.com/Calebpeterson22/SlaPyShot.git@main
    ```

=== "uv"

    ```bash
    uv pip install git+https://github.com/Calebpeterson22/SlaPyShot.git@main
    ```

=== "uv (dev/editable)"

    ```bash
    uv sync
    ```

---

## 2. Get a SportRadar API Key

SlaPyShot uses the [SportRadar NHL API](https://developer.sportradar.com/). The free trial tier gives you access to all endpoints used by this package.

1. Sign up at [developer.sportradar.com](https://developer.sportradar.com/)
2. Register a new application and request access to the **NHL Official API Trial**
3. Copy your API key

!!! note "Trial tier limits"
    The free trial tier allows **1 request per second** and **1,000 requests per month**. SlaPyShot's built-in rate limiter handles the 1 req/sec limit automatically.

---

## 3. Configure Your API Key

Create a `.env` file in your project root and add your key:

```bash
SPORTRADAR_API_KEY=your_key_here
```

SlaPyShot will load it automatically on import. You can also pass the key directly:

```python
from slapyshot import NHLClient

# From .env (recommended)
client = NHLClient()

# Or passed directly
client = NHLClient(api_key="your_key_here")
```

!!! warning "Keep your key out of version control"
    Add `.env` to your `.gitignore` so your API key is never committed to a repository.

---

## 4. Your First Request

```python
from slapyshot import NHLClient

client = NHLClient()

# Get all NHL teams
teams = client.teams.get_all_teams()
print(teams)
```

You should see a Polars DataFrame with one row per team:

```
shape: (32, 9)
┌──────────────────────┬────────────┬──────────┬───────┬─────────┬──────────────┬─────────────────┬─────────────┬───────────────┐
│ id                   ┆ name       ┆ market   ┆ alias ┆ founded ┆ conference_id┆ conference_name ┆ division_id ┆ division_name │
╞══════════════════════╪════════════╪══════════╪═══════╪═════════╪══════════════╪═════════════════╪═════════════╪═══════════════╡
│ 4416091c-0f24-11e2…  ┆ Wild       ┆ Minnesota┆ MIN   ┆ 2000    ┆ conf-west-id ┆ Western         ┆ div-cent-id ┆ Central       │
│ …                    ┆ …          ┆ …        ┆ …     ┆ …       ┆ …            ┆ …               ┆ …           ┆ …             │
└──────────────────────┴────────────┴──────────┴───────┴─────────┴──────────────┴─────────────────┴─────────────┴───────────────┘
```

---

## 5. Access Levels

SlaPyShot supports both SportRadar access levels:

```python
# Free trial (default)
client = NHLClient(access_level="trial")

# Paid production access
client = NHLClient(access_level="production")
```

---

## 6. Rate Limiting

The default delay between API calls is **1.0 seconds**, matching the trial tier limit. You can adjust this for production access:

```python
# Faster for production tier
client = NHLClient(rate_limit_delay=0.5)

# Slower if you want to be extra conservative
client = NHLClient(rate_limit_delay=2.0)
```

The rate limiter is automatic — you never need to call `time.sleep()` yourself.

---

## Next Steps

Now that you're set up, explore what SlaPyShot can do:

- [Teams & Rosters](vignettes/teams.md) — find team IDs and pull rosters
- [Schedules](vignettes/schedules.md) — get game IDs from daily or season schedules
- [Game Data](vignettes/games.md) — boxscores, summaries, and play-by-play
- [Player Stats](vignettes/players.md) — career profiles and season leaderboards