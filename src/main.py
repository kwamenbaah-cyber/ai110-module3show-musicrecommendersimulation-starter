"""Command line runner for the Music Recommender Simulation."""

from recommender import load_songs, recommend_songs

try:
    from tabulate import tabulate
    HAS_TABULATE = True
except ImportError:
    HAS_TABULATE = False


PROFILES = {
    "Happy Pop Fan": {
        "genre": "pop",
        "mood": "happy",
        "energy": 0.80,
        "valence": 0.85,
        "likes_acoustic": False,
    },
    "Chill Lofi Listener": {
        "genre": "lofi",
        "mood": "chill",
        "energy": 0.38,
        "valence": 0.58,
        "likes_acoustic": True,
    },
    "High-Energy EDM Head": {
        "genre": "EDM",
        "mood": "intense",
        "energy": 0.95,
        "valence": 0.65,
        "likes_acoustic": False,
    },
    "Moody Synthwave Night": {
        "genre": "synthwave",
        "mood": "moody",
        "energy": 0.72,
        "valence": 0.45,
        "likes_acoustic": False,
    },
    "Acoustic Folk Wanderer": {
        "genre": "folk",
        "mood": "relaxed",
        "energy": 0.32,
        "valence": 0.72,
        "likes_acoustic": True,
    },
}

MODES = ["balanced", "genre-first", "mood-first", "energy-focused"]


def _divider(width: int = 62) -> str:
    return "=" * width


def print_recommendations(label: str, recs, mode: str) -> None:
    print(f"\n{_divider()}")
    print(f"  {label}  [mode: {mode}]")
    print(_divider())

    if HAS_TABULATE:
        rows = [
            [rank, song["title"], song["artist"], f"{score:.2f}", explanation]
            for rank, (song, score, explanation) in enumerate(recs, 1)
        ]
        print(tabulate(
            rows,
            headers=["#", "Title", "Artist", "Score", "Reasons"],
            tablefmt="rounded_outline",
            maxcolwidths=[3, 22, 16, 6, 46],
        ))
    else:
        for rank, (song, score, explanation) in enumerate(recs, 1):
            print(f"  {rank}. {song['title']} by {song['artist']}  |  Score: {score:.2f}")
            print(f"     {explanation}")
            print()


def main() -> None:
    songs = load_songs("data/songs.csv")
    print(f"Loaded {len(songs)} songs.\n")

    print("=" * 62)
    print("  PROFILE RECOMMENDATIONS  (mode: balanced)")
    print("=" * 62)
    for name, prefs in PROFILES.items():
        recs = recommend_songs(prefs, songs, k=5, mode="balanced")
        print_recommendations(name, recs, "balanced")

    print("\n\n" + "=" * 62)
    print("  MODE COMPARISON  —  Happy Pop Fan  (top 3)")
    print("=" * 62)
    for mode in MODES:
        recs = recommend_songs(PROFILES["Happy Pop Fan"], songs, k=3, mode=mode)
        print_recommendations("Happy Pop Fan", recs, mode)


if __name__ == "__main__":
    main()
