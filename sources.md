# Sources

Every number used in the simulation and (later) on screen is listed here with its source.
Section 1 maps the parameter file `scenarios/mw_m31_vdm2012.yaml` to the papers. Section 2 lists
what we assumed because no source gives it. Section 3 compares our run with the published one. Section 4 holds the full verification notes for the simulation; section 5 lists the script's sources with the full fact-check record:
exact quotes, locations in the papers and confidence codes, checked against full texts on
2026-11-13.

## 1. Simulation parameters and their sources

| Parameter | Value in the run | Source |
|---|---|---|
| Frame | Galactocentric (X toward the Galactic Centre from the Sun, Z to the north Galactic pole), MW at rest at the origin | vdM2012 II §4.1; vdM2012 III §2.1 |
| M31 position | (−378.9, 612.7, −283.1) kpc, \|r\| = 774 kpc | vdM2012 II eq. (2) |
| M31 velocity | (72.6, −69.7, 50.9) km/s, Vtan = 27.7 km/s (the canonical N-body vector) | vdM2012 III Table 2, §3.1 |
| Virial masses | MW 1.5×10^12, M31 1.5×10^12 Msun (canonical, equal mass) | vdM2012 III Table 2 |
| Halo profile | Hernquist, a = 62.5 kpc, total Hernquist mass M_H = 1.36 (Mvir − Md − Mb) = 1.924×10^12 Msun | vdM2012 III §2.1, §3.1; vdM2012 II App. A |
| Disks | MW Md = 7.5×10^10 Msun, Rd = 3.0 kpc; M31 Md = 1.2×10^11 Msun, Rd = 5.0 kpc | vdM2012 III Tables 1–2 |
| Bulges | MW Mb = 1.0×10^10 Msun, R_e = 0.6 kpc; M31 Mb = 1.9×10^10 Msun, R_e = 1.0 kpc | vdM2012 III Table 1 |
| Spin axes | MW (0, 0, −1); M31 (−0.412, −0.767, −0.492) | vdM2012 III §3.2 |
| Published result to compare against | canonical run: first pericentre 3.97 Gyr at 35.0 kpc, apocentre 171.9 kpc at 4.79 Gyr, merger 6.29 Gyr. Monte Carlo: pericentre 3.87 (+0.42/−0.32) Gyr at 31 kpc, merger 5.86 (+1.61/−0.72) Gyr | vdM2012 III §3.3, §4.2 |
| Context for the script (not inputs) | Gaia DR2+HST Vtan = 57 (+35/−31) km/s, first pericentre ~4.5 Gyr at ~130 kpc (vdM2019). Merger probability within 10 Gyr: 44 % (MW–M31 only), 63 % (+M33), 37 % (+LMC), 54 % (all four); median merger time 7.6 Gyr among mergers (Sawala et al. 2025) | vdM2019 §3.2, §4.2; Sawala et al. 2025 |

## 2. Assumptions (no source gives these)

* **Disk scale heights:** z0 = 0.1 Rd (MW 0.3 kpc, M31 0.5 kpc), sech² vertical profile. Paper III does not list them.
* **Bulges:** modelled as Hernquist spheres with a = R_e / 1.8153 (MW 0.33 kpc, M31 0.55 kpc). Paper III uses R^1/4 bulges with effective radius R_e.
* **Halo truncation:** each halo is sampled out to r_max = 600 kpc (about 2 r_vir), containing 82 % of M_H (1.578×10^12 Msun per halo). Paper III does not state its truncation.
* **Disk dispersions:** Toomre Q = 1.5 at every radius (project brief). Paper III's disk kinematics are not reproduced exactly.
* **Omissions:** no central black holes (Paper III includes M_BH = 3.6×10^-6 M_H). No M33 and no LMC. No 1 Gyr isolated relaxation before the start (Paper III evolves each galaxy alone for 1 Gyr).
* **Resolution:** 100,000 particles (Paper III used about 3.2 million), Plummer softening 0.2 kpc, timestep 1 Myr.
* **Consequence:** our run is one realisation of the 2012 canonical scenario. It is not a prediction. The 2019 and 2025 results make a merger within 10 Gyr roughly a coin flip, and the script must say so.

## 3. Our run compared with the published result

The comparison uses the final-resolution coarse run `mw_m31_vdm2012_coarse` (100,000
particles, snapshots every 20 Myr). Its energy drift over 10 Gyr was 0.53 %.

| Event | Our run | vdM2012 III canonical N-body | vdM2012 III Monte Carlo |
|---|---|---|---|
| First pericentre | 3.72 Gyr, 25 kpc | 3.97 Gyr, 35.0 kpc | 3.87 (+0.42/−0.32) Gyr, 31.0 (+38.0/−19.8) kpc |
| First apocentre | 4.36 Gyr, 137 kpc | 4.79 Gyr, 171.9 kpc | – |
| Merger (centres within 5 kpc from then on) | 5.56 Gyr | 6.29 Gyr | 5.86 (+1.61/−0.72) Gyr |

Our first passage is somewhat closer and earlier than in the canonical run, so dynamical
friction brings the galaxies together sooner. All three times fall inside the published
Monte Carlo ranges. Differences we know of:

* no 1 Gyr isolated relaxation;
* the halo truncation at 600 kpc;
* no black holes;
* Toomre-Q disk kinematics;
* about 30 times fewer particles.

## 4. Verification notes

### Full verification record

Verified 2026-11-13. I read the full text of all four papers:

- arXiv PDFs, converted with `pdftotext`.
- The published IOP (ApJ) HTML full text for vdM2012 II and III. Their abstracts, Tables 1–3 and canonical-model numbers match arXiv v1.
- The published, open-access Nature Astronomy HTML full text for Sawala et al. 2025, plus its Table 1 page.

**About the quotes.** Text extraction flattens math: superscripts, subscripts and vector arrows are lost. Asymmetric errors appear as `X +a −b`, meaning X with +a/−b. "10^12" may appear as "1012" in the raw extraction. In the quotes below I restored it as 10^12. No other wording was changed.

**Confidence codes:**
- **VT** = verified in full text.
- **VA** = in the abstract, and also checked in the body unless noted.
- **FIG** = read off a figure, so approximate.
- **DER** = derived or computed by me. Not in the paper; flagged.
- **NF** = not found.

---

### 4.1 van der Marel et al. 2012a (Paper II)

**Citation.** van der Marel, R. P., Fardal, M., Besla, G., Beaton, R. L., Sohn, S. T., Anderson, J., Brown, T., & Guhathakurta, P. 2012. "The M31 Velocity Vector. II. Radial Orbit toward the Milky Way and Implied Local Group Mass." *The Astrophysical Journal*, 753(1), 8.

- DOI: 10.1088/0004-637X/753/1/8
- arXiv: 1205.6864 (v1, 31 May 2012; the only version)
- URLs: https://arxiv.org/abs/1205.6864 and https://iopscience.iop.org/article/10.1088/0004-637X/753/1/8
- ADS bibcode (standard form, not fetched because ADS refused automated access): 2012ApJ...753....8V

**Coordinate convention (§4.1, verbatim):** "we adopt a Cartesian coordinate system (X, Y, Z), with the origin at the Galactic Center, the Z-axis pointing towards the Galactic North Pole, the X-axis pointing in the direction from the Sun to the Galactic Center, and the Y-axis pointing in the direction of the Sun's Galactic rotation. We choose the origin of the frame to be at rest (the Galactocentric rest frame)".

Solar parameters: "R0 = 8.29 ± 0.16 kpc and V0 = 239 ± 5 km/s. These are the values we adopt here." The solar peculiar velocity is "(Upec, Vpec, Wpec) = (11.1, 12.24, 7.25)". So the Sun sits at X = −8.29 kpc, Y = 0, Z = 0 (DER). I checked this: placing M31 at D = 770 kpc with the Sun at (−8.29, 0, 0) and no z offset reproduces eq. (2) exactly. The solar Y-velocity "vY = V0 + Vpec, is 251.2 km/s" (§5.1).

