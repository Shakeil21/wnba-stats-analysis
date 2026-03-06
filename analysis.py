#!/usr/bin/env python3
"""
LA Sparks 2025 WNBA Season Analysis
4 Major Takeaways from the 2025 Season

Data source: ESPN public API
"""

import os

import matplotlib.gridspec as gridspec
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import requests

# -- Configuration

SEASON = 2025
ESPN_BASE = (
    "https://site.api.espn.com/apis/site/v2"
    "/sports/basketball/wnba"
)
ESPN_CORE = (
    "https://sports.core.api.espn.com/v2"
    "/sports/basketball/leagues/wnba"
)
SPARKS_NAME = "Los Angeles Sparks"
OUTPUT_DIR = "assets"

SPARKS_PURPLE = "#552583"
SPARKS_GOLD = "#FDB927"


# -- Data Fetching


def get(url, params=None):
    resp = requests.get(url, params=params, timeout=30)
    resp.raise_for_status()
    return resp.json()


def find_sparks_id():
    data = get(f"{ESPN_BASE}/teams")
    teams = data["sports"][0]["leagues"][0]["teams"]
    for entry in teams:
        team = entry["team"]
        if team["displayName"] == SPARKS_NAME:
            return team["id"]
    raise ValueError(f"{SPARKS_NAME} not found in ESPN teams list.")


def get_schedule(team_id):
    data = get(
        f"{ESPN_BASE}/teams/{team_id}/schedule",
        params={"season": SEASON},
    )
    events = data.get("events", [])
    rows = []
    for event in events:
        comp = event.get("competitions", [{}])[0]
        competitors = comp.get("competitors", [])
        if not competitors:
            continue
        status = comp.get("status", {}).get("type", {})
        if status.get("name") != "STATUS_FINAL":
            continue
        sparks_comp = next(
            (c for c in competitors
             if c["id"] == str(team_id)), None
        )
        opp_comp = next(
            (c for c in competitors
             if c["id"] != str(team_id)), None
        )
        if not sparks_comp or not opp_comp:
            continue
        sparks_score = int(
            sparks_comp.get("score", {}).get("value", 0)
        )
        opp_score = int(
            opp_comp.get("score", {}).get("value", 0)
        )
        rows.append({
            "date": event.get("date", "")[:10],
            "opponent": opp_comp.get(
                "team", {}
            ).get("abbreviation", ""),
            "home": sparks_comp.get("homeAway") == "home",
            "sparks_score": sparks_score,
            "opp_score": opp_score,
            "win": sparks_score > opp_score,
            "margin": sparks_score - opp_score,
        })
    return pd.DataFrame(rows)


def get_team_stats(team_id):
    data = get(
        f"{ESPN_BASE}/teams/{team_id}/statistics",
        params={"season": SEASON},
    )
    stats = {}
    for cat in data.get("results", {}).get("stats", {}).get(
        "categories", []
    ):
        for s in cat.get("stats", []):
            stats[s["name"]] = s.get("value")
    return stats


def get_all_team_stats():
    data = get(f"{ESPN_BASE}/teams")
    teams = data["sports"][0]["leagues"][0]["teams"]
    all_stats = []
    for entry in teams:
        tid = entry["team"]["id"]
        name = entry["team"]["displayName"]
        try:
            s = get_team_stats(tid)
            s["team"] = name
            all_stats.append(s)
        except Exception:
            continue
    return pd.DataFrame(all_stats)


def get_roster_stats(team_id):
    roster = get(
        f"{ESPN_BASE}/teams/{team_id}/roster",
        params={"season": SEASON},
    )
    rows = []
    for athlete in roster.get("athletes", []):
        pid = athlete["id"]
        name = athlete.get("fullName", "")
        url = (
            f"{ESPN_CORE}/seasons/{SEASON}/types/2"
            f"/athletes/{pid}/statistics/0"
        )
        try:
            data = get(url)
        except Exception:
            continue
        avg = {"name": name}
        for cat in (
            data.get("splits", {}).get("categories", [])
        ):
            for s in cat.get("stats", []):
                avg[s["name"]] = s.get("value")
        rows.append(avg)
    return pd.DataFrame(rows)


