# AI Interactions Log

---

## Agentic Workflow — Additional Song Attributes (Stretch Feature)

**What task did you give the agent?**

Expand the `data/songs.csv` from 10 to 20 songs while also adding five new numerical attributes: `popularity` (integer 0–100), `release_decade` (integer: 2000, 2010, or 2020), `instrumentalness` (float 0–1), `speechiness` (float 0–1), and `loudness_norm` (float 0–1, normalized perceived loudness). The new songs needed to cover genres not present in the starter file, including EDM, folk, classical, hip-hop, R&B, metal, country, and latin.

**Prompts used:**

> "I have a songs.csv with 10 entries and these headers: id, title, artist, genre, mood, energy, tempo_bpm, valence, danceability, acousticness. I need to expand it to 20 songs and add 5 new meaningful attributes. Suggest attributes that capture dimensions of a song that aren't already covered by the existing features, then generate the 10 new rows as valid CSV with all 15 columns. Make sure genres like EDM, hip-hop, classical, metal, folk, country, R&B, and latin are represented."

**What did the agent generate or change?**

The agent suggested `popularity`, `release_decade`, `instrumentalness`, `speechiness`, and `loudness_norm` as additions. It explained that instrumentalness captures whether a track is mostly instrumental (useful for listeners who prefer no vocals), speechiness identifies spoken-word or rap-heavy tracks, and loudness_norm gives a perceived intensity dimension that overlaps with but is distinct from energy. It then generated 10 new song rows spanning the target genres with realistic values across all 15 columns.

The agent also proposed updates to `load_songs()` to cast the five new fields to their correct Python types (`int` for popularity and release_decade, `float` for the rest) with safe defaults in case old CSV rows lack the new columns.

**What did you verify or fix manually?**

- Confirmed that all 20 energy and acousticness values stayed in the 0.0–1.0 range and that tempo values were reasonable for their genre (e.g., classical at 58 BPM, EDM at 140 BPM).
- Verified that the `Song` dataclass in `recommender.py` listed all five new fields with default values so the existing test suite — which creates `Song` objects without the new fields — continued to pass.
- Cross-checked that `load_songs()` used `.get()` with defaults when reading new columns so loading the old 10-song CSV would not raise a `KeyError`.

---

## Design Pattern — Multiple Scoring Modes (Stretch Feature)

**Which design pattern did you use?**

A lightweight Strategy pattern implemented as a dictionary of weight dictionaries (`SCORING_MODES`) combined with a `mode` parameter threaded through `score_song()` and `recommend_songs()`. Each entry in `SCORING_MODES` is a named set of weights that controls how much importance the scoring function places on genre, mood, energy, valence, and the acoustic bonus.

**How did AI help you brainstorm or implement it?**

The initial design question was whether to use subclasses (a classic Strategy with a `Scorer` base class and `GenreFirstScorer`, `MoodFirstScorer` subclasses) or a simpler data-driven approach. After describing both options and the constraint that the code should stay readable for a beginner audience, the agent recommended the dictionary approach: it achieves the same goal of swappable behavior without requiring the reader to understand inheritance or method dispatch. It also noted that adding a fifth mode would only require one new dictionary entry rather than a new class and import.

**How does the pattern appear in your final code?**

In `src/recommender.py`, the constant `SCORING_MODES` holds four named weight sets. `score_song(user_prefs, song, mode="balanced")` looks up the matching entry with `SCORING_MODES.get(mode, SCORING_MODES["balanced"])` and uses those weights throughout the calculation. `recommend_songs()` accepts the same `mode` parameter and passes it straight through to `score_song()`. In `src/main.py`, the `MODES` list drives a loop that runs the same profile through all four modes so the output comparison is easy to read side by side.