| Item | Value | Uncertainty | Exact quote | Location | Conf. |
|---|---|---|---|---|---|
| A. M31 heliocentric distance | 770 kpc | ±40 kpc | "Throughout this paper we adopt D = 770 ± 40 kpc (see references in vdMG08)." | §1 | VT |
| A. MW–M31 separation | 770 kpc (stated as "distance between the galaxies") | ±40 kpc | "Since the distance between the galaxies is D = 770 ± 40 kpc, the virial spheres are not currently overlapping." | §5.2 | VT |
| A. Galactocentric distance (computed) | \|r\| = 774.0 kpc | – | computed from eq. (2) | – | DER |
| B. Vrad (Galactocentric) | −109.3 km/s (abstract); −109.2 km/s (eq. 5) | ±4.4 km/s | Abstract: "a radial velocity of M31 with respect to the Milky Way of Vrad,M31 = −109.3 ± 4.4 km s−1". Eq. (5): "Vrad,M31 = −109.2 ± 4.4 km s−1" | Abstract; §4.2 eq. (5); §7 | VT (internal 0.1 km/s inconsistency; my projection of eq. 3 gives −109.3) |
| B. Vtan (Galactocentric) | 17.0 km/s | 1σ region ≤ 34.3 km/s (flat prior) | "Vtan,M31 = 17.0 km s−1 (1σ confidence region : Vtan,M31 ≤ 34.3 km s−1)" | §4.2 eq. (6) | VT |
| B. Total relative speed | 110.6 km/s | ±7.8 | "\|V M31\| = 110.6 ± 7.8 km s−1" | §4.2 eq. (4) | VT |
| B. Heliocentric transverse velocity (HST + satellites, weighted) | (vW, vN) = (−125.2, −73.8) km/s | (±30.8, ±28.4) | "(vW , vN ) = (−125.2 ± 30.8, −73.8 ± 28.4) km s−1" | §3.4 eq. (1); Table 3 | VT |
| B. HST-only COM (corrected for internal kinematics) | (−162.8, −117.2) km/s | (±47.0, ±45.0) | "(vW , vN )(COM) = (−162.8 ± 47.0, −117.2 ± 45.0) km/s" | §2.2 | VT |
| B. Line-of-sight velocity | −301 km/s | ±1 | "observed COM LOS velocity vLOS = −301 ± 1 km s−1 (vdMG08)" | §4.2 | VT |
| C. M31 position | (−378.9, 612.7, −283.1) kpc | not given | "~rM31 = (−378.9, 612.7, −283.1) kpc." | §4.2 eq. (2) | VT |
| C. M31 velocity | (66.1, −76.3, 45.1) km/s | (±26.7, ±19.0, ±26.5), correlated | "~vM31 = (66.1 ± 26.7, −76.3 ± 19.0, 45.1 ± 26.5) km s−1 . (3) The errors (which are correlated between the different components)…" | §4.2 eq. (3) | VT |
| C. M33 position and velocity | r = (−476.1, 491.1, −412.9) kpc; v = (43.1, 101.3, 138.8) km/s | v: (±21.3, ±23.5, ±28.1) | "~rM33 = (−476.1, 491.1, −412.9)kpc, and ~vM33 = (43.1 ± 21.3, 101.3 ± 23.5, 138.8 ± 28.1) km s−1" (DM33 = 794 ± 23 kpc, vlos = −180 ± 1) | §6.1 | VT |
| C. "Trigalaxy" frame unit vectors | uX′ = (−0.48958, 0.79153, −0.36577); uY′ = (−0.47945, −0.60013, −0.64029); uZ′ = (−0.72632, −0.13810, 0.67331) | – | as listed, eq. (8); M31 velocity in this frame "(−109.2, −15.5, −7.1)km s−1" | §6.1 eqs. (8)–(9) | VT |
| D. LG timing mass (cosmic bias and scatter included) | Mtot,vir = 4.93×10^12 M☉ | ±1.63×10^12 | "Mtot,vir = (4.93 ± 1.63) × 10^12 M⊙ (timing argument)." | §5.1 eq. (7); abstract | VT |
| D. Raw timing mass | 4.27×10^12 (observed Vtan); 4.23×10^12 (radial orbit) | ±0.53; ±0.45 | "the "timing mass" Mtot,timing = (4.27 ±0.53) × 10^12 M⊙ … When a radial orbit is assumed … Mtot,timing = (4.23 ± 0.45) × 10^12 M⊙" | §5.1 | VT |
| D. Final LG mass | 3.17×10^12 M☉ | ±0.57 (abstract, §7); ±0.56 (eq. 10, arXiv) | "MLG = (3.17 ± 0.57) × 10^12 M⊙" (abstract); "Mtot,vir = (3.17 ± 0.56) × 10^12 M⊙ (final estimate). (10)" | Abstract; §6.3 eq. (10); §7 | VT |
| D. MW virial mass | prior flat 0.75–2.25×10^12; posterior mean 1.63×10^12 | – | "a flat probability distribution for MMW,vir between 0.75 and 2.25 × 10^12 M⊙"; "Its average has increased from 1.50 to 1.63 × 10^12 M⊙." | §5.2 | VT |
| D. M31 virial mass | 1.51×10^12, then 1.54×10^12 once M33 is required to be bound | ±0.42; ±0.39 | "its average has increased from (1.38 ± 0.43) × 10^12 M⊙ to (1.51 ± 0.42) × 10^12 M⊙"; "increase from MM31,vir = (1.51 ± 0.42) × 10^12 M⊙ to (1.54 ± 0.39) × 10^12 M⊙" | §5.2; §6.3 | VT |
| D. M33 virial mass | 0.148×10^12 M☉ | ±0.058 | "MM33,vir = (0.148 ± 0.058) × 10^12 M⊙" | §6.2 | VT |
| D. Stellar masses | M31: 7.9×10^10; M33: 3.2×10^9 M☉ | ±0.9×10^10; ±0.4×10^9 | "MM31,∗ = (7.9 ± 0.9) × 10^10 M⊙"; "MM33,∗ = (3.2 ± 0.4) × 10^9 M⊙" | §6.2 | VT |
| D. Virial radii | MW 308 kpc; M31 300 kpc | – | "the corresponding virial radii are 308 kpc and 300 kpc, respectively" | §5.2 | VT |
| D. Concentration and mass definitions | cvir = 10 ± 2; M200/Mvir = 0.839 ± 0.014; Δvir = 360 (h = 0.7, Ωm = 0.27) | – | "For the MW and M31 we take cvir = 10 ± 2 … This implies M200 /Mvir = 0.839 ± 0.014"; "one has ∆vir = 360" | §5; App. A | VT |
| D. NFW→Hernquist conversion | cvir = 10 gives a200/rs = 2.01, MH,200/Mvir = 1.36 | – | "c200 = 7.4, M200 /Mvir = 0.84, a200 /rs = 2.01, MH,200 /Mvir = 1.36, avir /rs = 2.09, and MH,vir /Mvir = 1.46" | App. A | VT |
| E. Disk orientations | NF in Paper II (they are in Paper III, Table 1) | – | – | – | NF |
| F. Timeline | NF (deferred to Paper III) | – | – | – | NF |
| G. Stellar collisions | NF | – | – | – | NF |

---

### 4.2 van der Marel et al. 2012b (Paper III)

**Citation.** van der Marel, R. P., Besla, G., Cox, T. J., Sohn, S. T., & Anderson, J. 2012. "The M31 Velocity Vector. III. Future Milky Way–M31–M33 Orbital Evolution, Merging, and Fate of the Sun." *The Astrophysical Journal*, 753(1), 9.

- DOI: 10.1088/0004-637X/753/1/9
- arXiv: 1205.6865 (v1, 31 May 2012)
- URLs: https://arxiv.org/abs/1205.6865 and https://iopscience.iop.org/article/10.1088/0004-637X/753/1/9
- ADS bibcode (standard form, not fetched): 2012ApJ...753....9V

**Method.** "collisionless N-body simulations … including only stars and dark matter … GADGET-3". Halos are Hernquist, with "no adiabatic contraction". Disks are exponential and bulges R^1/4, with "Rb = 0.2Rdisk". Each galaxy has a central black hole "MBH = 3.6 × 10−6 MH". Each galaxy was "evolved … in isolation for 1Gyr before starting the actual simulation" (§2.1, §3.4). Initial conditions are "set up in the Galactocentric frame, defined in Section 4 of Paper II, with the MW starting at rest at the origin" (§2.1).

**Merger definition (footnote 3):** "we consider two galaxies to have merged if their COM separation stays within 5 kpc for an entire Gyr."

| Item | Value | Uncertainty | Exact quote | Location | Conf. |
|---|---|---|---|---|---|
| A. M31 distance used | 770.0 kpc (canonical); Monte Carlo 770 ± 40 | ±40.0 | Table 2, "DM31 kpc 770.0"; Table 3, "DM31 kpc 770.0 ± 40.0" (note: "distances from the Sun to M31 and M33") | Tables 2–3 | VT |
| A. M31 starting position | (−378.9, 612.7, −283.1) kpc | – | "At the start of the simulation (the present epoch, t = 0) M31 is at ~rM31 = (−378.9, 612.7, −283.1) kpc and M33 is at ~rM33 = (−476.1, 491.1, −412.9)." | §3.4 | VT |
| B/C. Canonical N-body M31 velocity | (VX, VY, VZ) = (72.6, −69.7, 50.9) km/s; Vtan = 27.7 km/s | – | Table 2 rows; "the transverse motion is Vtan,M31 = 27.7 km s−1. For comparison the best estimate from Paper II is Vtan,M31 = 17.0 km s−1" | §3.1; Table 2 | VT |
| B/C. Monte Carlo ranges | VX 66.1 ± 26.7; VY −76.3 ± 19.0; VZ 45.1 ± 26.5; Vtan ≤ 34.3 (1σ) | as given | Table 3, column (3) "Observed Range" | Table 3 | VT |
| C. Other N-body runs (VX, VY, VZ, Vtan) for M31 | retrograde (28.6, −102.5, 40.8; 29.1); first-M33 (61.6, −76.5, 58.3; 24.0); direct-hit (55.4, −90.4, 28.6; 12.2) | – | Table 2 | Table 2 | VT |
| D. Canonical virial masses | MW = M31 = 1.5×10^12; M33 = 0.15×10^12 M☉ | – | "we adopt galaxy masses MMW,vir = MM31,vir = 1.5 × 10^12 M⊙ and MM33,vir = 0.15 × 10^12 M⊙" | §3.1 | VT |
| D. Concentrations (canonical) | cvir: MW 9.56, M31 9.56, M33 11.37 | – | Table 2 rows cMW,vir / cM31,vir / cM33,vir | Table 2 | VT |
| D. Hernquist halo scale lengths | aMW = aM31 = 62.5 kpc; aM33 = 24.9 kpc | – | "The corresponding Hernquist scale lengths … are aMW = aM31 = 62.5 kpc and aM33 = 24.9 kpc." | §3.1 | VT |
| D. Halo mass rule | Mvir,h = Mvir − Md − Mb − MBH. Hernquist matched to NFW at r→0 and in enclosed M200 | – | "the virial mass of the dark halo was taken to be Mvir,h = Mvir − Md − Mb − MBH"; "if cvir = 10, then a/rs = 2.01, and MH /Mvir = 1.36" | §2.1 | VT |
| D. Disk masses (canonical) | MW 0.75×10^11; M31 1.20×10^11; M33 0.09×10^11 M☉ | – | Table 2 "MMW,disk 10^11 M⊙ 0.75 / MM31,disk 1.20 / MM33,disk 0.09"; text: "we use Md = 7.5 × 10^10 M⊙" | Table 2; §3.4 | VT |
| D. Disk scale lengths Rd | MW 3.0; M31 5.0; M33 1.3 kpc | – | Table 1 "Rd kpc 3.0f 5.0f 1.3g" | Table 1 | VT |
| D. Bulge masses and radii | Mb: MW 1.0, M31 1.9, M33 0.0 (×10^10 M☉). Rb (R^1/4 effective): MW 0.6, M31 1.0 kpc | – | Table 1 "Mb 10^10 M⊙ 1.0f 1.9f 0.0 / Rb kpc 0.6 1.0 ..." | Table 1 | VT |
| D. Particle numbers | Ndark 500k / 500k / 50k; Ndisk 750k / 1.2M / 93k; Nbulge 100k / 190k / 0 | – | Table 1 | Table 1 | VT |
| D. Rotation-curve targets | MW Vc ≈ 239 km/s at the Sun; M31 max Vc ≈ 250; M33 max ≈ 120 | – | "For the MW we choose Md to produce a circular velocity Vc ≈ 239 km s−1 at the solar radius … M31 … Vc ≈ 250 km s−1 … M33 … Vc ≈ 120 km s−1" | §2.1 | VT |
| E. M31 inclination and position angle | i = 77.5°, PA (line of nodes) = 37.5°. Approaching side SW, near side NW | – | Table 1 "inclination deg ... 77.5a,b … PA line of nodes deg ... 37.5a,b … approaching side SW … near side NW" | Table 1 | VT |
| E. M33 inclination and position angle | i = 52.9°, PA = 4.0°. Approaching N, near W | – | Table 1 | Table 1 | VT |
| E. MW spin axis | (0, 0, −1) | – | "The unit vector in the direction of the MW spin angular momentum equals ~lsp,MW = (0, 0, −1) (the Sun rotates clockwise in the X, Y plane)." | §3.2 | VT |
| E. MW disk plane | the Galactocentric X–Y plane | – | "projected onto the Galactocentric (X, Y) plane (i.e., the MW disk plane)" | §3.4 | VT |
| E. M31 spin axis (Galactocentric) | (−0.412, −0.767, −0.492) | – | "equals ~lsp,M31 = (−0.412, −0.767, −0.492)" | §3.2 | VT |
| E. Spin–orbit angles (canonical) | βMW = 32.6°, βM31 = 76.2° (both prograde) | – | "They are βMW = 32.6◦ and βM31 = 76.2◦." | §3.2; Table 2 | VT |
| F. First pericentre (Monte Carlo median) | 3.87 Gyr; 31.0 kpc | +0.42/−0.32 Gyr; +38.0/−19.8 kpc | "The first pericenter occurs at t = 3.87 +0.42 −0.32 Gyr, at a pericenter distance of r = 31.0 +38.0 −19.8 kpc." | Abstract; §4.2; §5 | VA/VT |
| F. Merger time (Monte Carlo median) | 5.86 Gyr; all orbits merge | +1.61/−0.72 Gyr | "the MW and M31 merge in all of the calculated orbits, with merger time t = 5.86 +1.61 −0.72 Gyr" | §4.2; abstract | VT |
| F. Direct-hit fraction | 41.0% with first pericentre < 25 kpc | ±~1.6% (DER, from their ∆p ≈ √Nf/N with N = 1000) | "In 41.0% of orbits the MW-M31 first-pericenter distance is less than 25 kpc." | §4.2 | VT |
| F. Canonical N-body timeline | pericentre 3.97 Gyr at 35.0 kpc; apocentre 171.9 kpc at 4.79 Gyr; merger at 6.29 Gyr | – | "M31 has its next pericenter with the MW at t = 3.97 Gyr from now, with a pericenter distance of r = 35.0 kpc. M31 then moves back out to an apocenter distance of r = 171.9 kpc at t = 4.79 Gyr … The two galaxies merge at t = 6.29 Gyr." | §3.3 | VT |
| F. Pericentre speed | 586.0 km/s | – | "At the first pericenter passage, the relative velocity is as large as 586.0 km s−1." | §3.3 | VT |
| F. Direct-hit N-body run | pericentre 3.2 kpc at 3.86 Gyr (Vtan = 12.2) | – | "This yields an MW-M31 pericenter separation of only 3.2 kpc at t = 3.86 Gyr" | App. B.3 | VT |
| F. M33 outcomes | hits MW first 9.3%; ejected from the LG 7.2%; generic 83.5%. M31–M33 pericentre 0.85 Gyr, 80.8 kpc | 0.85 +0.18/−0.13 Gyr; 80.8 +42.2/−31.7 kpc | "In 9.3% of the orbits, M33 "hits" the MW before M31 does"; "In 7.2% of orbits M33 leaves the LG" | §4.3; abstract | VT |
| F. Fate of the Sun | 85.4% end at r > R⊙; 10.4% at r > 50 kpc; 20.1% pass within 10 kpc of M33 | – | "14.6% of the candidate suns reside at r < R⊙ and 85.4% at r > R⊙ . A fraction 10.4% reside at r > 50 kpc" | §3.6 | VT |
| F. Sun's orbit | R⊙ ≈ 8.29 kpc; V⊙ ≈ 239 km/s | – | "The Sun is at R⊙ ≈ 8.29 kpc from the Galactic Center, and the circular velocity at this radius is V⊙ ≈ 239 km s−1" | §3.6 | VT |
| G. Stars do not collide | qualitative only | – | "For example, the structure of the outer solar system can be altered by nearby passages of other stars (e.g., Kenyon & Bromley 2004). Such passages are generally infrequent, owing to the collisionless nature of galaxies, and this remains true during galaxy interactions." | §5 | VT |
| G. Related | – | – | "The galaxies partially overlap at this time … the relative velocity between the galaxies is large, so that the immediate damage they inflict on one another is limited." | §3.4 | VT |

