# Sources

Every number used in the simulation and (later) on screen is listed here with its source.
Section 1 maps the parameter file `scenarios/mw_m31_vdm2012.yaml` to the papers. Section 2 lists
what we assumed because no source gives it. Section 3 compares our run with the published one. Section 4 holds the full verification notes:
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
