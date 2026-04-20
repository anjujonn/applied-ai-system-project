import csv
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass

@dataclass
class Song:
    """
    Represents a song and its attributes.
    Required by tests/test_recommender.py
    """
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

@dataclass
class UserProfile:
    """
    Represents a user's taste preferences.
    Required by tests/test_recommender.py
    """
    favorite_genre: str
    favorite_mood: str
    target_energy: float
    likes_acoustic: bool

class Recommender:
    """
    OOP implementation of the recommendation logic.
    Required by tests/test_recommender.py
    """
    def __init__(self, songs: List[Song]):
        self.songs = songs

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        # TODO: Implement recommendation logic
        return self.songs[:k]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        # TODO: Implement explanation logic
        return "Explanation placeholder"

def load_songs(csv_path: str) -> List[Dict]:
    """
    Loads songs from a CSV file.
    Required by src/main.py
    """
    songs = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            songs.append({
                "id":           int(row["id"]),
                "title":        row["title"],
                "artist":       row["artist"],
                "genre":        row["genre"],
                "mood":         row["mood"],
                "energy":       float(row["energy"]),
                "tempo_bpm":    int(row["tempo_bpm"]),
                "valence":      float(row["valence"]),
                "danceability": float(row["danceability"]),
                "acousticness": float(row["acousticness"]),
            })
    print(f"Loaded songs: {len(songs)}")
    return songs

def score_song(user_prefs: Dict, song: Dict) -> Tuple[float, List[str]]:
    """Return a (score, reasons) tuple rating how well a song matches the user's taste profile."""
    score = 0.0
    reasons = []

    # +1.0 for genre match
    if song["genre"] == user_prefs["favorite_genre"]:
        score += 1.0
        reasons.append("genre match")

    # +0.5 for mood match
    if song["mood"] == user_prefs["favorite_mood"]:
        score += 0.5
        reasons.append("mood match")

    # energy proximity: weight 0.40
    energy_score = (1 - abs(song["energy"] - user_prefs["target_energy"])) * 0.40
    score += energy_score
    reasons.append(f"energy score {energy_score:.2f}")

    # acousticness proximity: weight 0.40
    acousticness_score = (1 - abs(song["acousticness"] - user_prefs["target_acousticness"])) * 0.40
    score += acousticness_score
    reasons.append(f"acousticness score {acousticness_score:.2f}")

    # tempo proximity: normalize to 0-1 using dataset range (52–168 BPM), weight 0.20
    tempo_norm = (song["tempo_bpm"] - 52) / (168 - 52)
    tempo_score = (1 - abs(tempo_norm - user_prefs["target_tempo_norm"])) * 0.20
    score += tempo_score
    reasons.append(f"tempo score {tempo_score:.2f}")

    return score, reasons

def recommend_songs(user_prefs: Dict, songs: List[Dict], k: int = 5) -> List[Tuple[Dict, float, str]]:
    """Score every song in the catalog and return the top-k results sorted by score descending."""
    scored = [
        (song, *score_song(user_prefs, song))
        for song in songs
    ]
    ranked = sorted(scored, key=lambda x: x[1], reverse=True)
    return [(song, score, ", ".join(reasons)) for song, score, reasons in ranked[:k]]
