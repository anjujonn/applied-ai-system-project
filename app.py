from pathlib import Path

import streamlit as st
from dotenv import load_dotenv

load_dotenv()

from src.logger import get_logger
from src.rag_recommender import build_context, rag_recommend
from src.recommender import load_songs, recommend_songs

logger = get_logger()

GENRES = [
    "pop", "lofi", "rock", "ambient", "jazz", "synthwave", "indie pop",
    "hip-hop", "folk", "metal", "edm", "classical", "country", "reggae",
    "darkwave", "world",
]
MOODS = [
    "happy", "chill", "intense", "relaxed", "focused", "moody", "aggressive",
    "euphoric", "melancholic", "peaceful", "nostalgic", "romantic",
    "spiritual", "brooding", "laid-back",
]
PRESETS = {
    "Custom": None,
    "Chill Lofi":       {"genre": "lofi",       "mood": "chill",      "energy": 0.40, "acousticness": 0.75, "tempo": 78},
    "High-Energy Pop":  {"genre": "pop",        "mood": "happy",      "energy": 0.90, "acousticness": 0.10, "tempo": 132},
    "Deep Intense Rock":{"genre": "rock",       "mood": "intense",    "energy": 0.92, "acousticness": 0.08, "tempo": 152},
    "Late Night R&B":   {"genre": "r&b",        "mood": "romantic",   "energy": 0.61, "acousticness": 0.41, "tempo": 88},
    "Festival EDM":     {"genre": "edm",        "mood": "euphoric",   "energy": 0.95, "acousticness": 0.03, "tempo": 128},
}


@st.cache_data
def load_catalog():
    csv_path = Path(__file__).parent / "data" / "songs.csv"
    return load_songs(str(csv_path))


def main():
    st.set_page_config(page_title="AI Music Recommender", page_icon="🎵", layout="wide")
    st.title("🎵 AI Music Recommender")
    st.caption(
        "**RAG-powered** — your top song candidates are retrieved by a scoring engine, "
        "then Claude AI reads them and writes a personalized recommendation just for you."
    )

    songs = load_catalog()

    # ── Sidebar ──────────────────────────────────────────────────────────────
    with st.sidebar:
        st.header("Your Taste Profile")

        preset_name = st.selectbox("Quick Profile", list(PRESETS.keys()))
        p = PRESETS[preset_name]

        st.divider()

        genre = st.selectbox(
            "Genre", GENRES,
            index=GENRES.index(p["genre"]) if p and p["genre"] in GENRES else 0,
        )
        mood = st.selectbox(
            "Mood", MOODS,
            index=MOODS.index(p["mood"]) if p and p["mood"] in MOODS else 0,
        )
        energy = st.slider("Energy", 0.0, 1.0, p["energy"] if p else 0.70, 0.05)
        acousticness = st.slider("Acousticness", 0.0, 1.0, p["acousticness"] if p else 0.30, 0.05)
        tempo = st.slider("Tempo (BPM)", 52, 168, p["tempo"] if p else 110, 4)
        k = st.slider("Number of picks", 3, 8, 5)
        use_ai = st.checkbox("Generate AI narrative", value=True)

        st.divider()
        submit = st.button("Get Recommendations", type="primary", use_container_width=True)

    if not submit:
        st.info("Set your taste profile in the sidebar, then click **Get Recommendations**.")
        return

    tempo_norm = (tempo - 52) / (168 - 52)
    user_prefs = {
        "favorite_genre": genre,
        "favorite_mood": mood,
        "target_energy": energy,
        "target_acousticness": acousticness,
        "target_tempo_norm": tempo_norm,
    }
    logger.info(f"Request: genre={genre}, mood={mood}, energy={energy:.2f}, k={k}, ai={use_ai}")

    # ── Retrieve (and optionally generate) ───────────────────────────────────
    if use_ai:
        with st.spinner("Retrieving songs and generating AI recommendation..."):
            result = rag_recommend(user_prefs, songs, k=k)
        candidates = result["candidates"]
    else:
        with st.spinner("Scoring songs..."):
            candidates = recommend_songs(user_prefs, songs, k=k)
        result = {
            "candidates": candidates,
            "context": build_context(user_prefs, candidates),
            "ai_response": None,
            "confidence": None,
            "success": True,
        }

    # ── Tabs ─────────────────────────────────────────────────────────────────
    tab1, tab2, tab3 = st.tabs(["📊 Scored Results", "🤖 AI Recommendation", "🔍 RAG Context"])

    with tab1:
        st.subheader("Top Matches by Score")
        for rank, (song, score, reasons) in enumerate(candidates, 1):
            with st.container():
                col_info, col_score = st.columns([3, 1])
                with col_info:
                    st.markdown(f"**#{rank} — {song['title']}** by *{song['artist']}*")
                    st.caption(
                        f"Genre: {song['genre']} · Mood: {song['mood']} · "
                        f"Energy: {song['energy']} · Tempo: {song['tempo_bpm']} BPM"
                    )
                    st.caption(f"Why: {reasons}")
                with col_score:
                    st.metric("Score", f"{score:.2f} / 2.40")
                    st.progress(score / 2.40)
            st.divider()

    with tab2:
        if result.get("ai_response"):
            source = result.get("source", "")
            if source == "rule-based fallback":
                st.caption("Generated from scoring data (no API key needed)")
            else:
                st.caption("Generated by Gemini AI")
            conf = result.get("confidence")
            if conf is not None:
                col_conf, _ = st.columns([1, 3])
                with col_conf:
                    st.metric("AI Confidence", f"{conf:.2f} / 1.00")
                st.progress(conf)
                st.caption("Confidence reflects how closely the top-scored songs match your preferences.")
                st.divider()
            st.markdown(result["ai_response"])
        else:
            st.info("Uncheck the checkbox and re-submit if you only want scored results.")

    with tab3:
        st.subheader("What was retrieved and sent to Claude")
        st.caption(
            "This is the RAG step made visible: the scoring engine retrieves the best-matching songs, "
            "and this exact text becomes the context window Claude reads before writing its response."
        )
        st.code(result.get("context", "No context generated."), language="text")


if __name__ == "__main__":
    main()
