# Survey 04: Machine learning, verification, India/Delhi specifics, and open data and software

*radar-wow literature survey. Compiled 2026-11-03.*

**Scope.** This survey has four parts:
- **A.** Stage 9: machine learning for QPE and radar processing.
- **B.** Verification design.
- **C.** India and Delhi specifics.
- **D.** Open data and the software ecosystem, with a "use vs build" table.

**What it builds on.** It extends the background notes in `/Users/manmeet.singh/aircast/radar_wow/literature/03_machine_learning_deep_learning.md`, `04_india_delhi_radar.md` and `05_data_software_tutorials.md`, all compiled 2026-10-11. Those notes hold the longer per-paper tables, BibTeX, and the evidence trail for every IMD radar fact.

**Verification policy**
- **DOI verification.** Every DOI in this document was resolved through `https://api.crossref.org/works/<DOI>` on 2026-11-03. Each one returned a record whose first author, year and title match the citation given here.
- **Markers.**
  - Items without a DOI carry a URL and are marked *(URL only)*.
  - **[unverified]** means I could not confirm the item.
  - **[to confirm]** means a plausible fact that must be checked with IMD or the data provider before radar-wow relies on it.
- **Inherited facts.** Facts about IMD radars come from the 2026-10-11 notes. Those notes used WMO WRD records, IMD press releases, Parliament answers (some seen only through search excerpts) and one inspected IMD netCDF file. Their uncertainty markers are carried over here.

**Items that could not be found or are corrected**

| Item named in the brief | Finding |
|---|---|
| **MCB-Net** | No paper by this name was found in Crossref, arXiv or a two-pass web search. It is not listed as a citation; radar-wow should not implement it until someone supplies the reference. **[unverified]** |
| **"SPEED" (IPWG)** | No IPWG dataset by that name was found. The IPWG ML working-group benchmark is **SatRain** (Pfreundschuh et al. 2026, *Scientific Data*). "SPEED" may be an informal or older name. **[unverified]** |
| **"RadarBeamFilling"** | No repository by that name exists on GitHub (API search, 2026-11-03). Beam-blockage fraction is implemented in wradlib (`wradlib.qual.beam_block_frac`), in LROSE `RadxBeamBlock` and in pyrad. Radar-hole filling is available in Met Office IMPROVER (`FillRadarHoles`, BSD-3). **[unverified]** as a named package. |

---

## Part A. Stage 9: machine learning for radar QPE and radar processing

### A.0 State of the art in eight lines

1. **In-domain QPE.** Supervised learning from radar volumes or columns to gauges is now routine. Examples are tree ensembles (RainForest, MRMS-West) and CNN/3-D-CNN models (RQPENet, StarNet, the Yo et al. volume-to-point model). In-domain, these consistently beat fixed Z–R and fixed polarimetric relations, typically by 10–30 % RMSE (03 notes, §0).
2. **What the networks learn.** Explainability work shows that the networks mostly rediscover **Z_H and K_DP at the lowest tilts** (Li, Chen & Han 2024 GRL). This argues for physics-informed inputs over end-to-end raw volumes.
3. **Generalisation across radars, bands and climates is the main weakness.**
   - A Florida-trained dual-pol DL QPE degrades when applied in Oklahoma (Wang & Chen 2024 IGARSS).
   - Florida-to-UAE and S-to-C-band transfer was studied by the CSU group (URSI AT-RASC 2024 abstract, URL only).
   - Indian monsoon drop-size distributions (DSDs) are absent from every published training set.
4. **Operational wins come from emulating or replacing hand-tuned pipeline pieces.** Examples are NN QC (WDSS-II `w2qcnndp`; the Met Office NN-QC), DL dealiasing that emulates the ORPG, and cGAN beam-blockage infill. These are low-risk ways for ML to enter radar-wow.
5. **Physics-constrained losses are arriving, mostly in nowcasting.** FURECast (Pan et al. 2026 GRL) adds a Z_H–Z_DR–K_DP self-consistency loss and was tested on S- and C-band. **No peer-reviewed physics-constrained radar *QPE* model was found.** This is an open niche that radar-wow could fill.
6. **Radar foundation models do not yet exist** in a usable, pretrained, downstream-proven form (searched 2026-11). Existing "foundation" weather models (Prithvi-WxC, GraphCast, GenCast) produce ≥0.25° precipitation and are not radar QPE. "Radar DataTree" (arXiv:2510.24943) is a data framework, not a model.
7. **Benchmarks are nowcasting-centric** (SEVIR, HKO-7, MeteoNet, KNMI, TAASRAD19). **No public dual-pol volume + gauge QPE benchmark exists.** SatRain (satellite to gauge-corrected MRMS, with out-of-distribution splits) is the closest template.
8. **Labels are the bottleneck, not compute.** Gauges, disdrometers and QC masks matter most. For Delhi this is acute: IMD AWS/ARG data have needed a formal request since May 2025 (Part C).

### A.1 ML/DL QPE from radar (the brief's core list first)