---

### 4.3 van der Marel et al. 2019

**Citation.** van der Marel, R. P., Fardal, M. A., Sohn, S. T., Patel, E., Besla, G., del Pino, A., Sahlmann, J., & Watkins, L. L. 2019. "First Gaia Dynamics of the Andromeda System: DR2 Proper Motions, Orbits, and Rotation of M31 and M33." *The Astrophysical Journal*, 872(1), 24.

- DOI: 10.3847/1538-4357/ab001b
- arXiv: 1805.04079 (v1, 10 May 2018; v2, 29 Jan 2019). I quote from v2; the published ApJ abstract matches it.
- URLs: https://arxiv.org/abs/1805.04079 and https://iopscience.iop.org/article/10.3847/1538-4357/ab001b
- ADS bibcode (standard form, not fetched): 2019ApJ...872...24V

**Frame:** "These velocities are expressed in the Galactocentric (X, Y, Z) coordinate system defined in vdM12a, and make the same assumptions about the solar position and velocity." (§3.2). This is the same frame as Paper II: R0 = 8.29 kpc, V0 = 239 km/s.

| Item | Value | Uncertainty | Exact quote | Location | Conf. |
|---|---|---|---|---|---|
| A. M31 distance | 770 kpc (M33: 794 kpc) | none quoted | "Here and henceforth we assume a distance D = 770 kpc for M31 and D = 794 kpc for M33 (vdM12a; vdM12b and references therein)." | §2.1 (PM-to-velocity conversion) | VT |
| B. Gaia DR2 M31 proper motion | (µα*, µδ) = (65, −57) µas/yr | ±18 / ±15 random, plus ±16 systematic each | "~µM31,DR2 = (65 ± 18[rand] ± 16[syst], −57 ± 15[rand] ± 16[syst]) µas yr−1" | §3.2 eq. (1); abstract | VT |
| B. HST proper motion (vdM12) | (45, −32) µas/yr | ±13 / ±12 | "~µM31,HST = (45 ± 13, −32 ± 12) µas yr−1" | §3.2 eq. (2) | VT |
| B. DR2+HST weighted average | (49, −38) µas/yr | ±11 / ±11 | "~µM31,DR2+HST = (49 ± 11, −38 ± 11) µas yr−1" | §3.2 eq. (3) | VT |
| B. Radial-orbit proper motion | (39, −22) µas/yr | – | "~µM31,rad = (39, −22) µas yr−1 (4) that corresponds to a purely radial approach" | §3.2 eq. (4) | VT |
| B. Vtan, DR2+HST (Galactocentric) | 57 km/s (median) | +35/−31 (68%) | "the median and 68% confidence region are Vtan,DR2+HST = 57 +35 −31 km s−1" | §3.2; abstract; §5 | VA/VT |
| B. Vtan, HST only | 36 km/s | +39/−26 | "the HST-only measurement implies Vtan,HST = 36 +39 −26 km s−1" | §3.2 | VT |
| B. Vtan, DR2 only | 133 km/s | +70/−68 | "the Gaia-only measurement implies Vtan,DR2 = 133 +70 −68 km s−1" | §3.2 | VT |
| B. Vrad of M31 | NF as an explicit number. Projecting eq. (8) onto the vdM12a position gives about −107 km/s (DER) | – | – | – | NF / DER |
| C. M31 velocity, DR2+HST | (34, −123, −19) km/s | (±36, ±25, ±37) | "~vM31,DR2+HST = (34 ± 36, −123 ± 25, −19 ± 37) km s−1 . (8)" | §3.2 eq. (8) | VT |
| C. M31 velocity, DR2 only | (0, −176, −84) km/s | (±75, ±51, ±73) | "~vM31,DR2 = (0 ± 75, −176 ± 51, −84 ± 73) km s−1 . (7)" | §3.2 eq. (7) | VT |
| C. M33 velocity, DR2+VLBA | (45, 91, 124) km/s | (±20, ±22, ±26) | "~vM33,DR2+VLBA = (45 ± 20, 91 ± 22, 124 ± 26) km s−1 . (13)" | §3.3 eq. (13) | VT |
| C. Position vectors | NF (the frame is inherited from vdM12a) | – | – | – | NF |
| D. Masses used for orbits | MW/M31 = 1.0/2.0×10^12 or 1.5/1.5×10^12; LMC 10^11; M33 2.5×10^11 M☉ | – | "a high mass ratio encounter (Mvir,MW = 10^12 M⊙ and Mvir,M31 = 2×10^12 M⊙) and an equal mass ratio encounter (Mvir,MW = 1.5 × 10^12 M⊙ = Mvir,M31 …)"; "the LMC (Mvir,LMC = 10^11 M⊙) and M33 (Mvir,M33 = 2.5 × 10^11 M⊙)" | §4.2 | VT |
| D. Structural parameters | NF ("static halo models", following Patel et al. 2017) | – | – | – | NF |
| E. M31 orientation | i = 77.5°, Θ = 37.5°. M31 centre (RA, Dec) = (10.68333, 41.26917)° | – | "For M31 we use COM position (RA,Dec) = (10.68333, 41.26917) deg, vLOS = −301 km s−1 , i = 77.5 deg, and Θ = 37.5 deg" | §3.1 | VT |
| E. M31 rotation sense | counter-clockwise on the sky; near side NW | – | "Vrot = −206 ± 86 km s−1 … The minus sign indicates that the rotation is counterclockwise as seen on the sky" | §3.2 | VT |
| E. M31 spin vector | NF | – | – | – | NF |
| F. Effect of Gaia proper motion on the orbit | first pericentre ~3.9 → ~4.5 Gyr; ~31 → ~130 kpc; still merge | approximate, mean vectors only | "The MW and M31 are still destined to merge. However, both the timing and the impact parameter of the first encounter have increased relative to vdM12b, from Tperi =∼3.9 Gyr to ∼4.5 Gyr and Rperi ∼ 31 kpc to ∼130 kpc." | §4.2 | VT |
| F. Adding LMC and M33 | encounter about 1 Gyr later; impact parameter about 75 kpc | approximate | "This further delays the MW-M31 encounter time by ∼1 Gyr, but decreases the impact parameter by half (∼75 kpc). All these calculations assume the mean 3D velocity vectors and static halo models." | §4.2 | VT |
| F. Merger time | NF (only qualitative: "somewhat later") | – | "the future collision with the Milky Way will happen somewhat later, and with larger pericenter, than previously inferred by vdM12b." | §5 | VT (qualitative) |
| G. Stellar collisions | NF | – | – | – | NF |

---

### 4.4 Sawala et al. 2025

**Citation (published).** Sawala, T., Delhomelle, J., Deason, A. J., Frenk, C. S., Häkkinen, J., Johansson, P. H., Keitaanranta, A., Rawlings, A., & Wright, R. 2025. "No certainty of a Milky Way–Andromeda collision." *Nature Astronomy*, 9(8), 1206–1217.

- DOI: 10.1038/s41550-025-02563-1
- Received 21 June 2024; accepted 22 April 2025; published online 2 June 2025; August 2025 issue.
- Open access under CC BY 4.0.
- URL: https://www.nature.com/articles/s41550-025-02563-1

**arXiv:** 2408.00064, v1 only (31 Jul 2024). Its title differs: "Apocalypse When? No Certainty of a Milky Way -- Andromeda Collision". It has 8 authors (no J. Häkkinen) and no N-body validation section. The numbers below come from the published version. The arXiv numbers I checked (masses, Table 1, the 44/63/37/54% probabilities, the 7.6/8.0 Gyr medians) are identical.

**Code:** https://github.com/TillSawala/MW-M31 (galaxies.ipynb).

**Model.** Point-like NFW halos only, with no disks: "a simple dynamical model that assumes no spin, no triaxiality and no substructure". Orbits use a leapfrog integrator with a 1 Myr step and 20 kpc softening, plus Chandrasekhar dynamical friction. A merger is counted once the separation falls below 20 kpc. There are 50,000 Monte Carlo samples for the fiducial model and 2,500 for the variants, with every input truncated at ±2σ.

**Frame.** The paper text says: "the position of the Galactic centre with respect to the Sun is fixed at (RA, dec.) = (266.4051, −28.936175) … and d = 8.122 kpc … and that the galactocentric velocity of the Sun is (12.9, 245.6, 7.78) km s−1". The code uses astropy `Galactocentric` with `galactocentric_frame_defaults.set('v4.0')`. Its stored output prints "galcen_distance=8.122 kpc, galcen_v_sun=(12.9, 245.6, 7.78) km / s, z_sun=20.8 pc, roll=0.0 deg". So the Sun is at x ≈ −8.122 kpc, slightly above the plane. The z_sun value comes from the code output, not the paper.

