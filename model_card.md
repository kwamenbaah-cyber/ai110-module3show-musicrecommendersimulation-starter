# Model Card: VibeFinder 1.0

## 1. Model Name

**VibeFinder 1.0** — a content-based music recommender simulation built for an introductory AI course.

---

## 2. Intended Use

VibeFinder is designed for a classroom setting to simulate and explain how content-based music recommendation works. It takes a listener's stated preferences (favorite genre, mood, target energy level, and whether they like acoustic music) and returns a ranked list of songs from a small catalog with plain-language explanations for every suggestion.

It is not intended to be deployed in a real streaming product. It makes several assumptions that would break in the real world: that users know and can articulate their preferences in advance, that genre labels are consistent and exact, and that 20 songs is a meaningful catalog. This is an educational exploration tool, not a production system.

---

## 3. How the Model Works

Imagine you walk into a music store and hand the staff a note that says: "I want something pop, happy, and high energy." The clerk goes through every album in the store and gives each one a score. They award two points if it matches your genre, one point if the mood label fits, and they measure how close the energy feels to what you described — a song that is slightly more energetic than you wanted scores almost as high as a perfect match, while a song that is the opposite gets almost nothing. They also check whether you like acoustic sounds and reward that if applicable.

Once every album has a score, the clerk sorts them from highest to lowest and hands you the top five. If two albums happen to be by the same artist, the second one gets a small penalty so you do not end up with three songs from the same person.

VibeFinder does exactly this, in Python, for 20 songs. The user's preferences are compared against five numerical and two categorical features of each song. No listening history, no other users, no machine learning weights that were trained on data — just a weighted math formula that rewards closeness to what you said you wanted.

The system also supports four ranking modes that shift which feature is treated as most important: balanced, genre-first, mood-first, and energy-focused. This lets users see how the same catalog produces very different lists depending on what the algorithm cares about most.

---

## 4. Data

The catalog contains 20 songs stored in `data/songs.csv`. Each song has 15 attributes:

- **Categorical:** genre (10 unique genres), mood (7 unique moods), artist (18 unique artists), title
- **Numerical (0–1 scale):** energy, valence, danceability, acousticness, instrumentalness, speechiness, loudness_norm
- **Other numerical:** tempo_bpm (58–168 BPM), popularity (46–85 out of 100), release_decade (2000, 2010, 2020)

The genres represented are: pop, lofi, rock, EDM, ambient, jazz, synthwave, indie pop, folk, classical, hip-hop, R&B, metal, country, and latin. The moods are: happy, chill, intense, moody, relaxed, and focused.

The dataset was built for this simulation and does not reflect any real streaming platform's catalog. Several genres appear only once or twice, which limits the system's ability to produce diverse recommendations for listeners in those genres. There are no songs from before 2000, so users with a preference for older music have no matching catalog entries.

---

## 5. Strengths

The system works best for genres that have multiple representatives in the catalog. Listeners with a lofi or pop preference see genuinely varied top-five lists because there are enough matching songs to distinguish between them on energy and mood. The explanations the system produces are completely transparent — every point in a song's score is described in plain language, which is something real recommenders almost never offer.

The proximity-based energy scoring is also an improvement over a simple "higher is better" rule. For a user who wants moderate energy (0.5), the system correctly identifies soft songs and loud songs as equally bad, rather than always recommending the most intense track.

---

## 6. Limitations and Bias

**Genre label mismatch.** The genre field is an exact string comparison. A user who types "pop" will never receive a genre-match bonus for songs labeled "indie pop" even though those two genres overlap heavily. This creates a hard boundary between categories that human ears do not perceive.

**Small catalog filter bubble.** With only 20 songs, users in underrepresented genres (hip-hop, metal, country, classical) will almost always see off-genre songs filling the bottom half of their recommendations. The system never suggests that they might enjoy adjacent genres, so it reinforces rather than expands taste.

**Genre dominance.** In balanced mode, a genre match awards 2.0 points — twice the mood bonus and twice the maximum energy bonus. This means a mediocre pop song will always outrank an excellent R&B song for a pop listener, even if the R&B track is a better fit on every other dimension. The scoring formula was designed to be simple and explainable, but that simplicity creates a strong structural bias toward whichever genre is in the catalog in the largest numbers.

**No temporal or popularity signal.** The scoring function does not use popularity, release decade, instrumentalness, or speechiness in the default balanced mode. Those attributes exist in the dataset and could meaningfully improve results (for example, a user who prefers recent music could receive a recency bonus), but the current formula leaves them unused.

**No user feedback loop.** VibeFinder cannot learn. If a user skips every recommendation it makes, the weights never change. Real recommenders adjust continuously based on what gets played, liked, or skipped.

---

## 7. Evaluation

Five distinct user profiles were tested across all four ranking modes:

