#!/usr/bin/env python3
"""
LA Sparks 2025 WNBA Season Analysis
4 Major Takeaways from the 2025 Season

Data source: stats.wnba.com (public API)
"""

import os

import matplotlib.gridspec as gridspec
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import requests

# -- Configuration

SEASON = "2025"
BASE_URL = "https://stats.wnba.com/stats"
SPARKS_NAME = "Los Angeles Sparks"
OUTPUT_DIR = "output"

SPARKS_PURPLE = "#552583"
SPARKS_GOLD = "#FDB927"

HEADERS = {
    "Host": "stats.wnba.com",
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.9",
    "x-nba-stats-origin": "stats",
    "x-nba-stats-token": "true",
    "Referer": "https://www.wnba.com/",
    "Origin": "https://www.wnba.com",
}

# -- Data Fetching


def fetch(endpoint, params):
    url = f"{BASE_URL}/{endpoint}"
    resp = requests.get(url, headers=HEADERS, params=params, timeout=30)
    resp.raise_for_status()
    rs = resp.json()["resultSets"][0]
    return pd.DataFrame(rs["rowSet"], columns=rs["headers"])


def get_team_stats():
    return fetch("leaguedashteamstats", {
        "Season": SEASON,
        "SeasonType": "Regular Season",
        "PerMode": "PerGame",
        "MeasureType": "Base",
    })


def get_game_log(team_id):
    return fetch("teamgamelog", {
        "TeamID": team_id,
        "Season": SEASON,
        "SeasonType": "Regular Season",
    })


def get_player_stats(team_id):
    return fetch("leaguedashplayerstats", {
        "Season": SEASON,
        "SeasonType": "Regular Season",
        "PerMode": "PerGame",
        "MeasureType": "Base",
        "TeamID": team_id,
    })