| Item | Source | One-line description | Relevance to radar-wow |
|---|---|---|---|
| **RainForest** (Wolfensberger, Gabella, Boscacci, Germann, Berne 2021) | AMT 14:3169, doi:10.5194/amt-14-3169-2021 | Random-forest regression from polarimetric radar features (Z_H, Z_DR, K_DP, height, etc.) to gauge rain. Quasi-operational at MeteoSwiss. Code: `rainforest-mch` (PyPI), https://github.com/MeteoSwiss/rainforest | **First ML class to implement.** Tabular, cheap, interpretable and robust with few gauges. The reference implementation exists, so wrap or port it rather than re-derive it. |
| **Chen et al. 2019** hybrid DNN | GRL, doi:10.1029/2019GL084771 | Two cascaded DNNs: ground radar to gauge, then TRMM-PR to ground-radar QPE. The ground radar bridges the scale gap between gauge and space radar. | Template for a **GPM-DPR-to-ground** bridge in radar-sparse India, and for using the ground radar as the "teacher". |
| **Hilburn, Ebert-Uphoff & Miller 2021** (GREMLIN) | JAMC 60:3–21, doi:10.1175/JAMC-D-20-0084.1 | U-Net that turns GOES-16 ABI and GLM data into an MRMS-like composite Z, with explainable-AI (XAI) analysis. | Model for a **satellite "virtual radar" fallback**: INSAT-3D/3DR/3DS or Himawari to Delhi radar composite, for radar outages and gaps. |
| **Li, Chen & Han 2023** (RQPENet) | IEEE TGRS 61, doi:10.1109/TGRS.2023.3280799 | Family of dense, VGG and ResNet CNNs from KMLB (Florida) Z_H/Z_DR/K_DP volumes to gauge rain. | Reference **CNN QPE class**. Needs K_DP, which the IMD sample netCDF lacks (Part C). |
| **Li et al. 2024** (StarNet) | IEEE TGRS, doi:10.1109/TGRS.2024.3426532 | 3-D CNN with a physical height prior and a reweighted loss for heavy rain. | Shows how to inject physics (height prior) and handle the heavy-rain tail. |
| **Li, Chen & Han 2024** (DL QPE explainability) | GRL 51, doi:10.1029/2023GL107898 | Permutation importance shows lowest-tilt Z_H and K_DP dominate. | Supports feeding **physically derived features** (e.g. R(K_DP), R(A)) to ML instead of raw volumes. |
| **Yo et al. 2021** (volume-to-point) | ESS 8, doi:10.1029/2020EA001340 | CNN from a QPESUMS 3-D Z time series around each gauge to hourly gauge rain (Taiwan, 45 stations). | Directly matches a radar-wow **"column/patch around gauge" training design**. Works with Z only, so it fits IMD single-pol S-band (Palam, Patiala). |
| **Osborne et al. 2023** (ML MRMS West) | AIES 2, doi:10.1175/AIES-D-22-0053.1 | Tree ensembles on MRMS predictors (radar, environment, terrain) to gauge-like QPE in complex terrain. | Template for an **ML corrector after the composite (post-merge) stage**. |
| Osborne et al. 2026 (follow-on) | AIES 5(2), doi:10.1175/AIES-D-24-0013.1 | Optimisation of the 2023 approach. | Feature-selection and operational lessons. |
| Ho et al. 2023 | JHM 24:2057, doi:10.1175/JHM-D-22-0166.1 | DNN from Z_H and Z_DR (+K_DP) to DSD parameters and R, trained on 2DVD disdrometer truth. | **Disdrometer-trained** ML estimator. The Delhi IITM Joss–Waldvogel disdrometer (Part C) could supply training data. |
| Zhang Y. et al. 2021 | Remote Sens. 13:3157, doi:10.3390/rs13163157 | Deep CNN for polarimetric QPE in landfalling typhoons (South China, S-band). | Tropical heavy-rain analogue to monsoon conditions. |
| Peng et al. 2022 (CNGAT) | IEEE TGRS 60, doi:10.1109/TGRS.2021.3120218 | CNN + graph attention over the gauge network. | Graph-based radar–gauge model, suited to irregular Indian AWS/ARG networks. |
| Sarafian et al. 2025 (RadarGaugeNet) | IEEE TGRS 63, doi:10.1109/TGRS.2025.3640078 | Real-time DL radar–gauge fusion (Israel). | ML replacement for the **gauge-merging stage**. Compare it against conditional merging and kriging with external drift (KED). |
| Wang & Chen 2024 (adaptive learning, generalisation) | IGARSS 2024, 5567–5570, doi:10.1109/IGARSS53475.2024.10642359 | Quantifies how a Florida-trained DL QPE generalises to other regions, and proposes adaptive learning. | **Key domain-shift evidence.** Radar-wow must retrain or adapt per radar and climate. |
| Jung et al. 2026 (abstract) | EMS2026-254, doi:10.5194/ems2026-254 | Spatially coherent hybrid ML radar QPE (South Korea). | Conference abstract; it signals the hybrid physics + ML trend. |
| van den Heuvel et al. 2020 | AMT 13:2481, doi:10.5194/amt-13-2481-2020 | ANN extrapolation of the vertical profile of reflectivity (VPR) using hydrometeor-class fractions (Swiss Alps). | ML-VPR option for long-range Patiala/Jaipur coverage over Delhi. |
| Sharma & Kannan 2021 | J. Earth Syst. Sci. 130, doi:10.1007/s12040-020-01540-8 | Delhi IMD radar vs TRMM-PR alignment plus ANN. Reports a positive Delhi Z bias against TRMM-PR (abstract via search excerpt). | **Only Delhi-specific ML/radar paper found.** |

### A.2 ML for QC, classification and gap filling

| Item | Source | One-line description | Relevance |
|---|---|---|---|
| Lakshmanan et al. 2007 (QCNN) | JAMC 46, doi:10.1175/JAM2460.1 | Gate-wise neural network on texture features, plus spatial post-processing. WDSS-II tool `w2qcnn`. | Baseline ML QC that works for **single-pol** data (Palam, Patiala). |
| Lakshmanan et al. 2014 (dual-pol QCNN) | JTECH 31, doi:10.1175/JTECH-D-13-00073.1 | Dual-pol texture features into a neural network. Basis of `w2qcnndp`. | Reference "dpQCNN" (that name does not appear in the literature). |
| Husnoo et al. 2021 | JTECH 38, doi:10.1175/JTECH-D-20-0120.1 | Operational Met Office neural-network QC for QPE. | Operational template, C-band. |
| Lepetit et al. 2022 | IEEE TGRS 60, doi:10.1109/TGRS.2021.3052582 | Weakly supervised U-Net that restores precipitation echoes, supervised by gauges only. | Fits India, where **expert QC masks do not exist**. |
| Bölz et al. 2026 (preprint, AMT in review) | doi:10.5194/egusphere-2026-992 | U-Net trained on **synthetic** mixtures of precipitation and clutter (DWD). Beats the operational DWD classifier. | Synthetic-label QC is the most transferable approach for IMD radars. |
| Yang et al. 2026 (preprint, AMT in review) | doi:10.5194/egusphere-2026-590 | Pointwise MLP vs Swin U-Net for non-precipitation echoes (Guangzhou S-band dual-pol). | Shows how much polarimetric vs spatial vs temporal inputs each contribute. |
| Lin et al. 2019 (MistNet) | Methods Ecol. Evol. 10, doi:10.1111/2041-210X.13280 | FCN that separates biological from precipitation echoes in NEXRAD data. Shipped via `bioRad`/`vol2birdR`. | Delhi has insect and bird echoes in the hot season (**[to confirm]**: no Indian study). |
| Veillette et al. 2023 | AIES 2, doi:10.1175/AIES-D-22-0084.1 | U-Net that emulates the WSR-88D ORPG velocity dealiasing. | Not QPE-critical. Use UNRAVEL or Py-ART instead (Part D). |
| **Tan & Chen 2023** (cGAN beam blockage) | IEEE TGRS 61, doi:10.1109/TGRS.2023.3286181 | Conditional GAN that infills blocked PPI sectors. | **ML gap-filling class.** Relevant for the Himalayan X-band radars and any urban blockage at Delhi. |
| Tan, Chen & Lee 2025 | AIES 4, doi:10.1175/AIES-D-24-0111.1 | Measures the QPE impact of DL blockage correction (Northern California). | Gives the verification protocol for the infill class. |
| Geiss & Hardin 2021 | AMT 14:7729, doi:10.5194/amt-14-7729-2021 | CNN/GAN inpainting of blind zones and blocked sectors. Code on Zenodo (doi:10.5281/zenodo.5643624; DataCite, not checked in Crossref). | Alternative infill model with open code. |

### A.3 Physics-guided ML and foundation models

| Item | Source | Description | Relevance |
|---|---|---|---|
| Pan et al. 2026 (FURECast) | GRL 53, doi:10.1029/2025GL120431 | 3-D Z_H/Z_DR/K_DP nowcasting with a **polarimetric self-consistency physical loss**. Tested on S-band (GD-SPOL) and C-band (NJU-CPOL). | Its loss term can be borrowed for a physics-constrained radar-wow QPE class across bands. |
| Prithvi-WxC (Schmude et al. 2024) | arXiv:2409.13598 (URL only) | 2.3-billion-parameter weather foundation model trained on MERRA-2. | Not radar QPE. At most a source of environmental covariates. |
| Radar DataTree (Ladino-Rincon & Nesbitt 2025) | arXiv:2510.24943 (URL only) | FAIR, cloud-native radar archive (xarray DataTree + Zarr + Icechunk). | **Data layout to adopt** for radar-wow training stores, not a model. |
| SpaT-SparK (Li H. et al. 2024) | arXiv:2412.15917 (URL only) | Masked-image-modelling pretraining for nowcasting (KNMI). | Closest thing to radar self-supervised pretraining. Research option only. |

