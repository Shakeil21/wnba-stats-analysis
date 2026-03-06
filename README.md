# WNBA Stats Analysis · LA Sparks 2025

Statistical analysis of the LA Sparks' 2025 WNBA season, pulling live data from the public stats.wnba.com API.

## 4 Major Takeaways

1. **Scoring Output** - Game-by-game points with 5-game rolling average vs league average
2. **Shooting Efficiency** - FG%, 3P%, and FT% compared to league averages
3. **Top Performers** - Points, assists, and rebounds for the top 5 players
4. **Point Differential** - Win/loss margins across the season with average differential

## Setup

```bash
pip install -r requirements.txt
python analysis.py
```

Output is saved to `output/sparks_2025_analysis.png`.

## Data Source

[stats.wnba.com](https://stats.wnba.com) — public stats API, no API key required.
