# radar-wow build plan (from the four survey parts, 2026-11-03)

Sources: `01_calibration_and_qc.md`, `02_kdp_attenuation_classification.md`,
`03_estimation_merging_mosaic.md`, `04_ml_verification_india_data.md`. All DOIs in those files
were checked against Crossref. Two flags raised by the survey agents were wrong and have been
corrected in the files: the moving-regression KDP citation (Wolfensberger 2021, App. A, is correct)
and the QVP DOI (our notes were already correct).

## Rules that came out of the survey
1. **Archived moments only.** I/Q- or spectrum-level methods (GMAP, CMD with CPA, SZ coding, spectral
   polarimetric filters) cannot run on the data we have. We record which processor filter was used
   instead.
2. **Physics before ML.** Trained QPE models do not transfer across radars, mainly because of
   calibration offsets (up to -9.4 dB on IMD S band, Saini 2026). Calibration, QC and attenuation
   correction come first, and ML trains on their outputs.
3. **Prefer estimators that do not need calibration.** R(A) and R(KDP) are immune to Z calibration,
   wet-radome loss and partial blockage. R(Z) is kept as a fallback for single-pol data, which is all
   that today's IMD export provides.
4. **Wrap, don't rebuild, where good open code exists.** Validate against wradlib (beam blockage,
   attenuation), Py-ART (noise correction, R(A), R(KDP)), CSU_RadarTools (blended rain), pysteps
   (optical flow, verification) and `scores` (metrics).

## Milestone 1: a first rain map from one radar, at S, C or X band
| # | class | repo | paper | why now |
|---|---|---|---|---|
| 1 | `NoiseCorrection` (SNR censoring, rhoHV/ZDR noise correction) | qc | Ryzhkov et al. 2005 | Every rhoHV/ZDR threshold is biased without it, worst at long range and X band |
| 2 | `DEMBeamBlockage` + `HybridScan` | estimation | Bech et al. 2003; Crisologo et al. 2018 quality; Fulton et al. 1998 hybrid scan | Mountains, Himalayan radars; lowest usable tilt |
| 3 | `ZRRelation` presets (Marshall-Palmer, NEXRAD convective, Chennai) | estimation | Marshall & Palmer 1948; Fulton 1998; Suresh et al. 2005 | Works on single-pol IMD data today |
| 4 | `RainRateA` R(A) | estimation | Ryzhkov et al. 2014, Table 1 (S/C/X, 0-30 C) | Calibration-immune; uses AH from stage 4 |
| 5 | `RainRateKDP`, `RainRateZZDR` | estimation | Ryzhkov et al. 2005 (S); Py-ART documented C/X defaults | Heavy rain and hail |
| 6 | `QVP` + `MeltingLayerQVP` | classification | Ryzhkov et al. 2016; Giangrande et al. 2008 | Rain relations hold only below the melting layer |
| 7 | `SyntheticRainRate` | estimation | Zhang et al. 2020 (MRMS) logic | R(A) in rain below the ML, R(KDP) for Z >= 50 dBZ, R(Z) elsewhere |
| 8 | `Accumulation` + first verification | estimation / verify | - | Hourly totals checked against an independent reference |

## Milestone 2: classification and robustness
- `Park2009HCA` with band membership functions (Dolan et al. 2013 for C; Dolan & Rutledge 2009 for X), then `HCADrivenRainRate` following the NEXRAD Build 18/19 table (Grams et al. 2019).
- `DualPolNonMetClassifier` (Kilambi et al. 2018; Gourley et al. 2007). Dust has no published scheme; test on the Delhi May-June 2018 cases (Singh et al. 2021).
- Backscatter-phase (delta) removal: Hubbert & Bringi 1995, then Mishler 2024 (an LP extension).
- Calibration: `GPMVolumeMatchCalibration` (Warren 2018 + Crisologo 2018), `ClutterRCA` (Silberstein 2008; Wolff 2015), `ZDROffsetNaturalTargets` (Ryzhkov 2005; Sanchez-Rivas & Rico-Ramirez 2022), `SunHitMonitor` (Huuskonen & Holleman 2007).
- VPR correction (Zhang & Qi 2010). ZDR constraint for beta (Bringi 2001). C-band hot-spot correction (Gu 2011).

## Milestone 3: network
Quality-weighted mosaic; advection-corrected accumulation (pysteps); Kalman mean-field bias;
conditional merging / kriging with external drift (Sinclair & Pegram 2005; Goudenhoofdt & Delobbe 2009);
REAL-style ensembles (Germann 2009).

## Milestone 4: ML
RainForest (Wolfensberger 2021) on corrected features; DL non-met QC trained on synthetic labels
(Bölz 2026); a CNN QPE as challenger; cGAN fill-in for blockage; physics-constrained QPE as the
research contribution. No peer-reviewed physics-constrained radar QPE exists yet. Foundation and
diffusion models are deferred.

## Verification design (from 04)
Build only the radar-gauge matching and stratification layer; use `scores` and pysteps for metrics.
Always hold out gauges, radars and seasons. Report the gain added by each stage (ablation).

## Data track for Delhi (from 04)
1. Request full-moment IRIS RAW volumes from IMD for Delhi-area radars; the netCDF export lacks
   PHIDP and RHOHV. Pursue an MoU.
2. Request hourly AWS/ARG gauge data; the public portal has been closed since May 2025.
3. Ask IITM Delhi for the Joss-Waldvogel disdrometer data behind Kumar et al. 2024, the only Delhi Z-R.
   Note: part 03 found no Delhi disdrometer Z-R while part 04 found Kumar 2024. Verify that paper before use.
4. Meanwhile, develop on the Jaipur sample, the open Colombian IRIS volumes on AWS (for the IRIS reader),
   NEXRAD and European C-band open data.

## References the surveys could not find
MCB-Net, the cGAN beam-blockage paper, dpQCNN and Pérez Hortal 2023 (all from the original talk) were
not found by name. They need the full citations before they can become classes.
