# Music Recommender Simulation

## Project Summary

This project simulates how a streaming platform decides which songs to play next. It builds a content-based recommendation engine in Python that reads a catalog of 20 songs from a CSV file, scores each song against a user's taste profile, and returns a ranked list of suggestions with plain-language explanations for every pick. The system supports five distinct user profiles and four different ranking modes so you can see how shifting the weight on any single feature changes the output.

---

## How The System Works

Real-world recommenders like Spotify and YouTube Music rely on two main techniques. **Collaborative filtering** identifies users who listen to the same things you do and surfaces what they liked next — it works at scale but needs massive amounts of behavioral data. **Content-based filtering** ignores other users entirely and instead compares the properties of songs (genre, tempo, energy, mood) directly to the listener's stated preferences. This project uses content-based filtering because it is transparent, explainable, and does not require any listening history.

### Features used per song

| Feature | Type | Description |
|---|---|---|
| genre | text | Musical category (pop, lofi, rock, EDM, etc.) |
| mood | text | Emotional tone (happy, chill, intense, moody, relaxed, focused) |
| energy | float 0–1 | How driving or subdued the track feels |
| valence | float 0–1 | Musical positivity; 1.0 = very upbeat |
| danceability | float 0–1 | How suited the track is to dancing |
| acousticness | float 0–1 | Presence of acoustic instruments |
| popularity | int 0–100 | Approximate stream count ranking |
| release_decade | int | Decade the song was released (e.g. 2020) |
| instrumentalness | float 0–1 | How free of vocals the track is |
| speechiness | float 0–1 | Presence of spoken words |
| loudness_norm | float 0–1 | Normalized perceived loudness |

### User profile fields

Each listener profile stores `genre`, `mood`, `energy`, `valence`, and `likes_acoustic`. These are the preferences the scoring function compares against every song in the catalog.

### Algorithm Recipe (how scores are computed)

For each song the scorer awards points in four categories and adds them up:

1. **Genre match** — +2.0 points (or up to +4.0 in genre-first mode) when the song's genre matches the listener's favorite.
2. **Mood match** — +1.0 points (up to +3.0 in mood-first mode) when the mood label matches.
3. **Energy proximity** — up to +1.0 points based on how close the song's energy is to the listener's target. The formula is `weight × (1 − |song_energy − target_energy|)`, which rewards songs that are near the target rather than always preferring high or low values.
4. **Valence proximity** — up to +0.5 points using the same proximity formula on the valence (positivity) dimension.
5. **Acoustic bonus** — +0.5 points if the listener likes acoustic music and the song scores above 0.6 on acousticness.

After all songs are scored, a **diversity penalty** of −0.4 points is subtracted for each additional song by the same artist already in the results. This prevents one artist from dominating the top five.

### Ranking

`recommend_songs()` loops through all 20 songs, computes a score and a set of reasons for each, applies the diversity penalty, and returns the top `k` results sorted highest to lowest. `sorted()` is used rather than `.sort()` because it returns a new list and leaves the original catalog unchanged.

### Potential bias I expected going in

Genre gets twice as many points as mood, so the system will over-reward an exact genre match and may bury a song that nails the energy and mood but has a slightly different genre label. The small catalog (20 songs) also means certain genres appear only once, so users who prefer hip-hop, metal, or country will usually see off-genre songs filling the bottom of their list.

---

## Getting Started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate      # Mac / Linux
# .venv\Scripts\activate       # Windows

pip install -r requirements.txt
```

### Run the recommender

```bash
python -m src.main
```

### Run tests

```bash
pytest
```

---

## Sample Recommendation Output

### Happy Pop Fan (balanced mode, top 5)

```
==============================================================
  Happy Pop Fan  [mode: balanced]
==============================================================
╭─────┬──────────────────┬───────────────┬─────────┬────────────────────────────────────────────╮
│   # │ Title            │ Artist        │   Score │ Reasons                                    │
├─────┼──────────────────┼───────────────┼─────────┼────────────────────────────────────────────┤
│   1 │ Sunrise City     │ Neon Echo     │    4.47 │ genre match: pop (+2.0); mood match: happy │
│     │                  │               │         │ (+1.0); energy proximity (+0.98); valence  │
│     │                  │               │         │ proximity (+0.49)                          │
│   2 │ Gym Hero         │ Max Pulse     │    3.33 │ genre match: pop (+2.0); energy proximity  │
│     │                  │               │         │ (+0.87); valence proximity (+0.46)         │
│   3 │ Rooftop Lights   │ Indigo Parade │    2.44 │ mood match: happy (+1.0); energy proximity │
│     │                  │               │         │ (+0.96); valence proximity (+0.48)         │
│   4 │ Fuego Samba      │ Los Vibrantes │    2.42 │ mood match: happy (+1.0); energy proximity │
│     │                  │               │         │ (+0.92); valence proximity (+0.49)         │
│   5 │ Smooth Like That │ Vance Rhythm  │    2.33 │ mood match: happy (+1.0); energy proximity │
│     │                  │               │         │ (+0.85); valence proximity (+0.48)         │
╰─────┴──────────────────┴───────────────┴─────────┴────────────────────────────────────────────╯
```

### Chill Lofi Listener (balanced mode, top 5)

```
==============================================================
  Chill Lofi Listener  [mode: balanced]