| Item | Value | Uncertainty | Exact quote | Location | Conf. |
|---|---|---|---|---|---|
| A. M31 distance modulus | μ = 24.407 (≈ 761 kpc, DER; the ±1σ range is 750–772 kpc) | ±0.032 mag | Table 1: "M31 … 24.407 ± 0.032 (ref. 27)" (Li et al. 2021, HST Cepheids) | Table 1 | VT (kpc is DER) |
| A. M33 distance modulus | μ = 24.67 (≈ 859 kpc, DER) | ±0.07 | Table 1: "24.67 ± 0.07 (ref. 26)" | Table 1 | VT |
| B. M31 proper motion (fiducial, Gaia EDR3 via Salomon et al. 2021) | (µα*, µδ) = (48.9, −36.9) µas/yr | ±10.5 / ±8.1 | Table 1: "48.9 ± 10.5 (ref. 29) … −36.9 ± 8.1 (ref. 29)" | Table 1 | VT |
| B. M31 line-of-sight velocity | −301 km/s | ±1 | Table 1: "−301 ± 1" | Table 1 | VT |
| B. Vtan adopted | most probable vt = 76 km/s (Gaia DR3). Cosmological prior 75 +65/−40 | – | "a present-day MW-M31 transverse velocity prior of vt = 75 +65 −40 km s−1 (ref. 36) … the transverse velocity measured using Gaia DR3 (most probable value vt = 76 km s−1)" | "Sources of uncertainty" | VT |
| B. Radial-orbit proper motion | quoted as 38.03, −21.37 "mas yr−1" (probably a unit typo for µas/yr; compare vdM2019 eq. 4) | – | "a perfectly radial present-day M31-MW motion (v_t = 0, μ_α* = 38.03 mas yr−1 and μ_δ = −21.37 mas yr−1)" | "Sources of uncertainty" | VT (typo flagged) |
| B. Vrad | NF | – | – | – | NF |
| C. Cartesian vectors | NF in the paper. They are computed from the Table 1 observables with astropy Galactocentric v4.0 (code) | – | – | – | NF |
| D. Masses (M200, 200× critical density) | MW 1.0×10^12 (LMC excluded); M31 1.3×10^12; M33 3×10^11; LMC 1.5×10^11; SMC 1.5×10^10 M☉ | ±0.2; ±0.4; ±1; ±0.5 (×10^11); ±0.5 (×10^10) | "We adopted M_200 = 1 ± 0.2 × 10^12 M⊙ (excluding the mass of the LMC …). For M31, we adopted M_200 = 1.3 ± 0.4 × 10^12 M⊙. For M33, we assumed M_200 = 3 ± 1 × 10^11 M⊙, and for the LMC, we assumed M_200 = 1.5 ± 0.5 × 10^11 M⊙." | "A fiducial model…"; Table 1 | VT |
| D. Concentration | c = 10 for all galaxies | ±2 | "We assumed concentration parameters of 10 ± 2 for all galaxies" | Methods, "Halo concentrations" | VT |
| D. Disk and bulge parameters | NF (the model has no disks) | – | – | – | NF |
| E. Disk orientations and spins | NF ("assumes no spin") | – | – | – | NF |
| F. Merger probability within 10 Gyr (fiducial) | MW–M31 alone 44%; +M33 63%; +LMC 37%; all four 54% | statistical errors < 1% | "40% instead of 44% for the MW-M31 system, 56% instead of 63% for the MW-M31-M33 system, 34% instead of 37% for the MW-M31-LMC system, and 48% instead of 54% for the full MW-M31-M33-LMC system" (the first number in each pair is the HST+DR2 alternative) | Methods, "HST + DR2 proper motions"; Fig. 2 | VT |
| F. Headline | ~50% chance of no merger in 10 Gyr | – | "a probability of close to 50% that there will be no Milky Way–Andromeda merger during the next 10 billion years" | Abstract | VA |
| F. Merger probability within 5 Gyr | about 2% (the "<5 Gyr" bar in Fig. 3 is about 1–2%; the survival curve reads about 98% at 5 Gyr) | – | NF in paper text. ESA/Hubble release heic2508 (secondary, 2 June 2025): "a small chance of around 2% for a head-on collision between the galaxies in only 4 to 5 billion years" | Fig. 3; press release | FIG / secondary |
| F. Median merger time (among merging systems) | 7.6 Gyr (20 kpc threshold); 8.0 Gyr (10 kpc threshold) | – | "The median time to merger is 7.6 Gyr for systems that merge with a 20-kpc threshold and 8.0 Gyr for systems that merge with a 10-kpc threshold." | Fig. 3 caption; main text | VT |
| F. Bimodal outcome | orbits that come within ~200 kpc merge; the rest do not | – | "Orbits that come within less than ~200 kpc eventually merge … Orbits with larger pericentres do not decay due to dynamical friction." | "Evolution of the MW-M31-M33-LMC system" | VT |
| F. Role of M33 | raises the probability (two-body 44% → 63%) | – | "The addition of M33 increases the merger probability to ~2/3, with a similar median merger time." | same section | VT |
| F. Role of the LMC | lowers the probability (44% → 37%) | – | "the pure MW-M31-LMC system experiences a merger in only slightly more than 1/3 of cases and the merger probability of the full M31-MW-M33-LMC system is just over 50%." | same section | VT |
| F. Most-probable-value orbit (MW–M31–M33, vdM2019 inputs) | first pericentre ~4.5 Gyr, ~100 kpc | approximate | "we reproduced a very similar time for the first pericentre, ~4.5 Gyr, and a similar first pericentre distance, ~100 kpc, as reported by ref. 13." | "Evolution…" (published only) | VT |
| F. Proper-motion sensitivity | the ±2σ range of the M31 proper motion spans probabilities from >90% to ~0% | – | "The ±2σ ranges of the M31 proper motions include values that imply a merger probability above 90% but also values that imply a merger probability close to zero. The most probable proper motions (assuming no errors) lead to a merger in only ~2/3 of cases." | "Sources of uncertainty" | VT |
| F. LMC and M33 fates | LMC–MW merger median 1.3 Gyr (20 kpc) or 1.9 Gyr (10 kpc). M33–M31 merger ~86%, median 3.3 Gyr | – | "a median time for the LMC-MW merger of 1.3 Gyr … For M33, with a merger threshold of 20 kpc, we found an ~86% chance of a merger with M31 and a median time of 3.3 Gyr" | Methods, "Fate of the LMC and M33" | VT |
| G. Stellar collisions | NF | – | – | – | NF |

---

### 4.5 Discrepancies and caveats

1. **The tangential velocity is the decisive input, and it has moved.**
   - vdM2012: Vtan = 17.0 km/s (1σ ≤ 34.3). This came from HST combined with satellite kinematics.
   - vdM2019 (DR2+HST): 57 +35/−31 km/s. The same paper gets 36 +39/−26 km/s from HST alone.
   - Sawala 2025 (Gaia EDR3/DR3, Salomon et al. 2021): most probable 76 km/s.

   The radial velocity barely moves (about −109 km/s in 2012; about −107 km/s projected from vdM2019 eq. 8, DER). One quirk: the median Vtan from vdM2019's flat-prior method (57) is not the Vtan of its mean vector (about 72 km/s, DER). Use their quoted median when describing the paper, but expect to get about 72 if you plug in the mean vector.

2. **The predicted outcome changed from "certain merger" to "coin flip".**
   - vdM2012 III: every Monte Carlo orbit merges; first pericentre at 3.87 Gyr and 31 kpc; merger at 5.86 Gyr.
   - vdM2019 (mean vectors only, no Monte Carlo): pericentre ~4.5 Gyr at ~130 kpc. Adding the LMC and M33 delays it by ~1 Gyr and brings it in to ~75 kpc. The galaxies are "still destined to merge".
   - Sawala 2025: 54% merge within 10 Gyr in the four-body fiducial; median 7.6 Gyr among those that merge; about 2% within about 5 Gyr (figure and press release only).

   A video should not present a single merger date as a firm prediction.

3. **Merger definitions differ, so merger times are not directly comparable.**
   - vdM2012 III: centres stay within 5 kpc "for an entire Gyr", with the latest time the separation exceeded 5 kpc taken as the merger time.
   - Sawala: the first time the separation drops below 20 kpc, which they call "a lower limit for the time of the merger".

4. **Mass definitions differ.**
   - vdM uses Mvir (Δvir = 360 times the mean matter density). In its N-body runs the halo is Hernquist, with total mass MH ≈ 1.36 Mvir for c = 10, so the total particle mass exceeds Mvir.
   - Sawala uses M200 (200 times critical density). By vdM2012 II, M200/Mvir = 0.839 for c = 10, so vdM's canonical 1.5×10^12 Mvir is about 1.26×10^12 in M200 (DER).
   - Sawala's MW (1.0×10^12, with the LMC excluded) is therefore lighter than vdM's canonical MW. Lower masses lower the merger probability (Sawala Fig. 6).

5. **The solar frames differ.** vdM2012 and vdM2019 use R0 = 8.29 kpc, V0 = 239 km/s, Schönrich peculiar motion (vY = 251.2 km/s) and no z_sun. Sawala uses 8.122 kpc and (12.9, 245.6, 7.78) km/s, with z_sun = 20.8 pc per the code. Do not mix position and velocity vectors from different papers. Recompute every vector from the observables in one frame.

6. **Distances differ.** M31 is 770 ± 40 kpc in vdM, against μ = 24.407 ± 0.032 (about 761 kpc, DER) in Sawala. M33 is 794 ± 23 kpc in vdM, against μ = 24.67 ± 0.07 (about 859 kpc, DER) in Sawala. These are consistent for M31, but differ substantially for M33.

7. **Internal inconsistencies in the sources.**
   - vdM2012 II gives Vrad = −109.3 in the abstract but −109.2 in eq. (5) and §7. The LG mass is 3.17 ± 0.57 in the abstract and §7 but ± 0.56 in arXiv eq. (10).
   - §6.2 cites "MM31,vir = (1.50 ± 0.38)×10^12" from §5.2, but §5.2 gives (1.51 ± 0.42)×10^12.
   - The vdM2012 III canonical N-body run uses Vtan = 27.7 km/s, not the 17.0 best estimate (footnote 1 explains why).
   - Sawala's radial-orbit proper motion is printed in "mas yr−1"; it should almost certainly be µas/yr.
   - Sawala says it reproduced "~4.5 Gyr … ~100 kpc, as reported by ref. 13" for the MW–M31–M33 system. vdM2019 itself reports ~130 kpc for the two-body case and ~75 kpc (about 1 Gyr later) with the LMC and M33. I found no three-body number in vdM2019.

   - Sawala's M33 proper motion does not match its text. The text says it uses "the combined HST and Gaia Data Release 2 (DR2) proper motions of ref. 13 for M33". But Table 1 lists (31 ± 19, −29 ± 16) µas/yr, which is vdM2019's DR2-only value (eq. 9). vdM2019's combined M33 value is DR2+VLBA (24 ± 7, 3 ± 8) µas/yr (eq. 11), and vdM2019 has no HST proper motion for M33.

8. **Sawala's paper has no structural data for disks.** It models point-like NFW halos with no disks, spin or orientation. For an N-body visualisation with disks, the only fully specified, source-backed setup among these four papers is vdM2012 III: Table 1 (Rd, Mb, Rb, i, PA), Table 2 (masses, c, velocities), the Hernquist a values and both spin vectors.

   A reasonable approach is to use vdM2012 III's galaxy structure and swap in modern orbital initial conditions:
   - either vdM2019 eq. (8), keeping vdM's frame;
   - or Sawala's Table 1 observables converted with the astropy v4.0 Galactocentric frame.

   Say on screen that the outcome is uncertain. To be honest about Sawala's result, show both a merging and a non-merging realisation.

