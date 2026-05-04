# AI Music Recommender — RAG Edition

## Video Link
`https://www.loom.com/share/9845bad6881345aa9901e22fb1a06453`


## Original Project (Module 3)

So, **SingYourSong 1.0** was originally built in Module 3 as a rule-based music recommender that scores every song in a 20-song CSV catalog against a user's taste profile (the specific metrics I focused on were preferred genre, mood, energy level, acousticness, and tempo). It ranked songs by a weighted distance formula and returned the top-k results with plain-text explanations. The original system had no AI language model and no external API. It was a pretty plain ranking system.

---

## Title and Summary

**AI Music Recommender — RAG Edition** is a personalized music recommendation app that combines a weighted scoring engine with Gemini AI to explain why a song fits user's taste, not just that it does. It uses RAG: the scoring engine retrieves the best-matching songs from a catalog, and Gemini reads those results to write a natural-language recommendation grounded in real data. This matters because it demonstrates how RAG prevents AI hallucination -> the model can only recommend songs that were actually retrieved, making the output transparent and trustworthy.

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                        Streamlit UI (app.py)                 │
│    Sidebar: Genre · Mood · Energy · Acousticness · Tempo    │
└───────────────────────┬─────────────────────────────────────┘
                        │ user_prefs dict
                        ▼
┌─────────────────────────────────────────────────────────────┐
│              Scoring Engine  (src/recommender.py)            │
│   score_song() × 20 songs → sorted top-k candidates         │
│   Features: genre match, mood match, energy, acousticness,  │
│             tempo proximity  (max score = 2.40)              │
└────────────┬──────────────────────────┬──────────────────────┘
             │                          │
    ◄── songs.csv                  top-k candidates
             │                          │
             │                          ▼
             │          ┌─────────────────────────────────┐
             │          │  Context Builder                 │
             │          │  (src/rag_recommender.py)        │
             │          │  Formats user prefs + candidates │
             │          │  into a structured prompt        │
             │          └──────────────┬──────────────────┘
             │                         │ prompt + context
             │                         ▼
             │          ┌─────────────────────────────────┐
             │          │  Gemini API  (gemini-2.0-flash)  │
             │          │  Reads retrieved songs           │
             │          │  Generates narrative + confidence│
             │          └──────────────┬──────────────────┘
             │                         │ ai_response
             │                         ▼
             │          ┌─────────────────────────────────┐
             │          │  Output (3 tabs in Streamlit)    │
             │          │  📊 Scored Results               │
             │          │  🤖 AI Recommendation            │
             │          │  🔍 RAG Context (for inspection) │
             │          └─────────────────────────────────┘
             │
             ▼
┌───────────────────────┐
│  Logger               │
│  logs/recommender.log │
│  Tracks every request │
│  and API call/error   │
└───────────────────────┘
```

The system has four main components: the **Scoring Engine** retrieves the top-k songs from `songs.csv` using weighted feature matching; the **Context Builder** formats those results into a structured prompt; **Gemini AI** reads the prompt and generates a personalized narrative with a confidence score; and the **Logger** records every request and API call to `logs/recommender.log`. The RAG Context tab in the UI makes the retrieval step visible. You can actually see exactly what Gemini was given before it generated its response.

---

## Setup Instructions

**Prerequisites:** Python 3.10+, a free [Gemini API key](https://aistudio.google.com) (no credit card required)

```bash
# 1. Navigate to the project folder
cd ai110-module3show-musicrecommendersimulation-starter

# 2. Create and activate a virtual environment
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # Mac / Linux

# 3. Install dependencies
pip install -r requirements.txt

# 4. Add your Gemini API key
#    Open .env and replace "your_api_key_here" with your key from aistudio.google.com

# 5. Launch the Streamlit app
streamlit run app.py

# 6. (Optional) Run without the UI, command-line scoring only
python -m src.main

# 7. Run all tests
pytest
```

Select a preset profile (or customize), then click **Get Recommendations**.

---

## Sample Interactions

### Example 1 — Chill Lofi

**Input:** Genre: lofi · Mood: chill · Energy: 0.40 · Acousticness: 0.75 · Tempo: 78 BPM

**Scored Results tab:**
```
#1  Midnight Coding  by  LoRoom          Score: 2.37 / 2.40
    Genre: lofi · Mood: chill · Energy: 0.42 · Tempo: 78 BPM
    Why: genre match, mood match, energy score 0.78, acousticness score 0.38, tempo score 0.20

#2  Library Rain     by  Paper Lanterns  Score: 2.31 / 2.40
    Genre: lofi · Mood: chill · Energy: 0.35 · Tempo: 72 BPM
    Why: genre match, mood match, energy score 0.76, acousticness score 0.36, tempo score 0.19