### A.4 Benchmark and training datasets

| Dataset | Source | Content | Licence / access | Relevance |
|---|---|---|---|---|
| SEVIR | Veillette et al. 2020, NeurIPS (URL: proceedings.neurips.cc …fa78a161…) | More than 10k storm events: GOES-16 imagery, GLM lightning, NEXRAD VIL | AWS Open Data (`s3://sevir`), anonymous | Satellite-to-radar pretraining; nowcasting. No dual-pol, no gauges. |
| RainBench | Schroeder de Witt et al. 2021, AAAI 35, doi:10.1609/aaai.v35i17.17749 | SimSat + ERA5 to IMERG | Open (PyRain) | Global satellite context only. |
| **SatRain** (IPWG ML WG) | Pfreundschuh et al. 2026, *Sci. Data*, doi:10.1038/s41597-026-06565-0; `pip install satrain` | Multi-sensor satellite to gauge-corrected MRMS, with **out-of-distribution test splits in Asia and Europe** | Open | **Template for a radar-wow benchmark**, and an evaluation set for the satellite fallback. |
| MeteoNet | https://meteonet.umr-cnrm.fr/ (URL only) | Météo-France radar Z, rain, quality code, stations, NWP (2016–2018) | Etalab Open Licence 2.0 | Radar + gauge pairs with a quality code. Useful to pretrain or test QC and QPE. |
| HKO-7 | Shi et al. 2017, arXiv:1706.03458 (URL only) | HKO radar CAPPI 2009–2015 | On request | Nowcasting only. |
| KNMI 5-min radar archive (SmaAt-UNet) | Trebing et al. 2021, Pattern Recog. Lett., doi:10.1016/j.patrec.2021.01.036; KNMI Data Platform | NL C-band rain maps; KNMI also publishes full polarimetric volumes | CC BY 4.0 per KNMI (dataset names **[to confirm]**) | Nowcasting; also C-band dual-pol volumes (Part D). |
| TAASRAD19 | Franch et al. 2020, *Sci. Data* 7, doi:10.1038/s41597-020-0574-8 | Trentino C-band MAX(Z), 2010–2019 | Open (GitHub/Zenodo) | Complex terrain; nowcasting. |
| EURADCLIM | Overeem et al. 2023, ESSD 15:1441, doi:10.5194/essd-15-1441-2023 | Gauge-adjusted OPERA climatology, 2 km, 1 h/24 h | Open (KNMI DOIs) | Large-scale QPE labels, European climate. |
| MRMS (as labels) | Zhang J. et al. 2016, BAMS, doi:10.1175/BAMS-D-14-00174.1 | CONUS 1 km / 2 min QPE | AWS `noaa-mrms-pds`, anonymous | Pretraining labels paired with NEXRAD Level-II volumes. |
| **Gap** | — | No public **dual-pol volume + gauge** QPE benchmark exists | — | radar-wow could build one from NEXRAD + MRMS gauges + IMD (when shareable). |

### A.5 Lessons on generalisation across radars and bands (domain shift)

1. **Inputs.** Train on **band-invariant, physically normalised inputs**: attenuation-corrected Z, Z_DR, K_DP in deg/km, and R(K_DP) and R(A) estimates, instead of raw moments.
   - K_DP scales with frequency (roughly 1/λ at S vs C vs X), so normalise it to S-band-equivalent or include band as a feature.
   - Raw Z at C/X band carries uncorrected attenuation, which shifts the input distribution between bands.