9. **Stellar collisions.** The only statement in these four papers is vdM2012 III §5: close stellar passages "are generally infrequent, owing to the collisionless nature of galaxies, and this remains true during galaxy interactions." None of the four papers gives a number (for example a collision probability or a mean stellar separation). Any quantitative "stars won't collide" line needs another primary source.

10. **Gaps I could not verify.**
    - I could not reach ADS, so the bibcodes are not checked.
    - The 2% within 5 Gyr figure does not appear in Sawala's text. It is read from Fig. 3 and confirmed only by a press release.
    - vdM2019 gives no merger time and no explicit M31 Vrad.
    - vdM2012 II defers disk orientations to Paper III.

## 5. Script sources (keys used in `script.md`)

Fact-checked against primary or authoritative sources on 2026-11-14. Quotes, the safe
wordings and what must be labelled speculative are in the record below.

| Key | Source | Supports |
|---|---|---|
| S1 | NASA Hubble Mission Team / STScI, news release STScI-2012-20, 31 May 2012, "NASA's Hubble Shows Milky Way is Destined for Head-On Collision". https://science.nasa.gov/missions/hubble/nasas-hubble-shows-milky-way-is-destined-for-head-on-collision/ | stars "will not collide"; Andromeda "2.5 million light-years away". The release's "certainty" of a collision is superseded by S3 |
| S2 | van der Marel et al. 2012, ApJ 753, 8 (Paper II). DOI 10.1088/0004-637X/753/1/8 | D = 770 ± 40 kpc (about 2.5 million light-years) |
| S3 | Sawala et al. 2025, Nature Astronomy 9, 1206–1217. DOI 10.1038/s41550-025-02563-1 | "probability of close to 50% that there will be no Milky Way–Andromeda merger during the next 10 billion years" |
| S4 | van der Marel et al. 2012, ApJ 753, 9 (Paper III). DOI 10.1088/0004-637X/753/1/9 | the simulated scenario (sections 1–3 of this file) |
| S5 | NASA GSFC, Sun Fact Sheet (radius 695,700 km). https://nssdc.gsfc.nasa.gov/planetary/factsheet/sunfact.html | Sun diameter 1.39 million km |
| S6 | NASA, "What is a light-year?" (Proxima Centauri 4.25 ly; 9.46 trillion km per ly). https://science.nasa.gov/exoplanets/what-is-a-light-year/ | Proxima about 40 trillion km. Our arithmetic: 4.02×10^13 km / 1.39×10^6 km = 2.9×10^7, so a 1 mm Sun puts Proxima about 29 km away |
| S7 | Barnes & Hut 1986, Nature 324, 446–449. DOI 10.1038/324446a0 | direct summation grows as N^2; the tree method as N log N |
| S8 | Dehnen & Read 2011, Eur. Phys. J. Plus 126, 55. DOI 10.1140/epjp/i2011-11055-3, arXiv:1105.1082 | opening criterion θ w < r (cell size / distance < θ); O(N ln N) vs O(N^2) |
| S9 | Springel 2005, MNRAS 364, 1105. DOI 10.1111/j.1365-2966.2005.09655.x | direct-summation N^2 cost |
| S10 | Guth 2007, J. Phys. A 40, 6811. DOI 10.1088/1751-8113/40/25/S25, arXiv:hep-th/0702178 | eternal inflation; false vacuum keeps growing; understanding "remains incomplete" |
| S11 | Aguirre & Johnson 2011, Rep. Prog. Phys. 74, 074901. DOI 10.1088/0034-4885/74/7/074901, arXiv:0908.4105 | our observable universe inside one bubble; bubbles collide; walls approximated as on the light cone; observability needs "good fortune" |
| S12 | Feeney, Johnson, Mortlock & Peiris 2011, PRL 107, 071301. DOI 10.1103/PhysRevLett.107.071301, arXiv:1012.1995 | azimuthally symmetric disc on the CMB; WMAP 7-yr: N̄s < 1.6 at 68 % CL, "do not warrant augmenting ΛCDM with bubble collisions" |
| S13 | Feeney et al. 2011, PRD 84, 043507. DOI 10.1103/PhysRevD.84.043507, arXiv:1012.3667 | "confined to a disc on the sky" |
| S14 | Feeney et al. 2013, PRD 88, 043012. DOI 10.1103/PhysRevD.88.043012, arXiv:1210.2725 | WMAP 7-yr: fewer than 4.0 detectable collisions at 95 %; latest template search found (no published Planck-data disc search) |
| S15 | Planck Collaboration 2020, A&A 641, A4 (Planck 2018 IV). DOI 10.1051/0004-6361/201833881; map `COM_CMB_IQU-smica_2048_R3.00_full.fits` via NASA/IPAC IRSA (DOI 10.26131/IRSA558) | the CMB map shown. Credit: ESA/Planck Collaboration. "This research has made use of the NASA/IPAC Infrared Science Archive, which is funded by the National Aeronautics and Space Administration and operated by the California Institute of Technology." |
| S16 | Markkanen, Rajantie & Stopyra 2018, Front. Astron. Space Sci. 5, 40. DOI 10.3389/fspas.2018.00040, arXiv:1809.06923 | true-vacuum bubbles expand at (nearly) light speed. "No warning" is our inference (no source states it), so it is narrated as speculation |

### Full fact-check record (Phase 3)

Checked 2026-11-14. Every quote below was taken from the source text fetched during this check: arXiv PDF full texts converted with pdftotext, publisher or agency HTML pages, arXiv abstract pages, or Crossref/INSPIRE metadata. Ellipses (...) mark omitted text. Hyphenation and line breaks from PDF extraction have been rejoined. Where I could not get the original text (paywalled), the entry says so and gives the source actually used.

Verdict key: **SUPPORTED**, **PARTLY** (the source supports a weaker or narrower wording), **NOT SUPPORTED**, **NOT FOUND** (no verifiable source located).

---

### A. Stars almost never collide when galaxies merge

#### A1. Stars will not / almost never collide during the Milky Way-Andromeda merger

**Verdict: SUPPORTED** by the NASA/STScI release. Neither van der Marel et al. 2012 (Paper III) nor Cox & Loeb 2008 makes this statement explicitly; I searched both full texts for "collide/collision" and found nothing about star-star collisions.

Quote (NASA Hubble Mission Team, 31 May 2012):
> "Although the galaxies will plow into each other, stars inside each galaxy are so far apart that they will not collide with other stars during the encounter. However, the stars will be thrown into different orbits around the new galactic center."

Citation: NASA Hubble Mission Team / STScI, "NASA's Hubble Shows Milky Way is Destined for Head-On Collision", news release STScI-2012-20, 31 May 2012. https://science.nasa.gov/missions/hubble/nasas-hubble-shows-milky-way-is-destined-for-head-on-collision/ (STScI listing: https://www.stsci.edu/contents/news-releases/2012/news-2012-20, which gives "Release ID: 2012-20" and "May 31, 2012"). Science credits on the release: R. van der Marel, S. T. Sohn, J. Anderson (STScI), G. Besla (Columbia).

Science papers behind the release (checked, but they do not contain the star-collision sentence):
- van der Marel, R. P., Besla, G., Cox, T. J., Sohn, S. T., & Anderson, J. 2012, "The M31 Velocity Vector. III. Future Milky Way-M31-M33 Orbital Evolution, Merging, and Fate of the Sun", ApJ 753, 9. DOI 10.1088/0004-637X/753/1/9. arXiv:1205.6865.
- Cox, T. J. & Loeb, A. 2008, "The collision between the Milky Way and Andromeda", MNRAS 386, 461-474. DOI 10.1111/j.1365-2966.2008.13048.x. arXiv:0705.1170.

Caveat for the script: the same 2012 release says NASA could "predict with certainty" the collision. Sawala et al. 2025 (see G) now puts the merger probability near 50%. Do not say the collision is certain.

**Safe narration:** "When galaxies merge, the stars are so far apart that they almost never hit each other. Gravity reshuffles their orbits instead."
(NASA says "will not collide". "Almost never" is the more careful wording and is safe.)

#### A2. Numbers for the scale analogy

**Sun's diameter: SUPPORTED**
> NASA Sun Fact Sheet: "Volumetric mean radius (km) 695,700." (Sun column)
>
> NASA Sun facts page: "Its diameter is about 865,000 miles (1.4 million kilometers)."

Citations: Williams, D. R. (NASA GSFC/NSSDCA), "Sun Fact Sheet", last updated 9 May 2024, https://nssdc.gsfc.nasa.gov/planetary/factsheet/sunfact.html ; NASA Science, "Sun: Facts", https://science.nasa.gov/sun/facts/
The diameter is 2 x 695,700 = 1,391,400 km (my arithmetic), which matches NASA's "1.4 million kilometers".

**Distance to Proxima Centauri: SUPPORTED** (NASA, ESO, ESA/Hubble)
> NASA, "What is a light-year?": "Keep going to Proxima Centauri, our nearest neighboring star, and plan on arriving in 4.25 years at light speed."
>
> Same page: "The nearest-known exoplanet is a small, probably rocky planet orbiting Proxima Centauri – the next star over from Earth. A little more than four light-years away, or 24 trillion miles."
>
> Same page: "Light zips through interstellar space at 186,000 miles (300,000 kilometers) per second and 5.88 trillion miles (9.46 trillion kilometers) per year."
>
> ESO eso1629 (24 Aug 2016): "Just over four light-years from the Solar System lies a red dwarf star that has been named Proxima Centauri as it is the closest star to Earth apart from the Sun."
>
> ESA/Hubble potw1343a: "Proxima Centauri lies in the constellation of Centaurus (The Centaur), just over four light-years from Earth."

Citations: NASA Science / Exoplanet Exploration, "What is a light-year?", https://science.nasa.gov/exoplanets/what-is-a-light-year/ ; ESO press release eso1629, "Planet Found in Habitable Zone Around Nearest Star", https://www.eso.org/public/news/eso1629/ ; ESA/Hubble Picture of the Week potw1343a, "New shot of Proxima Centauri, our nearest neighbour", https://esahubble.org/images/potw1343a/

The distance in km comes from my arithmetic using NASA's numbers: 4.25 ly x 9.46e12 km/ly = **4.02e13 km (about 40 trillion km)**. NASA's "24 trillion miles" converts to 3.86e13 km (1 mile = 1.609344 km). A rounded "about 40 trillion km" is safe.

**Typical distance between stars: PARTLY** (authoritative, but described by the source itself as rough)
> NRAO "Ask an Astronomer" (J. Mangum): "I think what you are asking for is the average distance between any two stars in our galaxy. That number turns out to be about 5 light years, which is very close to the 4 light year distance between our Sun and Alpha Centauri."
>
> NRAO follow-up (18 Feb 2022): "I don't believe that there is a standard reference for the average distance between stars in the Milky Way galaxy as this distance is a rather subjective estimate. ... the average distance between stars in the Milky Way is about 5 light years. Note, though, that this estimate has a large uncertainty."
>
> OpenStax Astronomy 2e, Sect. 1.6: "Within a sphere 10 light-years in radius centered on the Sun, we find roughly ten stars."

