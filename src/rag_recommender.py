import os
import re
from typing import Dict, List, Optional, Tuple

from google import genai

from .recommender import recommend_songs
from .logger import get_logger

logger = get_logger()


def build_context(user_prefs: Dict, candidates: List[Tuple[Dict, float, str]]) -> str:
    """Format retrieved top-k songs and user preferences into a Claude prompt context."""
    lines = [
        "User preferences:",
        f"  Genre: {user_prefs['favorite_genre']}",
        f"  Mood: {user_prefs['favorite_mood']}",
        f"  Energy: {user_prefs['target_energy']:.2f}",
        f"  Acousticness: {user_prefs['target_acousticness']:.2f}",
        "",
        "Retrieved top matching songs (scored by relevance):",
    ]
    for i, (song, score, reasons) in enumerate(candidates, 1):
        lines.append(
            f"\n{i}. \"{song['title']}\" by {song['artist']}"
        )
        lines.append(
            f"   Genre: {song['genre']} | Mood: {song['mood']} | "
            f"Energy: {song['energy']} | Acousticness: {song['acousticness']} | "
            f"Tempo: {song['tempo_bpm']} BPM"
        )
        lines.append(f"   Relevance score: {score:.2f}/2.40 — {reasons}")
    return "\n".join(lines)


def extract_confidence(response_text: str) -> Optional[float]:
    """Parse a 0-1 confidence score from Claude's response text."""
    match = re.search(r"confidence[:\s]+(\d+\.?\d*)", response_text, re.IGNORECASE)
    if match:
        val = float(match.group(1))
        return min(1.0, val)
    return None


def generate_fallback_narrative(
    user_prefs: Dict, candidates: List[Tuple[Dict, float, str]]
) -> Tuple[str, float]:
    """
    Rule-based narrative built entirely from the scoring data.
    Used when no API key is available — no network call required.
    """
    genre = user_prefs["favorite_genre"]
    mood = user_prefs["favorite_mood"]
    top3 = candidates[:3]
    confidence = round(top3[0][1] / 2.40, 2) if top3 else 0.0

    lines = [f"Here are your top picks for a **{mood} {genre}** vibe:\n"]

    for i, (song, score, reasons) in enumerate(top3, 1):
        pct = score / 2.40
        match_label = "Perfect match" if pct > 0.90 else "Great match" if pct > 0.75 else "Good match"

        detail_parts = []
        if "genre match" in reasons:
            detail_parts.append(f"it's {song['genre']}")
        if "mood match" in reasons:
            detail_parts.append(f"the {song['mood']} mood is spot on")
        if not detail_parts:
            detail_parts.append(f"its features closely match your profile")
        if song["acousticness"] > 0.6 and user_prefs["target_acousticness"] > 0.5:
            detail_parts.append("the warm acoustic texture fits perfectly")
        elif song["acousticness"] < 0.2 and user_prefs["target_acousticness"] < 0.2:
            detail_parts.append("the clean electronic production is right in your zone")
        detail_parts.append(f"{song['tempo_bpm']} BPM keeps the pace just where you want it")

        detail = ", and ".join(detail_parts[:3]).capitalize() + "."
        lines.append(f"**{i}. {song['title']}** by {song['artist']} — {match_label} ({score:.2f}/2.40)")
        lines.append(f"   {detail}")
        lines.append("")

    lines.append(f"Confidence: {confidence:.2f}")
    return "\n".join(lines), confidence


def rag_recommend(user_prefs: Dict, songs: List[Dict], k: int = 5) -> Dict:
    """
    Full RAG pipeline:
      1. Retrieve — score all songs, keep top-k
      2. Augment  — format retrieved songs + user prefs as context
      3. Generate — Claude API if available, rule-based fallback otherwise
    """
    candidates = recommend_songs(user_prefs, songs, k=k)
    context = build_context(user_prefs, candidates)
    logger.info(
        f"Retrieval: {k} candidates for "
        f"genre={user_prefs['favorite_genre']}, mood={user_prefs['favorite_mood']}"
    )

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        logger.info("No GEMINI_API_KEY — using rule-based fallback narrative")
        narrative, confidence = generate_fallback_narrative(user_prefs, candidates)
        return {
            "candidates": candidates,
            "context": context,
            "ai_response": narrative,
            "confidence": confidence,
            "source": "rule-based fallback",
            "success": True,
        }

    prompt = f"""You are a friendly music recommendation assistant.
Based on the user's taste profile and the retrieved song matches below, write a short personalized recommendation.

{context}

Instructions:
- Recommend the top 3 songs from the retrieved list (use their exact titles)
- For each song, explain in 1-2 sentences why it suits the user's taste
- End your response with exactly this line: Confidence: X.XX
  (a number from 0.00 to 1.00 reflecting how well the top songs fit)
- Keep the tone warm and enthusiastic"""

    try:
        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt,
        )
        ai_response = response.text
        confidence = extract_confidence(ai_response)
        logger.info(f"Gemini generation complete. Confidence={confidence}")
        return {
            "candidates": candidates,
            "context": context,
            "ai_response": ai_response,
            "confidence": confidence,
            "source": "gemini-2.0-flash",
            "success": True,
        }
    except Exception as e:
        logger.error(f"Gemini API error: {e} — falling back to rule-based narrative")
        narrative, confidence = generate_fallback_narrative(user_prefs, candidates)
        return {
            "candidates": candidates,
            "context": context,
            "ai_response": narrative,
            "confidence": confidence,
            "source": "rule-based fallback",
            "success": True,
        }