# -- Analysis & Visualization


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    print("Fetching league team stats...")
    team_stats = get_team_stats()
    for col in team_stats.columns[2:]:
        team_stats[col] = pd.to_numeric(team_stats[col], errors="coerce")

    sparks = team_stats[
        team_stats["TEAM_NAME"] == SPARKS_NAME
    ].iloc[0]
    sparks_id = int(sparks["TEAM_ID"])
    league_avg = team_stats.mean(numeric_only=True)

    print("Fetching Sparks game log...")
    game_log = get_game_log(sparks_id)
    game_log = game_log.iloc[::-1].reset_index(drop=True)
    for col in [
        "PTS", "FG_PCT", "FG3_PCT", "FT_PCT",
        "REB", "AST", "TOV", "PLUS_MINUS",
    ]:
        if col in game_log.columns:
            game_log[col] = pd.to_numeric(
                game_log[col], errors="coerce"
            )
    game_log["WIN"] = (
        game_log["WL"].str.strip().str.upper() == "W"
    )

    print("Fetching Sparks player stats...")
    players = get_player_stats(sparks_id)
    for col in ["PTS", "AST", "REB", "FG_PCT"]:
        players[col] = pd.to_numeric(
            players[col], errors="coerce"
        )

    wins = int(game_log["WIN"].sum())
    losses = int((~game_log["WIN"]).sum())
    game_nums = range(1, len(game_log) + 1)
    top5 = players.nlargest(5, "PTS").reset_index(drop=True)
    avg_diff = game_log["PLUS_MINUS"].mean()

    # -- Figure
    fig = plt.figure(figsize=(18, 13))
    title = (
        f"LA Sparks · 2025 WNBA Season · 4 Major Takeaways"
        f"  ({wins}W\u2013{losses}L)"
    )
    fig.suptitle(
        title,
        fontsize=20,
        fontweight="bold",
        color=SPARKS_PURPLE,
        y=0.99,
    )
    gs = gridspec.GridSpec(2, 2, figure=fig, hspace=0.45, wspace=0.35)

    # -- 1. Scoring Output
    ax1 = fig.add_subplot(gs[0, 0])
    bar_colors = [
        SPARKS_PURPLE if w else "#cccccc" for w in game_log["WIN"]
    ]
    rolling = game_log["PTS"].rolling(5, min_periods=1).mean()
    ax1.bar(game_nums, game_log["PTS"], color=bar_colors, alpha=0.75)
    ax1.plot(
        game_nums, rolling,
        color=SPARKS_GOLD, linewidth=2.5, label="5-game rolling avg",
    )
    ax1.axhline(
        league_avg["PTS"],
        color="gray", linestyle="--", linewidth=1.2,
        label=f"League avg ({league_avg['PTS']:.1f})",
    )
    ax1.set_title(
        "1 · Scoring Output Throughout the Season",
        fontweight="bold",
    )
    ax1.set_xlabel("Game")
    ax1.set_ylabel("Points")
    ax1.legend(
        handles=[
            mpatches.Patch(color=SPARKS_PURPLE, label="Win"),
            mpatches.Patch(color="#cccccc", label="Loss"),
            plt.Line2D(
                [0], [0], color=SPARKS_GOLD, lw=2, label="5-game avg"
            ),
            plt.Line2D(
                [0], [0], color="gray", lw=1.2, linestyle="--",
                label=f"League avg ({league_avg['PTS']:.1f})",
            ),
        ],
        fontsize=8,
    )

    # -- 2. Shooting Efficiency vs League
    ax2 = fig.add_subplot(gs[0, 1])
    metrics = ["FG_PCT", "FG3_PCT", "FT_PCT"]
    labels = ["FG%", "3P%", "FT%"]
    sparks_vals = [float(sparks[m]) * 100 for m in metrics]
    league_vals = [float(league_avg[m]) * 100 for m in metrics]
    x = np.arange(len(labels))
    w = 0.35
    ax2.bar(x - w / 2, sparks_vals, w, label="LA Sparks",
            color=SPARKS_PURPLE)
    ax2.bar(x + w / 2, league_vals, w, label="League Avg",
            color="#aaaaaa")
    for i, (sv, lv) in enumerate(zip(sparks_vals, league_vals)):
        ax2.text(
            i - w / 2, sv + 0.4, f"{sv:.1f}%",
            ha="center", fontsize=9, fontweight="bold",
        )
        ax2.text(
            i + w / 2, lv + 0.4, f"{lv:.1f}%",
            ha="center", fontsize=9,
        )
    ax2.set_title(
        "2 · Shooting Efficiency vs League Average",
        fontweight="bold",
    )
    ax2.set_xticks(x)
    ax2.set_xticklabels(labels)
    ax2.set_ylabel("Percentage (%)")
    ax2.legend()

    # -- 3. Top 5 Performers
    ax3 = fig.add_subplot(gs[1, 0])
    x = np.arange(len(top5))
    w = 0.25
    ax3.bar(x - w, top5["PTS"], w, label="PPG", color=SPARKS_PURPLE)
    ax3.bar(x, top5["AST"], w, label="APG", color=SPARKS_GOLD)
    ax3.bar(x + w, top5["REB"], w, label="RPG", color="#8B4513")
    ax3.set_title(
        "3 · Top 5 Performers by Points Per Game",
        fontweight="bold",
    )
    ax3.set_xticks(x)
    ax3.set_xticklabels(
        [n.split()[-1] for n in top5["PLAYER_NAME"]], rotation=15
    )
    ax3.set_ylabel("Per Game")
    ax3.legend()

    # -- 4. Point Differential
    ax4 = fig.add_subplot(gs[1, 1])
    diff_colors = [
        SPARKS_PURPLE if d >= 0 else "#cc3333"
        for d in game_log["PLUS_MINUS"]
    ]
    ax4.bar(game_nums, game_log["PLUS_MINUS"], color=diff_colors)
    ax4.axhline(0, color="black", linewidth=0.8)
    ax4.axhline(
        avg_diff, color=SPARKS_GOLD, linestyle="--", linewidth=1.5,
    )
    ax4.set_title(
        "4 · Point Differential Per Game",
        fontweight="bold",
    )
    ax4.set_xlabel("Game")
    ax4.set_ylabel("Point Differential")
    ax4.legend(
        handles=[
            mpatches.Patch(color=SPARKS_PURPLE, label="Win"),
            mpatches.Patch(color="#cc3333", label="Loss"),
            plt.Line2D(
                [0], [0], color=SPARKS_GOLD, lw=1.5, linestyle="--",
                label=f"Season avg ({avg_diff:+.1f})",
            ),
        ],
        fontsize=8,
    )

    out_path = os.path.join(OUTPUT_DIR, "sparks_2025_analysis.png")
    plt.savefig(out_path, dpi=150, bbox_inches="tight")
    print(f"\nSaved to {out_path}")
    plt.show()

    # -- Console Summary
    top_scorer = top5.iloc[0]
    sep = "-" * 55
    print(f"\n{sep}")
    print("  LA Sparks 2025 - 4 Major Takeaways")
    print(sep)
    print(
        f"  1. Scoring:    {sparks['PTS']:.1f} PPG"
        f"  (league avg: {league_avg['PTS']:.1f})"
    )
    print(
        f"  2. Shooting:   "
        f"FG {float(sparks['FG_PCT']) * 100:.1f}%  "
        f"3P {float(sparks['FG3_PCT']) * 100:.1f}%  "
        f"FT {float(sparks['FT_PCT']) * 100:.1f}%"
    )
    print(
        f"  3. Top scorer: {top_scorer['PLAYER_NAME']}"
        f"  ({top_scorer['PTS']:.1f} PPG)"
    )
    print(
        f"  4. Record:     {wins}W - {losses}L"
        f"  (avg margin: {avg_diff:+.1f})"
    )
    print(f"{sep}\n")


if __name__ == "__main__":
    main()