Citations: National Radio Astronomy Observatory, "What is the Average Distance Between Stars in our Galaxy?", https://public.nrao.edu/ask/what-is-the-average-distance-between-stars-in-our-galaxy/ ; NRAO, "Is There a Reference for Average Distance Between Stars in the Milky Way?", https://public.nrao.edu/ask/is-there-a-reference-for-average-distance-between-stars-in-the-milky-way/ ; Fraknoi, A., Morrison, D. & Wolff, S., *Astronomy 2e*, OpenStax, Houston TX, 9 Mar 2022, Sect. 1.6 "A Tour of the Universe", https://openstax.org/books/astronomy-2e/pages/1-6-a-tour-of-the-universe

**Scale analogy (MY CALCULATION, not from a source)**
Inputs: Sun diameter D = 1,391,400 km (NASA fact sheet radius x 2). Proxima distance d = 4.25 ly x 9.46e12 km/ly = 4.0205e13 km (NASA).
Ratio d/D = 4.0205e13 / 1.3914e6 = **2.89e7** (the distance is about 29 million Sun-diameters).

| Sun shrunk to | Proxima at the same scale | With NASA's "24 trillion miles" (ratio 2.78e7) | "Typical" 5 ly spacing (NRAO; ratio 3.40e7) |
|---|---|---|---|
| 1 mm grain of sand | 2.89e7 x 1 mm = 28.9 km | 27.8 km | 34 km |
| 40 mm table-tennis ball (40 mm assumed, not checked) | 2.89e7 x 40 mm = 1,156 km | 1,110 km | 1,360 km |

Check using NASA's rounded figures (1.4 million km, 4.25 ly): 4.02e13 / 1.4e6 = 2.87e7, i.e. 28.7 km at the 1 mm scale.

**Safe narration:** "Shrink the Sun to a grain of sand. The nearest star would be another grain about 30 kilometres away." Or: "Make the Sun a ping-pong ball, and the nearest star is a second ball more than a thousand kilometres away." On screen: "Scale: Sun 1.39 million km across; Proxima Centauri 4.25 light-years (about 40 trillion km). Sources: NASA."

---

### B. N-body method

#### B3. Barnes & Hut 1986 citation and opening criterion

**Citation: SUPPORTED** (Nature article page and its citation metadata)
Barnes, J. & Hut, P. 1986, "A hierarchical O(N log N) force-calculation algorithm", *Nature* 324 (6096), 446-449. Published 4 December 1986. DOI 10.1038/324446a0. https://www.nature.com/articles/324446a0 . No arXiv version (it predates arXiv). Authors' affiliation: The Institute for Advanced Study, Princeton.

Abstract (Nature page):
> "Until recently the gravitational N-body problem has been modelled numerically either by direct integration, in which the computation needed increases as N^2, or by an iterative potential method in which the number of operations grows as N log N. Here we describe a novel method of directly calculating the force on N bodies that grows only as N log N. The technique uses a tree-structured hierarchical subdivision of space into cubic cells, each of which is recursively divided into eight subcells whenever more than one particle is found to occupy the same cell."

**Opening criterion: PARTLY.** The criterion is supported, but not quoted from the original. The 1986 full text is paywalled and I could not check its wording or notation. The criterion is confirmed by a peer-reviewed review:
> Dehnen & Read 2011, Sect. 3.5.1: "The gravity at any position x from all the particles within tree cell A is then simply approximated by applying equation (53) if θ w_A < r = |x − z_A| with some opening angle θ ≤ 1. Otherwise, the sum of the potentials obtained by applying the same algorithm to the daughter cells is used (or, if the cell is a tree leaf, from direct summation over all particles within the cell)."

Here w_A is the cell's size (w_A ≥ max |x_a − z_A|) and z_A is the expansion centre. θ w_A < r is the same as w_A / r < θ, which is the s/d < θ form in the claim.
> Springel 2005 (GADGET-2), Sect. 3.1: "In the approach of Barnes & Hut (1986, BH hereafter), a cubical root node is used to encompass the full mass distribution, which is repeatedly subdivided into eight daughter nodes of half the side-length each, until one ends up with 'leaf' nodes containing single particles. Forces are then obtained by 'walking' the tree, i.e. starting at the root node, a decision is made whether or not the multipole expansion of the node is considered to provide an accurate enough partial force (which will in general be the case for nodes that are small and distant enough)."

Citations: Dehnen, W. & Read, J. I. 2011, "N-body simulations of gravitational dynamics", *Eur. Phys. J. Plus* 126, 55. DOI 10.1140/epjp/i2011-11055-3. arXiv:1105.1082. Springel, V. 2005, "The cosmological simulation code GADGET-2", *MNRAS* 364, 1105-1134. DOI 10.1111/j.1365-2966.2005.09655.x. arXiv:astro-ph/0505010.

**Safe on-screen wording:** "Barnes-Hut tree (Barnes & Hut 1986, Nature 324, 446): a distant group of stars is treated as one body when (cell size) / (distance) < θ." Cite Dehnen & Read 2011 for the formula if a source line is shown.

#### B4. Direct summation scales as N^2

**Verdict: SUPPORTED**
> Barnes & Hut 1986 abstract: "...direct integration, in which the computation needed increases as N^2..."
>
> Springel 2005, Sect. 2: "a complete force computation involves a double sum, resulting in a N^2-scaling of the computational cost. This reflects the long-range nature of gravity, where each particle interacts with every other particle"
>
> Dehnen & Read 2011: "...the cost of computing all N forces is O(N ln N)" [tree code] ... "This represents a substantial reduction from the O(N^2) for direct summation."

**Safe narration:** "Adding up every pull between every pair of stars takes work that grows as N squared. A tree code groups distant stars together and gets close to N log N."

---

### C. Eternal inflation and bubble universes

#### C5. Inflation never ends everywhere; bubbles nucleate in the false vacuum; our observable universe may sit inside one

**Verdict: SUPPORTED** as a description of the theory.
> Aguirre & Johnson 2011, abstract: "In the picture of eternal inflation as driven by a scalar potential with multiple minima, our observable universe resides inside one of many bubbles formed from transitions out of a false vacuum."
>
> Aguirre & Johnson 2011, Sect. I: "inflation proceeds forever and ceases only locally in 'pockets' or 'bubbles' that may become radiation- or matter-dominated. One of these could contain our observable universe."
>
> Feeney et al. 2011 (PRL), introduction: "In this scenario, known as eternal inflation ..., our observable universe resides inside a single bubble nucleated out of a false vacuum de Sitter space. The rate of bubble formation is outpaced by the accelerated expansion of the inflating false vacuum, and therefore inflation does not end everywhere."
>
> Guth 2007, Sect. 2.1: "Therefore, even though the false vacuum is decaying, it never disappears, and in fact the total volume of the false vacuum, once inflation starts, continues to grow exponentially with time, ad infinitum." ... "There is no standard name for these local universes, but they are often called bubble universes. I prefer, however, to call them pocket universes, to avoid the suggestion that they are round." ... "Most important of all is the simple statement that once inflation happens, it produces not just one universe, but an infinite number of universes."

Citations:
- Aguirre, A. & Johnson, M. C. 2011, "A status report on the observability of cosmic bubble collisions", *Rep. Prog. Phys.* 74, 074901. DOI 10.1088/0034-4885/74/7/074901. arXiv:0908.4105.
- Feeney, S. M., Johnson, M. C., Mortlock, D. J. & Peiris, H. V. 2011, "First Observational Tests of Eternal Inflation", *Phys. Rev. Lett.* 107, 071301. DOI 10.1103/PhysRevLett.107.071301. arXiv:1012.1995.
- Guth, A. H. 2007, "Eternal inflation and its implications", *J. Phys. A: Math. Theor.* 40, 6811-6826. DOI 10.1088/1751-8113/40/25/S25. arXiv:hep-th/0702178.
- Coleman, S. & De Luccia, F. 1980, "Gravitational effects on and of vacuum decay", *Phys. Rev. D* 21 (12), 3305-3315. DOI 10.1103/PhysRevD.21.3305 (metadata from Crossref; paywalled; not on arXiv). Abstract (INSPIRE): "It is possible for a classical field theory to have two stable homogeneous ground states, only one of which is an absolute energy minimum. In the quantum version of the theory, the ground state of higher energy is a false vacuum, rendered unstable by barrier penetration. ... In this paper, we extend this theory to include the effects of gravitation." This supplies the bubble-nucleation (CDL) mechanism, not the eternal-inflation picture itself.

Note: Guth points out that eternal *new* inflation produces irregular "pocket" universes, while bubbles from first-order (CDL) transitions are round. The bubble-collision papers use the false-vacuum (CDL) picture.

**Safe narration:** "In one idea, called eternal inflation, inflation never stops everywhere. Bubbles keep forming in it, and our whole observable universe could sit inside one of them."

#### C6. Bubbles can collide; bubble walls expand at (nearly) the speed of light

**Verdict: SUPPORTED** (within the theory; "nearly the speed of light" is the safer phrase).
> Aguirre & Johnson 2011, abstract: "These bubbles necessarily collide, upsetting the homogeneity and isotropy of our bubble interior, and possibly leading to detectable signatures in the observable portion of our bubble"
>
> Aguirre & Johnson 2011, Fig. 1 caption: "If in addition the initial radius of the bubble is small, it is possible to approximate the bubble wall as lying on the light cone"
>
> Aguirre & Johnson 2011, Sect. V A: "Assuming – as per the thin wall and small bubble approximations – that the bubbles spread as a null cone emanating from a pointlike nucleation..."
>
> Kleban, Levi & Sigurdson 2013, abstract: "These bubble universes will generically collide, and collisions with ours produce cosmic wakes that enter our Hubble volume, appear as unusually symmetric disks in the cosmic microwave background (CMB)..."
>
> Markkanen, Rajantie & Stopyra 2018, Sect. 4 (vacuum-decay bubbles generally): "the bubble nucleates with O(3,1) symmetry. This causes it to expand at near the speed of light" ... and Sect. 4.7: "it rapidly approaches the speed of light ... Thus, just as in flat space, the bubble expands outwards at the speed of light."

Citations: Aguirre & Johnson 2011 (above). Kleban, M., Levi, T. S. & Sigurdson, K. 2013, "Observing the Multiverse with Cosmic Wakes", *Phys. Rev. D* 87, 041301. DOI 10.1103/PhysRevD.87.041301. arXiv:1109.3473. Markkanen, T., Rajantie, A. & Stopyra, S. 2018, "Cosmological Aspects of Higgs Vacuum Metastability", *Front. Astron. Space Sci.* 5, 40. DOI 10.3389/fspas.2018.00040. arXiv:1809.06923.

**Safe narration:** "If this picture is right, bubbles can collide, and their walls race outward at nearly the speed of light."

#### C7. Eternal inflation / the multiverse is speculative (not established)

