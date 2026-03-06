# WNBA Stats Analysis · LA Sparks 2025

Statistical analysis of the LA Sparks' 2025 WNBA season, pulling live data from the ESPN public API.

## 4 Major Takeaways

1. **Scoring Output** - Game-by-game points with 5-game rolling average vs league average
2. **Shooting Efficiency** - FG%, 3P%, and FT% compared to league averages
3. **Top Performers** - Points, assists, and rebounds for the top 5 players
4. **Point Differential** - Win/loss margins across the season with average differential

![LA Sparks 2025 Analysis](assets/sparks_2025_analysis.png)

---

## 2026 Coaching Points of Emphasis

Based on the 2025 season data (22W–23L, -2.5 avg point margin, Kelsey Plum 19.5 PPG, FG 45.7%, 3P 33.7%, FT 76.9%):

### 1. Win the Close Games
The Sparks finished just one game below .500 with an average margin of only -2.5 points — meaning most losses were decided late. The priority for 2026 is execution down the stretch: late-game offensive sets, disciplined ball movement, and defending without fouling in crunch time. A team this close to .500 doesn't need a roster overhaul; it needs composure.

### 2. Build a Second Scoring Option Around Kelsey Plum
Kelsey Plum's 19.5 PPG is elite, but over-reliance on one scorer makes the offense predictable and leaves the team exposed when she's off or double-teamed. Developing a consistent secondary scorer (15+ PPG) would take defensive pressure off Plum and open more opportunities throughout the lineup. Look to second-year players or targeted free agency to fill this role.

### 3. Improve Three-Point Efficiency and Volume
A 33.7% three-point percentage is below the threshold where volume shooting pays off. The coaching staff should identify which players are shooting within their range and which are forcing shots. Either increase attempts from high-percentage shooters or shift offensive emphasis toward mid-range and interior scoring until three-point depth improves.

### 4. Sharpen Free Throw Execution in Pressure Situations
76.9% from the line is acceptable but not a weapon — particularly in close games where late-game fouling is a strategic tool for opponents. Getting to 80%+ as a team, through focused practice reps and consistent pre-shot routines, could directly convert several of those narrow losses into wins across a 40-game season.

---

## Setup

```bash
pip install -r requirements.txt
python analysis.py
```

Output is saved to `assets/sparks_2025_analysis.png`.

## Data Source

[ESPN Public API](https://site.api.espn.com) — no API key required.