**Happy Pop Fan** (genre: pop, mood: happy, energy: 0.80): The top result was consistently Sunrise City, which matched on genre, mood, and was within 0.02 of the target energy. This felt correct. Gym Hero appeared second in balanced and genre-first modes even though its mood is "intense" rather than "happy" — it earned this spot through a genre match alone, which was a surprising edge case that revealed how much genre dominates.

**Chill Lofi Listener** (genre: lofi, mood: chill, energy: 0.38, likes_acoustic: True): The top two results were Library Rain and Midnight Coding, both lofi and chill. Without the diversity penalty, LoRoom would have placed both Midnight Coding and Focus Flow in the top three. The penalty correctly pushed Focus Flow down and surfaced Spacewalk Thoughts (ambient, chill) as a cross-genre alternative, which felt like a more useful list.

**High-Energy EDM Head** (genre: EDM, mood: intense, energy: 0.95): Bass Drop Kingdom scored almost a full point higher than the second-place song because it was the only EDM track in the catalog. Positions 2–5 were all non-EDM songs that shared the intense mood or high energy. The EDM listener with this profile would likely be disappointed in practice — one matching genre song followed by four rock/hip-hop/metal alternatives is a thin catalog.

**Moody Synthwave Night** (genre: synthwave, mood: moody, energy: 0.72): The top two slots were the only two synthwave songs (Neon Prophecy and Night Drive Loop). Position 3 was After Hours Blue (jazz, moody) — a cross-genre pick that matched on mood, which showed the system doing something reasonable even outside the primary genre.

**Acoustic Folk Wanderer** (genre: folk, mood: relaxed, energy: 0.32, likes_acoustic: True): Sunday Acoustic (the only folk track) dominated at 4.96. Positions 2–3 were Coffee Shop Stories (jazz) and Open Road Hymn (country), both relaxed and acoustic — this felt like a genuinely reasonable cross-genre recommendation.

**Profile comparison:** The EDM Head and Folk Wanderer profiles expose the catalog's thinness most clearly — a single song captures the #1 slot with a large score gap to #2. By contrast, the Lofi Listener profile produces a much tighter top-five because three lofi songs compete with each other on finer details like energy and valence proximity. The more songs exist per genre, the more useful the secondary scoring dimensions become.

---

## 8. Future Work

1. **Soft genre matching.** Replace the binary genre-match bonus with a genre-similarity matrix so that "indie pop" scores partial points for a "pop" listener and "R&B" scores partial points for a "soul" listener.

2. **Adaptive weights from implicit feedback.** Track whether recommended songs get "liked" and use that signal to slowly increase the weight on features that predicted liked songs and decrease the weight on features that predicted skips.

3. **Larger, more balanced catalog.** With 20 songs and 15+ genres, most genres have one or two entries. Expanding to 200+ songs with proportional genre coverage would allow the proximity-based energy and valence scoring to actually differentiate within genres rather than defaulting to cross-genre picks.

4. **Use all available features.** The dataset includes popularity, release decade, instrumentalness, and speechiness. Adding a recency preference field to the user profile and incorporating these features into the score would surface patterns the current formula cannot detect.

5. **Collaborative filtering hybrid.** The biggest real-world recommenders combine content-based and collaborative signals. Even a toy version that logs "users who liked X also liked Y" would demonstrate why Netflix and Spotify can surface songs you would never have described in a preference form.

---

## 9. Personal Reflection

Building VibeFinder clarified something I had never thought about carefully before: the gap between what an algorithm *maximizes* and what a listener *actually wants* is much wider than it looks. When I tested the Happy Pop Fan profile, the system kept surfacing Gym Hero at position 2 even though its mood is "intense" — not happy. The genre match was worth enough points to override the mood mismatch, and on paper the math was correct. But intuitively it felt wrong. That tension — the formula does exactly what you told it to do, and still produces a result you would not want — is probably the central challenge of real-world recommendation system design.

Using AI tools throughout the process was useful for generating the expanded song catalog quickly and for sanity-checking the scoring formula's math, but I had to manually verify every choice. The proximity formula for energy (`1 − |song_energy − target_energy|`) was suggested as a starting point, but I had to think through what it actually produces at the extremes and confirm it rewarded closeness rather than magnitude. The diversity penalty value (0.4) came from trial and error rather than any principled derivation — a real system would tune this on held-out data, but in this simulation it was a judgment call. That experience reinforced that AI tooling accelerates the build but the decisions still require a human to reason about what "correct" actually means.

The most unexpected insight was how much the score range depends on catalog size. A lone folk song can score 4.96 while the lofi catalog produces a tight cluster between 4.95 and 2.79 — not because folk is "better" but simply because there is less competition within the genre. Scale changes everything about how these numbers should be interpreted.