2. **Calibration.** Indian radars carry **calibration offsets of several dB**: −9.4 to +0.3 dB mean bias at four IMD east-coast S-band radars against GPM (Saini et al. 2026), and −8.3 dB at an IITM X-band radar (Jha et al. 2024). An ML model trained on a mis-calibrated radar learns that offset. **Calibration (GPM-matching) must run before ML training and inference.**
3. **Range and geometry.** Use beam height, range and beam-blockage fraction as features, so the model can tell geometry from microphysics (StarNet's height prior is the same idea).
4. **Splits.** Evaluate with **leave-radar-out and leave-season-out splits** (as SatRain does with OOD regions), not random gate splits. Random splits leak spatial and temporal autocorrelation.
5. **Fine-tuning.** Fine-tune per radar from a pretrained model, e.g. NEXRAD S-band → IMD Palam S-band, and Swiss/DWD C-band → IMD Lodhi Road C-band. Validate the gain over local Z–R before deploying (Wang & Chen 2024).
6. **Missing moments.** Design for them. Several IMD radars are single-pol, and the sample IMD netCDF has **no ρ_HV, Φ_DP or K_DP**. Models must therefore accept a Z-only mode (Yo et al. 2021 style) and a full dual-pol mode.

---

## Part B. Verification

### B.1 Radar–gauge matching practice (recommended defaults, with sources)

| Practice | Recommendation | Source |
|---|---|---|
| Spatial matching | Pixel containing the gauge, plus a 3×3 (1 km grid) neighbourhood statistic (mean or best-match) as a sensitivity test. Report both. | Ebert 2008, Met. Apps., doi:10.1002/met.25 (neighbourhood/"fuzzy" framework) |
| Height and time | Use the lowest usable, unblocked beam (hybrid scan), with beam height reported per gauge. Accumulate radar to the gauge interval: hourly first, then daily on IMD's 03 UTC (08:30 IST) day. Daily accumulations must match the IMD gridded day definition. | IMD gridded day: Pai et al. 2014, doi:10.54302/mausam.v65i1.851 |
| Gauge QC | Remove stuck or zero tipping buckets and duplicates. Screen against neighbours and IMERG for gross errors. Flag gauges under radar beam blockage. | Ciach 2003, JTECH, doi:10.1175/1520-0426(2003)20<752:LREITB>2.0.CO;2 (tipping-bucket random errors) |
| Representativeness (point vs area) | Do not treat gauge−radar differences as pure radar error. Use error-variance separation: var(R−G) = var(radar error) + var(area–point). | Ciach & Krajewski 1999, AWR, doi:10.1016/S0309-1708(98)00043-8 ; Villarini et al. 2008, JGR, doi:10.1029/2007JD009214 |
| Independence | Hold out gauges used for adjustment (leave-one-out or k-fold by station). Never verify against gauges used in merging or ML training. | Standard practice; see Wolfensberger et al. 2021 (station-based cross-validation) |
| Error-source attribution | Stratify errors by source: calibration, attenuation, VPR/bright band, blockage, Z–R variability, sampling. | Villarini & Krajewski 2010, Surv. Geophys., doi:10.1007/s10712-009-9079-x |

### B.2 Scores

| Category | Scores to report | Notes / source |
|---|---|---|
| Continuous (pairs ≥ threshold, e.g. ≥0.1 mm/h) | Multiplicative bias (ΣR/ΣG), mean error, MAE, RMSE, normalised RMSE, Pearson r, **Kling–Gupta efficiency (KGE)** and its decomposition | KGE: Gupta et al. 2009, J. Hydrol., doi:10.1016/j.jhydrol.2009.08.003 |
| Categorical (thresholds 0.1, 1, 5, 10, 20, 50 mm/h; daily 2.5, 15.6, 64.5, 115.6 mm = IMD rain categories **[to confirm exact IMD thresholds]**) | POD, FAR, CSI, frequency bias, ETS/GSS, HSS, and the **symmetric extremal dependence index (SEDI)** for rare heavy rain | Hogan et al. 2010, WAF, doi:10.1175/2009WAF2222350.1 (ETS is not equitable; prefer HSS/SEDI for rare events) |
| Neighbourhood / spatial (gridded references: IMERG, IMD 0.25°, a composite of another radar) | **Fractions skill score (FSS)** over scales of 1–50 km at several thresholds; optionally object-based (SAL/MODE) | Roberts & Lean 2008, MWR, doi:10.1175/2007MWR2123.1 ; Gilleland et al. 2009, WAF, doi:10.1175/2009WAF2222269.1 |
| Probabilistic (ensemble or ML-quantile QPE) | CRPS, reliability diagram, rank histogram, Brier score per threshold | Available in pysteps and `scores` |
| Extremes | Quantile–quantile plots of top 1 % hourly rates; bias in annual or event maxima | — |

### B.3 Stratification (mandatory in every radar-wow verification report)

- **By range** from each radar: 0–25, 25–50, 50–100, 100–150, >150 km. Also by beam height relative to the freezing level.
- **By band and radar.** For Delhi: S (Palam), C (Lodhi Road), X (Ayanagar). Neighbours: Patiala S and Jaipur C.
- **By rain type.** Convective vs stratiform (from a classifier), hail-flagged gates, bright-band-affected gates.
- **By season, using IMD seasons.**
  - Winter / western disturbances: Jan–Feb.
  - Pre-monsoon: Mar–May (dust storms, hail).
  - Monsoon: Jun–Sep.
  - Post-monsoon: Oct–Dec.
- **By intensity class and by beam-blockage fraction.**
- **By processing stage.** Report the incremental skill after each physical stage (raw Z–R → QC → calibration → attenuation → VPR → polarimetric → composite → gauge merge → ML). This is the core ablation for papers and for deciding where ML pays off.

### B.4 Verification tools (use, do not rebuild)

| Tool | Source | Coverage | Licence | radar-wow use |
|---|---|---|---|---|
| **pysteps.verification** | Pulkkinen et al. 2019, GMD, doi:10.5194/gmd-12-4185-2019; https://github.com/pySTEPS/pysteps | Categorical (`det_cat_fct`), continuous (`det_cont_fct`), FSS and intensity-scale (`spatialscores`), CRPS, reliability, rank histogram | BSD-3 | Gridded and FSS verification |
| **scores** (BoM / NCI) | Leeuwenburg et al. 2024, JOSS 9:6889, doi:10.21105/joss.06889; https://github.com/nci/scores | xarray-native continuous, categorical, probabilistic and FSS scores; reviewed implementations, with a tutorial per score | Apache-2.0 (GitHub API) | **Default score engine** (xarray-native, so it matches xradar/DataTree) |
| **MET / METplus** (NCAR DTC) | Brown et al. 2021, BAMS, doi:10.1175/BAMS-D-19-0093.1; https://github.com/dtcenter/METplus | Point-stat, grid-stat, MODE (object-based), series analysis | Apache-2.0 (GitHub API) | Optional heavy tool for MODE/object verification and operational-centre compatibility (NCMRWF/IMD use MET **[to confirm]**) |
| wradlib.verify | Heistermann et al. 2013, HESS, doi:10.5194/hess-17-863-2013 | Radar–gauge pair extraction (`PolarNeighbours`), error metrics | MIT | Extract radar values at gauges in polar geometry |
| GPM-API + wradlib SR/GR matching | https://github.com/ghiggi/gpm_api ; Warren et al. 2018, JTECH, doi:10.1175/JTECH-D-17-0128.1 ; Crisologo et al. 2018, AMT, doi:10.5194/amt-11-5223-2018 | Space-radar/ground-radar volume matching | Open | Calibration verification (not rainfall) |

### B.5 Reference datasets for verification (India-applicable)

IMD hourly AWS/ARG gauges (on request), IMD 0.25° daily gridded rainfall (Pai et al. 2014), GPM IMERG V07 (Early/Late/Final), GSMaP v8 (Gauge_NRT), the IMD–NCMRWF merged product, and GPM DPR for Z calibration. Details and URLs are in background notes 04 §5. For prior India-specific IMERG behaviour, see Prakash & Srinivasan 2021, Remote Sens. 13:3676, doi:10.3390/rs13183676.

---

## Part C. India and Delhi specifics

### C.1 IMD Doppler weather radar (DWR) network around Delhi

Sources for every row are in background notes 04 §1.2: WMO Weather Radar Database records, IMD press releases, and Parliament answers marked †.

| Radar | Band / pol | Vendor | Coordinates | Status / notes |
|---|---|---|---|---|
| Delhi HQ, Mausam Bhawan, Lodhi Road (WMO 42182) | C (5625 MHz), dual-pol | Vaisala | 28.5897 N, 77.2219 E (WMO WRD) | Operational since Jan 2012. Most-studied Delhi radar. "Delhi" products on the IMD web page usually come from this radar. |
| Delhi Palam (WMO 42181) | S (2825 MHz), single-pol | Beijing Metstar **[to confirm]** | 28.5594 N, 77.0731 E | Commissioned 2010 †. Rarely used in papers. Backbone candidate for long paths (no attenuation). |
| Delhi Ayanagar | X, dual-pol | Astra Microwave (indigenous, solid-state) | **[to confirm]**: no official coordinates | Inaugurated Jan 2022 (IMD press release). |
| Patiala (WMO 42101) | S, single-pol | **[to confirm]** | 30.3575 N, 76.4497 E | About 211 km from Delhi. |
| Jaipur | C (λ 5.33 cm), dual-pol | Vaisala | 26.8206 N, 75.8186 E | About 238 km. Public sample volume exists (Part D). |
| Lucknow | S, single-pol | **[to confirm]** | 26.7686 N, 80.8853 E | About 415 km. |
| Mukteshwar, Kufri, Surkanda Devi, Lansdowne, Jot, Murari Devi (Himalayan) | X (dual-pol for Mukteshwar and Kufri; others **[to confirm]**) | Astra (Mukteshwar, Kufri); others **[to confirm]** | **[to confirm]** | Ridge-top sites with heavy blockage. |
| Planned NCR / Uttar Pradesh X-band (Aligarh, etc.) | X | — | — | Announced 2024–2026; operational status **[to confirm]**. |

**Network size and data format**
- **Network size:** 22 S, 5 C and 12 X-band radars (39 total) in Feb 2024 (Bhat et al. 2025; RS Q 668 †). About 51 radars by Sep 2026 (secondary sources).
- **Data format (verified on one file):**
  - The IMD-distributed format is "FSL netCDF" re-encoded from **Vaisala IRIS/Sigmet RAW**, one sweep per file. Read it with PyScanCf or radarx.
  - The Jaipur sample contains only **T, Z, V, W, ZDR, HCLASS** (no RHOHV, PHIDP or KDP).
  - Ask IMD for IRIS RAW with all moments. Py-ART, wradlib and xradar read IRIS RAW natively.

### C.2 Data access (as of Oct–Nov 2026)

| Channel | What | How | Source |
|---|---|---|---|
| IMD Radar Data Supply Portal | Raw and processed DWR volumes on request (charged; research institutes get a 50 % concession; students free) | Register on the IMD Data Service Portal (https://dsp.imdpune.gov.in), then request at https://radarapi.imd.gov.in/dsp/frontend/login. Radar contact listed on the portal. Per-volume price **[to confirm]**. | 04 notes §2 |
| IMD web radar pages | Latest GIF products only (MAX(Z), PPI, SRI, PAC); no archive | https://mausam.imd.gov.in/imd_latest/contents/index_radar.php | 04 notes §2.1 |
| IMD AWS/ARG gauges | Hourly station rain | **Public portal locked since about May 2025.** Request through the Data Service Portal or an MoU. IMD announced 50 new AWS for Delhi in Jan 2026 (newsonair.gov.in, 15 Jan 2026). | Down To Earth, 10 Oct 2025 (https://www.downtoearth.org.in/climate-change/imd-locking-up-its-awsarg-data-portal-hampers-public-weather-alerts-experts) |
| IMD gridded rainfall | 0.25° daily, 1901– | `imdlib` (Python) | Pai et al. 2014 |
| MOSDAC (ISRO) | ISRO DWR products (e.g. TERLS), INSAT | Registration and order | https://www.mosdac.gov.in |
| Open sample | One Jaipur C-band volume (22 Aug 2022) | `open-radar-data` (`IMD/JPR220822135253-IMD-B.nc`) | https://github.com/openradar/open-radar-data |
| State / other gauges | Delhi Flood Control, DPCC/CPCB, IITM Delhi sites | **[to confirm]**: availability and licence | — |

### C.3 Indian radar QPE, calibration and DSD literature (all DOIs verified)

| Item | Source | One-line description | Relevance |
|---|---|---|---|
| **Bhat, Vivekanandan & Pradhan 2025** | MAUSAM 76(1):55–64, doi:10.54302/mausam.v76i1.6497 | History and current state of Indian radar meteorology: vendors, phases, the 22 S / 5 C / 12 X network. Calls for calibration, standardisation and a trained workforce. | Context and justification for radar-wow's calibration-first design. |
| **Sharma, Rastogi, Verma, Kumar & Choudhary 2025** | Phys. Chem. Earth 141:104182, doi:10.1016/j.pce.2025.104182 | Compares Z–R relations for Delhi DWR rainfall (2019 data). Per the 04 notes, Marshall–Palmer best in monsoon and post-monsoon, Rosenfeld tropical better in winter, pre-monsoon and heavier rain; overall r ≈ 0.62, RMSE 13.44. Which Delhi radar was used: **[to confirm]**. | **Delhi baseline Z–R class.** Seasonal Z–R switching. |
| **Saini, Das, Jha, Kolte, Murali Krishna & Deshpande 2026** | Radio Science 61, e2025RS008484, doi:10.1029/2025RS008484 | GPM Ku-band volume matching against four IMD east-coast S-band radars. Mean bias −9.4 to +0.3 dB, varying up to ±20 dB with precipitation type and bright band (abstract). | **Calibration method to apply to Palam, Patiala and Lodhi Road** before QPE or ML. |
| Kumar, Chakravarty, Deshpande, Kumar & Srivastava 2024 | JASTP 263:106333, doi:10.1016/j.jastp.2024.106333 | Joss–Waldvogel disdrometer at IITM New Delhi (2021–2023). Seasonal and convective/stratiform DSD and Z–R relations for Delhi; pre-monsoon has the largest Z–R coefficient (search-index abstract). | **The only Delhi disdrometer Z–R found.** Use it for the seasonal Z–R class and to simulate polarimetric relations (T-matrix). |
| Abhijeet, Deshpande & Pandithurai 2026 | Atmos. Res. 327:108381, doi:10.1016/j.atmosres.2025.108381 | Polarimetric study of pre-monsoon convection and hail microphysics over central India. | Pre-monsoon hail and convection signatures (title only read). |
| Sharma & Kannan 2021 | JESS 130, doi:10.1007/s12040-020-01540-8 | Delhi radar vs TRMM-PR, with ANN. | Delhi calibration evidence. |
| Singh D.K. et al. 2021 | MAUSAM 72(4), doi:10.54302/mausam.v72i4.3543 | Three severe May–June 2018 Delhi events (dual-pol DWR + GNSS). | **Dust-storm / thunderstorm case library.** |
| Amar Jyothi et al. 2022 | MAP 134, doi:10.1007/s00703-021-00851-9 | Delhi hail climatology (radar + model). | Hail masking before QPE. |
| Dutta et al. 2016 | J. Appl. Remote Sens. 10, doi:10.1117/1.JRS.10.026022 | Winter hail signatures in Delhi C-band polarimetric data. | Winter / western-disturbance hail. |
| Sen Roy et al. 2019 | MAP 131, doi:10.1007/s00703-019-0659-0 | Diurnal convection over NW India from DWR. | Climatology priors. |
| Bibraj et al. 2020/21 (Crossref lists 2021) | MAUSAM 71(1), doi:10.54302/mausam.v71i1.2 | Anomalous-propagation clutter vs inversion and refractivity gradients. | Winter and early-morning AP over the Indo-Gangetic Plain. |
| Amar Jyothi et al. 2016 | Proc. SPIE 9876, doi:10.1117/12.2223802 | NCMRWF gridded radar rainfall and quality index. | Existing national radar-QPE benchmark. |
| Das et al. 2020 | ESS 7, doi:10.1029/2019EA000861 | X-band attenuation correction and GPM/TRMM comparison (Western Ghats). | Template for Ayanagar X-band. |
| Jha et al. 2024 | JESS 133, doi:10.1007/s12040-024-02271-w | X-band bias correction (−8.3 dB). | Calibration evidence. |
| Das et al. 2017; Raut et al. 2021 | Atmos. Res. doi:10.1016/j.atmosres.2016.11.003 ; GRL doi:10.1029/2021GL093581 | Monsoon DSD regimes and Z–R by cloud type. | Monsoon DSD priors for polarimetric relations. |
| Karmakar et al. 2026 (preprint) | Research Square, doi:10.21203/rs.3.rs-9883892/v1 | Cyclone Remal DSD and Z–R. Cites IMD's operational default as Marshall–Palmer (per 04 notes). | Not peer-reviewed. IMD default Z–R **[to confirm]**. |
| Pai et al. 2014 | MAUSAM 65(1), doi:10.54302/mausam.v65i1.851 | IMD 0.25° gridded daily rainfall. | Daily verification reference. |
| Prakash & Srinivasan 2021 | Remote Sens. 13:3676, doi:10.3390/rs13183676 | IMERG evaluation over India. | Satellite reference behaviour. |

### C.4 Delhi-specific hazards and their effect on radar-wow

| Hazard | Effect on QPE | Mitigation stage |
|---|---|---|
| Pre-monsoon dust storms and gust fronts (Apr–Jun) | Non-meteorological echoes; low ρ_HV and noisy Z_DR from dust; strong winds | QC: needs ρ_HV (request full moments). ML-QC trained on synthetic labels (Bölz 2026) and the Singh 2021 cases. No Delhi dust-echo classifier exists (**gap**). |
| Pre-monsoon thunderstorms and hail | Z overestimates rain; C-band attenuation and differential attenuation | Hail cap (≈53–55 dBZ) or HCLASS mask; R(K_DP) / R(A); Palam S-band as backbone |
| Winter and early-morning inversions; smog and haze (Nov–Feb) | AP clutter (Bibraj 2020). Haze and smog particles are far too small to give significant echo; the impact is via inversions and AP, not aerosol reflectivity **[reasoned, not sourced]**. | Clutter maps, texture QC, NN QC, ducting flags from radiosonde |
| Urban clutter (dense high-rises, Palam airport and Lodhi Road surroundings) | Static clutter, partial blockage, possible wind-farm-like moving clutter (**[to confirm]**) | Clear-air clutter maps; DEM + building-height blockage; cGAN infill for blocked sectors |
| Monsoon heavy rain (e.g. July 2023) | Severe C/X path attenuation; wet radome; bright band in stratiform | Φ_DP-based attenuation correction; S-band priority; VPR correction; gauge merge |
| C-band RLAN interference (5.6 GHz) | Radial spikes | Interference filter (**[to confirm]**: no Indian study) |
| Bird and insect echoes (summer and monsoon nights) | False light rain | ML bio-classifier (MistNet / bioRad) or ρ_HV threshold |

### C.5 Gaps (India and Delhi)

1. No public archive of IMD raw volumes. All published studies obtained data on request or through IMD, IITM or NCMRWF co-authors.
2. Delivered netCDF lacks Φ_DP, K_DP and ρ_HV (one-file evidence).
3. No peer-reviewed Delhi polarimetric QPE (R(K_DP), R(Z, Z_DR)) and no Delhi radar ML QPE found.
4. No Delhi dust-echo or bio-echo classifier.
5. The only Delhi disdrometer Z–R is Kumar et al. 2024 (a single JWD).
6. Calibration of Palam, Ayanagar and Lodhi Road against GPM has not been published since Sharma & Kannan 2021 (TRMM, 2013 data).
7. Hourly gauge access has been restricted since May 2025.

---

## Part D. Open data and software ecosystem

### D.1 Free radar datasets with dual-pol moments

| Dataset | Band | Content | Access | Licence | Source |
|---|---|---|---|---|---|
| NEXRAD Level II (WSR-88D) | S, dual-pol since 2013 | Full volumes 1991– | AWS `s3://unidata-nexrad-level2` (anonymous). The old `noaa-nexrad-level2` bucket was retired 1 Sep 2025 (per 05 notes). Also Google Cloud and NCEI. | US public data, no restrictions | Ansari et al. 2018, BAMS, doi:10.1175/BAMS-D-16-0021.1 |
| NEXRAD ARCO (KLOT) | S | Zarr v3 / Icechunk DataTree, 2015– | `s3://nexrad-arco` anonymous | Open (AWS registry) | https://registry.opendata.aws/nexrad-arco/ |
| MRMS | — (products) | QPE, RQI, 3-D mosaic (archive from Oct 2020) | `s3://noaa-mrms-pds` | US public | Zhang et al. 2016 |
| ARM (CSAPR2, XSAPR, KAZR) | C, X, Ka | Campaign volumes (CACTI, TRACER, BNF) | Free ARM account; ADC discovery | ARM data policy (citation required) | https://adc.arm.gov/discovery/ |
| EUMETNET OPERA Open Radar Data | C (mostly) | Single-site ODIM volumes + composites | REST API via MeteoGate (https://api.meteogate.eu/eu-eumetnet-weather-radar) + MQTT | Docs are CC BY 4.0; data licence **[to confirm]** | Saltikoff et al. 2019, Atmosphere, doi:10.3390/atmos10060320 |
| FMI | C, dual-pol | ODIM HDF5 volumes, GeoTIFF composites | AWS `s3://fmi-opendata-radar-volume-hdf5` | CC BY 4.0 | https://registry.opendata.aws/fmi-radar/ |
| KNMI | C, dual-pol | Full polarimetric volumes (Herwijnen, Den Helder) | KNMI Open Data API (key) | CC BY 4.0 (dataset names **[to confirm]**) | https://developer.dataplatform.knmi.nl/open-data-api |
| MeteoSwiss OGD | C, dual-pol | Composites (RZC, CombiPrecip) with a 14-day rolling window; polar volumes via OPERA | STAC API | **CC BY 4.0** (verified on the terms-of-use page) | https://opendatadocs.meteoswiss.ch |
| DWD open data | C, dual-pol | Site sweeps (z, v, zdr, rhohv, phidp; rolling window), RADOLAN, RADKLIM (2001–) | HTTPS https://opendata.dwd.de ; `wetterdienst` | DWD open-data terms (CC BY 4.0 **[to confirm]**) | 05 notes §1b |
| BoM Operational Radar Level 1 (NCI `rq0`) | S/C (dual-pol at some sites) | ODIM HDF5 volumes, multi-decade | NCI THREDDS / OPeNDAP, anonymous. No AWS bucket found **[to confirm]**. | CC BY 4.0 (licence PDF in the archive) | doi:10.25914/5cb686a8d9450 (DataCite, not checked in Crossref) |
| Colombia IDEAM | C/X **[to confirm]** | IRIS/Sigmet volumes 2018– | AWS `ideam-radares`, anonymous | Open (AWS registry) | https://registry.opendata.aws/ideam-radares/ — **IRIS format, like IMD, so a good proxy for testing readers** |
| JMA | C (composites) | 1 km GRIB2 composites | Kyoto RISH research archive (http) | Research use **[to confirm]** | http://database.rish.kyoto-u.ac.jp/arch/jmadata/ |
| MeteoNet | C/S | Radar + gauges + quality code | Download | Etalab 2.0 | https://meteonet.umr-cnrm.fr/ |
| GPM DPR 2A V07 | Ku/Ka | Calibration reference | NASA Earthdata (free login); GPM-API | NASA open | https://disc.gsfc.nasa.gov/datasets/GPM_2ADPR_07/summary |
| open-radar-data | many | Sample files, **including the IMD Jaipur volume** | `pip install open-radar-data` | Per file | https://github.com/openradar/open-radar-data |

### D.2 Open software: what each package covers

| Package | Paper / URL | Covers | Licence |
|---|---|---|---|
| **Py-ART** | Helmus & Collis 2016, JORS, doi:10.5334/jors.119 | I/O (NEXRAD, IRIS/Sigmet, ODIM, CfRadial); gate filters; dealiasing; K_DP (Maesaka, Schneebeli, Vulpiani); attenuation (Z-PHI); `retrieve.qpe` (Z–R, R(K_DP), R(A), hybrid); gridding | BSD-3 |
| **pyrad / pyart-mch** (MeteoSwiss) | https://github.com/MeteoSwiss/pyrad | Config-driven operational chain: QC, calibration monitoring (sun, Z_DR, self-consistency), hydrometeor classification, polarimetric QPE, **radar–gauge comparison** | BSD |
| **xradar** | https://github.com/openradar/xradar | xarray DataTree readers for IRIS, ODIM, NEXRAD, Rainbow, GAMIC, Furuno, CfRadial1/2 (FM301) | MIT |
| **wradlib** | Heistermann et al. 2013, HESS, doi:10.5194/hess-17-863-2013 | Clutter (Gabella), **beam-blockage fraction**, attenuation, Z–R, gauge adjustment (`adjust`: additive, multiplicative, mixed, MFB), compositing, georeferencing, SR/GR matching, zonal stats | MIT |
| **LROSE** (Radx, RadxRate, RadxQpe, RadxBeamBlock, Radx2Grid, TITAN) | https://github.com/NCAR/lrose-core | C++ chain: K_DP, PID, rain rate, QPE, beam blockage, gridding | BSD-style |
| **BALTRAD** (RAVE, PPC, HLHDF) | Michelson et al. 2018, JORS, doi:10.5334/jors.193 | ODIM toolbox: QC, polarimetric processing chain, compositing | LGPL family **[to confirm]** |
| **PyDDA** | Jackson et al. 2020, JORS, doi:10.5334/jors.264 | Multi-Doppler wind retrieval (not QPE) | BSD |
| **pysteps** | Pulkkinen et al. 2019, GMD, doi:10.5194/gmd-12-4185-2019 | Readers, optical flow, nowcasting, **verification** | BSD-3 |
| **bioRad** (R) | Dokter et al. 2019, Ecography, doi:10.1111/ecog.04028 | Biological echo profiles (vol2bird), MistNet segmentation | **[to confirm]** (GitHub reports NOASSERTION) |
| **CSU_RadarTools** | https://github.com/CSU-Radarmet/CSU_RadarTools | Fuzzy-logic hydrometeor ID (HID), CSU-HIDRO blended rain rate, FIR K_DP, DSD retrievals | GPL-2.0 (**copyleft: wrap as optional dependency, do not vendor**) |
| **UNRAVEL** | Louf et al. 2020, JTECH, doi:10.1175/JTECH-D-19-0020.1 | Velocity dealiasing | MIT (GitHub; PyPI metadata says Apache-2.0) |
| **PyScanCf** | https://pyscancf.readthedocs.io (Zenodo DOI not checked in Crossref) | Reads **IMD single-sweep netCDF** into CfRadial | MIT |
| **RainForest** | https://github.com/MeteoSwiss/rainforest | RF QPE training and inference | **[to confirm]** (GitHub reports NOASSERTION) |
| **GPM-API** | https://github.com/ghiggi/gpm_api | DPR download, reading and SR/GR matching | MIT |
| **scores** | doi:10.21105/joss.06889 | Verification metrics (xarray) | Apache-2.0 |
| **MET/METplus** | doi:10.1175/BAMS-D-19-0093.1 | Verification incl. MODE | Apache-2.0 |
| **WRaINfo** | Künzel et al. 2023, JORS, doi:10.5334/jors.453 | Furuno X-band processing chain | Apache-2.0 |
| **IMPROVER** (Met Office) | https://github.com/metoppv/improver | Post-processing, incl. `FillRadarHoles` | BSD-3 |
| **imdlib** | https://imdlib.readthedocs.io | IMD gridded rainfall download/read | MIT |
| pycwr | https://github.com/YvZheng/pycwr | CINRAD readers and QPE | **PolyForm-Noncommercial**: avoid as a dependency |

### D.3 Use vs build (radar-wow decision table)

| radar-wow sub-component | Decision | Wrap from | Notes |
|---|---|---|---|
| Format I/O (IRIS RAW, ODIM, NEXRAD, CfRadial) | **USE** | xradar (primary), Py-ART (fallback) | Standardise on the xarray DataTree / FM301 internal model |
| IMD single-sweep netCDF | **USE + thin adapter** | PyScanCf, then xradar | Add a radar-wow adapter that merges sweeps into a volume and records missing moments |
| Gate filtering, texture, despeckle | **USE** | Py-ART `GateFilter`, wradlib clutter | — |
| Static clutter maps, AP flags | **BUILD (thin)** | wradlib Gabella as a component | Delhi-specific clear-air climatology |
| NN / RF clutter QC | **BUILD** (paper classes) | — | Lakshmanan 2014; Bölz 2026 synthetic-label U-Net |
| Bio-echo classification | **USE (optional)** | bioRad/MistNet (R; via rpy2 or offline) | Validate on Delhi first |
| Velocity dealiasing | **USE** | UNRAVEL, Py-ART region-based | Not QPE-critical |
| Φ_DP processing and K_DP | **USE** | Py-ART (Maesaka, Vulpiani), CSU FIR, pyrad (Schneebeli) | Implement extra papers only where no implementation exists |
| Attenuation correction (Z-PHI, ZPHI-α optimisation) | **USE**, then BUILD band-specific wrappers | Py-ART, wradlib | Tune α/β per band in radar-wow config |
| Beam-blockage fraction | **USE** | wradlib (`beam_block_frac`, Bech 2003), LROSE RadxBeamBlock | Add a building-height layer for Delhi |
| Beam-blockage infill (cGAN) | **BUILD** | — | Tan & Chen 2023; Geiss & Hardin 2021 (code exists) |
| Calibration: GPM SR/GR matching | **USE** | GPM-API + wradlib notebooks (Warren 2018, Crisologo 2018) | radar-wow class orchestrates; Saini 2026 protocol |
| Calibration: self-consistency, Z_DR, Sun | **USE** | pyrad | — |
| Hydrometeor classification | **USE** | CSU_RadarTools (GPL, optional), Py-ART, pyrad | IMD HCLASS as an extra input |
| VPR / bright-band correction | **BUILD** (paper classes) | wradlib helpers | Few general implementations exist |
| Rain-rate estimators (Z–R, R(K_DP), R(A), blends) | **BUILD as thin classes** on Py-ART `retrieve.qpe` | Py-ART | One class per paper (Sharma 2025 seasonal Z–R, etc.) |
| Compositing / mosaic | **USE** primitives, BUILD weighting | wradlib comp, Py-ART grid, BALTRAD | Quality-index weights are the radar-wow contribution |
| Gauge adjustment / merging | **USE** basic, BUILD advanced | wradlib `adjust`, pykrige / gstools | Conditional merging, KED and RadarGaugeNet as classes |
| ML QPE (RainForest) | **USE / port** | `rainforest-mch` | Retrain on Delhi |
| ML QPE (CNN, U-Net, physics-constrained) | **BUILD** | PyTorch | Paper classes (Part A ranking) |
| Nowcasting | **USE** (out of scope for QPE) | pysteps | — |
| Verification | **USE** | `scores` (xarray), pysteps.verification, wradlib pair extraction; METplus optional | radar-wow builds only the matching and stratification layer |
| Data stores | **USE** | Zarr / Icechunk (radar-datatree pattern) | — |

---

## Ranked recommendations

### 1. ML methods worth implementing, and when

The project's physical stages are QC → calibration → attenuation → K_DP → classification → estimation → composite → merging. ML enters only after the step listed in the "Prerequisite" column.

| Rank | Method (class) | Prerequisite | Why |
|---|---|---|---|
| 1 | **RainForest RF QPE** (Wolfensberger 2021) | Implement after the physical estimation stage. Train **on calibrated, attenuation-corrected features plus physical R estimates as inputs**. | Cheapest, robust with few gauges, interpretable. A reference implementation exists. Gives a Z-only variant for single-pol Palam/Patiala. |
| 2 | **ML clutter / non-met QC** (Lakshmanan 2014 dual-pol NN; Bölz 2026 synthetic-trained U-Net) | Sits in the QC stage itself, after the rule-based QC baseline exists to compare against. | Delhi dust, AP and urban clutter are the biggest error source, and synthetic labels avoid the absent-labels problem. |
| 3 | **Volume/patch-to-gauge CNN** (Yo 2021 Z-only; RQPENet / StarNet dual-pol) | After compositing; trained with leave-radar-out splits. Needs ≥2–3 seasons of gauges. | Best in-domain skill. Run as a challenger to RF, not a replacement, until OOD tests pass. |
| 4 | **cGAN beam-blockage infill** (Tan & Chen 2023 / 2025; Geiss & Hardin 2021) | After the beam-blockage-fraction stage; before estimation. | Needed for the Himalayan X-band radars and urban blocked sectors. Training data come from unblocked neighbours. |
| 5 | **ML post-merge corrector** (Osborne 2023 / 2026) or **graph radar–gauge fusion** (CNGAT, RadarGaugeNet) | After classical gauge merging. | Only worthwhile once real-time gauge access exists. |
| 6 | **Physics-constrained QPE** (FURECast-style self-consistency loss applied to estimation) | After K_DP and attenuation stages are validated. | Research contribution: no peer-reviewed physics-constrained radar QPE exists. |
| 7 | **Satellite virtual radar** (GREMLIN-type; evaluate with SatRain) | Independent fallback, after the composite exists to train against. | Covers radar outages and gaps. |
| — | Foundation models, diffusion QPE | Defer | No proven radar foundation model; revisit in 2027. |

**Generalisation rule.** Every ML class must report three things:
- in-domain skill;
- leave-radar-out and leave-season-out skill;
- skill gain over the best physical estimator in the same stratum.

**Pretraining and fine-tuning.**
- Pretrain on NEXRAD (S-band) and on DWD / FMI / KNMI / MeteoSwiss (C-band).
- Fine-tune on IMD data.
- Validate the S→S and C→C transfers separately.

### 2. Verification design radar-wow should adopt

1. **A `radarwow-verify` matching layer** that:
   - extracts radar values at gauges in polar and Cartesian geometry (wradlib);
   - accumulates them to the gauge interval: hourly, plus a daily IMD 03 UTC day;
   - records beam height, range, blockage fraction, band, radar ID, season, rain type and processing stage.
2. **Score engines.** `scores` for continuous, categorical and probabilistic scores; pysteps for FSS and the intensity-scale method. METplus only for MODE or interoperability with operational centres.
3. **Mandatory score set.**
   - Multiplicative bias, RMSE, MAE, r, KGE.
   - POD, FAR, CSI, frequency bias, HSS and SEDI at the fixed thresholds.
   - FSS at 1–50 km against IMERG and the gridded references.
   - CRPS and reliability for probabilistic outputs.
4. **Mandatory stratification:** range, band/radar, season, rain type, intensity and blockage (B.3). Also a **per-stage ablation table**.
5. **Independence.** Leave-one-gauge-out or station k-fold for any gauge-adjusted product. Leave-radar-out and leave-season-out for ML. Bootstrap confidence intervals.
6. **Representativeness.** Report the area–point error-variance correction (Ciach & Krajewski 1999). Where dense gauges exist, use a gauge-pair-derived error budget instead of raw R−G scatter.
7. **Calibration verification as a separate track.** Report GPM SR/GR Z bias per radar and season, with a beam-blockage-fraction quality filter (Saini 2026; Warren 2018; Crisologo 2018).
8. **Reference hierarchy for Delhi.** IMD hourly AWS/ARG (primary) > IMD 0.25° daily > IMERG V07 Final / GSMaP Gauge_NRT > IMD's own SRI/PAC images (qualitative only).

### 3. Concrete steps to get usable Delhi-area radar and gauge data

1. **Now, with no permissions needed:**
   - Develop readers and QC on the IMD Jaipur sample in `open-radar-data` and on IDEAM IRIS volumes (AWS), so IRIS-format handling is tested before IMD data arrive.
   - Develop and pretrain physics + ML classes on NEXRAD (S) and FMI / KNMI / DWD (C, dual-pol) open data.
2. **Register** on the IMD Data Service Portal (https://dsp.imdpune.gov.in) in the research-institute category, then file a request on the Radar Data Supply Portal (https://radarapi.imd.gov.in).
   - **Radars:** Lodhi Road C, Palam S, Ayanagar X, Patiala S, Jaipur C (optionally Mukteshwar and Lansdowne X).
   - **Format:** **IRIS RAW with all moments** (Φ_DP, K_DP, ρ_HV, SQI), or netCDF that includes them.
   - **Period:** ≥3 monsoons + 2 pre-monsoons (e.g. 2022–2025), including the July 2023 Delhi floods and the May–June 2018 storm cases.
   - **Metadata:** site coordinates, antenna heights, scan strategies, calibration logs, and the processor's Z–R and clutter settings.
3. **Gauges.** In the same Data Service Portal request, ask for **hourly AWS/ARG rainfall within about 150 km of Safdarjung** for the same periods, plus Safdarjung and Palam synoptic records.
   - Also ask whether the 50 new Delhi AWS announced in Jan 2026 are live.
   - In parallel, contact IITM Delhi (Rajendra Nagar) for the Joss–Waldvogel disdrometer data behind Kumar et al. 2024.
   - Ask the Delhi state Flood Control department and DPCC about their gauge and met networks (**[to confirm]**).
4. **Pursue an MoU route.** A research MoU with IMD (and NCMRWF for its gridded radar rainfall and quality index) is the realistic path to multi-year, full-moment archives and to publishing derived QPE grids. Since May 2025, IMD favours "genuine, purpose-driven requests".
5. **Free references to pull immediately:**
   - IMD 0.25° daily gridded rainfall (`imdlib`).
   - GPM IMERG V07 and GSMaP v8 over 27–30.5 N, 75.5–79 E.
   - GPM DPR 2A overpasses of the Delhi radars (GPM-API) for calibration.
6. **Licensing check before release.** Confirm with IMD whether derived QPE grids and trained model weights can be published openly. Until then, keep raw IMD data out of public radar-wow repositories and publish only code and open-data-derived artefacts.
