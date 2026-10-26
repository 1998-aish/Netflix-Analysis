"""Generate the README charts from data/movies.csv.

Run from the repo root:  python src/make_charts.py
"""
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "images"
OUT.mkdir(exist_ok=True)

ACCENT = "#E50914"  # Netflix red
GREY = "#B3B3B3"

plt.rcParams.update({
    "figure.dpi": 120,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.titleweight": "bold",
    "axes.titlesize": 13,
})


def load() -> pd.DataFrame:
    df = pd.read_csv(ROOT / "data" / "movies.csv", lineterminator="\n")
    df["year"] = pd.to_datetime(df["Release_Date"], errors="coerce").dt.year
    return df


def explode_genres(df: pd.DataFrame) -> pd.DataFrame:
    return df.assign(genre=df["Genre"].str.split(", ")).explode("genre")


def genre_share(df: pd.DataFrame) -> None:
    share = explode_genres(df)["genre"].value_counts().head(10) / len(df) * 100
    fig, ax = plt.subplots(figsize=(8, 4.5))
    colors = [ACCENT] + [GREY] * (len(share) - 1)
    ax.barh(share.index[::-1], share.values[::-1], color=colors[::-1])
    for i, v in enumerate(share.values[::-1]):
        ax.text(v + 0.5, i, f"{v:.0f}%", va="center", fontsize=9)
    ax.set_title("Top 10 genres (% of movies tagged)")
    ax.set_xlabel("% of movies (a movie can have several genres)")
    fig.tight_layout()
    fig.savefig(OUT / "genre_share.png")
    plt.close(fig)


def rating_by_genre(df: pd.DataFrame) -> None:
    g = explode_genres(df)
    stats = (g.groupby("genre")
               .agg(n=("Title", "size"), rating=("Vote_Average", "mean"))
               .query("n >= 200")
               .sort_values("rating"))
    fig, ax = plt.subplots(figsize=(8, 5))
    colors = [ACCENT if r >= 6.8 else (GREY if r > 6.0 else "#555555") for r in stats["rating"]]
    ax.barh(stats.index, stats["rating"], color=colors)
    ax.set_xlim(5.5, 7.2)
    for i, v in enumerate(stats["rating"]):
        ax.text(v + 0.02, i, f"{v:.2f}", va="center", fontsize=8)
    ax.set_title("Average audience rating by genre (genres with 200+ movies)")
    ax.set_xlabel("Average vote (0–10)")
    fig.tight_layout()
    fig.savefig(OUT / "rating_by_genre.png")
    plt.close(fig)


def releases_over_time(df: pd.DataFrame) -> None:
    per_year = df[df["year"].between(1970, 2023)].groupby("year").size()
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.plot(per_year.index, per_year.values, color=ACCENT, linewidth=2)
    ax.fill_between(per_year.index, per_year.values, color=ACCENT, alpha=0.1)
    ax.set_title("Movies in the catalog by release year (1970–2023)")
    ax.set_ylabel("Number of movies")
    fig.tight_layout()
    fig.savefig(OUT / "releases_over_time.png")
    plt.close(fig)


def language_share(df: pd.DataFrame) -> None:
    share = df["Original_Language"].value_counts(normalize=True).head(6) * 100
    names = {"en": "English", "ja": "Japanese", "es": "Spanish",
             "fr": "French", "ko": "Korean", "zh": "Chinese", "it": "Italian"}
    labels = [names.get(c, c) for c in share.index]
    fig, ax = plt.subplots(figsize=(8, 3.5))
    colors = [ACCENT] + [GREY] * (len(share) - 1)
    ax.bar(labels, share.values, color=colors)
    for i, v in enumerate(share.values):
        ax.text(i, v + 1, f"{v:.1f}%", ha="center", fontsize=9)
    ax.set_title("Original language of movies")
    ax.set_ylabel("% of movies")
    fig.tight_layout()
    fig.savefig(OUT / "language_share.png")
    plt.close(fig)


if __name__ == "__main__":
    data = load()
    genre_share(data)
    rating_by_genre(data)
    releases_over_time(data)
    language_share(data)
    print(f"Saved charts to {OUT}")
