from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
import csv


@dataclass
class Song:
    id: int
    title: str
    artist: str
    genre: str
    mood: str
    energy: float
    tempo_bpm: float
    valence: float
    danceability: float
    acousticness: float
    popularity: int = 50
    release_decade: int = 2020
    instrumentalness: float = 0.0
    speechiness: float = 0.1
    loudness_norm: float = 0.5


@dataclass
class UserProfile:
    favorite_genre: str
    favorite_mood: str
    target_energy: float
    likes_acoustic: bool
    target_valence: float = 0.7
    target_danceability: float = 0.7


class Recommender:
    def __init__(self, songs: List[Song]):
        self.songs = songs

    def _compute_score(self, user: UserProfile, song: Song) -> Tuple[float, List[str]]:
        score = 0.0
        reasons = []

        if song.genre == user.favorite_genre:
            score += 2.0
            reasons.append(f"genre match: {song.genre} (+2.0)")

        if song.mood == user.favorite_mood:
            score += 1.0
            reasons.append(f"mood match: {song.mood} (+1.0)")

        energy_pts = 1.0 - abs(song.energy - user.target_energy)
        score += energy_pts
        reasons.append(f"energy proximity (+{energy_pts:.2f})")

        valence_pts = 0.5 * (1.0 - abs(song.valence - user.target_valence))
        score += valence_pts
        reasons.append(f"valence proximity (+{valence_pts:.2f})")

        if user.likes_acoustic and song.acousticness > 0.6:
            score += 0.5
            reasons.append("acoustic preference match (+0.5)")

        return score, reasons

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        """Returns the top k songs sorted from highest to lowest score for the given user."""
        return sorted(
            self.songs,
            key=lambda s: self._compute_score(user, s)[0],
            reverse=True,
        )[:k]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        """Returns a human-readable explanation of why a song was recommended."""
        _, reasons = self._compute_score(user, song)
        return "; ".join(reasons)


SCORING_MODES: Dict[str, Dict[str, float]] = {
    "balanced":       {"genre": 2.0, "mood": 1.0, "energy": 1.0, "valence": 0.5, "acoustic": 0.5},
    "genre-first":    {"genre": 4.0, "mood": 0.5, "energy": 0.5, "valence": 0.25, "acoustic": 0.25},
    "mood-first":     {"genre": 1.0, "mood": 3.0, "energy": 0.5, "valence": 0.5,  "acoustic": 0.5},
    "energy-focused": {"genre": 1.0, "mood": 0.5, "energy": 3.0, "valence": 0.5,  "acoustic": 0.25},
}


def load_songs(csv_path: str) -> List[Dict]:
    """Reads songs from a CSV file and returns a list of dicts with numeric fields cast to the correct types."""
    songs = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            row["id"] = int(row["id"])
            row["tempo_bpm"] = float(row["tempo_bpm"])
            row["energy"] = float(row["energy"])
            row["valence"] = float(row["valence"])
            row["danceability"] = float(row["danceability"])
            row["acousticness"] = float(row["acousticness"])
            row["popularity"] = int(row.get("popularity", 50))
            row["release_decade"] = int(row.get("release_decade", 2020))
            row["instrumentalness"] = float(row.get("instrumentalness", 0.0))
            row["speechiness"] = float(row.get("speechiness", 0.1))
            row["loudness_norm"] = float(row.get("loudness_norm", 0.5))
            songs.append(row)
    return songs


def score_song(user_prefs: Dict, song: Dict, mode: str = "balanced") -> Tuple[float, List[str]]:
    """Scores a single song against user preferences using weighted feature matching; returns (score, reasons)."""
    w = SCORING_MODES.get(mode, SCORING_MODES["balanced"])
    score = 0.0
    reasons = []

    if song.get("genre") == user_prefs.get("genre"):
        pts = w["genre"]
        score += pts
        reasons.append(f"genre match: {song['genre']} (+{pts:.1f})")

    if song.get("mood") == user_prefs.get("mood"):
        pts = w["mood"]
        score += pts
        reasons.append(f"mood match: {song['mood']} (+{pts:.1f})")

    energy_pts = w["energy"] * (1.0 - abs(song.get("energy", 0.5) - user_prefs.get("energy", 0.5)))
    score += energy_pts
    reasons.append(f"energy proximity (+{energy_pts:.2f})")

    if "valence" in user_prefs:
        valence_pts = w["valence"] * (1.0 - abs(song.get("valence", 0.5) - user_prefs["valence"]))
        score += valence_pts
        reasons.append(f"valence proximity (+{valence_pts:.2f})")

    if user_prefs.get("likes_acoustic") and song.get("acousticness", 0.0) > 0.6:
        score += w["acoustic"]
        reasons.append(f"acoustic preference (+{w['acoustic']:.1f})")

    return score, reasons


def recommend_songs(
    user_prefs: Dict,
    songs: List[Dict],
    k: int = 5,
    mode: str = "balanced",
    diversity_penalty: float = 0.4,
) -> List[Tuple[Dict, float, str]]:
    """Ranks all songs by score and returns the top k, applying a per-artist diversity penalty to reduce filter bubbles."""
    scored = [
        (song, *score_song(user_prefs, song, mode))
        for song in songs
    ]
    scored = [(s, sc, "; ".join(r)) for s, sc, r in scored]
    scored.sort(key=lambda x: x[1], reverse=True)

    results = []
    seen_artists: Dict[str, int] = {}
    for song, base_score, explanation in scored:
        artist = song.get("artist", "")
        repeat = seen_artists.get(artist, 0)
        adjusted = base_score - repeat * diversity_penalty
        results.append((song, adjusted, explanation))
        seen_artists[artist] = repeat + 1

    results.sort(key=lambda x: x[1], reverse=True)
    return results[:k]
