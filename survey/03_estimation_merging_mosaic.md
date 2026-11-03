# 03 — Rain-rate estimation, radar–gauge merging and mosaicking (Stages 6–8)

*radar-wow literature survey, written 2026-11-03. Scope: Stage 6 (rain-rate estimators, VPR/bright band, beam blockage, hybrid scan, range effects), Stage 7 (radar–gauge merging, bias adjustment, uncertainty/ensembles, CML and satellite as extra sources) and Stage 8 (multi-radar compositing, temporal accumulation with advection correction, national operational systems as reference designs).*

## How to read this document

- **Every DOI in this file was checked against `https://api.crossref.org/works/<DOI>`** (or DataCite for the one DWD dataset DOI) on 2026-11-03. Title, first author and year matched. Items without a resolvable DOI are given a URL and labelled "no DOI". Preprints that have not been peer reviewed are labelled **[preprint]**.
- **Coefficients** are given only where I read them in a primary source, an operational document, or the source code of a maintained library (labelled as such). Each one carries its band and source. If I could not read it, it is not quoted.
- "Bands" means the radar wavelengths a method was designed for or validated at: S (~10–11 cm, NEXRAD, IMD S-band DWRs), C (~5.3 cm, most of Europe, IMD C-band), X (~3.2 cm, gap fillers, IMD Himalayan radars).
- One row is roughly one radar-wow class ("one class = one paper").
- Background notes reused: `radar_wow/literature/01_qpe_estimators_operational_systems.md` and `04_india_delhi_radar.md`. The QVP paper is `10.1175/JTECH-D-15-0020.1` (Crossref-verified). The literature notes already cite it correctly (`02_quality_control_and_polarimetric_processing.md`); an earlier draft of this survey wrongly reported a mistake there.

## Where these stages sit in radar-wow

```
QC'd polar volume (Stages 1–5: QC, calibration, attenuation, KDP, HCA/ML)
   │
   ├─ Stage 6  per-radar surface rain rate
   │     blockage map (DEM) → hybrid scan / lowest usable bin → VPR/bright-band correction
   │     → estimator selection (R(Z) | R(KDP) | R(Z,ZDR) | R(A) | synthetic/HCA-driven)
   │     → per-gate quality index (height, blockage, distance, HCA confidence)
   │
   ├─ Stage 8a multi-radar mosaic of rates (quality-weighted) on a common grid
   ├─ Stage 8b temporal accumulation (advection-corrected) → 1 h / 24 h totals
   │
   └─ Stage 7  bias adjustment & merging with gauges / CMLs / satellite
         → MFB → local bias / KED / conditional merging → uncertainty (ensembles)
```

---

## Stage 6a — Rain-rate estimators

| Sub-component | Method | Paper (DOI) | Plain-English description | Bands | Inputs | Open-source implementation | Operational use | Data needs |
|---|---|---|---|---|---|---|---|---|
| R(Z) climatological | Marshall–Palmer exponential DSD → Z = 200R^1.6 | Marshall & Palmer 1948, J. Meteor. — 10.1175/1520-0469(1948)005<0165:TDORWS>2.0.CO;2 | Classic single power law from an exponential raindrop spectrum. Best for widespread stratiform rain. | S, C, X (no band dependence at Rayleigh) | Z | wradlib `zr.z_to_r(z, a=200, b=1.6)` (default); Py-ART `est_rain_rate_z` | Default in many national systems; reported as IMD default (unverified, see 04 notes) | none |
| R(Z) NEXRAD legacy PPS | Z = 300R^1.4 convective, hybrid scan, hail cap, gauge bias | Fulton et al. 1998, Wea. Forecasting — 10.1175/1520-0434(1998)013<0377:TWRA>2.0.CO;2 | The original WSR-88D rainfall algorithm. Single convective Z–R, lowest-unblocked-tilt "hybrid scan", hail cap at high Z. | S | Z, blockage map | CSU_RadarTools default (`r_z_a=300, r_z_b=1.4`) | NEXRAD PPS (still produced) | DEM/occultation, gauges for bias |
| R(Z) regime/tropical | Probability-matched (window PMM) Z–R per regime (e.g. tropical) | Rosenfeld et al. 1993, J. Appl. Meteor. — 10.1175/1520-0450(1993)032<0050:GPMRBR>2.0.CO;2 | Matches the CDF of radar Z to the CDF of gauge rain rate to get a climate/regime-specific Z–R. Source of the "tropical" Z–R. | S, C | Z, gauges | — (easy to implement) | NEXRAD "tropical" option; MRMS regime-based R(Z) | Gauges (or disdrometer) |
| R(Z) regime by precip type | Multiple R(Z) by automated classification (convective, stratiform, tropical, snow, hail) plus VPR | Zhang et al. 2016, BAMS — 10.1175/BAMS-D-14-00174.1 | MRMS radar-only QPE: each pixel gets a Z–R chosen by a classifier (using 3-D reflectivity, temperature) and VPR-corrected Z. | S (C supplemental) | 3-D Z mosaic, model T | — (algorithm in paper) | MRMS (US) | NWP temperature profile |
| R(KDP) | Power law in specific differential phase | Ryzhkov & Zrnić 1996, J. Appl. Meteor. — 10.1175/1520-0450(1996)035<2080:AORMTU>2.0.CO;2 | Rain rate from phase shift. Immune to calibration, attenuation, partial blockage; noisy in light rain; good in hail/rain mixture. | S, C, X (stronger signal at C/X) | KDP | Py-ART `est_rain_rate_kdp`; CSU_RadarTools | NEXRAD DP-QPE (hail/heavy rain); Météo-France; MRMS (Z ≥ 50 dBZ) | none |
| R(KDP) at X band | X-band KDP rainfall | Matrosov et al. 2005, J. Hydrometeor. — 10.1175/JHM424.1 | Shows KDP-based rain at X band is accurate because KDP is ~3× larger than at S band. | X | KDP | Py-ART | X-band networks (CASA, Japan XRAIN-type) | none |
| R(Z,ZDR), R(KDP,ZDR) | Two-parameter polarimetric estimators | Ryzhkov & Zrnić 1995, JTECH — 10.1175/1520-0426(1995)012<0249:CODPRE>2.0.CO;2 | Gauge-based comparison of R(Z), R(KDP), R(Z,ZDR), R(KDP,ZDR); ZDR adds drop-size information. | S | Z, ZDR, KDP | Py-ART, CSU_RadarTools | NEXRAD DP-QPE uses R(Z,ZDR) in rain | ZDR calibration critical |
| Synthetic (JPOLE) | Rate-dependent blend of R(Z), R(KDP), R(Z,ZDR) | Ryzhkov, Giangrande & Schuur 2005, J. Appl. Meteor. — 10.1175/JAM2213.1 | "Synthetic" algorithm: choose estimator by R(Z) intensity bin. Basis of the NEXRAD dual-pol QPE. | S | Z, ZDR, KDP | — | Prototype for NEXRAD | none |
| HCA-driven selection | Estimator per hydrometeor class | Giangrande & Ryzhkov 2008, JAMC — 10.1175/2008JAMC1753.1 | Rain rate formula chosen gate by gate from the classification (rain, heavy rain, hail, wet/dry snow, graupel) with class multipliers. | S | Z, ZDR, KDP, HCA, ML | — (logic in NEXRAD ORPG; table below) | NEXRAD DP-QPE since 2011 | Melting layer (sounding/NWP) |
| CSU-HIDRO / blended | Decision tree on HID + thresholds on Z, ZDR, KDP | Cifelli et al. 2011, JTECH — 10.1175/2010JTECHA1488.1 | Uses R(KDP,ZDR) when signals are strong, R(Z,ZDR) for light rain, R(KDP) for ice-contaminated rain, R(Z) otherwise. | S (C/X variants without ZDR) | Z, ZDR, KDP, HID | **CSU_RadarTools** `csu_blended_rain.calc_blended_rain`, `csu_hidro_rain` — https://github.com/CSU-Radarmet/CSU_RadarTools | CSU-CHILL research; NASA GPM GV | none |
| DROPS2.0 | Region-based blended estimator with DSD-informed relations | Chen, Chandrasekar & Bechini 2017, J. Hydrometeor. — 10.1175/JHM-D-16-0124.1 | Improved CSU blended algorithm; uses a hydrometeor ID and region-based logic; tested at IFloodS. | S (X variants in DFW) | Z, ZDR, KDP, HID | — | NASA IFloodS, DFW testbed | none |
| R(A) specific attenuation | ZPHI-type retrieval of A constrained by ΔΦDP, then R = a·A^b | Ryzhkov, Diederich, Zhang & Simmer 2014, JTECH — 10.1175/JTECH-D-13-00038.1 | Rain rate from specific attenuation; nearly linear in R, immune to calibration and partial blockage, less DSD-sensitive than R(Z) or R(KDP). Needs pure rain and ΔΦDP above a few degrees. | S, C, X (coefficients for all three) | Z, ΦDP (ZDR for α) | **Py-ART** `est_rain_rate_a`, `calculate_attenuation_zphi`; wradlib attenuation module | MRMS, NEXRAD DP-QPE (Build 19) | Temperature (for coefficients) |
| R(A) at X band | Calibration, PBB, clutter, temperature sensitivity of R(A) | Diederich et al. 2015 Part I (10.1175/JHM-D-14-0066.1) and Part II (10.1175/JHM-D-14-0067.1), J. Hydrometeor. | Two German X-band radars: uses R(A) to estimate miscalibration and partial blockage, then compares R(A), R(Z), R(KDP) with gauges. | X | Z, ΦDP | Py-ART (coefficients cite Diederich 2015) | BoXPol/JuXPol research | Gauges for evaluation |
| R(A)+R(KDP) operational | α from Z–ZDR slope, R(A) in rain, R(KDP) for Z ≥ 50 dBZ | Wang et al. 2019, J. Hydrometeor. — 10.1175/JHM-D-18-0071.1; Cocks et al. 2019 (Part II) — 10.1175/JHM-D-18-0070.1 | Prototype S-band R(A)/R(KDP) algorithm for WSR-88D, one α per volume from the ZDR-vs-Z slope; CONUS verification. | S | Z, ZDR, ΦDP, ML | — | MRMS | Melting layer (NWP + ρhv) |
| Synthetic operational QPE | R(A) in pure rain, R(KDP) where hail possible, VPR-corrected R(Z) elsewhere; evaporation correction | Zhang et al. 2020, J. Hydrometeor. — 10.1175/JHM-D-19-0194.1 | The operational MRMS dual-pol synthetic QPE; R(Z) fills far-range areas above the ML; 50-km blend zone at the R(A) edge. | S | Z, ZDR, ΦDP, HCA, ML, 3-D mosaic | — | MRMS (operational) | NWP T/RH |
| French operational C-band | KDP/ZPHI-based C-band dual-pol rain | Figueras i Ventura & Tabary 2013, JAMC — 10.1175/JAMC-D-12-0179.1; Figueras i Ventura et al. 2012, QJRMS — 10.1002/qj.1934 | Météo-France's switch to polarimetric rain at C band, with long-term data-quality monitoring and estimator comparison. | C | Z, ZDR, ΦDP | Py-ART C-band R(KDP) coefficients cite the 2012 paper | Météo-France PANTHERE | none |
| UK C-band dual-pol | Operational C-band polarimetric QPE and error analysis | Bringi et al. 2011, J. Hydrometeor. — 10.1175/JHM-D-10-05013.1 | Shows attenuation-corrected C-band polarimetric estimators beat R(Z) against UK gauges. | C | Z, ZDR, ΦDP | — | UK Met Office | Gauges |
| Tropical maritime | DSD-based dual-pol estimators for tropical oceanic rain | Thompson et al. 2018, JAMC — 10.1175/JAMC-D-17-0160.1 | Tropical (DYNAMO) rain has many small drops; estimators tuned on continental DSDs overestimate or underestimate. | S | Z, ZDR, KDP | — | Research | Disdrometer |
| Subtropical | Polarimetric rainfall in a subtropical (Florida) environment | Brandes et al. 2002, J. Appl. Meteor. — 10.1175/1520-0450(2002)041<0674:EIREWA>2.0.CO;2 | Evaluation of polarimetric estimators in subtropical rain; source of a widely used drop-shape model. | S | Z, ZDR, KDP | — | Research | Gauges |
| Snow | S(KDP,Z) and S(Z,ZDR) polarimetric snow relations | Bukovčić et al. 2018, JAMC — 10.1175/JAMC-D-17-0090.1; Bukovčić et al. 2020, JAMC — 10.1175/JAMC-D-19-0140.1 | Snow water equivalent rate from KDP and Z jointly, reducing the factor-of-ten ambiguity of Z–S. | S (C/X need re-fit) | Z, KDP, ZDR | — | MRMS research | Temperature; snow gauges |
| Review | Polarimetric QPE review (S/C/X, R(A), R(KDP), VPR, snow, MRMS) | Ryzhkov et al. 2022, Remote Sens. — 10.3390/rs14071695 | Best single review of what works at each band and why. | S, C, X | — | — | — | — |
| Review | Dual-pol QPE principles, operations (US, China, France), challenges | Zhang, Zhao, Qi & Xiong 2025 (Z. Zhang et al.), Remote Sens. — 10.3390/rs17213619 | Recent review contrasting US, Chinese and French operational dual-pol QPE. | S, C | — | — | — | — |
| Textbook | Radar Polarimetry for Weather Observations | Ryzhkov & Zrnić 2019, Springer — 10.1007/978-3-030-05093-1 | The reference for every polarimetric estimator above. | S, C, X | — | — | — | — |