==============================================================
╭─────┬────────────────────┬────────────────┬─────────┬───────────────────────────────────────────────╮
│   # │ Title              │ Artist         │   Score │ Reasons                                       │
├─────┼────────────────────┼────────────────┼─────────┼───────────────────────────────────────────────┤
│   1 │ Library Rain       │ Paper Lanterns │    4.96 │ genre match: lofi (+2.0); mood match: chill   │
│     │                    │                │         │ (+1.0); energy proximity (+0.97); valence     │
│     │                    │                │         │ proximity (+0.49); acoustic preference (+0.5) │
│   2 │ Midnight Coding    │ LoRoom         │    4.95 │ genre match: lofi (+2.0); mood match: chill   │
│     │                    │                │         │ (+1.0); energy proximity (+0.96); valence     │
│     │                    │                │         │ proximity (+0.49); acoustic preference (+0.5) │
│   3 │ Focus Flow         │ LoRoom         │    3.58 │ genre match: lofi (+2.0); energy proximity    │
│     │                    │                │         │ (+0.98); valence proximity (+0.49); acoustic  │
│     │                    │                │         │ preference (+0.5)                             │
│   4 │ Spacewalk Thoughts │ Orbit Bloom    │    2.86 │ mood match: chill (+1.0); energy proximity    │
│     │                    │                │         │ (+0.90); valence proximity (+0.46); acoustic  │
│     │                    │                │         │ preference (+0.5)                             │
│   5 │ Raindrop Sonata    │ Elara Keys     │    2.79 │ mood match: chill (+1.0); energy proximity    │
│     │                    │                │         │ (+0.84); valence proximity (+0.45); acoustic  │
│     │                    │                │         │ preference (+0.5)                             │
╰─────┴────────────────────┴────────────────┴─────────┴───────────────────────────────────────────────╯
```

### High-Energy EDM Head (balanced mode, top 5)

```
==============================================================
  High-Energy EDM Head  [mode: balanced]
==============================================================
╭─────┬───────────────────┬─────────────┬─────────┬──────────────────────────────────────────────╮
│   # │ Title             │ Artist      │   Score │ Reasons                                      │
├─────┼───────────────────┼─────────────┼─────────┼──────────────────────────────────────────────┤
│   1 │ Bass Drop Kingdom │ Subzero     │    4.49 │ genre match: EDM (+2.0); mood match: intense │
│     │                   │             │         │ (+1.0); energy proximity (+1.00); valence    │
│     │                   │             │         │ proximity (+0.48)                            │
│   2 │ Gym Hero          │ Max Pulse   │    2.42 │ mood match: intense (+1.0); energy proximity │
│     │                   │             │         │ (+0.98); valence proximity (+0.44)           │
│   3 │ Storm Runner      │ Voltline    │    2.38 │ mood match: intense (+1.0); energy proximity │
│     │                   │             │         │ (+0.96); valence proximity (+0.41)           │
│   4 │ Street Cipher     │ Blok Theory │    2.33 │ mood match: intense (+1.0); energy proximity │
│     │                   │             │         │ (+0.90); valence proximity (+0.43)           │
│   5 │ Thunder Descent   │ Iron Vale   │    2.3  │ mood match: intense (+1.0); energy proximity │
│     │                   │             │         │ (+0.98); valence proximity (+0.32)           │
╰─────┴───────────────────┴─────────────┴─────────┴──────────────────────────────────────────────╯
```

### Moody Synthwave Night (balanced mode, top 5)

```
==============================================================
  Moody Synthwave Night  [mode: balanced]
==============================================================
╭─────┬──────────────────┬─────────────┬─────────┬─────────────────────────────────────────────╮
│   # │ Title            │ Artist      │   Score │ Reasons                                     │
├─────┼──────────────────┼─────────────┼─────────┼─────────────────────────────────────────────┤
│   1 │ Neon Prophecy    │ Grid Rider  │    4.5  │ genre match: synthwave (+2.0); mood match:  │
│     │                  │             │         │ moody (+1.0); energy proximity (+1.00);     │
│     │                  │             │         │ valence proximity (+0.49)                   │
│   2 │ Night Drive Loop │ Neon Echo   │    4.45 │ genre match: synthwave (+2.0); mood match:  │
│     │                  │             │         │ moody (+1.0); energy proximity (+0.97);     │
│     │                  │             │         │ valence proximity (+0.48)                   │
│   3 │ After Hours Blue │ Velvet Trio │    2.25 │ mood match: moody (+1.0); energy proximity  │
│     │                  │             │         │ (+0.76); valence proximity (+0.48)          │
│   4 │ Street Cipher    │ Blok Theory │    1.33 │ energy proximity (+0.87); valence proximity │
│     │                  │             │         │ (+0.46)                                     │
│   5 │ Storm Runner     │ Voltline    │    1.29 │ energy proximity (+0.81); valence proximity │
│     │                  │             │         │ (+0.48)                                     │
╰─────┴──────────────────┴─────────────┴─────────┴─────────────────────────────────────────────╯
```

### Acoustic Folk Wanderer (balanced mode, top 5)

```
==============================================================
  Acoustic Folk Wanderer  [mode: balanced]
