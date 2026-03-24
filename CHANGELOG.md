# Changelog

## v0.0.1 (2026-01-13)

First release of `slapyshot`!

### Features

- `NHLClient` with automatic API key loading from `.env`, configurable access level (`trial` / `production`), and built-in rate limiting
- `TeamsEndpoint` — `get_all_teams()`, `get_team_roster()`, `get_team_profile()`
- `ScheduleEndpoint` — `get_daily_schedule()`, `get_season_schedule()`
- `GamesEndpoint` — `get_game_boxscore()`, `get_game_summary()`, `get_game_play_by_play()`
- `PlayersEndpoint` — `get_player_profile()`, `get_player_season_stats()`
- All endpoints return [Polars](https://pola.rs) DataFrames