### NEXRAD dual-pol QPE: class-based rate selection

Read from Grams et al. 2019 (NWS ROC, AMS Annual Meeting paper, no DOI; https://training.weather.gov/wdtd/courses/rac/principles/qpe/story_content/external_files/Grams_et_al_2019.pdf), Table 1 (ORPG Build 18). This is a ready-made specification for a radar-wow `HCADrivenRainRate` class:

| HCA class / condition | Rate |
|---|---|
| Ground clutter, unknown, or MetSignal < 80 % | not computed |
| No echo, biological | 0 |
| Light/moderate rain, big drops | R(Z,ZDR) |
| Heavy rain, blockage < 20 % and ≤ 45 dBZ | R(Z,ZDR) |
| Heavy rain, blockage ≥ 20 % or Z > 45 dBZ | R(KDP) |
| Rain/hail, blockage ≥ 5 %; or at/below ML top with blockage < 5 % | R(KDP) |
| Rain/hail above ML top, blockage < 5 % | 0.8·R(Z) |
| Graupel | 0.8·R(Z) |
| Wet snow | 0.6·R(Z) |
| Dry snow at/below ML top | R(Z) |
| Dry snow above ML top, ice crystals | 2.8·R(Z) (site adjustable) |

The same paper reports that Build 19 replaces R(Z,ZDR) with R(A) below the melting layer, with α = 0.04875 − 0.75·K (K = slope of median ZDR vs Z between 20 and 50 dBZ), α bounded between 0.015 (continental) and 0.04 (tropical), 0.035 for pure stratiform and 0.015 as default. It also introduces a rain/hail R(KDP) with multiplier 27 instead of 44 where ρhv < 0.97.

---

## Coefficient table (R in mm h⁻¹; Z in mm⁶ m⁻³ linear; ZDR linear unless stated; KDP in ° km⁻¹; A in dB km⁻¹)

| Band | Relation | Coefficients | Conditions | Source actually read |
|---|---|---|---|---|
| any | Z = 200 R^1.6 | a = 200, b = 1.6 | stratiform, Marshall–Palmer | Dixon et al. 2015 (NCAR, AMS 37th Radar Conf. 9A.1, no DOI) states 0.0365 Z^0.625 "is equivalent to Marshall Palmer Z = 200R^1.6"; wradlib default. Origin: Marshall & Palmer 1948 |
| S | Z = 300 R^1.4 ⇔ R = 1.70×10⁻² Z^0.714 | | NEXRAD convective default, Z capped at 53 dBZ | Ryzhkov, Giangrande & Schuur AMS preprint (4B.1, https://ams.confex.com/ams/pdfpapers/64216.pdf), precursor of Ryzhkov et al. 2005; Fulton et al. 1998 |
| S | Z = 250 R^1.2 | | tropical (Rosenfeld) | Read only via a secondary source (Moser et al., AMS conference paper quoting Rosenfeld et al. 1993). **Check against Rosenfeld 1993 before use.** |
| S | R(KDP) = 45.3 \|KDP\|^0.786 sign(KDP) | | Oklahoma 2D-video DSD, Brandes drop shape | Ryzhkov, Giangrande & Schuur AMS preprint (above) |
| S | R(Z,ZDR) = 1.42×10⁻² Z^0.770 ZDR^−1.67 | | Oklahoma DSD | same preprint |
| S | R(KDP,ZDR) = 136 \|KDP\|^0.968 ZDR^−2.86 | | Oklahoma DSD | same preprint |
| S | R(KDP) = 44.0 \|KDP\|^0.822 sign(KDP) | | NEXRAD DP-QPE (attributed to Berkowitz et al. 2013) | Dixon et al. 2015 (NCAR) quoting NEXRAD; multiplier 44 confirmed by Grams et al. 2019 |
| S | R(Z,ZDR) = 0.0067 Z^0.927 ZDR^−3.43 | | NEXRAD DP-QPE (Berkowitz et al. 2013) | Dixon et al. 2015; same values are CSU_RadarTools defaults (`6.7e-3, 0.927`, ZDR exponent written as 10^(−0.343·ZDR_dB)) |
| S | R(KDP) = 40.5 KDP^0.85; R(KDP,ZDR) = 90.8 KDP^0.93 10^(−0.169·ZDR_dB) | | CSU blended defaults (code cites Bringi & Chandrasekar textbook) | CSU_RadarTools source, `csu_blended_rain.py` |
| S | R(KDP) = 29.0 \|KDP\|^0.77 | | MRMS, for Z ≥ 50 dBZ; from Oklahoma disdrometer data near hailstorms | Zhang et al. 2017, 38th AMS Radar Conf. 22B.3 (precursor of Zhang et al. 2020) |
| S | R(KDP) = 50.70 KDP^0.85 | | Py-ART default ("Beard and Chuang"), docstring cites Figueras i Ventura et al. 2012 | Py-ART `retrieve/qpe.py` |
| S | R(A) = a·A_h^1.03; a = 2230 (0 °C), 3100 (10 °C), 4120 (20 °C), 5330 (30 °C) | λ = 11.0 cm | horizontal polarisation | **Ryzhkov et al. 2014, Table 1** (read) |
| S | R(A) = 4120 A^1.03 | | single relation used for whole WSR-88D network; T-dependence of a and α cancel at S band | Zhang et al. 2017 AMS 22B.3; MRMS poster 2023 |
| S | α = A/KDP: 0.015 dB/° typical | | S-band default; MRMS: α = 0.04875 − 0.75·K | Ryzhkov et al. 2014; Zhang et al. 2017; Grams et al. 2019 |
| C | R(A) = 221 A^0.92 (0 °C); 250 A^0.91 (10 °C); 294 A^0.89 (20 °C); 352 A^0.89 (30 °C) | λ = 5.3 cm | horizontal | **Ryzhkov et al. 2014, Table 1** (read); Py-ART C default (250, 0.91) cites Diederich 2015 |
| C | R(KDP) = 29.70 KDP^0.85 | | Py-ART default ("Beard and Chuang"), cites Figueras i Ventura et al. 2012 | Py-ART `retrieve/qpe.py` |
| X | R(A) = 49.1 A^0.87 (0 °C); 45.5 A^0.83 (10 °C); 43.5 A^0.79 (20 °C); 43.0 A^0.76 (30 °C) | λ = 3.2 cm | horizontal | **Ryzhkov et al. 2014, Table 1** (read) |
| X | R(KDP) = 15.81 KDP^0.7992 | | Py-ART default ("Brandes coefficients") | Py-ART `retrieve/qpe.py` |
| S/C/X | γ = β/α (ZPHI) medians: continental 0.36/0.39/0.19; tropical 0.12/0.14/0.14 (S/C/X, 20 °C) | | Oklahoma DSD simulations | **Ryzhkov et al. 2014, Table 2** (read) |
| S (India, Chennai) | Z = 267 R^1.345 | | Chennai S-band DWR vs gauges ≤ 100 km, Nov–Dec 2001; accumulations within 15 % in 2002–03 | Suresh et al. 2005, MAUSAM — 10.54302/mausam.v56i2.950 (abstract, read) |
| disdrometer (India, Kolkata) | overall Z = 244 R^1.36; convective Z = 798 R^1.01; stratiform Z = 216 R^1.27 | | 4 years of JW RD-80 disdrometer at Dum Dum; MP underestimates R > 10 mm h⁻¹ by 20–31 % | Karmakar 2026 **[preprint]**, Research Square — 10.21203/rs.3.rs-9290725/v1 (abstract, read) |
| S (snow/ice, NEXRAD) | dry snow above ML: 2.8·R(Z); wet snow: 0.6·R(Z); graupel: 0.8·R(Z) | | class multipliers | Grams et al. 2019 Table 1 |
| any (NCAR) | R = 0.0274 Z^0.694 (≡ Z = 178 R^1.44) rain; R = 0.0365 Z^0.625 dry snow | | NCAR PID-based QPE | Dixon et al. 2015 |

**Not quoted (not read):** Bukovčić snow S(KDP,Z) coefficients; Diederich 2015 Part II fitted values; Bringi 2011 UK C-band fits; Wang 2019 final α–Z local adjustment; Indian Western Ghats/Gadanki fits (Das 2017; Kirankumar 2008; Narayana Rao 2009). Implementers should read these from the papers before coding.

**Note on Indian DSDs.** Gadanki studies show the southwest-monsoon DSD is more "continental" (larger drops, higher Dm) and the northeast-monsoon DSD more "oceanic" (more small drops) (Narayana Rao et al. 2009, QJRMS — 10.1002/qj.432; Kirankumar et al. 2008, JAMC — 10.1175/2007JAMC1610.1). Over the Western Ghats and rain-shadow region, DSDs cluster by cloud type and microphysical origin (Das et al. 2017, Atmos. Res. — 10.1016/j.atmosres.2016.11.003; Raut et al. 2021, GRL — 10.1029/2021GL093581). Practical consequence: a single Z–R fails across seasons and regimes in India, which argues for R(A)/R(KDP) wherever ΦDP is available, and for regime-dependent R(Z) where it is not. No peer-reviewed Delhi disdrometer Z–R was found (see 04 notes).

---

## Stage 6b — Vertical profile of reflectivity (VPR), bright band, range effects

| Sub-component | Method | Paper (DOI) | Plain-English description | Bands | Inputs | Open-source | Operational use | Data needs |
|---|---|---|---|---|---|---|---|---|
| Long-range sampling | Simulation of beam broadening/overshooting | Kitchen & Jackson 1993, J. Appl. Meteor. — 10.1175/1520-0450(1993)032<0975:WRPALR>2.0.CO;2 | Quantifies how beam height and width make QPE degrade with range. Motivates every VPR scheme. | any | Z, beam geometry | — | UK | — |
| Range bias documentation | NEXRAD intercomparison | Smith et al. 1996, WRR — 10.1029/96WR00270 | Shows systematic range-dependent underestimation by NEXRAD. | S | — | — | — | Gauges |
| Bright-band/range correction | Idealised VPR from model freezing level + radar | Kitchen, Brown & Davies 1994, QJRMS — 10.1002/qj.49712051906 | UK real-time correction for bright band, range and orographic growth. | C | Z, freezing level | — | UK Nimrod | NWP freezing level |
| VPR identification | Mean, local and inverse methods | Vignal et al. 2000, J. Appl. Meteor. — 10.1175/1520-0450-39.10.1715 | Compares three ways to get the VPR from volume scans; inverse method accounts for beam smoothing. | any | Volume Z | wradlib `vpr` (norm_vpr_stats, CAPPI tools) | — | — |
| VPR range-bias | Real-time VPR adjustment for WSR-88D | Seo et al. 2000, J. Hydrometeor. — 10.1175/1525-7541(2000)001<0222:RTAORD>2.0.CO;2 | Range-dependent bias removal using a VPR. | S | Volume Z | — | NWS | — |
| VPR evaluation | Large-sample test of VPR vs gauge range correction | Vignal & Krajewski 2001, J. Hydrometeor. — 10.1175/1525-7541(2001)002<0490:LSEOTM>2.0.CO;2 | VPR correction vs simple range-gauge correction on many events. | S | Volume Z, gauges | — | — | Gauges |
| Mesobeta VPR | Local, time-smoothed VPR over ~mesobeta domains, climatological fallback | Germann & Joss 2002, J. Appl. Meteor. — 10.1175/1520-0450(2002)041<0542:MPTERP>2.0.CO;2 | Extrapolates radar measurements high above the Alps down to ground with a regional VPR. | C | Volume Z | — | MeteoSwiss | — |
| Swiss operational chain | Clutter, visibility, VPR, global bias in mountains | Germann et al. 2006, QJRMS — 10.1256/qj.05.190 | End-to-end operational design for mountainous QPE. | C | Volume Z | — | MeteoSwiss | DEM, gauges |
| Brightband ID | BB detection from VPR | Zhang, Langston & Howard 2008, JTECH — 10.1175/2008JTECHA1039.1 | Finds bright-band top/bottom from WSR-88D VPRs. | S | Volume Z | — | NMQ/MRMS | — |
| Apparent VPR correction | Apparent VPR (as seen by each tilt), BB correction | **Zhang & Qi 2010**, J. Hydrometeor. — 10.1175/2010JHM1201.1 | Builds an "apparent VPR" per tilt so the correction includes beam broadening, then corrects bright-band contamination in real time. | S | Volume Z | — | NMQ/MRMS | — |
| Rain-type VPR | VPR identification by rainfall classification | Kirstetter et al. 2010, JAMC — 10.1175/2010JAMC2369.1 | Separate convective/stratiform VPRs improve the correction. | any | Volume Z | — | Météo-France research | — |
| Lagrangian VPR | VPR with uncertainty using a Lagrangian approach | Hazenberg et al. 2011, WRR — 10.1029/2010WR009068; Hazenberg et al. 2013, JGR — 10.1002/jgrd.50726 | Stratiform winter rain in the Belgian Ardennes; VPR identified along storm motion with uncertainty estimates. | C | Volume Z | — | Research | — |
| Low BB | Correction for low/partially observed bright band | Qi et al. 2013, J. Hydrometeor. — 10.1175/JHM-D-13-040.1 | Handles bright bands close to the ground (cool season). | S | Volume Z | — | MRMS | — |
| Pol-VPR | VPR correction using polarimetric BB detection | Qi, Zhang, Zhang & Cao 2013, JGR — 10.1002/jgrd.50364 | Uses ρhv/ZDR to locate the bright band more reliably. | S | Z, ρhv, ZDR | — | MRMS | — |
| Apparent VPR, X band pol | Polarimetric correction for apparent VPR | Kalogiros et al. 2013, JAMC — 10.1175/JAMC-D-12-0140.1 | Corrects Z and rain for apparent VPR using polarimetric data. | X | Z, ZDR, KDP | — | Research | — |
| VPR ensembles | VPR-based correction ensembles for ground-level Z | Koistinen & Pohjola 2014, JAMC — 10.1175/JAMC-D-13-0343.1 | FMI operational VPR correction, with ensemble to express uncertainty of the extrapolation. | C | Volume Z | — | FMI | NWP |
| Dual-pol VPR (MRMS) | dpVPR: linear VPR model fitted to sector-mean Z and ρhv range profiles | Hanft, Zhang & Simpson 2023, J. Hydrometeor. — 10.1175/JHM-D-22-0010.1 | Uses ρhv-identified melting layer to fit a simple linear VPR; reduces near-range overestimation and far-range underestimation. | S | Z, ρhv | — | MRMS (operational) | NWP |
| QVP | Quasi-vertical profiles from high-elevation PPIs | Ryzhkov et al. 2016, JTECH — 10.1175/JTECH-D-15-0020.1 | Azimuthally averaged high-tilt data give a time–height profile of Z, ZDR, ρhv; basis for ML detection and QVP-informed VPR. | S, C, X | Volume Z, ZDR, ρhv | Py-ART `retrieve.quasi_vertical_profile`, `compute_qvp`, `compute_rqvp` | Research; inputs to MRMS-style dpVPR | — |
| ML detection | Polarimetric melting-layer designation | Giangrande, Krause & Ryzhkov 2008, JAMC — 10.1175/2007JAMC1634.1 | Detects ML top/bottom from ρhv/ZDR/Z in a conical scan; used by NEXRAD HCA and QPE. | S | Z, ZDR, ρhv | — | NEXRAD MLDA | Sounding fallback |

---

## Stage 6c — Beam blockage, hybrid scan / lowest usable elevation

| Sub-component | Method | Paper (DOI) | Plain-English description | Bands | Inputs | Open-source | Operational use | Data needs |
|---|---|---|---|---|---|---|---|---|
| DEM-based PBB | Beam-blockage fraction from DEM + beam pattern; refractivity sensitivity | **Bech et al. 2003**, JTECH — 10.1175/1520-0426(2003)020<0845:TSOSPW>2.0.CO;2 | Computes the fraction of the beam blocked by terrain and corrects Z; shows the correction depends on the vertical refractivity gradient (ducting). | any | DEM, antenna geometry, refractivity | **wradlib** `qual.beam_block_frac`, `qual.cum_beam_block_frac` (docstring: "From Bech et al. (2003), Eqn 2 and Appendix") | Catalonia (SMC); widely copied | DEM (SRTM/Copernicus), sounding for refractivity |
| GIS blockage | GIS-based blockage assessment | Krajewski, Ntelekos & Goska 2006, Comput. Geosci. — 10.1016/j.cageo.2005.06.024 | DEM/GIS assessment of NEXRAD blockage in mountains. | S | DEM | — | NEXRAD studies | DEM |
| BBF as quality | Beam-blockage fraction as quality filter | Crisologo et al. 2018, AMT — 10.5194/amt-11-5223-2018 | Uses wradlib BBF to filter ground vs spaceborne radar comparisons; template for a BBF quality index. | any | DEM | wradlib | — | DEM |
| Pol PBB (phase) | Self-consistency of Z, ZDR, KDP/ΦDP to correct blocked Z | Giangrande & Ryzhkov 2005, JTECH — 10.1175/JTECH1766.1 | Uses unbiased KDP to restore Z bias in blocked sectors. | S | Z, ZDR, KDP | — | NEXRAD research | — |
| Pol PBB (ΦDP) | ΦDP-based partial blockage correction | **Lang, Nesbitt & Carey 2009**, JTECH — 10.1175/2008JTECHA1133.1 | Self-consistency between Z and ΦDP rises along the ray to estimate how much a blocked sector loses. | C, S | Z, ΦDP | — | Research | — |
| Pol PBB (operational) | Self-consistency PBB correction | Zhang, Zrnić & Ryzhkov 2013, JTECH — 10.1175/JTECH-D-12-00075.1 | Operational-style PBB correction from polarimetric consistency. | S | Z, ZDR, KDP | — | NEXRAD | — |
| R(A) blockage immunity | R(A) uses only the ΦDP span and Z shape, so it is blockage-insensitive | Ryzhkov et al. 2014 (above); Diederich et al. 2015 Part I | Blocked sectors give correct R(A) because a constant Z offset cancels in the retrieval. | S, C, X | Z, ΦDP | Py-ART | MRMS | — |
| Hybrid scan | Lowest unblocked bin (blockage < threshold, above clutter) per range bin | Fulton et al. 1998 (above) | Build a 2-D "hybrid scan reflectivity" from the lowest usable tilt at each azimuth/range. | any | Volume Z, blockage map | — (simple) | NEXRAD PPS, MRMS | DEM |
| Seamless hybrid scan | Quality-index-based seamless hybrid scan mosaic | Qi & Zhang 2017, J. Hydrometeor. — 10.1175/JHM-D-16-0197.1 | Chooses lowest good-quality bin and blends radars by height, blockage and ML so there are no seams. | S | Volume Z, blockage, ML | — | MRMS SHSR | DEM, NWP |
| Hybrid vs CAPPI | Hybrid surface rainfall vs CAPPI | Kwon, Jung & Lee 2015, J. Hydrol. — 10.1016/j.jhydrol.2015.08.063 | Korean S-band dual-pol: hybrid surface rainfall beats CAPPI-based rain. | S | Volume Z | — | KMA HSR | DEM |

---

## Stage 7 — Radar–gauge merging, bias adjustment, uncertainty, extra sources

| Sub-component | Method | Paper (DOI) | Plain-English description | Bands | Inputs | Open-source | Operational use | Data needs |
|---|---|---|---|---|---|---|---|---|
| Mean field bias (MFB) | Kalman-filter MFB | Smith & Krajewski 1991, J. Appl. Meteor. — 10.1175/1520-0450(1991)030<0397:EOTMFB>2.0.CO;2 | One multiplicative factor for the whole radar, updated in time with a Kalman filter. | any | Radar accumulation, gauges | wradlib `adjust.AdjustMFB` | NWS (Seo 1999) | Gauges (few are enough) |
| MFB (operational) | Real-time MFB | Seo, Breidenbach & Johnson 1999, J. Hydrol. — 10.1016/S0022-1694(99)00106-7 | NWS operational MFB with memory over past hours. | any | same | — | NWS MPE | Gauges |
| Local bias | Spatially non-uniform bias | Seo & Breidenbach 2002, J. Hydrometeor. — 10.1175/1525-7541(2002)003<0093:RTCOSN>2.0.CO;2 | Local bias field interpolated from radar/gauge ratios. | any | same | wradlib `AdjustMultiply` / `AdjustMixed` (related) | NWS MPE | Dense gauges |
| Optimal estimation | Radar+gauge optimal estimation | Seo 1998, J. Hydrol. — 10.1016/S0022-1694(98)00141-3 | Statistical optimal merging behind NWS multisensor precipitation. | any | same | — | NWS Stage III/MPE | Gauges |
| Co-kriging | Cokriging radar and gauge | Krajewski 1987, JGR — 10.1029/JD092iD08p09571 | Earliest geostatistical merging. | any | same | — | — | Gauges |
| Bayesian | Bayesian (Kalman) block-kriging conditioning | Todini 2001, HESS — 10.5194/hess-5-187-2001 | Treats radar as prior and gauges as observations, giving a posterior field with variance. | any | same | — | Research | Gauges |
| Conditional merging | Kriged gauges + (radar − kriged radar-at-gauges) | **Sinclair & Pegram 2005**, Atmos. Sci. Lett. — 10.1002/asl.85 | Keeps the radar's spatial pattern but forces the field to equal gauges at gauge locations. | any | same | wradlib (adjust/ipol building blocks); mergeplg | South Africa; widely used in research | Moderate gauge density |
| KNMI adjustment | MFB + spatial adjustment, long-term verification | Holleman 2007, Meteorol. Appl. — 10.1002/met.22 | KNMI daily spatial adjustment and hourly MFB. | C | same | — | KNMI | Gauges (manual daily + automatic hourly) |
| KNMI climatology | 10-year gauge-adjusted radar climatology | Overeem, Holleman & Buishand 2009, JAMC — 10.1175/2009JAMC1954.1 | Reference design for a reprocessed, gauge-adjusted archive. | C | same | KNMI Data Platform | KNMI | Gauges |
| Benchmark | Comparison of MFB, range-dependent, static/dynamic local bias, OK, KED | **Goudenhoofdt & Delobbe 2009**, HESS — 10.5194/hess-13-195-2009 | Belgian benchmark: methods using both radar and gauges (KED, range-dependent adjustment) win; MFB is a robust baseline. | C | same | — | RMI Belgium | Gauges |
| KED | Kriging with external drift with non-parametric correlograms | Velasco-Forero et al. 2009, Adv. Water Resour. — 10.1016/j.advwatres.2008.10.004 | Radar is the drift, gauges are the data; correlogram estimated from radar itself. | any | same | mergeplg (KED/BK functions) | — | Gauges |
| KED (Swiss) | KED in Switzerland; transformation and uncertainty | Schiemann et al. 2011, HESS — 10.5194/hess-15-1515-2011; Erdin, Frei & Künsch 2012, J. Hydrometeor. — 10.1175/JHM-D-11-096.1 | Box–Cox transform and uncertainty of geostatistical merging. | C | same | — | MeteoSwiss | Gauges |
| CombiPrecip | Spatio-temporal co-kriging with external drift | Sideris et al. 2014, QJRMS — 10.1002/qj.2188 | Operational MeteoSwiss merging in alpine terrain, using time information as well as space. | C | same | — | MeteoSwiss CombiPrecip | ~250+ automatic gauges |
| Merging ensembles | Kriging-variance multi-member ensembles | Sideris et al. 2025, QJRMS — 10.1002/qj.4990 | Generates ensemble members from the kriging variance of CombiPrecip. | C | same | — | MeteoSwiss | Gauges |
| CB-penalised kriging | Conditional-bias-penalised optimal estimation | Seo et al. 2014, J. Hydrol. — 10.1016/j.jhydrol.2014.09.055 | Reduces systematic underestimation of extremes typical of kriging. | any | same | — | Research | Gauges |
| UK kriging | Assessment of kriging merging variants | Jewell & Gaussiat 2015, QJRMS — 10.1002/qj.2522 | UK Met Office comparison of kriging-based merging. | C | same | — | UK Met Office | Gauges |
| Australia | Assessment of combination algorithms | Hasan et al. 2016, WRR — 10.1002/2015WR018441 | Compares merging approaches over Australia. | S/C | same | — | BoM Rainfields context | Gauges |
| Review | Merging-method review for urban hydrology | Ochoa-Rodriguez et al. 2019, WRR — 10.1029/2018WR023332 | Taxonomy (bias adjustment, error-variance, geostatistical, Bayesian) and recommendations by gauge density and scale. | any | — | — | — | — |
| MRMS gauge correction + Mountain Mapper | Local gauge bias + PRISM orographic climatology | Zhang et al. 2014, J. Hydrometeor. — 10.1175/JHM-D-13-0163.1 | MRMS gauge-corrected QPE (inverse-distance local bias) and gauge+PRISM where radar coverage is poor. | S | Radar QPE, gauges, PRISM | — | MRMS | Gauges, precipitation climatology |
| Gauge QC | Multi-sensor automated gauge QC | Qi et al. 2016, J. Hydrometeor. — 10.1175/JHM-D-15-0188.1; Martinaitis et al. 2015 — 10.1175/JHM-D-15-0020.1; Martinaitis et al. 2021 — 10.1175/JHM-D-20-0234.1 | Flags gauges that disagree with radar/NWP context before merging. Essential with crowdsourced/sparse gauges. | any | Gauges, radar | — | MRMS | Gauges |
| Uncertainty (ensemble) | REAL ensemble radar QPE | **Germann et al. 2009**, QJRMS — 10.1002/qj.375 | Ensemble members = deterministic QPE + stochastic perturbations with realistic space–time error covariance. | C | QPE, gauges (error stats) | pysteps noise generators (building block) | MeteoSwiss | Gauges for error model |
| Uncertainty (error model) | Product-error-driven model | Ciach, Krajewski & Villarini 2007, J. Hydrometeor. — 10.1175/2007JHM814.1 | Multiplicative error model conditioned on rain rate and scale. | S | QPE, gauges | — | Research | Gauges |
| Uncertainty (probabilistic) | Probabilistic QPE conditioned on rain type and radar quality | Kirstetter et al. 2015, WRR — 10.1002/2014WR015672 | Gives a PDF of rain rate per pixel for MRMS. | S | QPE, quality | — | MRMS research | — |
| Uncertainty reviews | Sources of uncertainty; 30 years of effort | Villarini & Krajewski 2010, Surv. Geophys. — 10.1007/s10712-009-9079-x; Krajewski, Villarini & Smith 2010, BAMS — 10.1175/2009BAMS2747.1 | Reference lists of error sources and the state of uncertainty modelling. | any | — | — | — | — |
| CML rainfall | Country-wide rain maps from commercial microwave links | Overeem, Leijnse & Uijlenhoet 2013, PNAS — 10.1073/pnas.1217961110; Overeem et al. 2016, AMT — 10.5194/amt-9-2425-2016 | Rain-induced attenuation on mobile-network links gives path-averaged rain; RAINLINK retrieval. | link frequencies 6–40 GHz | Link RSL/TSL | RAINLINK (R; https://github.com/overeem11/RAINLINK) | Research (NL) | Operator link data |
| CML (Germany) | Optimised processing over a national CML network | Graf et al. 2020, HESS — 10.5194/hess-24-2931-2020 | Wet/dry detection, baseline, wet-antenna and validation for a year of German data. | — | Link data | **pycomlink** (https://github.com/pycomlink/pycomlink): `processing.wet_dry`, `baseline`, `wet_antenna`, `k_R_relation`, `spatial.interpolator` | DWD research | Operator link data |
| CML wet/dry | CNN rain-event detection in CML attenuation | Polz et al. 2020, AMT — 10.5194/amt-13-3835-2020 | Deep-learning wet/dry classification, in pycomlink. | — | Link data | pycomlink `wet_dry.mlp`/CNN | — | — |
| CML review | Status and challenges | Chwala & Kunstmann 2019, WIREs Water — 10.1002/wat2.1337 | Review of CML rainfall, including merging with radar. | — | — | — | — | — |
| CML+gauge+radar merging | Point/line/grid merging library | mergeplg (OpenSense COST Action), no paper DOI | Merging methods for "point (gauges), line (CMLs) and grid (radar)" data; includes RADOLAN-style adjustment and block kriging. | — | Gauges, CMLs, radar | https://github.com/OpenSenseAction/mergeplg | Research | — |
| Satellite | IMERG multi-satellite precipitation | Huffman et al. 2020, in *Satellite Precipitation Measurement* (Springer) — 10.1007/978-3-030-24568-9_19 | Global 0.1°, 30-min precipitation; Early/Late/Final runs; candidate background where radar is absent. | — | — | NASA GES DISC | Global | — |
| Satellite over India | IMERG evaluation, southwest monsoon | Prakash & Srinivasan 2021, Remote Sens. — 10.3390/rs13183676 | Near-real-time IMERG has much larger all-India bias than Final. | — | — | — | — | — |
| Satellite–gauge India | IMD–NCMRWF merged satellite–gauge | Mitra et al. 2009, JMSJ — 10.2151/jmsj.87A.265 | Daily Indian analysis merging gauges with TRMM TMPA; template for adding satellite where radar is missing. | — | — | — | IMD/NCMRWF | IMD gauges |
| Gauge+radar+satellite | China 1 km merged product (CMPA lineage) | Shen et al. 2018, Remote Sens. — 10.3390/rs10020264; Shen et al. 2014, JGR — 10.1002/2013JD020686 | Multi-source merging at 1 km/hourly: gauges as truth, radar for structure, satellite to fill gaps. | S, C | Gauges, radar, satellite | — | CMA | Dense gauges |

---

## Stage 8 — Multi-radar compositing, accumulation, national reference designs

| Sub-component | Method | Paper (DOI) | Plain-English description | Bands | Inputs | Open-source | Operational use | Data needs |
|---|---|---|---|---|---|---|---|---|
| 3-D mosaic | Distance/height-weighted 3-D multi-radar mosaic | Zhang, Howard & Gourley 2005, JTECH — 10.1175/JTECH-1689.1 | Weights each radar's bin by distance and vertical offset to build a 3-D Cartesian mosaic. | any | Volume Z | Py-ART `map.grid_from_radars` (similar weighting); wradlib `comp` | NMQ/MRMS | — |
| NMQ | National mosaic + multi-sensor QPE | Zhang et al. 2011, BAMS — 10.1175/2011BAMS-D-11-00047.1 | The integrated design: QC → 3-D mosaic → hybrid scan → VPR → classification → R(Z) → gauge correction. | S | Volume Z, NWP, gauges | — | NMQ → MRMS | NWP, gauges |
| MRMS QPE | Radar-only, gauge-corrected, Mountain Mapper; Pass 1/2 latency | **Zhang et al. 2016**, BAMS — 10.1175/BAMS-D-14-00174.1 | Operational US reference system for 1-km/2-min QPE. | S (+C) | same | Products on AWS (noaa-mrms-pds) | NOAA/NWS | NWP, gauges, PRISM |
| MRMS companion | Severe weather/aviation products, 3-D mosaic | Smith et al. 2016, BAMS — 10.1175/BAMS-D-14-00173.1 | QC and mosaic details for the non-QPE side. | S | — | — | NOAA | — |
| Quality-weighted composite | Quality-index-weighted and max-quality ("KO") compositing | Michelson et al. 2018, J. Open Res. Softw. — 10.5334/jors.193 | BALTRAD toolbox: ODIM-HDF5 exchange, quality-flagged products, composite generation. | any | ODIM volumes + quality fields | **BALTRAD** (https://github.com/baltrad); wradlib `comp.compose_weighted`, `comp.compose_ko` | Several European NMHSs | — |
| OPERA | Pan-European composite (ODYSSEY hub) | Huuskonen, Saltikoff & Holleman 2014, BAMS — 10.1175/BAMS-D-12-00216.1; Saltikoff et al. 2019, Atmosphere — 10.3390/atmos10060320 | How 200+ radars of mixed bands and QC become one European composite. | S, C | National volumes | — | EUMETNET OPERA | — |
| EURADCLIM | Gauge-adjusted OPERA climatology | Overeem et al. 2023, ESSD — 10.5194/essd-15-1441-2023 | 2 km, 1 h/24 h European gauge-adjusted radar dataset; template for a reprocessed archive. | S, C | OPERA composite, gauges | KNMI Data Platform | KNMI | ECA&D gauges |
| MeteoSwiss | Rad4Alp, CPC/RZC, CombiPrecip in complex orography | **Germann et al. 2022**, Remote Sens. — 10.3390/rs14030503 | Reference design for mountains: high-elevation radars, visibility maps, VPR, KED merging. | C | — | — | MeteoSwiss | DEM, gauges |
| DWD RADKLIM | Reprocessed RADOLAN-based climatology | Winterrath et al. 2018, DWD dataset — 10.5676/DWD/RADKLIM_YW_V2017.002 (DataCite); Kreklow et al. 2020, Atmosphere — 10.3390/atmos11020217 | Quasi gauge-adjusted 5-min and hourly German QPE; evaluation of artefacts. | C | RADOLAN, gauges | wradlib RADOLAN readers; DWD Open Data | DWD | ~1000+ gauges |
| DWD RADOLAN | Hourly gauge-adjusted composite (RW) | No peer-reviewed DOI; wradlib RADOLAN guide: https://docs.wradlib.org/projects/radolan | Operational combination of multiplicative and additive adjustment; mergeplg reimplements parts (`mergeplg.radolan`). | C | — | wradlib, mergeplg | DWD | Gauges |
| UK Met Office | QC/correction chain; hydrological products | Harrison, Driscoll & Kitchen 2000, Meteorol. Appl. — 10.1017/S1350482700001468; Harrison et al. 2012, Proc. ICE Water Manag. — 10.1680/wama.2012.165.2.89 | UK national composite with VPR, blockage and gauge adjustment. | C | — | — | UK Met Office | Gauges |
| Météo-France | National rainfall product methodology/validation | Tabary 2007, Wea. Forecasting — 10.1175/WAF1004.1; Tabary et al. 2007 — 10.1175/WAF1005.1 | VPR, blockage, adjustment in a national C-band network. | C, S | — | — | Météo-France | Gauges |
| JMA | Radar/Raingauge-Analyzed Precipitation | Nagata 2011, JMA Technical Review 13 (no DOI): https://www.jma.go.jp/jma/jma-eng/jma-center/rsmc-hp-pub-eg/techrev/text13-2.pdf; Ishizaki & Matsuyama 2018, SOLA — 10.2151/sola.2018-034 | Hourly radar composite calibrated with AMeDAS gauges; climatological evaluation. | C | — | — | JMA | Dense gauges |
| KMA | Operational real-time adjustment | Suk et al. 2013, JMSJ — 10.2151/jmsj.2013-409 | Real-time radar rainfall adjustment over South Korea. | S | — | — | KMA | Gauges |
| KMA RRBF | Radar–gauge merging with residual radial basis functions | Ryu et al. 2026 **[preprint, ESSD discussions]** — 10.5194/essd-2026-302 | 10-min, 0.5-km merged dataset: temporally constrained bias scaling, then RBF interpolation of residuals. | S | KMA composite, 1-min gauges | — | KMA dataset | Dense gauges |
| CMA | Gauge–radar–satellite merging | Shen et al. 2018 (above) | CMPA/CMPAS-lineage multi-source analysis. | S, C | — | — | CMA | Dense gauges |
| India | Radar mosaic with composite quality index and gridded radar rainfall | Amar Jyothi et al. 2016, Proc. SPIE — 10.1117/12.2223802; Roy Bhowmik et al. 2011, Meteorol. Atmos. Phys. — 10.1007/s00703-010-0120-x | NCMRWF mosaic and gridded QPE; IMD DWR processing for mesoscale use. Closest thing to an Indian national radar QPE. | S, C, X | IMD volumes | — | NCMRWF (internal) | — |
| Temporal sampling | Sampling problem for small basins; advection | Fabry et al. 1994, J. Hydrol. — 10.1016/0022-1694(94)90138-4 | Shows that scan interval, not just resolution, controls small-basin accumulation errors. | any | Rain maps | — | — | — |
| Advection-corrected accumulation | Advection interpolation between scans | Anagnostou & Krajewski 1999, JTECH — 10.1175/1520-0426(1999)016<0189:RTRREP>2.0.CO;2 | Interpolates rain maps between scans along the motion field before summing. | any | Rain maps, motion | **pysteps** example `advection_correction.py` (optical flow, Lucas–Kanade) | — | — |
| Advection sensitivity | Effect of advection parameters on temporal sampling correction | Seo & Krajewski 2015, J. Hydrol. — 10.1016/j.jhydrol.2015.04.018 | Quantifies how motion estimation choices affect corrected accumulations. | S | Rain maps | — | — | — |
| ML advection/adjustment | 3-D CNN temporal super-resolution, ground adjustment, advection correction | Polz et al. 2024, IEEE TGRS — 10.1109/TGRS.2024.3371577 | Learns interpolation between radar frames jointly with gauge/CML adjustment. | C | Rain maps, CMLs/gauges | — | Research | — |

---

## Place-dependent issues and which methods address them

| Issue | Where it matters (examples) | Failure mode | Methods that address it (this survey) |
|---|---|---|---|
| Mountains / partial beam blockage | Alps, western US, Himalaya and its foothills (IMD X-band radars), Western Ghats; locally, tall buildings around urban radars | Blocked sectors underestimate; lowest usable tilt rises; overshooting | Bech 2003 DEM PBB (wradlib); Lang 2009 / Zhang 2013 / Giangrande 2005 polarimetric PBB; R(A) blockage immunity (Ryzhkov 2014; Diederich 2015); hybrid scan (Fulton 1998; Qi & Zhang 2017); Germann & Joss 2002 VPR; Germann 2006/2022 design; MRMS Mountain Mapper (Zhang 2014) |
| Monsoon deep convection, hail, very high rain rates | Delhi pre-monsoon hail, monsoon MCSs, NE India, Chennai NE monsoon | Z–R saturates/overestimates in hail, underestimates tropical heavy rain; C/X attenuation | R(KDP) (Ryzhkov & Zrnić 1996); HCA-driven selection (Giangrande & Ryzhkov 2008, Grams 2019 table); R(A) with α from ZDR slope (Wang 2019; Zhang 2020); regime Z–R (Rosenfeld 1993; Suresh 2005; Karmakar 2026 preprint); attenuation correction (Stage 3) |
| DSD regime variability | SW vs NE monsoon (Gadanki), continental vs maritime | Single Z–R biased by factor up to ~2 | R(A) (least DSD-sensitive), dynamic α (Wang 2019), Indian DSD studies (Kirankumar 2008; Narayana Rao 2009; Das 2017; Raut 2021) |
| Stratiform bright band | Winter western disturbances in N India, mid-latitude stratiform, post-monsoon | Bright-band overestimation at mid range; underestimation beyond | Zhang & Qi 2010; Qi 2013 (low BB); Qi 2013 JGR pol-VPR; Hanft 2023 dpVPR; Kirstetter 2010; Koistinen & Pohjola 2014; QVP (Ryzhkov 2016) for ML height |
| Long range / overshooting | > 100 km from any radar; sparse networks (central India) | Underestimation, missed shallow rain | VPR (Vignal 2000; Germann & Joss 2002); range-dependent adjustment (Goudenhoofdt & Delobbe 2009); quality-weighted mosaic (Qi & Zhang 2017; BALTRAD); satellite fill (IMERG, Huffman 2020; Mitra 2009); MRMS R(Z) fill beyond R(A) (Zhang 2020) |
| Sparse or poor-quality gauges | Most of India outside cities; Africa | Kriging unstable, local bias noisy | MFB (Smith & Krajewski 1991; Seo 1999) first; conditional merging only with enough gauges; gauge QC (Qi 2016; Martinaitis 2021); CMLs as extra sensors (Overeem 2013; Graf 2020; pycomlink, mergeplg); satellite–gauge background (Mitra 2009; Shen 2018) |
| Dense gauges, urban | Delhi NCR, Mumbai, Korea, Switzerland | Need to keep radar small-scale structure | KED (Velasco-Forero 2009; Sideris 2014); conditional merging (Sinclair & Pegram 2005); RRBF (Ryu 2026 preprint); Ochoa-Rodriguez 2019 review guidance |
| Coasts / sea clutter / tropical maritime rain | Chennai, Mumbai, Kolkata, Bay of Bengal cyclones | AP/sea clutter; maritime DSD with many small drops | Polarimetric QC (Stage 2); tropical estimators (Thompson 2018; Rosenfeld 1993 tropical); R(A) α tropical default (Ryzhkov 2014 Table 2; Grams 2019) |
| Mixed-band networks | IMD S + C + X; Europe S + C | Calibration and attenuation differences create seams | R(A) (calibration-immune); quality-weighted compositing (Michelson 2018; Saltikoff 2019); OPERA/EURADCLIM experience (Overeem 2023) |
| Snow / mixed phase | Himalaya, Kashmir; US/Europe winter | Z–S ambiguity, gauge undercatch | Bukovčić 2018/2020; NEXRAD class multipliers (Grams 2019); Martinaitis 2015/2021 gauge QC |
| Long scan intervals, fast storms | IMD volumes every 10 min; fast pre-monsoon squall lines | "Stripes" in accumulations | Advection-corrected accumulation (Anagnostou & Krajewski 1999 via pysteps; Fabry 1994; Seo & Krajewski 2015; Polz 2024) |

---

## Ranked recommendation: what radar-wow should implement next (target: a first end-to-end rain map)

The ranking favours (1) methods that make a usable map with the inputs IMD actually delivers today (the 04 notes found IMD netCDF may lack KDP/ρhv), (2) robustness across S/C/X, and (3) existing open code we can test against.

| Rank | Class (stage) | Paper(s) | Why now | Reference implementation to test against |
|---|---|---|---|---|
| 1 | `BeamBlockageFraction` + `HybridScan` (6c) | Bech et al. 2003; Fulton et al. 1998; Qi & Zhang 2017 | Every downstream step needs "lowest usable bin" and a blockage quality index; needs only a DEM. Single-pol-safe. | wradlib `beam_block_frac`, `cum_beam_block_frac` |
| 2 | `ZRPowerLaw` with regime presets (6a) | Marshall & Palmer 1948; Fulton 1998; Rosenfeld 1993; Suresh 2005 (Chennai) | The always-available fallback for single-pol radars and when ΦDP is missing; presets: MP, NEXRAD convective, tropical, Indian (Chennai), user-fitted. Hail cap at 53 dBZ (Ryzhkov et al. preprint / NEXRAD). | wradlib `zr`, Py-ART `est_rain_rate_z` |
| 3 | `RainRateA` (6a) | Ryzhkov et al. 2014 (band/temperature table above); Diederich 2015; Wang 2019 (α from ZDR slope) | Best single dual-pol estimator: calibration- and blockage-immune, least DSD-sensitive, valid at S, C and X; ideal for a mixed IMD network. | Py-ART `calculate_attenuation_zphi` + `est_rain_rate_a` |
| 4 | `SyntheticRainRate` / HCA-driven selector (6a) | Zhang et al. 2020 (MRMS); Giangrande & Ryzhkov 2008 + Grams 2019 table; Cifelli 2011 (CSU-HIDRO) | Combines R(A) in rain, R(KDP) in hail (Delhi hail!), R(Z) elsewhere/above ML; the operational state of the art. | CSU_RadarTools `csu_hidro_rain`; Grams 2019 Table 1 as spec |
| 5 | `ApparentVPRCorrection` (6b) | Zhang & Qi 2010 (+ Hanft 2023 dpVPR when ρhv exists) | Removes bright-band overestimation and far-range underestimation for winter/post-monsoon stratiform rain and beyond ~100 km. | wradlib `vpr` utilities (partial); no full open implementation (gap to fill) |
| 6 | `QualityWeightedComposite` (8) | Zhang et al. 2005; Qi & Zhang 2017; Michelson et al. 2018 (BALTRAD) | Delhi has three radars (+ Patiala, Jaipur); combine by quality index (height, blockage, distance) not "max". | wradlib `compose_weighted` / `compose_ko`; BALTRAD |
| 7 | `AdvectionCorrectedAccumulation` (8) | Anagnostou & Krajewski 1999; Fabry 1994; Seo & Krajewski 2015 | IMD 10-min scans + fast pre-monsoon storms produce stripes in 1-h/24-h totals. | pysteps `examples/advection_correction.py` |
| 8 | `MeanFieldBias` (Kalman) (7) | Smith & Krajewski 1991; Seo et al. 1999 | Robust with sparse gauges; the minimum to remove calibration bias for the first map. | wradlib `AdjustMFB` |
| 9 | `ConditionalMerging` and `KED` (7) | Sinclair & Pegram 2005; Velasco-Forero 2009; benchmarked by Goudenhoofdt & Delobbe 2009 | Once gauge QC exists and density is adequate (Delhi NCR AWS network), these give the best merged field. | wradlib `adjust`/`ipol`; mergeplg |
| 10 | `REALEnsemble` (7) | Germann et al. 2009 (+ Sideris 2025 for merged fields) | Turns the deterministic map into an uncertainty product for hydrology; do after 1–9 are verified. | pysteps noise generators as building block |

**Why this order.** Ranks 1–2 alone already give a crude single-pol rain map. Ranks 3–4 give the dual-pol quality jump and handle hail and mixed bands. Rank 5 fixes the dominant non-convective error. Ranks 6–7 turn per-radar rates into a city/regional accumulation. Ranks 8–9 tie it to gauges. Rank 10 adds uncertainty. CML merging (pycomlink + mergeplg) and IMERG background are the natural next sources once operator/IMD data agreements exist.

---

## References (all DOIs verified via Crossref on 2026-11-03 unless marked)

### Estimators and DSD
- Marshall, J. S., Palmer, W. McK. (1948). The distribution of raindrops with size. *J. Meteor.* https://doi.org/10.1175/1520-0469(1948)005<0165:TDORWS>2.0.CO;2
- Joss, J., Waldvogel, A. (1969). Raindrop size distribution and sampling size errors. *J. Atmos. Sci.* https://doi.org/10.1175/1520-0469(1969)026<0566:RSDASS>2.0.CO;2
- Rosenfeld, D., Wolff, D. B., Atlas, D. (1993). General probability-matched relations between radar reflectivity and rain rate. *J. Appl. Meteor.* https://doi.org/10.1175/1520-0450(1993)032<0050:GPMRBR>2.0.CO;2
- Ryzhkov, A., Zrnić, D. (1995). Comparison of dual-polarization radar estimators of rain. *JTECH.* https://doi.org/10.1175/1520-0426(1995)012<0249:CODPRE>2.0.CO;2
- Ryzhkov, A., Zrnić, D. (1996). Assessment of rainfall measurement that uses specific differential phase. *J. Appl. Meteor.* https://doi.org/10.1175/1520-0450(1996)035<2080:AORMTU>2.0.CO;2
- Fulton, R. A., et al. (1998). The WSR-88D rainfall algorithm. *Wea. Forecasting.* https://doi.org/10.1175/1520-0434(1998)013<0377:TWRA>2.0.CO;2
- Brandes, E. A., Zhang, G., Vivekanandan, J. (2002). Experiments in rainfall estimation with a polarimetric radar in a subtropical environment. *J. Appl. Meteor.* https://doi.org/10.1175/1520-0450(2002)041<0674:EIREWA>2.0.CO;2
- Ryzhkov, A. V., Giangrande, S. E., Schuur, T. J. (2005). Rainfall estimation with a polarimetric prototype of WSR-88D. *J. Appl. Meteor.* https://doi.org/10.1175/JAM2213.1
- Matrosov, S. Y., et al. (2005). The utility of X-band polarimetric radar for quantitative estimates of rainfall parameters. *J. Hydrometeor.* https://doi.org/10.1175/JHM424.1
- Suresh, R., et al. (2005). On optimum rain rate estimation from a pulsed Doppler weather radar at Chennai. *MAUSAM* 56(2). https://doi.org/10.54302/mausam.v56i2.950
- Giangrande, S. E., Ryzhkov, A. V. (2008). Estimation of rainfall based on the results of polarimetric echo classification. *JAMC.* https://doi.org/10.1175/2008JAMC1753.1
- Kirankumar, N. V. P., Rao, T. N., Radhakrishna, B., Rao, D. N. (2008). Statistical characteristics of raindrop size distribution in southwest monsoon season. *JAMC.* https://doi.org/10.1175/2007JAMC1610.1
- Narayana Rao, T., Radhakrishna, B., Nakamura, K., Prabhakara Rao, N. (2009). Differences in raindrop size distribution from southwest monsoon to northeast monsoon at Gadanki. *QJRMS.* https://doi.org/10.1002/qj.432
- Park, H. S., et al. (2009). The hydrometeor classification algorithm for the polarimetric WSR-88D. *Wea. Forecasting.* https://doi.org/10.1175/2008WAF2222205.1
- Cifelli, R., et al. (2011). A new dual-polarization radar rainfall algorithm: application in Colorado precipitation events. *JTECH.* https://doi.org/10.1175/2010JTECHA1488.1
- Bringi, V. N., et al. (2011). Rainfall estimation with an operational polarimetric C-band radar in the United Kingdom. *J. Hydrometeor.* https://doi.org/10.1175/JHM-D-10-05013.1
- Figueras i Ventura, J., et al. (2012). Long-term monitoring of French polarimetric radar data quality and evaluation of several polarimetric QPE estimators at C-band. *QJRMS.* https://doi.org/10.1002/qj.1934
- Figueras i Ventura, J., Tabary, P. (2013). The new French operational polarimetric radar rainfall rate product. *JAMC.* https://doi.org/10.1175/JAMC-D-12-0179.1
- Ryzhkov, A., Diederich, M., Zhang, P., Simmer, C. (2014). Potential utilization of specific attenuation for rainfall estimation, mitigation of partial beam blockage, and radar networking. *JTECH* 31, 599–619. https://doi.org/10.1175/JTECH-D-13-00038.1
- Diederich, M., Ryzhkov, A., Simmer, C., Zhang, P., Trömel, S. (2015). Use of specific attenuation for rainfall measurement at X-band radar wavelengths. Part I. *J. Hydrometeor.* https://doi.org/10.1175/JHM-D-14-0066.1 ; Part II. https://doi.org/10.1175/JHM-D-14-0067.1
- Chen, H., Chandrasekar, V., Bechini, R. (2017). An improved dual-polarization radar rainfall algorithm (DROPS2.0). *J. Hydrometeor.* https://doi.org/10.1175/JHM-D-16-0124.1
- Das, S. K., Konwar, M., Chakravarty, K., Deshpande, S. M. (2017). Raindrop size distribution of different cloud types over the Western Ghats. *Atmos. Res.* https://doi.org/10.1016/j.atmosres.2016.11.003
- Bukovčić, P., et al. (2018). Polarimetric radar relations for quantification of snow based on disdrometer data. *JAMC.* https://doi.org/10.1175/JAMC-D-17-0090.1
- Thompson, E. J., et al. (2018). Dual-polarization radar rainfall estimation over tropical oceans. *JAMC.* https://doi.org/10.1175/JAMC-D-17-0160.1
- Wang, Y., et al. (2019). A prototype QPE algorithm for operational S-band polarimetric radar utilizing specific attenuation and specific differential phase. Part I. *J. Hydrometeor.* https://doi.org/10.1175/JHM-D-18-0071.1
- Cocks, S. B., et al. (2019). … Part II: Performance verification and case study analysis. *J. Hydrometeor.* https://doi.org/10.1175/JHM-D-18-0070.1
- Ryzhkov, A. V., Zrnić, D. S. (2019). *Radar Polarimetry for Weather Observations.* Springer. https://doi.org/10.1007/978-3-030-05093-1
- Bukovčić, P., Ryzhkov, A., Zrnić, D. (2020). Polarimetric relations for snow estimation—radar verification. *JAMC.* https://doi.org/10.1175/JAMC-D-19-0140.1
- Zhang, J., Tang, L., Cocks, S., Zhang, P., Ryzhkov, A., Howard, K. (2020). A dual-polarization radar synthetic QPE for operations. *J. Hydrometeor.* https://doi.org/10.1175/JHM-D-19-0194.1
- Raut, B. A., et al. (2021). Microphysical origin of raindrop size distributions during the Indian monsoon. *GRL.* https://doi.org/10.1029/2021GL093581
- Ryzhkov, A., Zhang, P., Bukovčić, P., Zhang, J., Cocks, S. (2022). Polarimetric radar quantitative precipitation estimation. *Remote Sens.* 14, 1695. https://doi.org/10.3390/rs14071695
- Zhang, Z., Zhao, Z., Qi, Y., Xiong, M. (2025). Dual-polarization radar quantitative precipitation estimation (QPE): principles, operations, and challenges. *Remote Sens.* 17, 3619. https://doi.org/10.3390/rs17213619
- Karmakar (2026). Region-specific Z-R relationships from disdrometer observations … Kolkata, India. **[preprint, Research Square]** https://doi.org/10.21203/rs.3.rs-9290725/v1

### VPR, bright band, blockage, hybrid scan
- Kitchen, M., Jackson, P. M. (1993). Weather radar performance at long range—simulated and observed. *J. Appl. Meteor.* https://doi.org/10.1175/1520-0450(1993)032<0975:WRPALR>2.0.CO;2
- Kitchen, M., Brown, R., Davies, A. G. (1994). Real-time correction of weather radar data for the effects of bright band, range and orographic growth. *QJRMS.* https://doi.org/10.1002/qj.49712051906
- Smith, J. A., et al. (1996). An intercomparison study of NEXRAD precipitation estimates. *WRR.* https://doi.org/10.1029/96WR00270
- Vignal, B., et al. (2000). Three methods to determine profiles of reflectivity from volumetric radar data. *J. Appl. Meteor.* https://doi.org/10.1175/1520-0450-39.10.1715
- Seo, D.-J., et al. (2000). Real-time adjustment of range-dependent biases in WSR-88D rainfall estimates due to nonuniform VPR. *J. Hydrometeor.* https://doi.org/10.1175/1525-7541(2000)001<0222:RTAORD>2.0.CO;2
- Germann, U., Joss, J. (2002). Mesobeta profiles to extrapolate radar precipitation measurements above the Alps to the ground level. *J. Appl. Meteor.* https://doi.org/10.1175/1520-0450(2002)041<0542:MPTERP>2.0.CO;2
- Bech, J., Codina, B., Lorente, J., Bebbington, D. (2003). The sensitivity of single polarization weather radar beam blockage correction to variability in the vertical refractivity gradient. *JTECH.* https://doi.org/10.1175/1520-0426(2003)020<0845:TSOSPW>2.0.CO;2
- Giangrande, S. E., Ryzhkov, A. V. (2005). Calibration of dual-polarization radar in the presence of partial beam blockage. *JTECH.* https://doi.org/10.1175/JTECH1766.1
- Krajewski, W. F., Ntelekos, A. A., Goska, R. (2006). A GIS-based methodology for the assessment of weather radar beam blockage. *Comput. Geosci.* https://doi.org/10.1016/j.cageo.2005.06.024
- Germann, U., Galli, G., Boscacci, M., Bolliger, M. (2006). Radar precipitation measurement in a mountainous region. *QJRMS.* https://doi.org/10.1256/qj.05.190
- Giangrande, S. E., Krause, J. M., Ryzhkov, A. V. (2008). Automatic designation of the melting layer with a polarimetric prototype of the WSR-88D. *JAMC.* https://doi.org/10.1175/2007JAMC1634.1
- Zhang, J., Langston, C., Howard, K. (2008). Brightband identification based on vertical profiles of reflectivity from the WSR-88D. *JTECH.* https://doi.org/10.1175/2008JTECHA1039.1
- Lang, T. J., Nesbitt, S. W., Carey, L. D. (2009). On the correction of partial beam blockage in polarimetric radar data. *JTECH.* https://doi.org/10.1175/2008JTECHA1133.1
- Zhang, J., Qi, Y. (2010). A real-time algorithm for the correction of brightband effects in radar-derived QPE. *J. Hydrometeor.* https://doi.org/10.1175/2010JHM1201.1
- Kirstetter, P.-E., Andrieu, H., Delrieu, G., Boudevillain, B. (2010). Identification of vertical profiles of reflectivity for correction of volumetric radar data using rainfall classification. *JAMC.* https://doi.org/10.1175/2010JAMC2369.1
- Hazenberg, P., Leijnse, H., Uijlenhoet, R. (2011). Radar rainfall estimation of stratiform winter precipitation in the Belgian Ardennes. *WRR.* https://doi.org/10.1029/2010WR009068
- Hazenberg, P., et al. (2013). Identification and uncertainty estimation of vertical reflectivity profiles using a Lagrangian approach. *JGR Atmos.* https://doi.org/10.1002/jgrd.50726
- Qi, Y., Zhang, J., Zhang, P. (2013). Correction of radar QPE errors associated with low and partially observed brightband layers. *J. Hydrometeor.* https://doi.org/10.1175/JHM-D-13-040.1
- Qi, Y., Zhang, J., Zhang, P., Cao, Q. (2013). VPR correction of bright band effects in radar QPEs using polarimetric radar observations. *JGR Atmos.* https://doi.org/10.1002/jgrd.50364
- Kalogiros, J., et al. (2013). Correction of polarimetric radar reflectivity measurements and rainfall estimates for apparent vertical profile in stratiform rain. *JAMC.* https://doi.org/10.1175/JAMC-D-12-0140.1
- Zhang, P., Zrnić, D., Ryzhkov, A. (2013). Partial beam blockage correction using polarimetric radar measurements. *JTECH.* https://doi.org/10.1175/JTECH-D-12-00075.1
- Koistinen, J., Pohjola, H. (2014). Estimation of ground-level reflectivity factor in operational weather radar networks using VPR-based correction ensembles. *JAMC.* https://doi.org/10.1175/JAMC-D-13-0343.1
- Kwon, S., Jung, S.-H., Lee, G. (2015). Inter-comparison of radar rainfall rate using CAPPI and hybrid surface rainfall maps. *J. Hydrol.* https://doi.org/10.1016/j.jhydrol.2015.08.063
- Ryzhkov, A., et al. (2016). Quasi-vertical profiles—a new way to look at polarimetric radar data. *JTECH.* https://doi.org/10.1175/JTECH-D-15-0020.1
- Qi, Y., Zhang, J. (2017). A physically based two-dimensional seamless reflectivity mosaic for radar QPE in the MRMS system. *J. Hydrometeor.* https://doi.org/10.1175/JHM-D-16-0197.1
- Crisologo, I., et al. (2018). Enhancing the consistency of spaceborne and ground-based radar comparisons by using beam blockage fraction as a quality filter. *AMT.* https://doi.org/10.5194/amt-11-5223-2018
- Hanft, W., Zhang, J., Simpson, M. (2023). Dual-pol VPR corrections for improved operational radar QPE in MRMS. *J. Hydrometeor.* https://doi.org/10.1175/JHM-D-22-0010.1

### Merging, uncertainty, CML, satellite
- Krajewski, W. F. (1987). Cokriging radar-rainfall and rain gage data. *JGR.* https://doi.org/10.1029/JD092iD08p09571
- Smith, J. A., Krajewski, W. F. (1991). Estimation of the mean field bias of radar rainfall estimates. *J. Appl. Meteor.* https://doi.org/10.1175/1520-0450(1991)030<0397:EOTMFB>2.0.CO;2
- Seo, D.-J. (1998). Real-time estimation of rainfall fields using radar rainfall and rain gage data. *J. Hydrol.* https://doi.org/10.1016/S0022-1694(98)00141-3
- Seo, D.-J., Breidenbach, J. P., Johnson, E. R. (1999). Real-time estimation of mean field bias in radar rainfall data. *J. Hydrol.* https://doi.org/10.1016/S0022-1694(99)00106-7
- Todini, E. (2001). A Bayesian technique for conditioning radar precipitation estimates to rain-gauge measurements. *HESS.* https://doi.org/10.5194/hess-5-187-2001
- Seo, D.-J., Breidenbach, J. P. (2002). Real-time correction of spatially nonuniform bias in radar rainfall data using rain gauge measurements. *J. Hydrometeor.* https://doi.org/10.1175/1525-7541(2002)003<0093:RTCOSN>2.0.CO;2
- Sinclair, S., Pegram, G. (2005). Combining radar and rain gauge rainfall estimates using conditional merging. *Atmos. Sci. Lett.* https://doi.org/10.1002/asl.85
- Holleman, I. (2007). Bias adjustment and long-term verification of radar-based precipitation estimates. *Meteorol. Appl.* https://doi.org/10.1002/met.22
- Ciach, G. J., Krajewski, W. F., Villarini, G. (2007). Product-error-driven uncertainty model for probabilistic QPE with NEXRAD data. *J. Hydrometeor.* https://doi.org/10.1175/2007JHM814.1
- Goudenhoofdt, E., Delobbe, L. (2009). Evaluation of radar-gauge merging methods for quantitative precipitation estimates. *HESS* 13, 195–203. https://doi.org/10.5194/hess-13-195-2009
- Velasco-Forero, C. A., et al. (2009). A non-parametric automatic blending methodology to estimate rainfall fields from rain gauge and radar data. *Adv. Water Resour.* https://doi.org/10.1016/j.advwatres.2008.10.004
- Germann, U., Berenguer, M., Sempere-Torres, D., Zappa, M. (2009). REAL—ensemble radar precipitation estimation for hydrology in a mountainous region. *QJRMS.* https://doi.org/10.1002/qj.375
- Overeem, A., Holleman, I., Buishand, A. (2009). Derivation of a 10-year radar-based climatology of rainfall. *JAMC.* https://doi.org/10.1175/2009JAMC1954.1
- Mitra, A. K., et al. (2009). Daily Indian precipitation analysis formed from a merge of rain-gauge data with TRMM TMPA. *JMSJ.* https://doi.org/10.2151/jmsj.87A.265
- Villarini, G., Krajewski, W. F. (2010). Review of the different sources of uncertainty in single polarization radar-based estimates of rainfall. *Surv. Geophys.* https://doi.org/10.1007/s10712-009-9079-x
- Krajewski, W. F., Villarini, G., Smith, J. A. (2010). Radar-rainfall uncertainties: where are we after thirty years of effort? *BAMS.* https://doi.org/10.1175/2009BAMS2747.1
- Schiemann, R., et al. (2011). Geostatistical radar-raingauge combination with nonparametric correlograms. *HESS.* https://doi.org/10.5194/hess-15-1515-2011
- Erdin, R., Frei, C., Künsch, H. R. (2012). Data transformation and uncertainty in geostatistical combination of radar and rain gauges. *J. Hydrometeor.* https://doi.org/10.1175/JHM-D-11-096.1
- Overeem, A., Leijnse, H., Uijlenhoet, R. (2013). Country-wide rainfall maps from cellular communication networks. *PNAS.* https://doi.org/10.1073/pnas.1217961110
- Sideris, I. V., Gabella, M., Erdin, R., Germann, U. (2014; Crossref issue year 2013). Real-time radar–rain-gauge merging using spatio-temporal co-kriging with external drift in the alpine terrain of Switzerland. *QJRMS.* https://doi.org/10.1002/qj.2188
- Zhang, J., Qi, Y., Langston, C., Kaney, B., Howard, K. (2014). A real-time algorithm for merging radar QPEs with rain gauge observations and orographic precipitation climatology. *J. Hydrometeor.* https://doi.org/10.1175/JHM-D-13-0163.1
- Seo, D.-J., Siddique, R., Zhang, Y., Kim, D. (2014). Improving real-time estimation of heavy-to-extreme precipitation using rain gauge data via conditional bias-penalized optimal estimation. *J. Hydrol.* https://doi.org/10.1016/j.jhydrol.2014.09.055
- Kirstetter, P.-E., et al. (2015). Probabilistic precipitation rate estimates with ground-based radar networks. *WRR.* https://doi.org/10.1002/2014WR015672
- Jewell, S. A., Gaussiat, N. (2015). An assessment of kriging-based rain-gauge–radar merging techniques. *QJRMS.* https://doi.org/10.1002/qj.2522
- Hasan, M. M., et al. (2016). Merging radar and in situ rainfall measurements: an assessment of different combination algorithms. *WRR.* https://doi.org/10.1002/2015WR018441
- Qi, Y., et al. (2016). A real-time automated quality control of hourly rain gauge data based on multiple sensors in MRMS. *J. Hydrometeor.* https://doi.org/10.1175/JHM-D-15-0188.1
- Overeem, A., Leijnse, H., Uijlenhoet, R. (2016). Retrieval algorithm for rainfall mapping from microwave links in a cellular communication network. *AMT.* https://doi.org/10.5194/amt-9-2425-2016
- Ochoa-Rodriguez, S., Wang, L.-P., Willems, P., Onof, C. (2019). A review of radar-rain gauge data merging methods and their potential for urban hydrological applications. *WRR.* https://doi.org/10.1029/2018WR023332
- Chwala, C., Kunstmann, H. (2019). Commercial microwave link networks for rainfall observation. *WIREs Water.* https://doi.org/10.1002/wat2.1337
- Graf, M., Chwala, C., Polz, J., Kunstmann, H. (2020). Rainfall estimation from a German-wide commercial microwave link network. *HESS.* https://doi.org/10.5194/hess-24-2931-2020
- Polz, J., Chwala, C., Graf, M., Kunstmann, H. (2020). Rain event detection in commercial microwave link attenuation data using convolutional neural networks. *AMT.* https://doi.org/10.5194/amt-13-3835-2020
- Huffman, G. J., et al. (2020). Integrated Multi-satellite Retrievals for the GPM Mission (IMERG). In *Satellite Precipitation Measurement*, Adv. Global Change Res. https://doi.org/10.1007/978-3-030-24568-9_19
- Martinaitis, S. M., et al. (2015). Understanding winter precipitation impacts on automated gauge observations within a real-time system. *J. Hydrometeor.* https://doi.org/10.1175/JHM-D-15-0020.1
- Martinaitis, S. M., et al. (2021). Advancements and characteristics of gauge ingest and quality control within MRMS. *J. Hydrometeor.* https://doi.org/10.1175/JHM-D-20-0234.1
- Prakash, S., Srinivasan, J. (2021). A comprehensive evaluation of near-real-time and research products of IMERG precipitation over India for the southwest monsoon period. *Remote Sens.* https://doi.org/10.3390/rs13183676
- Sideris, I. V., et al. (2025). Kriging-variance-based multi-member ensembles of radar–rain-gauge precipitation estimates. *QJRMS.* https://doi.org/10.1002/qj.4990

### Mosaics, accumulation, national systems
- Anagnostou, E. N., Krajewski, W. F. (1999). Real-time radar rainfall estimation. Part I: algorithm formulation. *JTECH.* https://doi.org/10.1175/1520-0426(1999)016<0189:RTRREP>2.0.CO;2
- Fabry, F., Bellon, A., Duncan, M. R., Austin, G. L. (1994). High resolution rainfall measurements by radar for very small basins: the sampling problem reexamined. *J. Hydrol.* https://doi.org/10.1016/0022-1694(94)90138-4
- Harrison, D. L., Driscoll, S. J., Kitchen, M. (2000). Improving precipitation estimates from weather radar using quality control and correction techniques. *Meteorol. Appl.* https://doi.org/10.1017/S1350482700001468
- Zhang, J., Howard, K., Gourley, J. J. (2005). Constructing three-dimensional multiple-radar reflectivity mosaics. *JTECH.* https://doi.org/10.1175/JTECH-1689.1
- Tabary, P. (2007). The new French operational radar rainfall product. Part I. *Wea. Forecasting.* https://doi.org/10.1175/WAF1004.1 ; Tabary et al. (2007) Part II. https://doi.org/10.1175/WAF1005.1
- Roy Bhowmik, S. K., et al. (2011). Processing of Indian Doppler weather radar data for mesoscale applications. *Meteorol. Atmos. Phys.* https://doi.org/10.1007/s00703-010-0120-x
- Zhang, J., et al. (2011). National Mosaic and Multi-Sensor QPE (NMQ) system. *BAMS.* https://doi.org/10.1175/2011BAMS-D-11-00047.1
- Harrison, D. L., et al. (2012). Radar products for hydrological applications in the UK. *Proc. ICE Water Manag.* https://doi.org/10.1680/wama.2012.165.2.89
- Suk, M.-K., Chang, K.-H., Cha, J.-W., Kim, K.-E. (2013). Operational real-time adjustment of radar rainfall estimation over the South Korea region. *JMSJ.* https://doi.org/10.2151/jmsj.2013-409
- Kitzmiller, D., et al. (2013). Radar and multisensor precipitation estimation techniques in NWS hydrologic operations. *J. Hydrol. Eng.* https://doi.org/10.1061/(ASCE)HE.1943-5584.0000523
- Huuskonen, A., Saltikoff, E., Holleman, I. (2014). The operational weather radar network in Europe. *BAMS.* https://doi.org/10.1175/BAMS-D-12-00216.1
- Shen, Y., et al. (2014). A high spatiotemporal gauge-satellite merged precipitation analysis over China. *JGR Atmos.* https://doi.org/10.1002/2013JD020686
- Seo, B.-C., Krajewski, W. F. (2015). Correcting temporal sampling error in radar-rainfall: effect of advection parameters and rain storm characteristics. *J. Hydrol.* https://doi.org/10.1016/j.jhydrol.2015.04.018
- Zhang, J., et al. (2016). Multi-Radar Multi-Sensor (MRMS) quantitative precipitation estimation: initial operating capabilities. *BAMS.* https://doi.org/10.1175/BAMS-D-14-00174.1
- Smith, T. M., et al. (2016). MRMS severe weather and aviation products: initial operating capabilities. *BAMS.* https://doi.org/10.1175/BAMS-D-14-00173.1
- Amar Jyothi, K., et al. (2016). Gridded radar rainfall product for comparison with model rainfall. *Proc. SPIE* 9876. https://doi.org/10.1117/12.2223802
- Cocks, S. B., et al. (2017). MRMS QPE performance east of the Rockies during the 2014 warm season. *J. Hydrometeor.* https://doi.org/10.1175/JHM-D-16-0179.1
- Michelson, D., et al. (2018). BALTRAD advanced weather radar networking. *J. Open Res. Softw.* https://doi.org/10.5334/jors.193
- Shen, Y., et al. (2018). China's 1 km merged gauge, radar and satellite experimental precipitation dataset. *Remote Sens.* https://doi.org/10.3390/rs10020264
- Ishizaki, H., Matsuyama, H. (2018). Distribution of the annual precipitation ratio of Radar/Raingauge-Analyzed Precipitation to AMeDAS across Japan. *SOLA.* https://doi.org/10.2151/sola.2018-034
- Winterrath, T., et al. (2018). RADKLIM Version 2017.002 (YW). DWD dataset. https://doi.org/10.5676/DWD/RADKLIM_YW_V2017.002 (DataCite DOI; not in Crossref)
- Saltikoff, E., et al. (2019). OPERA the radar project. *Atmosphere.* https://doi.org/10.3390/atmos10060320
- Pulkkinen, S., et al. (2019). Pysteps: an open-source Python library for probabilistic precipitation nowcasting (v1.0). *GMD.* https://doi.org/10.5194/gmd-12-4185-2019
- Kreklow, J., Tetzlaff, B., Burkhard, B., Kuhnt, G. (2020). Radar-based precipitation climatology in Germany. *Atmosphere.* https://doi.org/10.3390/atmos11020217
- Schleiss, M., et al. (2020). The accuracy of weather radar in heavy rain: a comparative study for Denmark, the Netherlands, Finland and Sweden. *HESS.* https://doi.org/10.5194/hess-24-3157-2020
- Germann, U., Boscacci, M., Clementi, L., et al. (2022). Weather radar in complex orography. *Remote Sens.* 14, 503. https://doi.org/10.3390/rs14030503
- Overeem, A., et al. (2023). EURADCLIM: the European climatological high-resolution gauge-adjusted radar precipitation dataset. *ESSD.* https://doi.org/10.5194/essd-15-1441-2023
- Polz, J., et al. (2024). Temporal super-resolution, ground adjustment, and advection correction of radar rainfall using 3-D-convolutional neural networks. *IEEE TGRS.* https://doi.org/10.1109/TGRS.2024.3371577
- Ryu, S., Song, J., Lim, K., Lee, G. (2026). RRBF-KMA: high-resolution radar–gauge merged precipitation dataset for South Korea (2016–2024). **[preprint, ESSD discussions]** https://doi.org/10.5194/essd-2026-302

### Software
- Heistermann, M., Jacobi, S., Pfaff, T. (2013). Technical note: an open source library for processing weather radar data (wradlib). *HESS.* https://doi.org/10.5194/hess-17-863-2013 — https://github.com/wradlib/wradlib
- Helmus, J. J., Collis, S. M. (2016). The Python ARM Radar Toolkit (Py-ART). *J. Open Res. Softw.* https://doi.org/10.5334/jors.119 — https://github.com/ARM-DOE/pyart
- pysteps (Pulkkinen et al. 2019, above) — https://github.com/pySTEPS/pysteps
- pycomlink — https://github.com/pycomlink/pycomlink (no paper DOI used here)
- mergeplg — https://github.com/OpenSenseAction/mergeplg (no DOI)
- CSU_RadarTools — https://github.com/CSU-Radarmet/CSU_RadarTools (no DOI)
- BALTRAD — https://github.com/baltrad (Michelson et al. 2018, above)

### Non-DOI technical sources read for coefficients
- Ryzhkov, A. V., Giangrande, S., Schuur, T. J. Rainfall estimation with a polarimetric prototype of the operational WSR-88D radar. AMS conference preprint 4B.1. https://ams.confex.com/ams/pdfpapers/64216.pdf
- Dixon, M. J., Wilson, J. W., Weckwerth, T. M., Albo, D., Thompson, E. J. (2015). A dual-polarization QPE method based on the NCAR Particle ID algorithm. 37th AMS Conf. Radar Meteor., 9A.1. https://ams.confex.com/ams/37RADAR/webprogram/Manuscript/Paper275705/AMS_20150917.extended_abs.dixon.9A.1.pdf
- Zhang, J., et al. (2017). MRMS dual-polarization radar synthetic QPE. 38th AMS Conf. Radar Meteor., 22B.3. https://ams.confex.com/ams/38RADAR/webprogram/Manuscript/Paper320875/MRMS_DPQPE_Extended%20Abstract_v2.pdf
- Grams, H. M., Biggs, Z., Berkowitz, D. S., Murnan, R. L. (2019). Dual polarization QPE on the WSR-88D: current status and future plans. AMS Annual Meeting. https://training.weather.gov/wdtd/courses/rac/principles/qpe/story_content/external_files/Grams_et_al_2019.pdf
- Zhang, J., Tang, L., Cocks, S., Osborne, A. (2023). An update on the operational MRMS QPE. 40th AMS Conf. Radar Meteor. poster. https://ams.confex.com/ams/40RADAR/webprogram/Handout/Paper426078/40RadConf_2023%20MRMS%20poster%20-%20Zhang.pdf
- Py-ART `pyart/retrieve/qpe.py` (coefficient tables), CSU_RadarTools `csu_blended_rain.py` (defaults), pysteps `examples/advection_correction.py` (cites Anagnostou & Krajewski 1999).

### Items without a verifiable DOI
- Berkowitz, D. S., et al. (2013) — source of NEXRAD R(Z,ZDR) and R(KDP) coefficients (AMS conference paper; no DOI; not read directly).
- Nagata (2011) JMA Technical Review — no DOI.
