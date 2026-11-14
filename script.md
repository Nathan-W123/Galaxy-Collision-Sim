# What happens if our universe collided with another one?

Narration script: 249 words, 1:58.5 total; timestamps estimated at 150 words per minute.
Every claim cites a source key from `sources.md` (section 5). On-screen labels mark what
is simulated, what is an illustration, and what is speculative.

## 1. Hook  (0:00.6–0:09.4)

*Engine footage of the two galaxies approaching (frames from the verified MW-M31 clip).*

**[0:00.6–0:04.2]** What happens if our universe collided with another one?

- On screen: What happens if our universe collided with another one?
- Visual: N-body footage: Milky Way and Andromeda approaching
- Label: "N-body simulation"

**[0:05.0–0:09.4]** Let's start with a collision that might actually happen to us.

- Visual: N-body footage continues

## 2. Galaxies  (0:10.6–0:57.6)

**[0:10.6–0:15.4]** Andromeda, two and a half million light-years away, is falling toward us.

- On screen: Andromeda · 2.5 million light-years away
- Visual: N-body footage: approach
- Sources: S1, S2

**[0:15.8–0:21.4]** Whether they merge is roughly a coin flip. Here's one way it could go.

- On screen: Chance of a merger within 10 billion years: about 50 % (estimate) · this run: one possible outcome
- Visual: N-body footage: approach, first passage begins
- Label: "estimate"
- Sources: S3, S4

**[0:22.0–0:26.0]** Here's the surprise: the stars almost never hit each other.

- On screen: Stars almost never collide
- Visual: N-body footage: first passage in slow motion
- Sources: S1

**[0:26.4–0:33.6]** Make the Sun a grain of sand, and the nearest star is another grain about thirty kilometres away.

- On screen: Sun → 1 mm grain of sand · nearest star → about 29 km away
- Visual: inset over the footage: grain of sand and a 29 km distance bar; footnote with NASA numbers
- Sources: S5, S6

**[0:34.2–0:41.0]** I wrote my own N-body engine for this. Every particle pulls on every other: N squared work.

- On screen: N = 100,000 particles → N(N−1)/2 ≈ 5 billion pairs, every step
- Visual: Manim: dots with every pair joined; the line count explodes
- Sources: S7, S9

**[0:41.4–0:49.8]** The fix: treat a distant clump as one mass when its size over distance is small. That's about N log N.

- On screen: s / d < θ   (θ = 0.6)  ·  N² → N log N  ·  Barnes & Hut 1986
- Visual: Manim: the engine's real octree from a simulation snapshot; one star's accepted cells highlighted; s and d drawn on one cell
- Sources: S7, S8

**[0:50.4–0:57.6]** Gravity does the damage: it flings out tidal tails, and the spirals settle into one smooth elliptical galaxy.

- Visual: N-body footage: tails, second passage, coalescence, remnant (cut, not retimed)
- Sources: S4

## 3. Universes  (0:59.0–1:21.2)

**[0:59.0–1:04.6]** But a universe isn't an object in space. You can't fly one into another.

- On screen: A universe isn't an object in space.
- Visual: Manim: the remnant galaxy shrinks to a dot; text

**[1:05.2–1:11.2]** In one speculative idea, eternal inflation, space inflates forever and bubbles keep forming in it.

- On screen: Eternal inflation (speculative)
- Visual: Manim: an expanding grid; bubbles appear in it
- Label: "illustration · speculative"
- Sources: S10, S11

**[1:11.6–1:16.0]** Our whole observable universe could sit inside one of those bubbles.

- Visual: Manim: zoom into one bubble, marked 'our observable universe?'
- Label: "illustration · speculative"
- Sources: S11, S12

**[1:16.4–1:21.2]** Their walls grow at nearly light speed, so neighbouring bubbles can collide.

- Visual: Toy bubble simulation: random nucleation, walls growing, collisions flash where walls meet
- Label: "illustration (toy model)"
- Sources: S11, S16

## 4. What would happen  (1:22.3–1:50.9)

**[1:22.3–1:29.9]** A past collision would leave a disk-shaped mark on the cosmic microwave background, the oldest light we can see.

- On screen: Planck 2018 map of the cosmic microwave background
- Visual: Real Planck SMICA map (Mollweide); a disk drawn on it
- Label: "disk: illustration of a predicted signature"
- Sources: S12, S13, S15

**[1:30.3–1:35.1]** Searches of the WMAP satellite's map found no convincing sign of one.

- On screen: WMAP 7-year data: fewer than 1.6 detectable collisions expected (68 % confidence) · no convincing evidence so far
- Visual: Planck map; disk fades; result text
- Sources: S12, S14

**[1:35.7–1:43.7]** In our future? A wall would arrive at nearly light speed, with almost no warning. That part is pure speculation.

- On screen: speculative
- Visual: Manim: a bright wall sweeping across the frame
- Label: "illustration · speculative"
- Sources: S11, S16

**[1:44.5–1:50.9]** We can watch Andromeda coming for billions of years. Another universe, we would never see coming.

- Visual: split: N-body footage of the approach | empty dark frame
- Sources: S4

## 5. End card  (1:52.1–1:56.1)

**[1:52.1–1:56.1]** 

- On screen: Every frame of the galaxy collision was computed by my own N-body engine.
- Visual: End card with credits: simulation (own Barnes-Hut code, 100,000 particles, initial conditions from van der Marel et al. 2012); CMB map: ESA/Planck Collaboration (Planck 2018), via NASA/IPAC IRSA; full sources in the description
- Sources: S4, S15
