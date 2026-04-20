"""
Command line runner for the Music Recommender Simulation.

This file helps you quickly run and test your recommender.

You will implement the functions in recommender.py:
- load_songs
- score_song
- recommend_songs
"""

from .recommender import load_songs, recommend_songs


PROFILES = {
    "Chill Lofi": {
        "favorite_genre": "lofi",
        "favorite_mood": "chill",
        "target_energy": 0.40,
        "target_acousticness": 0.75,
        "target_tempo_norm": 0.22,  # ~78 BPM normalized (52–168 range)
    },
    "High-Energy Pop": {
        "favorite_genre": "pop",
        "favorite_mood": "happy",
        "target_energy": 0.90,
        "target_acousticness": 0.10,
        "target_tempo_norm": 0.69,  # ~132 BPM normalized
    },
    "Deep Intense Rock": {
        "favorite_genre": "rock",
        "favorite_mood": "aggressive",
        "target_energy": 0.92,
        "target_acousticness": 0.08,
        "target_tempo_norm": 0.86,  # ~152 BPM normalized
    },
    "Late Night R&B": {
        "favorite_genre": "r&b",
        "favorite_mood": "romantic",
        "target_energy": 0.61,
        "target_acousticness": 0.41,
        "target_tempo_norm": 0.31,  # ~88 BPM normalized
    },
    "Festival EDM": {
        "favorite_genre": "edm",
        "favorite_mood": "euphoric",
        "target_energy": 0.95,
        "target_acousticness": 0.03,
        "target_tempo_norm": 0.66,  # ~128 BPM normalized
    },
}


def print_recommendations(label: str, recommendations: list) -> None:
    print("\n" + "=" * 40)
    print(f"   {label.upper()}")
    print("=" * 40)
    for rank, (song, score, explanation) in enumerate(recommendations, start=1):
        print(f"\n#{rank}  {song['title']} by {song['artist']}")
        print(f"    Genre: {song['genre']}  |  Mood: {song['mood']}")
        print(f"    Score: {score:.2f} / 2.40")
        print(f"    Why:   {explanation}")
    print("\n" + "=" * 40)


def main() -> None:
    songs = load_songs("data/songs.csv")

    for label, user_prefs in PROFILES.items():
        recommendations = recommend_songs(user_prefs, songs, k=5)
        print_recommendations(label, recommendations)


if __name__ == "__main__":
    main()