**Verdict: SUPPORTED**, with quotes from the same reviews.
> Guth 2007, conclusions: "Although eternal inflation has fascinating consequences, our understanding of it remains incomplete." ... "It is the success of these predictions that justifies spending time on the more speculative aspects of inflationary cosmology."
>
> Guth 2007, abstract: "Although the infinity of pocket universes produced by eternal inflation are unobservable, ..."
>
> Feeney et al. 2011 (PRL): "Although there is ample motivation to consider the eternal inflation scenario, a concrete model (of, say, the string theory landscape) providing all of these details does not currently exist."
>
> Feeney et al. 2011 (PRL) abstract: "Data from the Planck satellite can be used to more definitively test the bubble collision hypothesis."
>
> Aguirre & Johnson 2011, Sect. I: "collisions between bubbles just might leave relic observable signatures, and hence provide – if we are very fortunate – a direct way to test the eternal inflation scenario."
>
> Aguirre & Johnson 2011, Sect. VI: "While requiring no small amount of good fortune, the detection of such a signal would truly be an epochal discovery." ... "While we currently do not have strong grounds either observationally or theoretically to single out a specific inflaton model..."
>
> NASA/IPAC U.S. Planck Data Center feature (22 Feb 2016): "But do multiple universes really exist? Scientists continue to debate the concept and come up with new theories." ... "The research is still in its infancy, and more testing is needed before any firm conclusions can be drawn."

Extra citation: NASA/IPAC U.S. Planck Data Center, "Looking Within Our Universe For Something Beyond", 22 Feb 2016, https://planck.ipac.caltech.edu/news/planck16-001

**Safe narration / on-screen tag:** "This is a hypothesis. Nobody has observed another universe."

---

### D. Observational searches

#### D8. A past collision would leave an azimuthally symmetric, disc-shaped patch on the CMB

**Verdict: SUPPORTED** as a prediction. Only the boundary of the patch is a ring; the predicted temperature modulation fills the disc inside it.
> Feeney et al. 2011 (PRL): "Azimuthal symmetry: A collision between two bubbles leaves an imprint on the CMB sky that has azimuthal symmetry. This is a consequence of the SO(2,1) symmetry of the spacetime describing the collision of two vacuum bubbles. Causal boundary: The surface of last scattering can only be affected inside the future light cone of a collision event, which forms a ring on the CMB sky. The observed temperature of the CMB need not be continuous across this boundary."
>
> Feeney et al. 2011 (PRD), Sect. I: "From the spherical symmetry of the colliding bubbles, the collision possess azimuthal symmetry, and by causality must be confined to a disc on the sky."
>
> Feeney et al. 2011 (PRD), Fig. 2 caption: "The region affected by the collision appears as a disc of angular radius θ_crit on the CMB sky."
>
> Aguirre & Johnson 2011, Sect. III: "a single collision retains an azimuthal symmetry on the sky. ... appears as circle on the observer's sky, the disk interior to which represents the part of this surface possibly affected by the collision."

Citations: Feeney et al. 2011 PRL (above). Feeney, S. M., Johnson, M. C., Mortlock, D. J. & Peiris, H. V. 2011, "First observational tests of eternal inflation: Analysis methods and WMAP 7-year results", *Phys. Rev. D* 84, 043507. DOI 10.1103/PhysRevD.84.043507. arXiv:1012.3667.

**Safe narration:** "A collision in our distant past would show up as a round patch on the cosmic microwave background, a disc with a sharp edge."

#### D9. WMAP 7-year result

**Verdict: SUPPORTED.** No evidence was found; there is an upper limit on the expected number of detectable collisions.
> Feeney et al. 2011 (PRL) abstract: "We conclude that the WMAP 7-year data do not warrant augmenting ΛCDM with bubble collisions, constraining the average number of detectable bubble collisions on the full sky N̄s < 1.6 at 68% CL."
>
> Feeney et al. 2011 (PRL) body: "Therefore, the WMAP 7-year data-set does not favor the bubble collision hypothesis for any value of N̄s; from the posterior we find N̄s < 1.6 at 68% probability."
>
> Same paper: "We can therefore rule out the presence of any large-angular-scale bubble collisions with values of {z0, zcrit} in the CHT exclusion region of Fig. 2."
>
> Same paper, nuance: "Interestingly, however, the Bayesian evidence ratios obtained for four of the features in the WMAP data are systematically larger than expected from false detections"
>
> Feeney et al. 2011 (PRD) abstract: "Our model selection results based on WMAP 7-year data do not warrant augmenting ΛCDM with bubble collisions."

**Safe narration:** "Astronomers searched NASA's WMAP map for such discs. They found no convincing sign of one."
On screen: "WMAP 7-yr: average number of detectable collisions < 1.6 (68% confidence). Feeney et al. 2011."

#### D10. Later searches, and whether a Planck-data search was published

**Verdict:** No published search of Planck data with the standard disc template (the Feeney/McEwen/Osborne type) was found, either peer-reviewed or by the Planck Collaboration. **One** peer-reviewed paper used Planck maps in a different (spectral) way and reported unconfirmed anomalies (Chary 2016). The latest peer-reviewed template searches use WMAP 7-year data (2013).

1. **Feeney et al. 2013 (WMAP7, latest peer-reviewed template search, SUPPORTED):**
   > "We conclude that the WMAP 7-year data do not favor the addition of either cosmic textures or bubble collisions to the standard cosmological model, and place robust constraints on the predicted number of such sources. The expected numbers of bubble collisions and cosmic textures on the CMB sky within our detection thresholds are constrained to be fewer than 4.0 and 5.2 at 95% confidence, respectively."

   Feeney, S. M., Johnson, M. C., McEwen, J. D., Mortlock, D. J. & Peiris, H. V. 2013, "Hierarchical Bayesian detection algorithm for early-universe relics in the cosmic microwave background", *Phys. Rev. D* 88, 043012. DOI 10.1103/PhysRevD.88.043012. arXiv:1210.2725.
2. **McEwen et al. 2012 (WMAP7 candidates):**
   > "Applying our algorithm to WMAP 7-year observations, we detect eight new candidate bubble collision signatures for follow-up analysis."

   These are candidates to follow up, not detections. McEwen, J. D., Feeney, S. M., Johnson, M. C. & Peiris, H. V. 2012, "Optimal filters for detecting cosmic bubble collisions", *Phys. Rev. D* 85, 103502. DOI 10.1103/PhysRevD.85.103502. arXiv:1202.2861.
3. **Osborne, Senatore & Smith 2013 (WMAP7, arXiv preprint; no journal reference found):**
   > "We find no detectable signal, and constrain the amplitude, a, of the initial curvature perturbation that would be generated by a collision: -4.66 × 10^-8 < a (sin θ_bubble)^(4/3) < 4.73 × 10^-8 [Mpc^-1] at 95% confidence"

   arXiv:1305.1964, "Collisions with other Universes: the Optimal Analysis of the WMAP data". Companion methods paper: Osborne, Senatore & Smith 2013, "Optimal analysis of azimuthal features in the CMB", *JCAP* 10 (2013) 001, DOI 10.1088/1475-7516/2013/10/001, arXiv:1305.1970.
4. **Chary 2016 (Planck maps, spectral method; claim unconfirmed):**
   > "We analyze the spectral properties of masked, foreground-cleaned maps between 100 and 545 GHz constructed from the Planck dataset. Four distinct ~2-4° regions associated with CMB cold spots show anomalously strong 143 GHz emission but no correspondingly strong emission at either 100 or 217 GHz." ... "A plausible explanation is that the collision of our Universe with an alternate Universe whose baryon to photon ratio is a factor of ~4500 larger than ours, could produce enhanced Hydrogen Paschen-series emission at the epoch of recombination. Future spectral mapping and deeper observations at 100 and 217 GHz are needed to mitigate systematics arising from unknown Galactic foregrounds and to confirm this unusual hypothesis."

   Chary, R.-R. 2016, "Spectral Variations of the Sky: Constraints on Alternate Universes", *ApJ* 817, 33. DOI 10.3847/0004-637X/817/1/33. arXiv:1510.00126. NASA/IPAC feature (above): "'Unusual claims like evidence for alternate universes require a very high burden of proof,' said Ranga-Ram Chary". The narration should NOT present this as evidence.
5. **Planck Collaboration papers:** Planck 2015 XVI (isotropy and statistics) names a bubble collision as one proposed explanation of the Cold Spot. It does not run a search:
   > "several non-standard physical mechanisms have been proposed as possible explanations. These include ... a cosmic bubble collision within the eternal inflation framework (Czech et al. 2010; Feeney et al. 2011; McEwen et al. 2012)" ... "Since the other scenarios lack additional evidence, the void hypothesis would seem to be the most plausible" ... "a specific pattern might be expected in a bubble collision scenario (Czech et al. 2010). Appropriate tests will be pursued in future work, once the large-scale polarization data are available."

   Planck Collaboration 2016, "Planck 2015 results. XVI. Isotropy and statistics of the CMB", *A&A* 594, A16, DOI 10.1051/0004-6361/201526681, arXiv:1506.07135. Neither Planck 2018 VII (*A&A* 641, A7, DOI 10.1051/0004-6361/201935201, arXiv:1906.02552) nor Planck 2013 XXIII (arXiv:1303.5083) contains the word "bubble" (full-text search).
6. **Forecasts, not searches:** Feeney, Elsner, Johnson & Peiris 2015, "Forecasting constraints from the cosmic microwave background on eternal inflation", *Phys. Rev. D* 92, 083515, DOI 10.1103/PhysRevD.92.083515, arXiv:1506.01716:
   > "We can therefore view data from Planck as having the final word on bubble collisions in the CMB."

   This is a forecast of what Planck *could* do, not a Planck result. The most recent related paper found is Cai, Zhang & Guan 2026, "Eternal inflation bubble collision signature on CMB remote dipole and quadrupole fields", *Phys. Rev. D* 113, 063545, DOI 10.1103/4c9h-tk5t, arXiv:2510.12134 (also a forecast).
7. **Unverified grey literature:** a 2024 conference contribution (indico.global event 12919, contribution 113513, workshop "Standard Model and Beyond 2024") reportedly ran a blob-detection search on 2021 Planck CMB data and found no features meeting its thresholds, while flagging 14 features as possible candidates. **NOT VERIFIED**: the page was behind a bot check and I could not read it. It is not peer-reviewed. Do not use.

**Safe narration:** "Searches of NASA's WMAP data found no convincing collision. ESA's sharper Planck maps have not turned one up either." The "not turned one up" claim rests on the absence of any published detection. Safer still: "No convincing evidence has been found so far."
Do NOT say "Planck ruled it out".

#### D11. Future tests (polarization etc.)

**Verdict: SUPPORTED**
> Czech et al. 2010, abstract: "We predict the polarization of cosmic microwave background (CMB) photons that results from a cosmic bubble collision. The polarization is purely E-mode, symmetric around the axis pointing towards the collision bubble, and has several salient features in its radial dependence that can help distinguish it from a more conventional explanation for unusually cold or hot features in the CMB sky."
>
> Feeney et al. 2015, abstract: "...we find that there is no improvement to be gained from future temperature data, that adding polarization improves detectability by approximately 30%, and that cosmic-variance-limited polarization data offer only marginal improvements over Planck."
>
> Cai, Zhang & Guan 2026, abstract: "We find that, for an CMB-S4-like and an LSST-like experiment, the RDF reconstruction can provide comparable constraining power as that from the primary CMB alone; and the RQF reconstruction can improve the constraining power by about an order of magnitude."

Citation: Czech, B., Kleban, M., Larjo, K., Levi, T. S. & Sigurdson, K. 2010, "Polarizing bubble collisions", *JCAP* 12 (2010) 023. DOI 10.1088/1475-7516/2010/12/023. arXiv:1006.0832.

**Safe narration:** "Future maps of the CMB's polarization, along with other new probes, could test the idea further."

---

### E. A collision in our future

#### E12. A wall would arrive at nearly light speed, with no warning

