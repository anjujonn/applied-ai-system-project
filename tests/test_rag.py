"""
Reliability tests for the RAG-enhanced music recommender.
Tests cover: retrieval pipeline, context builder, confidence extraction,
and the fixed Recommender class. No network calls are made.
"""

import pytest

from src.recommender import Recommender, Song, UserProfile, recommend_songs, score_song
from src.rag_recommender import build_context, extract_confidence

# ── Shared test data ──────────────────────────────────────────────────────────

SAMPLE_SONGS = [
    {
        "id": 1, "title": "Pop Track", "artist": "Artist A",
        "genre": "pop", "mood": "happy",
        "energy": 0.80, "tempo_bpm": 120, "valence": 0.90,
        "danceability": 0.80, "acousticness": 0.20,
    },
    {
        "id": 2, "title": "Lofi Beat", "artist": "Artist B",
        "genre": "lofi", "mood": "chill",
        "energy": 0.40, "tempo_bpm": 80, "valence": 0.60,
        "danceability": 0.50, "acousticness": 0.90,
    },
    {
        "id": 3, "title": "Rock Anthem", "artist": "Artist C",
        "genre": "rock", "mood": "intense",
        "energy": 0.95, "tempo_bpm": 155, "valence": 0.30,
        "danceability": 0.60, "acousticness": 0.05,
    },
]

POP_USER = {
    "favorite_genre": "pop",
    "favorite_mood": "happy",
    "target_energy": 0.80,
    "target_acousticness": 0.20,
    "target_tempo_norm": (120 - 52) / (168 - 52),
}


# ── Retrieval pipeline tests ──────────────────────────────────────────────────

def test_recommend_songs_returns_correct_count():
    results = recommend_songs(POP_USER, SAMPLE_SONGS, k=2)
    assert len(results) == 2


def test_recommend_songs_sorted_by_score_descending():
    results = recommend_songs(POP_USER, SAMPLE_SONGS, k=3)
    scores = [score for _, score, _ in results]
    assert scores == sorted(scores, reverse=True)


def test_pop_user_gets_pop_song_as_top_result():
    results = recommend_songs(POP_USER, SAMPLE_SONGS, k=3)
    assert results[0][0]["genre"] == "pop"


def test_score_song_genre_match_adds_half_point():
    score, reasons = score_song(POP_USER, SAMPLE_SONGS[0])  # pop song
    assert score >= 0.5
    assert "genre match" in reasons


def test_score_song_no_match_stays_below_one():
    lofi_song = SAMPLE_SONGS[1]
    score, _ = score_song(POP_USER, lofi_song)
    # no genre or mood bonus, only numeric proximity
    assert score < 1.0


# ── Context builder tests ─────────────────────────────────────────────────────

def test_build_context_contains_all_song_titles():
    candidates = recommend_songs(POP_USER, SAMPLE_SONGS, k=3)
    context = build_context(POP_USER, candidates)
    for song, _, _ in candidates:
        assert song["title"] in context


def test_build_context_contains_user_genre_and_mood():
    candidates = recommend_songs(POP_USER, SAMPLE_SONGS, k=2)
    context = build_context(POP_USER, candidates)
    assert "pop" in context
    assert "happy" in context


def test_build_context_contains_relevance_scores():
    candidates = recommend_songs(POP_USER, SAMPLE_SONGS, k=2)
    context = build_context(POP_USER, candidates)
    assert "Relevance score" in context


# ── Confidence extraction tests ───────────────────────────────────────────────

def test_extract_confidence_parses_decimal_value():
    response = "These songs are perfect for you!\n\nConfidence: 0.87"
    assert extract_confidence(response) == pytest.approx(0.87)


def test_extract_confidence_returns_none_when_absent():
    response = "Here are your top picks for the evening!"
    assert extract_confidence(response) is None


def test_extract_confidence_clamps_values_above_one():
    response = "Confidence: 1.50"
    result = extract_confidence(response)
    assert result is not None
    assert result <= 1.0


def test_extract_confidence_case_insensitive():
    response = "CONFIDENCE: 0.92"
    assert extract_confidence(response) == pytest.approx(0.92)


# ── Fixed Recommender class tests ─────────────────────────────────────────────

def _make_song_objects():
    return [
        Song(id=s["id"], title=s["title"], artist=s["artist"],
             genre=s["genre"], mood=s["mood"], energy=s["energy"],
             tempo_bpm=s["tempo_bpm"], valence=s["valence"],
             danceability=s["danceability"], acousticness=s["acousticness"])
        for s in SAMPLE_SONGS
    ]


def test_recommender_class_ranks_pop_song_first():
    songs = _make_song_objects()
    user = UserProfile(
        favorite_genre="pop", favorite_mood="happy", target_energy=0.80,
        target_acousticness=0.20, target_tempo_norm=(120 - 52) / (168 - 52),
    )
    rec = Recommender(songs)
    results = rec.recommend(user, k=2)
    assert results[0].genre == "pop"
    assert results[0].mood == "happy"


def test_recommender_returns_song_objects_not_dicts():
    songs = _make_song_objects()
    user = UserProfile(favorite_genre="pop", favorite_mood="happy", target_energy=0.80)
    rec = Recommender(songs)
    results = rec.recommend(user, k=2)
    assert all(isinstance(s, Song) for s in results)


def test_explain_recommendation_returns_non_empty_string():
    songs = _make_song_objects()
    user = UserProfile(
        favorite_genre="pop", favorite_mood="happy", target_energy=0.80,
        target_acousticness=0.20, target_tempo_norm=(120 - 52) / (168 - 52),
    )
    rec = Recommender(songs)
    explanation = rec.explain_recommendation(user, songs[0])
    assert isinstance(explanation, str)
    assert explanation.strip() != ""
    assert "Score" in explanation
