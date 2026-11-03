# Survey 02 — PHIDP/KDP (Stage 3), attenuation (Stage 4), hydrometeor classification and melting layer (Stage 5)

*radar-wow literature survey. Compiled 2026-11-03. Every DOI below was resolved against `https://api.crossref.org/works/<DOI>` on that date. Crossref's author, year, title and venue were checked against the citation. Items without a DOI, or whose DOI could not be resolved, are marked **DOI unverified**.*

## 0. Introduction and scope

This survey covers three consecutive radar-wow stages. All of them run on xradar DataTrees with ODIM moment names.

| Stage | Package | Consumes | Produces |
|---|---|---|---|
| 3 PHIDP/KDP | `radarwow-kdp` | PHIDP, RHOHV, DBZH, ZDR, SNRH, SQIH | unfolded/offset-corrected PHIDP, KDP, (delta) |
| 4 Attenuation | `radarwow-attenuation` | DBZH, ZDR, PHIDP (processed), KDP, ML height/HCA mask | corrected DBZH/ZDR, specific attenuation A (AH), differential attenuation ADP |
| 5 Classification | `radarwow-classification` | DBZH, ZDR, KDP, RHOHV, (LDR n/a), T or ML height | hydrometeor class + confidence, ML top/bottom, QVP products |

**Already implemented in radar-wow.** KDP: Vulpiani 2012, Giangrande 2013 linear programming (LP), and "moving regression". Attenuation: linear-PHIDP, ZPHI, and the Bringi 2001 self-consistent method, with alpha = 0.015 / 0.08 / 0.28 dB/deg at S / C / X. On real data, LP gave the best phase closure.

**Citation check (resolved, citation correct).** The survey agent first flagged Wolfensberger et al. 2021 AMT (doi:10.5194/amt-14-3169-2021) as the wrong source for radar-wow's moving-regression KDP, because the abstract describes the RainForest QPE only. The full text settles it: *Appendix A, "Computation of Kdp and Ah"* describes the method. The raw Psi_dp is corrected for the system offset, filtered with a moving median, and KDP is half the slope of a moving linear regression, with the same window for both. The appendix cites Wolfensberger et al. 2018 and Timothy et al. 1999 as the origin of the approach. `MovingRegressionKDP` implements that appendix, so the citation stands (checked against the AMT HTML on 2026-11-03). The method is also the generic least-squares-fit (LSF) baseline used on NEXRAD and in wradlib `kdp_from_phidp`. Reimann, Simmer & Trömel 2021 is an LWC-estimator paper and is not a KDP-method reference.

Column conventions in the tables below:
- **Bands:** S/C/X applicability and caveats.
- **Inputs:** ODIM names.
- **Code:** open-source implementation, if one exists.
- **Arch?:** whether the method can be implemented from archived moments alone (Y), or needs time series/IQ, other radars or extra data (N/partial).

---

## 1. Stage 3 — PHIDP processing and KDP

### 1a. PHIDP unfolding, system offset, texture masking

| Sub-component | Method | Paper | What it does (plain English) | Bands | Inputs | Code | Operational | Arch? |
|---|---|---|---|---|---|---|---|---|
| Masking / processing | Coherent dual-pol processing framework | Hubbert, Chandrasekar, Bringi & Meischner 1993, JTECH, doi:10.1175/1520-0426(1993)010<0155:PAIOCD>2.0.CO;2 | Lays out how PHIDP is measured, what corrupts it (noise, delta, wrapping), and how to interpret it. | S/C/X | PHIDP, RHOHV | — | background | Y |
| Unfolding + system offset | Offset from first valid rain gates; unfold with monotone constraint | Giangrande et al. 2013 (LP, below); Wang & Chandrasekar 2009 (below) | Estimates the system PHIDP offset from the first N "good" rain gates per ray, then unwraps 180/360 deg folds before differentiating. | S/C/X (X folds more often) | PHIDP, RHOHV, DBZH | Py-ART `phase_proc_lp` (offset + unfold); wradlib `dp` module | NEXRAD, MeteoSwiss | Y |
| Texture masking | PHIDP texture / complex-phase texture | Gourley, Tabary & Parent du Chatelet 2006, JTECH, doi:10.1175/JTECH1912.1 | Uses the local standard deviation of PHIDP (and other moments) to flag noisy, non-meteorological gates before KDP. | C (generic) | PHIDP, RHOHV, DBZH | Py-ART `texture_of_complex_phase` | Météo-France | Y |
| Offset via calibration | PHIDP-based Z calibration (self-consistency) | Vivekanandan et al. 2003, Radio Sci., doi:10.1029/2002RS002676 | Uses the PHIDP–Z consistency in rain to check reflectivity calibration. A by-product is a check on PHIDP quality. | S | DBZH, ZDR, PHIDP | — | research | Y |

### 1b. Backscatter differential phase (delta) removal