# -- Analysis & Visualization


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    print("Finding LA Sparks team ID...")
    sparks_id = find_sparks_id()
    print(f"  Team ID: {sparks_id}")

    print("Fetching game schedule/results...")
    games = get_schedule(sparks_id)
    if games.empty:
        print("No completed games found for 2025 season.")
        return

    print(f"  Found {len(games)} completed games.")

    print("Fetching Sparks season stats...")
    sparks_stats = get_team_stats(sparks_id)

    print("Fetching league-wide team stats for comparison...")
    league_df = get_all_team_stats()

    print("Fetching roster/player stats...")
    players = get_roster_stats(sparks_id)

    wins = int(games["win"].sum())
    losses = int((~games["win"]).sum())
    game_nums = range(1, len(games) + 1)
    avg_margin = games["margin"].mean()

    # -- Figure
    fig = plt.figure(figsize=(18, 13))
    fig.suptitle(
        f"LA Sparks · 2025 WNBA Season · 4 Major Takeaways"
        f"  ({wins}W\u2013{losses}L)",
        fontsize=20,
        fontweight="bold",
        color=SPARKS_PURPLE,
        y=0.99,
    )
    gs = gridspec.GridSpec(2, 2, figure=fig, hspace=0.45, wspace=0.35)

    # -- 1. Scoring Output
    ax1 = fig.add_subplot(gs[0, 0])
    bar_colors = [
        SPARKS_PURPLE if w else "#cccccc" for w in games["win"]
    ]
    rolling = games["sparks_score"].rolling(5, min_periods=1).mean()
    ax1.bar(
        game_nums, games["sparks_score"],
        color=bar_colors, alpha=0.75,
    )
    ax1.plot(
        game_nums, rolling,
        color=SPARKS_GOLD, linewidth=2.5, label="5-game avg",
    )
    league_ppg = league_df["avgPoints"].mean() if (
        "avgPoints" in league_df.columns
    ) else None
    if league_ppg:
        ax1.axhline(
            league_ppg, color="gray", linestyle="--", linewidth=1.2,
            label=f"League avg ({league_ppg:.1f})",
        )
    ax1.set_title(
        "1 · Scoring Output Throughout the Season",
        fontweight="bold",
    )
    ax1.set_xlabel("Game")
    ax1.set_ylabel("Points Scored")
    ax1.legend(
        handles=[
            mpatches.Patch(color=SPARKS_PURPLE, label="Win"),
            mpatches.Patch(color="#cccccc", label="Loss"),
            plt.Line2D(
                [0], [0], color=SPARKS_GOLD, lw=2,
                label="5-game avg",
            ),
        ],
        fontsize=8,
    )

    # -- 2. Shooting Efficiency vs League
    ax2 = fig.add_subplot(gs[0, 1])
    shoot_keys = [
        ("fieldGoalPct", "FG%"),
        ("threePointFieldGoalPct", "3P%"),
        ("freeThrowPct", "FT%"),
    ]
    available = [
        (k, lbl) for k, lbl in shoot_keys
        if k in sparks_stats and k in league_df.columns
    ]
    if available:
        keys, labels = zip(*available)
        sparks_vals = [
            float(sparks_stats[k] or 0) * 100 for k in keys
        ]
        league_vals = [
            float(league_df[k].mean() or 0) * 100 for k in keys
        ]
        x = np.arange(len(labels))
        w = 0.35
        ax2.bar(
            x - w / 2, sparks_vals, w,
            label="LA Sparks", color=SPARKS_PURPLE,
        )
        ax2.bar(
            x + w / 2, league_vals, w,
            label="League Avg", color="#aaaaaa",
        )
        for i, (sv, lv) in enumerate(zip(sparks_vals, league_vals)):
            ax2.text(
                i - w / 2, sv + 0.4, f"{sv:.1f}%",
                ha="center", fontsize=9, fontweight="bold",
            )
            ax2.text(
                i + w / 2, lv + 0.4, f"{lv:.1f}%",
                ha="center", fontsize=9,
            )
        ax2.set_xticks(x)
        ax2.set_xticklabels(labels)
        ax2.set_ylabel("Percentage (%)")
        ax2.legend()
    ax2.set_title(
        "2 · Shooting Efficiency vs League Average",
        fontweight="bold",
    )

    # -- 3. Top 5 Performers
    ax3 = fig.add_subplot(gs[1, 0])
    stat_cols = {
        "avgPoints": "PPG",
        "avgAssists": "APG",
        "avgRebounds": "RPG",
    }
    available_cols = {
        k: v for k, v in stat_cols.items() if k in players.columns
    }
    if "avgPoints" in players.columns and not players.empty:
        players["avgPoints"] = pd.to_numeric(
            players["avgPoints"], errors="coerce"
        )
        top5 = players.nlargest(5, "avgPoints").reset_index(drop=True)
        x = np.arange(len(top5))
        w = 0.25
        colors_bars = [SPARKS_PURPLE, SPARKS_GOLD, "#8B4513"]
        for i, (col, lbl) in enumerate(available_cols.items()):
            if col in top5.columns:
                vals = pd.to_numeric(
                    top5[col], errors="coerce"
                ).fillna(0)
                ax3.bar(
                    x + (i - 1) * w, vals, w,
                    label=lbl, color=colors_bars[i],
                )
        ax3.set_xticks(x)
        ax3.set_xticklabels(
            [n.split()[-1] for n in top5["name"]], rotation=15
        )
        ax3.set_ylabel("Per Game")
        ax3.legend()
    ax3.set_title(
        "3 · Top 5 Performers by Points Per Game",
        fontweight="bold",
    )

    # -- 4. Point Differential
    ax4 = fig.add_subplot(gs[1, 1])
    diff_colors = [
        SPARKS_PURPLE if d >= 0 else "#cc3333"
        for d in games["margin"]
    ]
    ax4.bar(game_nums, games["margin"], color=diff_colors)
    ax4.axhline(0, color="black", linewidth=0.8)
    ax4.axhline(
        avg_margin,
        color=SPARKS_GOLD, linestyle="--", linewidth=1.5,
    )
    ax4.set_title(
        "4 · Point Differential Per Game", fontweight="bold"
    )
    ax4.set_xlabel("Game")
    ax4.set_ylabel("Point Differential")
    ax4.legend(
        handles=[
            mpatches.Patch(color=SPARKS_PURPLE, label="Win"),
            mpatches.Patch(color="#cc3333", label="Loss"),
            plt.Line2D(
                [0], [0], color=SPARKS_GOLD, lw=1.5,
                linestyle="--",
                label=f"Season avg ({avg_margin:+.1f})",
            ),
        ],
        fontsize=8,
    )

    out_path = os.path.join(OUTPUT_DIR, "sparks_2025_analysis.png")
    plt.savefig(out_path, dpi=150, bbox_inches="tight")
    print(f"\nSaved to {out_path}")
    plt.show()

    # -- Console Summary
    sparks_ppg = sparks_stats.get("avgPoints", "N/A")
    sparks_fg = sparks_stats.get("fieldGoalPct")
    sparks_3p = sparks_stats.get("threePointFieldGoalPct")
    sparks_ft = sparks_stats.get("freeThrowPct")

    def pct(v):
        return f"{float(v) * 100:.1f}%" if v is not None else "N/A"

    sep = "-" * 55
    print(f"\n{sep}")
    print("  LA Sparks 2025 - 4 Major Takeaways")
    print(sep)
    print(f"  1. Scoring:    {sparks_ppg} PPG")
    print(
        f"  2. Shooting:   FG {pct(sparks_fg)}  "
        f"3P {pct(sparks_3p)}  FT {pct(sparks_ft)}"
    )
    if "avgPoints" in players.columns and not players.empty:
        top = players.nlargest(1, "avgPoints").iloc[0]
        print(
            f"  3. Top scorer: {top['name']}"
            f"  ({top['avgPoints']:.1f} PPG)"
        )
    print(
        f"  4. Record:     {wins}W - {losses}L"
        f"  (avg margin: {avg_margin:+.1f})"
    )
    print(f"{sep}\n")


if __name__ == "__main__":
    main()
