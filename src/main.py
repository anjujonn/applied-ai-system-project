"""
Command line runner for the Music Recommender Simulation.

This file helps you quickly run and test your recommender.

You will implement the functions in recommender.py:
- load_songs
- score_song
- recommend_songs
"""

from .recommender import load_songs, recommend_songs


def main() -> None:
    songs = load_songs("data/songs.csv") 

    user_prefs = {
        "favorite_genre": "lofi",
        "favorite_mood": "chill",

        "target_energy": 0.40,
        "target_acousticness": 0.60,
        "target_tempo_norm": 0.22,

        "weights": {
            "energy":       0.40,
            "acousticness": 0.40,
            "tempo_norm":   0.20,
        },
    }

    recommendations = recommend_songs(user_prefs, songs, k=5)

    print("\n" + "=" * 40)
    print("   TOP RECOMMENDATIONS FOR YOU")
    print("=" * 40)

    for rank, (song, score, explanation) in enumerate(recommendations, start=1):
        print(f"\n#{rank}  {song['title']} by {song['artist']}")
        print(f"    Genre: {song['genre']}  |  Mood: {song['mood']}")
        print(f"    Score: {score:.2f} / 2.00")
        print(f"    Why:   {explanation}")

    print("\n" + "=" * 40)


if __name__ == "__main__":
    main()