| Sub-component | Method | Paper | What it does | Bands | Inputs | Code | Operational | Arch? |
|---|---|---|---|---|---|---|---|---|
| delta filtering | Iterative FIR range filter | Hubbert & Bringi 1995, JTECH, doi:10.1175/1520-0426(1995)012<0643:AIFTFT>2.0.CO;2 | Repeatedly low-pass filters PHIDP and keeps the filtered value wherever the raw minus filtered difference is large. This strips the bumps caused by delta in big drops and hail. | S/C/X; essential at C/X, where delta reaches several degrees in Mie-scattering drops | PHIDP, RHOHV | CSU_RadarTools `csu_kdp` (https://github.com/CSU-Radarmet/CSU_RadarTools) | CSU, many research | Y |
| delta estimation | delta variability climatology | Trömel et al. 2013, JAMC, doi:10.1175/JAMC-D-13-0124.1 | Estimates delta and documents how variable it is (rain, melting layer, hail). Shows delta is not negligible at C/X. | X/C (Bonn) | PHIDP, ZDR, DBZH | — | research | Y |
| Joint KDP + delta | Constrained joint estimation | Otto & Russchenberg 2011, IEEE GRSL, doi:10.1109/LGRS.2011.2145354 | Fits KDP and delta together, using the physical link between delta and ZDR in rain. | X/C | PHIDP, ZDR | — | research | Y |
| Joint A + delta | Short-path A/delta estimator | Reinoso-Rondinel, Unal & Russchenberg 2018, JTECH, doi:10.1175/JTECH-D-17-0219.1 | Estimates specific attenuation and delta over short rain paths, where ZPHI is unstable. | X | DBZH, ZDR, PHIDP | — | research | Y |
| LP + classification delta | LP restricted to Rayleigh rain + delta retrieval | Mishler et al. 2024, JAMC, doi:10.1175/JAMC-D-23-0204.1 | Applies LP only over Rayleigh rain gates and attributes the remainder to delta. Reduces KDP bias in hail and debris, and delta becomes a hail/debris signature. | S (NEXRAD), principle applies at C/X | PHIDP, DBZH, ZDR, RHOHV, classification | — | NEXRAD research | Y |
| delta in hot spots | Hot-spot attenuation/delta | Carey et al. 2000, JAM, doi:10.1175/1520-0450(2000)039<1405:CPEICB>2.0.CO;2 | Identifies tropical big-drop "hot spots" where delta and propagation effects are extreme at C band. | C (tropical, Darwin) | DBZH, ZDR, PHIDP | — | BMRC/Darwin | Y |

### 1c. KDP estimators

| Method | Paper | What it does | Bands | Inputs | Code | Operational | Arch? |
|---|---|---|---|---|---|---|---|
| Moving-window least-squares slope (LSF) | Classic baseline (e.g. Ryzhkov & Zrnić 1996, JAM, doi:10.1175/1520-0450(1996)035<2080:AORMTU>2.0.CO;2 explains the use and benefit of R(KDP)) | Takes KDP as half the slope of PHIDP over a sliding range window. Window length is the trade-off between noise and resolution. | S/C/X | PHIDP | wradlib `kdp_from_phidp`; NEXRAD | NEXRAD ORPG | Y |
| Iterative FIR | Hubbert & Bringi 1995 (above) | FIR-smoothed PHIDP, then derivative; delta-robust. | S/C/X | PHIDP, RHOHV | CSU_RadarTools | research | Y |
| **Vulpiani (implemented)** | Vulpiani et al. 2012, JAMC, doi:10.1175/JAMC-D-10-05024.1 | Iterative moving-window derivative: KDP → integrate to PHIDP → re-derive, with KDP limits per band. Built for C band in mountains. | C (tuned), S/X with re-tuning | PHIDP | Py-ART `kdp_vulpiani`; wradlib `phidp_kdp_vulpiani` | DPC Italy | Y |
| Adaptive range filter (CASA) | Wang & Chandrasekar 2009, JTECH, doi:10.1175/2009JTECHA1358.1 | Adapts the filter length to the PHIDP signal level, from short windows in heavy rain to long windows in light rain. Includes unfolding and delta handling. | X (CASA), S/C | PHIDP, RHOHV, DBZH | — | CASA DFW | Y |
| Extended Kalman filter | Schneebeli & Berne 2012, JTECH, doi:10.1175/JTECH-D-10-05053.1 | State-space filter that jointly estimates PHIDP, KDP and delta along a ray. | X | PHIDP, DBZH, ZDR | — | research | Y |
| **Giangrande LP (implemented)** | Giangrande, McGraw & Lei 2013, JTECH, doi:10.1175/JTECH-D-12-00147.1 | Linear programming finds the closest monotone, non-decreasing PHIDP profile, so KDP ≥ 0. Gives physically consistent PHIDP for attenuation correction. | S/C/X | PHIDP, DBZH, RHOHV | Py-ART `phase_proc_lp`, `phase_proc_lp_gf` | ARM, research | Y |
| Variational (monotone) | Maesaka, Iwanami & Maki 2012, ERAD 2012 proceedings — **DOI unverified** (no DOI; conference) | Variational retrieval that forces cumulative PHIDP to be monotone (KDP ≥ 0) below the melting layer. | X (Japan), S/C | PHIDP | Py-ART `kdp_maesaka` | research | Y |
| Kalman filter ensemble | Schneebeli et al. 2014, IEEE TGRS, doi:10.1109/TGRS.2013.2287017 | Runs several Kalman filters tuned for different KDP regimes, averages them, and outputs KDP uncertainty. | X/C (MeteoSwiss), S | PHIDP | Py-ART `kdp_schneebeli`; pyrad | MeteoSwiss | Y |
| LP + physics hybrid | Huang, Zhang, Doviak et al. 2017, IEEE TGRS, doi:10.1109/TGRS.2016.2596295 | Combines LP KDP with a Z-based KDP constraint in light rain, where PHIDP noise dominates. | S | PHIDP, DBZH, ZDR | — | research | Y |
| Adaptive high-res | Reinoso-Rondinel et al. 2018, JTECH, doi:10.1175/JTECH-D-17-0105.1 | Adaptive window, high-resolution KDP for X band. Includes an intercomparison with other estimators. | X | PHIDP, DBZH | — | research | Y |
| LP + delta classification | Mishler et al. 2024 (above) | Newest LP variant; separates KDP from delta. | S (C/X principle) | PHIDP + class | — | research | Y |
| KDP from Z–ZDR self-consistency | Scarchilli, Gorgucci, Chandrasekar & Dobaie 1996, IEEE TGRS, doi:10.1109/36.481887 | In rain, KDP can be predicted from Z and ZDR. Useful as a fallback where PHIDP is noisy, and for checking calibration. | S/C (X with care) | DBZH, ZDR | — | research | Y |

### 1d. KDP in snow / ice / low SNR

| Method | Paper | What it does | Bands | Code | Arch? |
|---|---|---|---|---|---|
| QVP averaging for KDP in ice | Ryzhkov et al. 2016, JTECH, doi:10.1175/JTECH-D-15-0020.1 | Azimuthal averaging at high elevation brings small KDP (0.05–0.2 deg/km) in snow and the dendritic-growth layer above noise. | S/C/X | Py-ART `compute_qvp`; wradlib | Y |
| KDP in melting and DGL layers | Trömel, Ryzhkov, Hickman & Mühlbauer 2019, JAMC, doi:10.1175/JAMC-D-19-0056.1 | Documents KDP/ZDR signatures in the dendritic-growth and melting layers at X band; uses them for nowcasting. | X | — | Y |
| KDP in DGL (validation) | Kötsche, Myagkov, von Terzi & Maahn 2025, ACP, doi:10.5194/acp-25-14045-2025 | Recent work on KDP signatures inside and below the DGL with W-band Doppler radar. | W/X | — | partial |
| Snow from KDP and Z | Bukovčić et al. 2018, JAMC, doi:10.1175/JAMC-D-17-0090.1 | S(KDP, Z) snow-rate relations. These need reliable low-SNR KDP, usually from QVP or heavy averaging. | S/C/X | — | Y |
| LWC estimators (negative-KDP handling) | Reimann, Simmer & Trömel 2021, Met. Z., doi:10.1127/metz/2021/1072 | LWC from KDP. Where KDP < 0, it is replaced by a Z-based KDP. A practical low-SNR fallback rule. | C (DWD) | — | Y |

### 1e. KDP evaluations / benchmarks

| Paper | Finding (from abstracts) |
|---|---|
| Grazioli et al. 2014, IEEE GRSL, doi:10.1109/LGRS.2013.2278620 | Benchmarks phase-based KDP algorithms on simulated polarimetric data, which gives a known truth. |
| Reinoso-Rondinel et al. 2018 (above) | X-band intercomparison of KDP estimators with an adaptive method. |
| Huang et al. 2017 (above) | LP compared with the hybrid physics-constrained estimator; LP is noisy in light rain. |
| Mishler et al. 2024 (above) | LP compared with operational LSF on hail/debris cases; delta biases LSF KDP. |
| radar-wow internal | LP has the best phase closure on real data. This is consistent with LP enforcing monotone PHIDP, which ZPHI/self-consistent attenuation needs. |

---

## 2. Stage 4 — Attenuation and differential attenuation

| Sub-component | Method | Paper | What it does | Bands | Inputs | Code | Operational | Arch? |
|---|---|---|---|---|---|---|---|---|
| Z-only (historical) | Hitschfeld–Bordan | Hitschfeld & Bordan 1954, J. Meteor., doi:10.1175/1520-0469(1954)011<0058:EIITRM>2.0.CO;2 | Gate-by-gate correction from Z alone. Unstable when calibration is off; useful only as a bounded fallback. | C/X | DBZH | wradlib `atten` (constrained) | legacy | Y |
| **Linear PHIDP (implemented)** | A = alpha·KDP, ADP = beta·KDP | Bringi, Chandrasekar, Balakrishnan & Zrnić 1990, JTECH, doi:10.1175/1520-0426(1990)007<0829:AEOPEI>2.0.CO;2 | Path-integrated attenuation (PIA) = alpha × (PHIDP − PHIDP0). Fixed alpha/beta per band. | S/C/X | PHIDP, DBZH, ZDR | Py-ART `calculate_attenuation_philinear` | many | Y |
| Linear PHIDP, C-band tropical | Hot-spot aware | Carey et al. 2000 (above) | C-band PHIDP correction in tropical convection. Big-drop hot spots need larger beta. | C | as above | — | Darwin | Y |
| **ZPHI (implemented)** | Rain-profiling algorithm | Testud et al. 2000, JTECH, doi:10.1175/1520-0426(2000)017<0332:TRPAAT>2.0.CO;2 | Spreads the total PHIDP span along the ray in proportion to Z^b. Gives A per gate and is immune to Z miscalibration. | C/X (S: very small A) | DBZH, PHIDP | Py-ART `calculate_attenuation_zphi`; wradlib ZPHI recipe | MeteoSwiss, DWD research | Y |
| **Self-consistent (implemented)** | ZPHI with optimal alpha per ray | Bringi, Keenan & Chandrasekar 2001, IEEE TGRS, doi:10.1109/36.951081 | Searches alpha so that the ZPHI-reconstructed PHIDP best matches the measured PHIDP. Also corrects ZDR via ADP = beta·A. | C (C-POL), adapted to X | DBZH, ZDR, PHIDP | Py-ART `calculate_attenuation` (Gu et al. variant) | research | Y |
| ZDR constraint | Far-side light-rain ZDR ≈ 0 constraint | Smyth & Illingworth 1998, QJRMS — **DOI unverified** (candidate DOI resolved to a different paper) | Uses the expectation that ZDR returns to light-rain values beyond a storm to constrain the total differential attenuation. | C | ZDR, DBZH | — | UK research | Y |
| X-band coefficients | Self-consistent at X | Park et al. 2005a, JTECH, doi:10.1175/JTECH1803.1; Park et al. 2005b, JTECH, doi:10.1175/JTECH1804.1 | Adapts Bringi 2001 to X band (MP-X, Japan). Gives DSD-based alpha, gamma = ADP/AH, and the Z exponent b. | X | DBZH, ZDR, PHIDP | — | NIED Japan | Y |
| X-band evaluation | PHIDP-linear vs ZPHI | Gorgucci & Chandrasekar 2005, JTECH, doi:10.1175/JTECH1763.1 | Quantitative evaluation at X band. Both methods give nearly unbiased corrected Z; quantifies the impact of delta. | X | as above | — | CASA | Y |
| X-band self-consistency | Z–ZDR–KDP self-consistency | Gorgucci, Chandrasekar & Baldini 2006, JTECH, doi:10.1175/JTECH1950.1 | Self-consistency-based A and ADP correction. Bias under 10% when Z/ZDR are calibrated within ±1/±0.2 dB. | X | DBZH, ZDR, KDP | — | CASA | Y |
| C-band heavy rain / hot spots | Hot-spot separation | Gu et al. 2011, JAMC, doi:10.1175/2010JAMC2258.1 | Splits PIA into hot-spot and background contributions. Corrects up to 40 dB of attenuation at C band; ratios inside hot spots are highly variable. | C | DBZH, ZDR, PHIDP | Py-ART `calculate_attenuation` | NSSL research | Y |
| Regime-adaptive alpha | Bayesian rain-regime classification | Vulpiani et al. 2008, JTECH, doi:10.1175/2007JTECHA936.1 | Bayesian classification picks the prevailing rain regime and its alpha/beta; compared against other C-band methods. | C (Trappes) | DBZH, ZDR, PHIDP | — | Météo-France research | Y |
| X mobile + HCA | Attenuation then HCA | Snyder et al. 2010, JTECH, doi:10.1175/2010JTECHA1356.1 | Tests several X-band corrections in supercells against S-band, then runs an X-band fuzzy HCA. | X | all | — | research | Y |
| Specific attenuation A for QPE | R(A) via ZPHI | Ryzhkov, Diederich, Zhang & Simmer 2014, JTECH, doi:10.1175/JTECH-D-13-00038.1 | A from ZPHI is immune to miscalibration, partial beam blockage (PBB) and wet radome. R(A) is less DSD-sensitive and works at S/C/X. | S/C/X | DBZH, PHIDP, T (alpha) | wradlib ZPHI notebook; Py-ART (A field from ZPHI) | NEXRAD research/QPE upgrades (operational status not verified here), DWD research | Y |
| A at X band, operational test | R(A) evaluation | Diederich et al. 2015a, JHM, doi:10.1175/JHM-D-14-0066.1; 2015b, doi:10.1175/JHM-D-14-0067.1 | Twin X-band radars. Z(A) − Z gives calibration and PBB offsets, and the temperature dependence of A has little impact. | X | as above | — | Bonn | Y |
| Network (CASA) | Networked reflectivity retrieval | Chandrasekar & Lim 2008, JTECH, doi:10.1175/2008JTECHA1008.1; Lim & Chandrasekar 2016, IEEE TGRS, doi:10.1109/TGRS.2015.2487984 | Uses overlapping radars to retrieve intrinsic Z. Robust correction system for Z/ZDR. | X network | multi-radar | — | CASA DFW | partial (needs overlap) |
| Network context | Distributed short-wavelength radars | McLaughlin et al. 2009, BAMS, doi:10.1175/2009BAMS2507.1 | Concept and attenuation challenges of dense X-band networks. | X | — | — | CASA | — |
| Melting hail attenuation | Spectral-bin simulations | Borowska, Ryzhkov, Zrnić & Simmer 2011, JAMC, doi:10.1175/2010JAMC2465.1; Ryzhkov et al. 2013b, JAMC, doi:10.1175/JAMC-D-13-074.1 | Shows that A/KDP and ADP/KDP are much larger in melting hail at C band than in rain. Standard alpha under-corrects below the melting layer in hail. | C (S, X) | DBZH, ZDR, KDP, HCA | — | research | Y (needs HCA) |
| Wet radome, X | Proximity-Z proxy | Frasier et al. 2013, JTECH, doi:10.1175/JTECH-D-12-00148.1 | Uses near-radar Z as a radome-wetting proxy, calibrated against a radome-less neighbouring radar. | X | DBZH (near-range) | — | Météo-France (Alps) | Y (after one-off fit) |
| Wet radome, X | Self-consistency real-time | Gorgucci, Bechini, Baldini & Cremonini 2013, JTECH, doi:10.1175/JTECH-D-12-00071.1 | Uses Z–ZDR–KDP self-consistency to estimate and remove wet-radome loss in real time. | X (ARPA Piemonte) | DBZH, ZDR, KDP | — | ARPA Piemonte | Y |
| Wet radome, C | Measured transmission loss | Kurri & Huuskonen 2008, JTECH, doi:10.1175/2008JTECHA1056.1 | Measures radome loss as a function of rain intensity; supports an empirical loss(R) model. | C | gauge/DBZH | — | FMI | Y (empirical) |
| Spaceborne-constrained | GPM/TRMM matching | Warren et al. 2018, JTECH, doi:10.1175/JTECH-D-17-0128.1; Louf et al. 2019, JTECH, doi:10.1175/JTECH-D-18-0007.1; Crisologo et al. 2018, AMT, doi:10.5194/amt-11-5223-2018 | Volume-matching with the GPM DPR calibrates Z and can check residual attenuation and PBB. Uses only the Ku-band DPR above the melting layer or in light rain. | S/C/X | DBZH + GPM 2A-DPR | wradlib (GR/SR matching); `gpmmatch` (Louf) | BoM | partial (needs GPM overpasses) |

### 2a. Published alpha (A/KDP) and beta (ADP/KDP) values per band

| Band | alpha (dB/deg) | beta (dB/deg) | Source and notes |
|---|---|---|---|
| S | ~0.018 (vendor default) | — | Leonardo/Gematronik Rainbow5 product document (vendor default, secondary). |
| S | DSD- and temperature-dependent; the factor of ~2 change over 0–30 °C is stated for 2.8 and 5.5 GHz | — | Bringi et al. 2001 (text as quoted via secondary search; the paper itself was not read). |
| S | Tuned per site (ZPHI alpha must be tuned; A is "vanishingly small" at S) | — | Ryzhkov et al. 2014 (abstract). |
| C | 0.05–0.11 | 0.01–0.03; hot spots > 0.06 | Carey et al. 2000, as quoted in a French Trappes C-band study (likely Gourley et al. 2006) — secondary source. |
| C | ~0.08 (vendor default) | — | Rainbow5 document (secondary). |
| C | Ratios "highly variable" inside hot spots | — | Gu et al. 2011 (abstract). |
| C | Optimised per ray (search range; an upper bound of ~0.18 is quoted secondarily) | beta via beta/alpha | Bringi et al. 2001 (exact bounds unverified). |
| X | **0.139–0.335, mean 0.254** (9.375 GHz, DSD simulations) | gamma = ADP/AH 0.114–0.174, mean 0.139, so **beta ≈ 0.016–0.058, mean ≈ 0.035** (derived as gamma × alpha) | Park et al. 2005a (abstract; primary). |
| X | ~0.25 (vendor default) | — | Rainbow5 document (secondary). |
| X | 0.28 (example value) | — | wradlib ZPHI notebook (secondary). |

**Implications for radar-wow:**
- **C (0.08):** sits at the centre of the Carey range.
- **X (0.28):** inside Park's range, about 10% above Park's mean.
- **S (0.015):** slightly below the vendor 0.018. S-band correction is small either way.
- **Recommendation:** keep the fixed values as linear-PHIDP defaults, but expose them as config. Rely on the Bringi 2001 alpha search with band-specific bounds:
  - S: 0.01–0.04 (*suggested bound, not a published range*)
  - C: 0.05–0.18
  - X: 0.14–0.34
- Store the fitted alpha per ray as a diagnostic.

**Not verified:** exact S-band alpha/beta tables (Bringi & Chandrasekar 2001 textbook, doi:10.1017/CBO9780511541094; Ryzhkov & Zrnić 2019 book, doi:10.1007/978-3-030-05093-1). These books are the definitive sources for alpha/beta per band versus temperature. Pull the numbers from them before freezing defaults.

---

## 3. Stage 5 — Hydrometeor classification, melting layer, QVP/CVP

### 3a. Fuzzy-logic HCAs

| Method | Paper | What it does | Bands | Inputs | Classes (incl. non-met) | Code | Operational | Arch? |
|---|---|---|---|---|---|---|---|---|
| Relation synthesis | Straka, Zrnić & Ryzhkov 2000, JAM, doi:10.1175/1520-0450(2000)039<1341:BHCAQU>2.0.CO;2 | Canonical tables of Z/ZDR/KDP/RHOHV/LDR ranges per hydrometeor; the basis of most membership functions. | S | all | 11+ met. | — (CSU `csu_fhc` uses similar MBFs) | — | Y |
| Fuzzy / neuro-fuzzy | Liu & Chandrasekar 2000, JTECH, doi:10.1175/1520-0426(2000)017<0140:COHBOP>2.0.CO;2; Lim, Chandrasekar & Bringi 2005, IEEE TGRS, doi:10.1109/TGRS.2004.843077 | First fuzzy and neuro-fuzzy HCA, followed by model improvements with in-situ verification. | S | all + T | met. | — | CSU-CHILL | Y |
| **NEXRAD HCA** | Park et al. 2009, WAF, doi:10.1175/2008WAF2222205.1 | 10 classes, including ground clutter/AP and biological scatterers. Uses weights, confidence vectors (SNR, PBB, attenuation) and melting-layer (MLDA) height. | S | DBZH, ZDR, KDP, RHOHV, texture(Z), texture(PHIDP), ML | GC/AP, **BI**, DS, WS, CR, GR, BD, RA, HR, RH | — (described fully; ports exist) | NEXRAD (since 2013) | Y |
| X-band theory-based HID | Dolan & Rutledge 2009, JTECH, doi:10.1175/2009JTECHA1208.1 | Membership functions from X-band scattering simulations. | X | DBZH, ZDR, KDP, RHOHV, T | met. | CSU_RadarTools `csu_fhc` | CSU | Y |
| **C-band HID** | Dolan et al. 2013, JAMC, doi:10.1175/JAMC-D-12-0275.1 | Robust C-band HID applied to a long tropical (Darwin) dataset. Tropical-ready. | C | DBZH, ZDR, KDP, RHOHV, T | 10 met. | CSU_RadarTools `csu_fhc` | research, IITM use | Y |
| Winter HID | Thompson et al. 2014, JTECH, doi:10.1175/JTECH-D-13-00119.1 | HCA for winter precipitation, including ice crystal types and wet snow. | S/C/X | + T | winter | CSU_RadarTools `csu_fhc` (winter) | research | Y |
| X-band after attenuation | Snyder et al. 2010 (above) | X-band HCA after attenuation correction, using KOUN as reference. | X | all | met. | — | research | Y |
| **Multi-band French** | Al-Sakka et al. 2013, JAMC, doi:10.1175/JAMC-D-12-0236.1 | One fuzzy scheme with band-specific membership functions for X, C and S. Uses ML height and robust to attenuation. | S/C/X | DBZH, ZDR, KDP, RHOHV, ML | met. + non-met. | — | Météo-France | Y |
| Bayesian (C) | Yang, Zhao, Zhang & Chen 2019, Remote Sens., doi:10.3390/rs11161884 | Bayesian HCA for C-band polarimetric radar (China). | C | all | met. | — | research | Y |

### 3b. Semi-supervised, clustering and ML/DL HCAs

| Method | Paper | What it does | Bands | Code | Operational | Arch? |
|---|---|---|---|---|---|---|
| Spatial clustering | Grazioli, Tuia & Berne 2015, AMT, doi:10.5194/amt-8-149-2015 | Unsupervised, spatially constrained clustering, then labelling. | X/C | — | research | Y |
| Semi-supervised k-means | Bechini & Chandrasekar 2015, JTECH, doi:10.1175/JTECH-D-14-00097.1 | Starts from fuzzy-logic centroids and adapts them to local data. | S/C/X | — | research | Y |
| **Semi-supervised (in list)** | Besic et al. 2016, AMT, doi:10.5194/amt-9-4425-2016 | Clustering with centroids learned from data, robust to band and site; 8 classes. | C (MeteoSwiss); X | Py-ART `hydroclass_semisupervised`; pyrad | MeteoSwiss | Y |
| Demixing | Besic et al. 2018, AMT, doi:10.5194/amt-11-4847-2018 | Estimates the proportions of mixed hydrometeors per gate. | C/X | pyrad | MeteoSwiss | Y |
| Tropical X-band | Ribaud, Machado & Biscaro 2019, AMT, doi:10.5194/amt-12-811-2019 | Clustering-based HCA adapted to Brazilian tropical systems. | X | — | research | Y |
| CNN | Lu & Kumar 2019, IEEE ICDMW, doi:10.1109/ICDMW.2019.00050 | ResNet on NEXRAD Z/ZDR/RHOHV/KDP, with labels taken from the NEXRAD HCA. Limited classes; reports a seasonal-shift problem. | S | — | research | Y |
| Note | — | No mature, widely benchmarked deep-learning HCA was found. Most DL "truth" is an existing fuzzy HCA, which makes DL an emulator rather than an improvement. | — | — | — | — |

### 3c. Melting layer detection

| Method | Paper | What it does | Bands | Inputs | Code | Operational | Arch? |
|---|---|---|---|---|---|---|---|
| Freezing level | Brandes & Ikeda 2004, JAM, doi:10.1175/JAM2155.1 | ZDR/RHOHV/Z profile signatures of the freezing level. | S | DBZH, ZDR, RHOHV | — | research | Y |
| ML for VPR | Matrosov, Clark & Kingsmill 2007, JAMC, doi:10.1175/JAM2508.1 | RHOHV/ZDR identification of rain, ML and snow regions. | X | ZDR, RHOHV | — | NOAA HMT | Y |
| **NEXRAD MLDA (in list)** | Giangrande, Krause & Ryzhkov 2008, JAMC, doi:10.1175/2007JAMC1634.1 | Flags gates with ML-like RHOHV/ZDR/Z on 4–10 deg elevations, then takes azimuthal statistics for ML top and bottom. | S (C/X with retune) | DBZH, ZDR, RHOHV | MeteoSwiss Py-ART fork / pyrad `pyart.retrieve.melting_layer_giangrande` (https://meteoswiss.github.io/pyart/; not confirmed in ARM mainline) | NEXRAD | Y |
| MLDA at C band | Boodoo et al. 2010, JAMC, doi:10.1175/2010JAMC2421.1 | Applies the Giangrande MLDA to Environment Canada C-band radars and validates it. | C | as above | — | ECCC | Y |
| RHI/PPI gradient | Wolfensberger, Scipion & Berne 2016 (online 2015), QJRMS, doi:10.1002/qj.2672 | Combines Z and RHOHV gradients to detect ML top/bottom, from RHIs and adapted to PPIs. | X/C | DBZH, RHOHV | pyrad | MeteoSwiss | Y |
| Melting level, profile-based | Sanchez-Rivas & Rico-Ramirez 2021, AMT, doi:10.5194/amt-14-2873-2021 | Detects the melting level from vertical profiles of Z, ZDR and RHOHV (UK C band). | C | DBZH, ZDR, RHOHV | **Towerpy** (Sanchez-Rivas & Rico-Ramirez 2023, Env. Model. Softw., doi:10.1016/j.envsoft.2023.105746) | UKMO research | Y |
| New NEXRAD ML | Ryzhkov & Krause 2022, JTECH, doi:10.1175/JTECH-D-21-0130.1 | Successor to MLDA: QVP-like processing, better in shallow/low ML and with sloping MLs. | S (generic) | DBZH, ZDR, RHOHV | — | NEXRAD candidate | Y |

### 3d. QVP / CVP and hail size

| Method | Paper | What it does | Bands | Code | Arch? |
|---|---|---|---|---|---|
| **QVP** | Ryzhkov et al. 2016, JTECH, doi:10.1175/JTECH-D-15-0020.1 | Azimuthal averaging of a high-elevation PPI gives a time–height view. Good for ML, DGL, KDP in snow and ZDR monitoring. | S/C/X | Py-ART `compute_qvp`, `compute_rqvp`; wradlib; Towerpy | Y |
| CVP | Murphy et al. 2020, JTECH, doi:10.1175/JTECH-D-20-0011.1 | Columnar vertical profile over a sector, for comparing with aircraft or along-track data. | S/C/X | — (simple) | Y |
| HSDA theory | Ryzhkov et al. 2013a, JAMC, doi:10.1175/JAMC-D-13-073.1 | Spectral-bin simulations of melting hail across bands. | S/C | — | — |
| HSDA practice | Ryzhkov et al. 2013b, JAMC, doi:10.1175/JAMC-D-13-074.1 | Hail size discrimination (small, large, giant), plus C-band attenuation implications. | S (C caveats) | — | Y |
| HSDA validation | Ortega et al. 2016, JAMC, doi:10.1175/JAMC-D-15-0203.1 | Validates the HSDA against reports. | S | — | Y |
| Signatures | Kumjian & Ryzhkov 2008, JAMC, doi:10.1175/2007JAMC1874.1 | ZDR arcs and columns, KDP foot, hail signatures; helps set HCA rules. | S | — | Y |
| Tutorial | Kumjian 2013, J. Operational Meteor., doi:10.15191/nwajom.2013.0119 | Operational primer on polarimetric variables (Parts II and III cover applications and artifacts). | S | — | — |

### 3e. Tropical / monsoon / India

| Paper | Notes |
|---|---|
| Dolan et al. 2013 (Darwin, C band) | Tropical C-band HID; used by IITM groups for the Indian monsoon. The IITM poster seen was not verified as a paper. |
| Kumar, Jash, Resmi & Sumesh 2024, Theor. Appl. Climatol., doi:10.1007/s00704-024-05185-1 | Fuzzy-logic HID on Thiruvananthapuram C-band radar during the 2022 monsoon. Drizzle/rain near the surface; aggregates/crystals above the ML. |
| Ribaud et al. 2019 | Tropical X-band clustering (Brazil). |
| Carey et al. 2000 | Tropical C-band hot spots (big drops). |
| IITM X-band dataset (IEEE DataPort, doi:10.21227/0sk0-pq45) | **DOI unverified** via Crossref (DataCite DOI). Fuzzy HCA with azimuth-dependent ML at Mahabaleshwar. |

---

## 4. Place-dependent issues

| Issue | Where | Effect | Methods that address it |
|---|---|---|---|
| Heavy monsoon/tropical rain with big drops | India (incl. Delhi monsoon), Darwin, Brazil | Strong C/X attenuation, large delta, hot spots, LP/FIR artifacts, ZDR attenuation | Gu 2011 hot-spot correction; Carey 2000; Bringi 2001 alpha search; Hubbert & Bringi 1995 or Mishler 2024 delta removal; Ryzhkov 2014 R(A) |
| High melting layer (4.5–5.5 km) | Tropics/monsoon; pre-monsoon Delhi | Rain path is longer, so PIA is larger; ML intersects the beam only at long range; climatological ML defaults fail | MLDA (Giangrande 2008) or Ryzhkov & Krause 2022 with a local prior; QVP climatology; Dolan 2013 tropical HID |
| Low/sloping ML, bright band | Mid-latitude winter, mountains, Delhi winter western disturbances | ML contamination of rain-based KDP/A and of QPE | Wolfensberger 2016; Sanchez-Rivas 2021; Matrosov 2007; restrict attenuation to rain below the ML bottom |
| Hail regions | US Plains, north/north-east India pre-monsoon (Nor'westers), Alps | Melting hail: A/KDP and ADP/KDP far above rain values at C band; delta and KDP bias | Borowska 2011; Ryzhkov 2013b; Ryzhkov HSDA; Mishler 2024 delta; HCA-masked alpha |
| Wet radome in humid climates | Monsoon India, tropics (X and C) | Several dB of loss when rain falls on the radome; biases Z, not PHIDP | Frasier 2013 (X); Gorgucci 2013 (X self-consistency); Kurri & Huuskonen 2008 (C empirical); Ryzhkov 2014 R(A) (A is immune) |
| Mountains / partial beam blockage (PBB) | Alps, Himalaya foothills, Western Ghats | Biased Z; KDP/A immune | Vulpiani 2012 (designed for mountains); Ryzhkov 2014 / Diederich 2015 Z(A) PBB check; Crisologo 2018 GPM+BBF |
| Dust / haze / biological scatterers | Delhi pre-monsoon dust storms, insects in clear air | Low RHOHV, high ZDR, noisy PHIDP; misclassified as precipitation | Park 2009 includes BI and GC/AP; Al-Sakka 2013 has a non-met. class. **No verified dust-specific HCA was found — a gap.** |
| Short-path X networks | CASA, urban X | ZPHI unstable over short PHIDP spans | Reinoso-Rondinel 2018b short-path A/delta; Chandrasekar & Lim 2008 network retrieval |

---

## 5. Ranked recommendation — next methods to implement

1. **Ryzhkov et al. 2014 specific attenuation A and R(A) product (Stage 4 output).** This is a small step from the existing ZPHI: A is already computed internally. It is immune to calibration error, wet radome and partial beam blockage, which suits IMD radars with uncertain calibration and humid radomes. It is operational on NEXRAD and works at S/C/X. It also gives a Z(A)-versus-Z calibration check (Diederich 2015).
2. **delta-robust PHIDP: Hubbert & Bringi 1995 iterative FIR, then Mishler et al. 2024 LP + delta.** radar-wow's LP gives the best phase closure, but LP does not separate delta. At C/X in monsoon big drops and hail, delta biases KDP and the PHIDP span used by ZPHI. FIR has a reference implementation (CSU_RadarTools). Mishler's method builds directly on the existing LP class and outputs delta as a hail flag.
3. **Melting layer: Giangrande et al. 2008 MLDA, with the Ryzhkov & Krause 2022 upgrade.** Both HCA and attenuation correction need ML bottom/top: attenuation should run only in rain, and the alpha choice depends on it. It is in the existing literature list, operational, and needs only DBZH/ZDR/RHOHV. Ryzhkov & Krause adds robustness to high or sloping MLs.
4. **QVP (Ryzhkov et al. 2016), with optional CVP.** Cheap to build and useful across stages: ML detection, ZDR/PHIDP-offset monitoring, KDP in snow, and site climatologies for tuning alpha and HCA. Reference code exists in Py-ART and wradlib.
5. **Park et al. 2009 NEXRAD HCA with band-specific membership functions from Dolan 2013 (C) and Dolan & Rutledge 2009 (X), or Al-Sakka 2013 (S/C/X).** Gives a baseline fuzzy HCA with non-meteorological classes (GC/AP, biological) and confidence vectors. CSU_RadarTools `csu_fhc` provides reference membership functions; Dolan 2013 is already used for Indian monsoon C-band work.
6. **Besic et al. 2016 semi-supervised HCA.** The Py-ART/pyrad implementation is a reference. Centroids can be re-learned for Indian climatology, which avoids hand-tuning fuzzy membership functions per band. Pair with Besic 2018 demixing later.
7. **Gu et al. 2011 hot-spot C-band correction, with HCA-masked alpha in hail (Borowska 2011 / Ryzhkov 2013b).** This is the main failure mode of Bringi 2001 in monsoon/hail convection at C band. It needs items 3 and 5 for the hail mask.
8. **Schneebeli et al. 2014 Kalman ensemble KDP (benchmark/uncertainty).** A fourth KDP class with per-gate uncertainty, for the benchmark harness (with the Grazioli 2014 synthetic-truth approach). Reference implementation in Py-ART.

Also flagged:
- Wet-radome correction (Frasier 2013 / Gorgucci 2013) for humid-climate X/C sites, once a radome-less or co-located reference exists.
- Ryzhkov 2013 HSDA for S-band hail regions.
- Fix the moving-regression citation (see §0).

---

## 6. Software references

- Py-ART: Helmus & Collis 2016, J. Open Res. Softw., doi:10.5334/jors.119 — https://github.com/ARM-DOE/pyart
  - `pyart.correct`: `phase_proc_lp`, `phase_proc_lp_gf`, `calculate_attenuation`, `calculate_attenuation_zphi`, `calculate_attenuation_philinear`
  - `pyart.retrieve`: `kdp_maesaka`, `kdp_schneebeli`, `kdp_vulpiani`, `hydroclass_semisupervised`, `compute_qvp`, `compute_rqvp`, `quasi_vertical_profile`
- wradlib: Heistermann, Jacobi & Pfaff 2013, HESS, doi:10.5194/hess-17-863-2013 — https://github.com/wradlib/wradlib
  - `dp.kdp_from_phidp`, `dp.phidp_kdp_vulpiani`, `atten`, ZPHI notebook, QVP recipes
- CSU_RadarTools — https://github.com/CSU-Radarmet/CSU_RadarTools
  - `csu_kdp` (FIR), `csu_fhc` (summer/winter HID)
- pyrad (MeteoSwiss) — https://github.com/MeteoSwiss/pyrad
  - Kalman KDP, semi-supervised HCA, demixing, ML detection (Giangrande 2008 MLDA, Wolfensberger 2016)
- Towerpy: Sanchez-Rivas & Rico-Ramirez 2023, doi:10.1016/j.envsoft.2023.105746
  - QVP-based ML, attenuation, ZDR offset
- BALTRAD: Michelson et al. 2018, doi:10.5334/jors.193

---

## 7. Verified reference list (Crossref-resolved, 2026-11-03)

1. Al-Sakka, H., et al. (2013). A new fuzzy logic hydrometeor classification scheme applied to the French X-, C-, and S-band polarimetric radars. *JAMC*. doi:10.1175/JAMC-D-12-0236.1
2. Bechini, R., & Chandrasekar, V. (2015). A semisupervised robust hydrometeor classification method for dual-polarization radar applications. *JTECH*. doi:10.1175/JTECH-D-14-00097.1
3. Besic, N., et al. (2016). Hydrometeor classification through statistical clustering of polarimetric radar measurements: a semi-supervised approach. *AMT*. doi:10.5194/amt-9-4425-2016
4. Besic, N., Gehring, J., Praz, C., Figueras i Ventura, J., et al. (2018). Unraveling hydrometeor mixtures in polarimetric radar measurements. *AMT* 11, 4847–4866. doi:10.5194/amt-11-4847-2018
5. Boodoo, S., Hudak, D., Donaldson, N., & Leduc, M. (2010). Application of dual-polarization radar melting-layer detection algorithm. *JAMC* 49, 1779–1793. doi:10.1175/2010JAMC2421.1
6. Borowska, L., Ryzhkov, A., Zrnić, D., & Simmer, C. (2011). Attenuation and differential attenuation of 5-cm-wavelength radiation in melting hail. *JAMC* 50, 59–76. doi:10.1175/2010JAMC2465.1
7. Brandes, E. A., & Ikeda, K. (2004). Freezing-level estimation with polarimetric radar. *J. Appl. Meteor.* 43, 1541–1553. doi:10.1175/JAM2155.1
8. Bringi, V. N., & Chandrasekar, V. (2001). *Polarimetric Doppler Weather Radar*. Cambridge Univ. Press. doi:10.1017/CBO9780511541094
9. Bringi, V. N., Chandrasekar, V., Balakrishnan, N., & Zrnić, D. S. (1990). An examination of propagation effects in rainfall on radar measurements at microwave frequencies. *JTECH*. doi:10.1175/1520-0426(1990)007<0829:AEOPEI>2.0.CO;2
10. Bringi, V. N., Keenan, T. D., & Chandrasekar, V. (2001). Correcting C-band radar reflectivity and differential reflectivity data for rain attenuation: a self-consistent method with constraints. *IEEE TGRS*. doi:10.1109/36.951081
11. Bukovčić, P., et al. (2018). Polarimetric radar relations for quantification of snow based on disdrometer data. *JAMC*. doi:10.1175/JAMC-D-17-0090.1
12. Carey, L. D., et al. (2000). Correcting propagation effects in C-band polarimetric radar observations of tropical convection using differential propagation phase. *J. Appl. Meteor.* doi:10.1175/1520-0450(2000)039<1405:CPEICB>2.0.CO;2
13. Chandrasekar, V., & Lim, S. (2008). Retrieval of reflectivity in a networked radar environment. *JTECH*. doi:10.1175/2008JTECHA1008.1
14. Crisologo, I., Warren, R. A., Mühlbauer, K., & Heistermann, M. (2018). Enhancing the consistency of spaceborne and ground-based radar comparisons by using beam blockage fraction as a quality filter. *AMT* 11, 5223–5236. doi:10.5194/amt-11-5223-2018
15. Diederich, M., et al. (2015a). Use of specific attenuation for rainfall measurement at X-band radar wavelengths. Part I. *JHM*. doi:10.1175/JHM-D-14-0066.1
16. Diederich, M., et al. (2015b). Part II: Rainfall estimates and comparison with rain gauges. *JHM*. doi:10.1175/JHM-D-14-0067.1
17. Dolan, B., & Rutledge, S. A. (2009). A theory-based hydrometeor identification algorithm for X-band polarimetric radars. *JTECH*. doi:10.1175/2009JTECHA1208.1
18. Dolan, B., et al. (2013). A robust C-band hydrometeor identification algorithm and application to a long-term polarimetric radar dataset. *JAMC*. doi:10.1175/JAMC-D-12-0275.1
19. Frasier, S. J., et al. (2013). In-place estimation of wet radome attenuation at X band. *JTECH*. doi:10.1175/JTECH-D-12-00148.1
20. Giangrande, S. E., Krause, J. M., & Ryzhkov, A. V. (2008). Automatic designation of the melting layer with a polarimetric prototype of the WSR-88D radar. *JAMC*. doi:10.1175/2007JAMC1634.1
21. Giangrande, S. E., McGraw, R., & Lei, L. (2013). An application of linear programming to polarimetric radar differential phase processing. *JTECH*. doi:10.1175/JTECH-D-12-00147.1
22. Gorgucci, E., & Chandrasekar, V. (2005). Evaluation of attenuation correction methodology for dual-polarization radars: application to X-band systems. *JTECH* 22, 1195–1206. doi:10.1175/JTECH1763.1
23. Gorgucci, E., Chandrasekar, V., & Baldini, L. (2006). Correction of X-band radar observation for propagation effects based on the self-consistency principle. *JTECH*. doi:10.1175/JTECH1950.1
24. Gorgucci, E., Bechini, R., Baldini, L., Cremonini, R., et al. (2013). The influence of antenna radome on weather radar calibration and its real-time assessment. *JTECH* 30, 676–689. doi:10.1175/JTECH-D-12-00071.1
25. Gourley, J. J., Tabary, P., & Parent du Chatelet, J. (2006). Data quality of the Meteo-France C-band polarimetric radar. *JTECH* 23, 1340–1356. doi:10.1175/JTECH1912.1
26. Grazioli, J., et al. (2014). Accuracy of phase-based algorithms for the estimation of the specific differential phase shift using simulated polarimetric weather radar data. *IEEE GRSL*. doi:10.1109/LGRS.2013.2278620
27. Grazioli, J., Tuia, D., & Berne, A. (2015). Hydrometeor classification from polarimetric radar measurements: a clustering approach. *AMT*. doi:10.5194/amt-8-149-2015
28. Gu, J.-Y., et al. (2011). Polarimetric attenuation correction in heavy rain at C band. *JAMC*. doi:10.1175/2010JAMC2258.1
29. Heistermann, M., Jacobi, S., & Pfaff, T. (2013). Technical Note: An open source library for processing weather radar data (wradlib). *HESS*. doi:10.5194/hess-17-863-2013
30. Helmus, J. J., & Collis, S. M. (2016). The Python ARM Radar Toolkit (Py-ART). *J. Open Res. Softw.* 4. doi:10.5334/jors.119
31. Hitschfeld, W., & Bordan, J. (1954). Errors inherent in the radar measurement of rainfall at attenuating wavelengths. *J. Meteor.* doi:10.1175/1520-0469(1954)011<0058:EIITRM>2.0.CO;2
32. Hubbert, J., Chandrasekar, V., Bringi, V. N., & Meischner, P. (1993). Processing and interpretation of coherent dual-polarized radar measurements. *JTECH*. doi:10.1175/1520-0426(1993)010<0155:PAIOCD>2.0.CO;2
33. Hubbert, J., & Bringi, V. N. (1995). An iterative filtering technique for the analysis of copolar differential phase and dual-frequency radar measurements. *JTECH*. doi:10.1175/1520-0426(1995)012<0643:AIFTFT>2.0.CO;2
34. Huang, H., et al. (2017). A hybrid method to estimate specific differential phase and rainfall with linear programming and physics constraints. *IEEE TGRS*. doi:10.1109/TGRS.2016.2596295
35. Kötsche, A., Myagkov, A., von Terzi, L., Maahn, M., et al. (2025). Investigating KDP signatures inside and below the dendritic growth layer with W-band Doppler radar. *ACP* 25, 14045–14070. doi:10.5194/acp-25-14045-2025
36. Kumar, Jash, Resmi & Sumesh (2024). Hydrometeor categorization in stratiform and convective precipitation systems over a tropical coastal region. *Theor. Appl. Climatol.* 155, 9305–9325. doi:10.1007/s00704-024-05185-1
37. Kumjian, M. R. (2013). Principles and applications of dual-polarization weather radar. Part I. *J. Operational Meteor.* 1, 226–242. doi:10.15191/nwajom.2013.0119
38. Kumjian, M. R., & Ryzhkov, A. V. (2008). Polarimetric signatures in supercell thunderstorms. *JAMC* 47, 1940–1961. doi:10.1175/2007JAMC1874.1
39. Kurri, M., & Huuskonen, A. (2008). Measurements of the transmission loss of a radome at different rain intensities. *JTECH*. doi:10.1175/2008JTECHA1056.1
40. Lim, S., Chandrasekar, V., & Bringi, V. N. (2005). Hydrometeor classification system using dual-polarization radar measurements: model improvements and in situ verification. *IEEE TGRS*. doi:10.1109/TGRS.2004.843077
41. Lim, S., & Chandrasekar, V. (2016). A robust attenuation correction system for reflectivity and differential reflectivity in weather radars. *IEEE TGRS* 54, 1727–1737. doi:10.1109/TGRS.2015.2487984
42. Liu, H., & Chandrasekar, V. (2000). Classification of hydrometeors based on polarimetric radar measurements: development of fuzzy logic and neuro-fuzzy systems, and in situ verification. *JTECH*. doi:10.1175/1520-0426(2000)017<0140:COHBOP>2.0.CO;2
43. Louf, V., Protat, A., Warren, R. A., Collis, S. M., et al. (2019). An integrated approach to weather radar calibration and monitoring using ground clutter and satellite comparisons. *JTECH* 36, 17–39. doi:10.1175/JTECH-D-18-0007.1
44. Lu, Y., & Kumar, J. (2019). Convolutional neural networks for hydrometeor classification using dual polarization Doppler radars. *2019 ICDMW*, 288–295. doi:10.1109/ICDMW.2019.00050
45. Matrosov, S. Y., Clark, K. A., & Kingsmill, D. E. (2007). A polarimetric radar approach to identify rain, melting-layer, and snow regions for applying corrections to vertical profiles of reflectivity. *JAMC*. doi:10.1175/JAM2508.1
46. McLaughlin, D., Pepyne, D., Chandrasekar, V., Philips, B., et al. (2009). Short-wavelength technology and the potential for distributed networks of small radar systems. *BAMS* 90, 1797–1818. doi:10.1175/2009BAMS2507.1
47. Michelson, D., et al. (2018). BALTRAD advanced weather radar networking. *J. Open Res. Softw.* 6. doi:10.5334/jors.193
48. Mishler, C., et al. (2024). Improving estimation of specific differential phase and assessing differential backscattering phase. *JAMC*. doi:10.1175/JAMC-D-23-0204.1
49. Murphy, A. M., et al. (2020). Columnar vertical profile (CVP) methodology for validating polarimetric radar retrievals in ice using in situ aircraft measurements. *JTECH*. doi:10.1175/JTECH-D-20-0011.1
50. Ortega, K. L., et al. (2016). Polarimetric radar characteristics of melting hail. Part III: Validation of the algorithm for hail size discrimination. *JAMC*. doi:10.1175/JAMC-D-15-0203.1
51. Otto, T., & Russchenberg, H. W. J. (2011). Estimation of specific differential phase and differential backscatter phase from polarimetric weather radar measurements of rain. *IEEE GRSL* 8, 988–992. doi:10.1109/LGRS.2011.2145354
52. Park, H. S., et al. (2009). The hydrometeor classification algorithm for the polarimetric WSR-88D: description and application to an MCS. *WAF*. doi:10.1175/2008WAF2222205.1
53. Park, S.-G., Bringi, V. N., Chandrasekar, V., Maki, M., & Iwanami, K. (2005a). Correction of radar reflectivity and differential reflectivity for rain attenuation at X band. Part I. *JTECH*. doi:10.1175/JTECH1803.1
54. Park, S.-G., et al. (2005b). Part II: Evaluation and application. *JTECH*. doi:10.1175/JTECH1804.1
55. Reimann, L., Simmer, C., & Trömel, S. (2021). Dual-polarimetric radar estimators of liquid water content over Germany. *Meteorol. Z.* 30, 237–249. doi:10.1127/metz/2021/1072
56. Reinoso-Rondinel, R., et al. (2018a). Adaptive and high-resolution estimation of specific differential phase for polarimetric X-band weather radars. *JTECH*. doi:10.1175/JTECH-D-17-0105.1
57. Reinoso-Rondinel, R., Unal, C., & Russchenberg, H. (2018b). Improved estimation of the specific attenuation and backscatter differential phase over short rain paths. *JTECH* 35, 2359–2381. doi:10.1175/JTECH-D-17-0219.1
58. Ribaud, J.-F., Machado, L. A. T., & Biscaro, T. (2019). X-band dual-polarization radar-based hydrometeor classification for Brazilian tropical precipitation systems. *AMT*. doi:10.5194/amt-12-811-2019
59. Ryzhkov, A. V. (2007). The impact of beam broadening on the quality of radar polarimetric data. *JTECH*. doi:10.1175/JTECH2003.1
60. Ryzhkov, A., & Zrnić, D. S. (1995). Precipitation and attenuation measurements at a 10-cm wavelength. *J. Appl. Meteor.* 34, 2121–2134. doi:10.1175/1520-0450(1995)034<2120:PAAMAA>2.0.CO;2
61. Ryzhkov, A. V., & Zrnić, D. S. (1996). Assessment of rainfall measurement that uses specific differential phase. *J. Appl. Meteor.* doi:10.1175/1520-0450(1996)035<2080:AORMTU>2.0.CO;2
62. Ryzhkov, A. V., et al. (2013a). Polarimetric radar characteristics of melting hail. Part I. *JAMC*. doi:10.1175/JAMC-D-13-073.1
63. Ryzhkov, A. V., et al. (2013b). Polarimetric radar characteristics of melting hail. Part II: Practical implications. *JAMC*. doi:10.1175/JAMC-D-13-074.1
64. Ryzhkov, A., Diederich, M., Zhang, P., & Simmer, C. (2014). Potential utilization of specific attenuation for rainfall estimation, mitigation of partial beam blockage, and radar networking. *JTECH*. doi:10.1175/JTECH-D-13-00038.1
65. Ryzhkov, A., Zhang, P., Reeves, H., Kumjian, M., et al. (2016). Quasi-vertical profiles—a new way to look at polarimetric radar data. *JTECH* 33, 551–562. doi:10.1175/JTECH-D-15-0020.1
66. Ryzhkov, A. V., & Zrnić, D. S. (2019). *Radar Polarimetry for Weather Observations*. Springer. doi:10.1007/978-3-030-05093-1
67. Ryzhkov, A., & Krause, J. (2022). New polarimetric radar algorithm for melting-layer detection and determination of its height. *JTECH*. doi:10.1175/JTECH-D-21-0130.1
68. Sanchez-Rivas, D., & Rico-Ramirez, M. A. (2021). Detection of the melting level with polarimetric weather radar. *AMT* 14, 2873–2890. doi:10.5194/amt-14-2873-2021
69. Sanchez-Rivas, D., & Rico-Ramirez, M. A. (2023). Towerpy: an open-source toolbox for processing polarimetric weather radar data. *Environ. Model. Softw.* 167, 105746. doi:10.1016/j.envsoft.2023.105746
70. Scarchilli, G., Gorgucci, E., Chandrasekar, V., & Dobaie, A. (1996). Self-consistency of polarization diversity measurement of rainfall. *IEEE TGRS* 34, 22–26. doi:10.1109/36.481887
71. Schneebeli, M., & Berne, A. (2012). An extended Kalman filter framework for polarimetric X-band weather radar data processing. *JTECH*. doi:10.1175/JTECH-D-10-05053.1
72. Schneebeli, M., et al. (2014). Improved estimation of the specific differential phase shift using a compilation of Kalman filter ensembles. *IEEE TGRS*. doi:10.1109/TGRS.2013.2287017
73. Snyder, J. C., et al. (2010). Attenuation correction and hydrometeor classification of high-resolution, X-band, dual-polarized mobile radar measurements in severe convective storms. *JTECH*. doi:10.1175/2010JTECHA1356.1
74. Straka, J. M., Zrnić, D. S., & Ryzhkov, A. V. (2000). Bulk hydrometeor classification and quantification using polarimetric radar data: synthesis of relations. *J. Appl. Meteor.* doi:10.1175/1520-0450(2000)039<1341:BHCAQU>2.0.CO;2
75. Testud, J., et al. (2000). The rain profiling algorithm applied to polarimetric weather radar. *JTECH*. doi:10.1175/1520-0426(2000)017<0332:TRPAAT>2.0.CO;2
76. Thompson, E. J., Rutledge, S. A., Dolan, B., Chandrasekar, V., et al. (2014). A dual-polarization radar hydrometeor classification algorithm for winter precipitation. *JTECH* 31, 1457–1481. doi:10.1175/JTECH-D-13-00119.1
77. Trömel, S., et al. (2013). Backscatter differential phase—estimation and variability. *JAMC*. doi:10.1175/JAMC-D-13-0124.1
78. Trömel, S., Ryzhkov, A. V., Hickman, B., Mühlbauer, K., et al. (2019). Polarimetric radar variables in the layers of melting and dendritic growth at X band—implications for a nowcasting strategy in stratiform rain. *JAMC* 58, 2497–2522. doi:10.1175/JAMC-D-19-0056.1
79. Vivekanandan, J., Zhang, G., Ellis, S. M., Rajopadhyaya, D., et al. (2003). Radar reflectivity calibration using differential propagation phase measurement. *Radio Sci.* 38. doi:10.1029/2002RS002676
80. Vulpiani, G., Tabary, P., Parent du Chatelet, J., & Marzano, F. S. (2008). Comparison of advanced radar polarimetric techniques for operational attenuation correction at C band. *JTECH* 25, 1118–1135. doi:10.1175/2007JTECHA936.1
81. Vulpiani, G., et al. (2012). On the use of dual-polarized C-band radar for operational rainfall retrieval in mountainous areas. *JAMC*. doi:10.1175/JAMC-D-10-05024.1
82. Wang, Y., & Chandrasekar, V. (2009). Algorithm for estimation of the specific differential phase. *JTECH*. doi:10.1175/2009JTECHA1358.1
83. Warren, R. A., et al. (2018). Calibrating ground-based radars against TRMM and GPM. *JTECH*. doi:10.1175/JTECH-D-17-0128.1
84. Wolfensberger, D., Scipion, D., & Berne, A. (2016; online 2015). Detection and characterization of the melting layer based on polarimetric radar scans. *QJRMS* 142, 108–124. doi:10.1002/qj.2672
85. Wolfensberger, D., et al. (2021). RainForest: a random forest algorithm for quantitative precipitation estimation over Switzerland. *AMT*. doi:10.5194/amt-14-3169-2021 — *RainForest QPE; its Appendix A defines the median + moving-regression KDP used by radar-wow (see §0).*
86. Yang, J., Zhao, K., Zhang, G., Chen, G., et al. (2019). A Bayesian hydrometeor classification algorithm for C-band polarimetric radar. *Remote Sens.* 11, 1884. doi:10.3390/rs11161884

### DOI unverified / dropped
- Maesaka, T., Iwanami, K., & Maki, M. (2012). Non-negative KDP estimation by monotone increasing PHIDP assumption below melting layer. ERAD 2012 proceedings. No DOI; cited because Py-ART implements it as `kdp_maesaka`.
- Smyth, T. J., & Illingworth, A. J. (1998). Correction for attenuation of radar reflectivity using polarization data. QJRMS. The candidate DOI 10.1002/qj.49712455117 resolved to an unrelated paper. **DOI unverified.**
- IITM SSPA X-band HCA dataset, IEEE DataPort doi:10.21227/0sk0-pq45. Not checked in Crossref (likely a DataCite DOI).
- Dropped: 10.1175/JTECH1782.1 resolves to an unrelated pyranometer paper; the correct Gorgucci & Chandrasekar 2005 DOI is 10.1175/JTECH1763.1. Also dropped 10.1175/WAF-D-13-00059.1 (404) and 10.1175/JAM2147.1 (unrelated); correct DOIs are given above.
- Secondary sources for alpha values (not peer-reviewed / not DOI-verified): Leonardo Rainbow5 DPATC product document (NASA GHRC OLYMPEX archive) and the wradlib ZPHI notebook (docs.wradlib.org).