```

**AI Recommendation tab:**
> Your chill lofi vibe is perfectly matched! **Midnight Coding** by LoRoom should be your first listen — its 78 BPM groove and dreamy acousticness align almost exactly with your target. **Library Rain** by Paper Lanterns is equally mesmerizing, with delicate piano textures ideal for late-night study. Rounding out the trio, **Focus Flow** by LoRoom brings that same quiet focus energy.
>
> Confidence: 0.95

---

### Example 2 — Festival EDM

**Input:** Genre: edm · Mood: euphoric · Energy: 0.95 · Acousticness: 0.03 · Tempo: 128 BPM

**Scored Results tab:**
```
#1  Neon Carnival  by  Drop District   Score: 2.40 / 2.40
    Genre: edm · Mood: euphoric · Energy: 0.95 · Tempo: 128 BPM
    Why: genre match, mood match, energy score 0.80, acousticness score 0.40, tempo score 0.20
```
*(Perfect score — the catalog has exactly one EDM/euphoric song, and it matches on every feature.)*

**AI Recommendation tab:**
> Drop everything — **Neon Carnival** by Drop District is a perfect 2.40/2.40 match for your profile! The 128 BPM pulse and wall-of-synth energy were practically built for a festival crowd. **Gym Hero** is the next best pick if you need extra intensity, and **Concrete Jungle** rounds out a high-energy set.
>
> Confidence: 0.98

---

### Example 3 — No API key (rule-based fallback)

**Input:** Genre: lofi · Mood: chill · Energy: 0.40 · Acousticness: 0.75 · Tempo: 78 BPM (no `GEMINI_API_KEY` set)

**AI Recommendation tab:**
> Here are your top picks for a **chill lofi** vibe:
>
> **1. Midnight Coding** by LoRoom — Perfect match (2.37/2.40)
> It's lofi, and the chill mood is spot on, 78 BPM keeps the pace just where you want it.
>
> Confidence: 0.99

The app never crashes and the AI tab always produces output whether or not the API key is set.

---

## Design Decisions

**Why RAG over fine-tuning or an agentic loop?**
The catalog is small (20 songs) and the scoring logic is already a well-defined retrieval function. RAG lets the existing scorer do what it does well - precise numeric matching - and delegates the explanation step to Gemini. Fine-tuning would require labeled training data we don't have. An agentic loop would add latency without meaningful benefit for a single-turn recommendation.

**Why keep the weighted scorer as the retriever rather than letting Gemini pick songs directly?**
Gemini doesn't have access to the CSV. Letting the scorer narrow to 5 candidates first is cheaper, faster, and more reliable. This also prevents hallucination since Gemini can only discuss songs that were actually retrieved -> short and sweet!

**Why `gemini-2.0-flash` instead of a larger model?**
Speed and cost. Recommendations are short (under 600 tokens actually) and Gemini Flash handles them well at the lowest latency. It's also on the free tier, making the project fully reproducible without any billing setup! Basically it's great for something short and sweet without any complication

**Trade-off: catalog size.**
With 20 songs, some profiles (like r&b or world) have no exact genre match, so the top result is always a numeric-proximity pick rather than a true genre match. A real system would need a much larger catalog.

---

## Testing Summary

All **17 tests pass** (`pytest tests/`):

| Test file | Tests | What's covered |
|---|---|---|
| `tests/test_rag.py` | 15 | Retrieval count/order, score_song math, context builder content, confidence regex parsing, clamping, Recommender class correctness |
| `tests/test_recommender.py` | 2 | Original class tests (now passing after fixing the stub) |

**What worked well:** The scoring tests are deterministic — given the same songs and user profile, the output is always identical, making assertions straightforward. Confidence extraction with `re.search` is robust to minor variations in Gemini's phrasing.

**What didn't work at first:** The original `Recommender.recommend()` was a stub returning `self.songs[:k]` (first k, unsorted), so the original tests were passing for the wrong reasons. Fixing the class to use `score_song()` made both old and new tests actually verify the logic

**What I learned:** Deterministic components (the scorer) are easy to test with confidence. Non-deterministic components (which is just the AI narrative) need indirect testing, where you need to be checking that the right context was built and passed, rather than checking the exact output.

---

## Reflection

This project taught me that AI systems work best when responsibilities are clearly split: let precise algorithms do retrieval and let language models do generation. Trying to make the LLM do both leads to hallucination and wasted tokens. It also reminded me again how a test that passing doesn't mean the code is correct. The original Recommender stub proved that. You have to test the right thing, not just test that something runs.

**Limitations and bias:** The 20-song catalog reflects one developer's taste. Genres like r&b, world, and reggae each have only one song, so those users always get imprecise results, unfortunately :/. Valence and danceability are unused features, so two very different-sounding songs can score identically. I think for another time ensuring that all features are being considered could be a good idea depending on their effectiveness.

**Potential misuse:** The narrative generator could be used to produce fake personalized marketing copy at scale. The RAG constraint helps, where Gemini can only discuss retrieved songs, but prompt injection could still be a risk if user input were passed directly into the prompt without sanitization

**What surprised me:** Gemini's tone shifted naturally with the genre (calm for lofi, high-energy for EDM) without any explicit instruction!

**AI collaboration:** One helpful suggestion was surfacing the RAG context as a third tab in the UI, which made the retrieval step visible and the system more educational. One flawed suggestion was an early confidence regex that matched energy scores earlier in the response instead of the intended confidence value. It had to be anchored to the word "confidence" to work correctly I guess...