==============================================================
╭─────┬─────────────────────┬────────────────┬─────────┬───────────────────────────────────────────────╮
│   # │ Title               │ Artist         │   Score │ Reasons                                       │
├─────┼─────────────────────┼────────────────┼─────────┼───────────────────────────────────────────────┤
│   1 │ Sunday Acoustic     │ Clara Fields   │    4.96 │ genre match: folk (+2.0); mood match: relaxed │
│     │                     │                │         │ (+1.0); energy proximity (+0.98); valence     │
│     │                     │                │         │ proximity (+0.48); acoustic preference (+0.5) │
│   2 │ Coffee Shop Stories │ Slow Stereo    │    2.94 │ mood match: relaxed (+1.0); energy proximity  │
│     │                     │                │         │ (+0.95); valence proximity (+0.49); acoustic  │
│     │                     │                │         │ preference (+0.5)                             │
│   3 │ Open Road Hymn      │ Dust & Draw    │    2.87 │ mood match: relaxed (+1.0); energy proximity  │
│     │                     │                │         │ (+0.87); valence proximity (+0.49); acoustic  │
│     │                     │                │         │ preference (+0.5)                             │
│   4 │ Spacewalk Thoughts  │ Orbit Bloom    │    1.93 │ energy proximity (+0.96); valence proximity   │
│     │                     │                │         │ (+0.47); acoustic preference (+0.5)           │
│   5 │ Library Rain        │ Paper Lanterns │    1.91 │ energy proximity (+0.97); valence proximity   │
│     │                     │                │         │ (+0.44); acoustic preference (+0.5)           │
╰─────┴─────────────────────┴────────────────┴─────────┴───────────────────────────────────────────────╯
```

---

## Experiments You Tried

### Mode comparison for the Happy Pop Fan profile

Switching from `balanced` to `genre-first` mode doubles the genre weight from 2.0 to 4.0. The top two results stay the same (both are pop songs), but the gap between them and the third-place indie-pop song widens dramatically — the third-place score drops from 2.44 to 1.22. This shows how heavily genre dominates once its weight goes up; a song that perfectly matches mood and energy but misses on genre gets buried.

In `mood-first` mode the rankings shuffle noticeably. Rooftop Lights (indie pop, happy) and Fuego Samba (latin, happy) both jump to positions 2–3 because their mood match is now worth 3.0 points instead of 1.0. The EDM Head and Folk Wanderer profiles are the most stable across modes because those genres and moods are each represented by only one or two songs in the catalog — there is less competition to reshuffle.

### Weight shift experiment

When the energy weight was tripled (energy-focused mode), Sunrise City still won for the Happy Pop Fan profile because it hit all three bonus categories (genre + mood + energy proximity). However the gap between rank 2 and rank 3 tightened: Gym Hero and Rooftop Lights are closer in score because Rooftop's very high energy score (0.76, near the 0.80 target) compensates for its missing genre match when energy is worth 3× as much.

### Diversity penalty

Without the diversity penalty, LoRoom would appear twice in the top 3 for the Chill Lofi Listener (Midnight Coding at #2 and Focus Flow at #3). The 0.4-per-repeat penalty drops Focus Flow's effective score enough that Spacewalk Thoughts edges into #4 instead, giving the list more variety.

---

## Limitations and Risks

- The catalog is only 20 songs, so for any genre that appears just once, the system has almost nothing to recommend within that genre.
- Genre labels are exact-match strings. A song labeled "indie pop" will never earn the genre bonus for a user who typed "pop," even though the two are closely related.
- The scoring formula treats features independently. It cannot understand that "chill + high energy" is a contradiction the way a human would.
- Content-based filtering creates a filter bubble: if a user only likes lofi, they will almost never be shown jazz or ambient music even though those genres often share the same low-energy, relaxed quality.
- The system does not learn. It cannot update weights based on whether a user actually liked the recommendation.

---

## Reflection

See [model_card.md](model_card.md) for the full model card and personal reflection.

The most surprising thing was how much the exact-match genre rule dominates the score. Songs that were intuitively a great fit — same energy, same mood, nearly identical vibe — kept getting outranked by genre matches that felt less relevant subjectively. That gap between what a number maximizes and what a listener would actually choose is the central challenge in recommendation system design.