**Verdict: PARTLY.**
- "Walls move at (nearly) the speed of light": SUPPORTED (C6; Markkanen et al. 2018).
- "No warning": **NOT FOUND** as a statement in any peer-reviewed source I could read. It is a reasonable inference (a wall moving at almost c arrives almost together with any light that could announce it), but no source says it. The closest peer-reviewed wording:
  > Markkanen, Rajantie & Stopyra 2018, Sect. 5.1: "This is because, once nucleated, a bubble of true vacuum expands at the speed of light and destroys everything in its way. If even a single bubble had nucleated at any time, anywhere in our past lightcone, it would have already hit us."
  >
  > Same paper, Sect. 6: "Once a bubble has formed, it expands at the speed of light, destroying everything in its way."

  This is about **vacuum decay** (true-vacuum bubbles in our universe), not about collisions with other bubble universes.
- Bubble *collisions* can be fatal in some models:
  > Aguirre & Johnson 2011, Sect. I: "1. Fatal: collisions that either destroy, or prevent the formation of, physical observers to their future."
- **Coleman & De Luccia 1980, the famous passage.** I could not read the original (APS, paywalled; the APS page returned 403). The text below is as reproduced verbatim, with attribution, in Banks, T. 2002, "Heretics of the False Vacuum: Gravitational Effects On and Of Vacuum Decay. 2.", arXiv:hep-th/0211160 (Introduction epigraph):
  > "The possibility that we are living in a false vacuum has never been a cheering one to contemplate. Vacuum decay is the ultimate ecological catastrophe; in a new vacuum there are new constants of nature; after vacuum decay, not only is life as we know it impossible, so is chemistry as we know it. However, one could always draw stoic comfort from the possibility that perhaps in the course of time the new vacuum would sustain, if not life as we know it, at least some structures capable of knowing joy. This possibility has now been eliminated." (S. Coleman, F. De Luccia, 1980)

  **What it covers:** it is about **vacuum decay** (our false vacuum decaying into a lower one), specifically the gravitational result that decay into a negative-energy vacuum collapses. It does **not** mention bubble collisions, wall speed, or warning. Some secondary sources write "in the new vacuum" rather than "in a new vacuum". Check the wording against the APS original before quoting it on screen.
- **Coleman 1977**: Coleman, S. 1977, "Fate of the false vacuum: Semiclassical theory", *Phys. Rev. D* 15 (10), 2929-2936, DOI 10.1103/PhysRevD.15.2929. The INSPIRE abstract does not mention the wall speed, and the full text is paywalled, so its wording on the wall approaching light speed is **NOT FOUND / not verified**.
- Turner, M. S. & Wilczek, F. 1982, "Is our vacuum metastable?", *Nature* 298, 633-634, DOI 10.1038/298633a0. The visible abstract has no "warning" wording; the full text is paywalled. **NOT VERIFIED.**

**Safe narration (recommended):** "If such a wall ever reached us, it would be moving at nearly the speed of light, so we would get almost no warning. But this is pure speculation: there is no evidence that any such wall is coming."
If vacuum decay is mentioned, keep it separate: "A related idea, vacuum decay, would also spread at nearly light speed (also speculative)."
Do not attribute "no warning" to Coleman or to Coleman & De Luccia.

---

### F. Data credit: Planck 2018 SMICA CMB map

#### F13. Citation, file location, acknowledgement

**Citation: SUPPORTED**
Planck Collaboration (Akrami, Y. et al.) 2020, "Planck 2018 results. IV. Diffuse component separation", *A&A* 641, A4. DOI 10.1051/0004-6361/201833881. arXiv:1807.06208. (Also listed on ESA's page: "Planck 2018 results. IV. Diffuse component separation Planck Collaboration 2020, A&A, 641, A4".)

**Files (IRSA directory listing, checked 2026-11-14; byte counts from HTTP Content-Length; columns read from the FITS headers via a small byte-range request):**
Directory: https://irsa.ipac.caltech.edu/data/Planck/release_3/all-sky-maps/maps/component-maps/cmb/

| File | Listing size | Exact bytes | Contents (FITS header) |
|---|---|---|---|
| `COM_CMB_IQU-smica_2048_R3.00_full.fits` (standard SMICA, full mission) | 1.9G | 2,013,312,960 | 10 float32 columns: I_STOKES, Q_STOKES, U_STOKES, TMASK, PMASK, I/Q/U_STOKES_INP, TMASKINP, PMASKINP. HEALPix Nside 2048, NESTED, GALACTIC, K_CMB |
| `COM_CMB_IQU-smica-nosz_2048_R3.00_full.fits` (SMICA SZ-free, **smallest full-mission SMICA file**) | 384M | 402,661,440 | 2 columns: I_STOKES, I_STOKES_INP (temperature only). Nside 2048, NESTED, GALACTIC, K_CMB |
| `..._hm1/_hm2/_oe1/_oe2.fits` variants | 192M (nosz) / 576M (smica) | — | Half-mission / odd-even splits. Not recommended for a display map |

- Direct URL (smallest suitable): https://irsa.ipac.caltech.edu/data/Planck/release_3/all-sky-maps/maps/component-maps/cmb/COM_CMB_IQU-smica-nosz_2048_R3.00_full.fits
- Direct URL (standard SMICA): https://irsa.ipac.caltech.edu/data/Planck/release_3/all-sky-maps/maps/component-maps/cmb/COM_CMB_IQU-smica_2048_R3.00_full.fits
- There is **no Nside 1024 SMICA map** in the PR3 CMB directory. Nside 1024 appears only for the SEVEM 70 GHz cleaned maps. PLA wiki: "All CMB products are provided at an approximate angular resolution of 5 arcmin FWHM, and HEALPix resolution N_side=2048."
- What the SZ-free variant is (PLA wiki, "CMB maps"): "In addition, for SMICA, we also provide a CMB map from which Sunyaev-Zeldovich (SZ) sources have been projected out". Planck 2018 IV, Appendix D: "SZ-free CMB map: A CMB map free of SZ contamination is produced by a simple adaptation of Eq. (2)". If you use it, credit it as "SMICA (SZ-free)". For a visual it is practically the same as the standard SMICA temperature map, but the label should be accurate.
- IRSA dataset DOI: 10.26131/IRSA558 ("Planck Public Data Release 3 Maps", publisher IPAC, author "Planck team"), https://doi.org/10.26131/IRSA558
- ESA Planck Legacy Archive alternative: https://pla.esac.esa.int/pla/aio/product-action?MAP.MAP_ID=COM_CMB_IQU-smica_2048_R3.00_full.fits . This returned HTTP 503 at check time, so it is **not verified today**.
- PLA wiki CMB maps page: https://wiki.cosmos.esa.int/planck-legacy-archive/index.php/CMB_maps

**Acknowledgement text:**
> ESA Planck publications page: "If you use any of these results for presentations, please acknowledge the corresponding paper, ESA/Planck, and the Planck Collaboration." (https://www.cosmos.esa.int/web/planck/publications)
>
> ESA image page for the Planck 2018 CMB map: "Credits ESA/Planck Collaboration Licence ESA Standard Licence" (https://www.esa.int/ESA_Multimedia/Images/2018/07/Planck_s_view_of_the_cosmic_microwave_background)
>
> IRSA acknowledgement page: "This research has made use of the NASA/IPAC Infrared Science Archive, which is funded by the National Aeronautics and Space Administration and operated by the California Institute of Technology." (https://irsa.ipac.caltech.edu/ack.html; IRSA asks for this "in addition to any further acknowledgments required by individual missions and data providers")
>
> The widely used sentence "Based on observations obtained with Planck (http://www.esa.int/Planck), an ESA science mission with instruments and contributions directly funded by ESA Member States, NASA, and Canada." was found verbatim in the acknowledgements of Clements, D. L. 2017, "An Introduction to the Planck Mission", arXiv:1707.09220. **I did not find it on an official ESA page in this check**, so treat it as standard practice rather than a documented requirement.

**Suggested on-screen credit:** "Cosmic microwave background: ESA/Planck Collaboration. Planck 2018 SMICA map (Planck Collaboration 2020, A&A 641, A4), via NASA/IPAC IRSA." In the description/end card, add the IRSA sentence and the "Based on observations obtained with Planck..." sentence.

---

### G. Two narration numbers

#### G-a. Andromeda is about 2.5 million light-years away (770 kpc)

**Verdict: SUPPORTED**
> NASA 2012 release: "The galaxy is now 2.5 million light-years away"
>
> van der Marel et al. 2012 (Paper II), Sect. 2: "Throughout this paper we adopt D = 770 ± 40 kpc (see references in vdMG08)."

Citation for 770 kpc: van der Marel, R. P., Fardal, M., Besla, G. et al. 2012, "The M31 Velocity Vector. II. Radial Orbit Towards the Milky Way and Implied Local Group Mass", *ApJ* 753, 8. DOI 10.1088/0004-637X/753/1/8. arXiv:1205.6864. (Paper III, ApJ 753, 9, uses the same value and cites Paper II.)
My calculation: 770 kpc x 3.26 ly/pc = 2.51 million ly, which is consistent.
**Safe narration:** "about 2.5 million light-years away".

#### G-b. About a 50% chance of a merger within the next 10 billion years

**Verdict: SUPPORTED.** The abstract states the complement.
> Sawala et al. 2025, abstract: "...uncertainties in the present positions, motions and masses of all galaxies leave room for drastically different outcomes and a probability of close to 50% that there will be no Milky Way–Andromeda merger during the next 10 billion years. Based on the best available data, the fate of our Galaxy is still completely open."
>
> Same paper, body: "About half of the systems reach the merger threshold within 10 Gyr, whereas the vast majority of the remaining systems do not approach closer than 200 kpc."

Citation: Sawala, T., Delhomelle, J., Deason, A. J., Frenk, C. S., Häkkinen, J., Johansson, P. H., Keitaanranta, A., Rawlings, A. et al. 2025, "No certainty of a Milky Way–Andromeda collision", *Nature Astronomy* 9, 1206-1217. DOI 10.1038/s41550-025-02563-1. https://www.nature.com/articles/s41550-025-02563-1
**Safe narration:** "Recent estimates give roughly a 50-50 chance that the Milky Way and Andromeda merge within the next 10 billion years."

---

### Claims that must be marked "speculative" on screen

1. That eternal inflation is real, and that a multiverse of other "bubble" or "pocket" universes exists.
2. That our observable universe sits inside one such bubble.
3. That bubbles collide with ours, or that any collision happened in our past.
4. Any disc drawn on the real Planck/WMAP map to show a collision imprint. Label it "illustration of a predicted signature; none has been found".
5. Any "universe collision" visual or simulation. These are artistic, not N-body results of real physics.
6. A future collision, or a bubble wall arriving at nearly light speed with "no warning". The "no warning" part is an inference with no source (see E12).
7. Vacuum decay, if mentioned. It is a separate speculative scenario and must not be conflated with bubble collisions.
8. The CMB Cold Spot, or Chary's 143 GHz patches, as collision evidence. These are unconfirmed proposals; Planck 2015 XVI calls the void explanation "the most plausible".
9. The Andromeda merger outcome. It is a probability estimate (~50% within 10 Gyr), not a certainty. Mark it "estimate", not "speculative".

These are established and need no tag: stars almost never collide in galaxy mergers; the scale numbers; N^2 direct summation and the Barnes-Hut tree method; the existence and features of the CMB maps; the WMAP null result (state it as a measured upper limit).
