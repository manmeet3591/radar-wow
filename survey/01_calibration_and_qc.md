# radar-wow survey 01: Stage 1 (calibration) and Stage 2 (quality control)

*Survey date: 2026-11-03. Scope: absolute and relative calibration of Z, ZDR and ΦDP, and removal or flagging of non-meteorological echoes, for S-, C- and X-band dual-polarisation radars (NEXRAD, OPERA and other European networks, IMD including the Delhi C-band, Palam S-band and Ayanagar X-band radars).*

## 0. Introduction and how to read this file

radar-wow implements each algorithm as one Python class that runs on an xradar `DataTree` with ODIM moment names (`DBZH, ZDR, PHIDP, RHOHV, KDP, VRADH, WRADH, SNRH, SQIH`). Most of the archive we expect to process holds **moments only, with no I/Q time series or Doppler spectra**. The key column in every table below is therefore **"Archived moments?"**:

- **Yes**: works on archived ODIM/CfRadial moments.
- **Partly**: works on moments but needs something extra, such as a DEM, a sounding/NWP field, a long time series, special scans (birdbath, sun scans), or an external reference (GPM).
- **No**: needs I/Q or spectra. These methods belong in the radar signal processor. radar-wow can only *detect their residue* or document what the processor did.

Method sets:
- **New:** papers found and verified in this survey.
- **Existing:** methods carried over from `radar_wow/literature/02_quality_control_and_polarimetric_processing.md` and `04_india_delhi_radar.md`.
- **Seed:** the seven papers in the project's seed list. All of them are kept and marked **[seed]**.

**DOI verification.** Every DOI in §5 was resolved against the Crossref REST API (`api.crossref.org/works/<DOI>`) on 2026-11-03. Title, first authors and year matched in every case. Volume and page numbers are given only where Crossref returned them. Items without a DOI, such as ERAD proceedings and software, are marked *no DOI*. Items I could not find are listed in §5.3 and were not invented.

Band abbreviations: S ≈ 10 cm, C ≈ 5 cm, X ≈ 3 cm. "All" means the method is band-agnostic once the band-dependent constants are adjusted.

---

## 1. Stage 1: Calibration

### 1.1 Absolute Z calibration against spaceborne radar (GPM DPR / TRMM PR)

| Method | Paper (DOI) | What it does | Bands | Inputs | Open source | Operational use | Archived moments? |
|---|---|---|---|---|---|---|---|
| GPM Validation Network volume matching | Schwaller & Morris 2011, JTECH 28, 301 (10.1175/2010JTECHA1403.1) | Averages ground-radar (GR) and spaceborne-radar (SR) samples in common volumes along the SR beam and compares their reflectivities. | All | DBZH plus GPM 2A-DPR or 2A-Ku | NASA VN (not packaged) | NASA GPM GV, used on NEXRAD | Partly (needs GPM files) |
| **[seed]** GR–SR geometric matching with Ku→S/C/X frequency correction | Warren et al. 2018, JTECH 35, 323 (10.1175/JTECH-D-17-0128.1) | Matches GR and SR in volume, converts Ku to the GR band using phase-dependent relations, and takes the mean bias as the calibration offset. Covers both TRMM and GPM. | All | DBZH, GPM 2A, freezing-level/bright-band info | wradlib GPM-matching tutorial; [gpmmatch](https://github.com/vlouf/gpmmatch) | BoM Australia (Louf et al. 2019) | Partly |
| **[seed]** Beam-blockage-fraction quality filter for GR–SR matching | Crisologo et al. 2018, AMT 11, 5223 (10.5194/amt-11-5223-2018) | Drops or down-weights matched samples affected by partial beam blockage (DEM-derived) and path-integrated attenuation. This makes the calibration bias much more consistent. | All (tested on a Philippine radar) | DBZH, DEM, GPM | [wradlib](https://github.com/wradlib/wradlib) | Research / wradlib users | Partly |
| GPM–NEXRAD inter-comparison | Keem et al. 2019, Atmos. Res. 226, 49 (10.1016/j.atmosres.2019.04.010) | Systematic DPR–NEXRAD comparison that quantifies matching uncertainties. | S | DBZH, GPM | — | Research | Partly |
| X-band calibration against GPM DPR | Loulli et al. 2025, Remote Sens. 17, 1712 (10.3390/rs17101712) | Applies GR–SR matching to two X-band radars. This is a recent X-band demonstration. | X | DBZH, GPM | — | Cyprus | Partly |
| Indian S-band calibration vs GPM | Saini et al. 2026, Radio Sci. 61 (10.1029/2025RS008484) | Evaluates and corrects calibration bias of IMD S-band radars on India's east coast using GPM Ku. | S (IMD) | DBZH, GPM | — | IMD research | Partly |
| X-band bias correction (disdrometer and GPM) | Jha et al. 2024, J. Earth Syst. Sci. 133 (10.1007/s12040-024-02271-w) | Finds and corrects a large Z bias in an Indian X-band radar. | X (IITM) | DBZH, disdrometer, GPM | — | IITM | Partly |

### 1.2 Relative calibration adjustment (RCA) from ground clutter

| Method | Paper (DOI) | What it does | Bands | Inputs | Open source | Operational use | Archived moments? |
|---|---|---|---|---|---|---|---|
| RCA | Silberstein et al. 2008, JTECH 25, 2037 (10.1175/2008JTECHA1063.1) | Tracks a high percentile (e.g. 95th) of the Z distribution of stable clutter pixels near the radar on dry days. Changes in it give relative calibration drift. | S (Kwajalein); all in principle | DBZH (ideally unfiltered), clutter map, rain mask | — | NASA TRMM GV | Yes (needs a clutter map from dry days; filtered Z degrades it) |
| RCA generalised | Wolff et al. 2015, JTECH 32, 496 (10.1175/JTECH-D-13-00185.1) | Generalises RCA to NEXRAD and other sites and shows how to correct Z with it. | S | as above | — | NASA GPM GV | Yes |
| eRCA for X/Ka and RHI | Hunzinger et al. 2020, AMT 13, 3147 (10.5194/amt-13-3147-2020) | Extends RCA to higher frequencies and RHI scans. | X, Ka (also C) | DBZH, clutter map | — | ARM | Yes |
| Integrated RCA + GPM + self-consistency | Louf et al. 2019, JTECH 36, 17 (10.1175/JTECH-D-18-0007.1) | Uses GPM to fix the absolute offset and RCA to track day-to-day drift between overpasses. Self-consistency serves as a cross-check. | All (S/C in Australia) | DBZH, ZDR, PHIDP, GPM | Louf's code ([github.com/vlouf](https://github.com/vlouf)) | BoM | Partly |
| Real-time network calibration and pointing monitoring | Louf & Protat 2023, JTECH 40, 823 (10.1175/JTECH-D-22-0118.1) | Operational near-real-time monitoring of calibration and antenna pointing across a national network. | All | moments, GPM, sun hits | — | BoM | Partly |

### 1.3 Polarimetric self-consistency (Z from ZDR and KDP/ΦDP in rain)

| Method | Paper (DOI) | What it does | Bands | Inputs | Open source | Operational use | Archived moments? |
|---|---|---|---|---|---|---|---|
| Self-consistency principle | Gorgucci et al. 1992, IEEE TGRS 30, 853 (10.1109/36.175319) | KDP is immune to calibration error, so Z can be calibrated from KDP = f(Z, ZDR) in rain. | All | DBZH, ZDR, KDP | — | — | Yes |
| Procedure using rain-medium properties | Gorgucci et al. 1999, IEEE TGRS 37, 269 (10.1109/36.739161) | Operational procedure for the above. | All | as above | — | — | Yes |
| ΦDP-integral calibration | Vivekanandan et al. 2003, Radio Sci. 38 (10.1029/2002RS002676) | Compares the measured ΦDP increase along rain paths with ΦDP predicted by integrating KDP(Z, ZDR). The ratio gives the Z bias. Using the integral avoids noisy KDP. | All | DBZH, ZDR, PHIDP | — | NCAR | Yes |
| **[seed]** Calibration issues of dual-pol radars | Ryzhkov et al. 2005, JTECH 22, 1138 (10.1175/JTECH1772.1) | Sets accuracy targets and gives self-consistency Z calibration plus natural ZDR targets (light rain, dry aggregated snow). Also covers noise effects on ρhv/ZDR. | S (formulas adapt to C/X) | DBZH, ZDR, KDP/PHIDP, RHOHV, ML height | Related functions in MeteoSwiss Py-ART (`selfconsistency_bias`, `zdr_precip`, `zdr_snow`) | NEXRAD / NSSL | Yes |
| Operational self-consistency (Météo-France) | Gourley et al. 2009, JTECH 26, 689 (10.1175/2008JTECHA1152.1) | Evaluates self-consistency on operational radars and its sensitivity to the assumed drop-shape relation, a systematic uncertainty at the ~1 dB level. | C (also S/X) | DBZH, ZDR, PHIDP | — | Météo-France | Yes |
| Integrated calibration-stability monitoring | Vaccarono et al. 2016, AMT 9, 5367 (10.5194/amt-9-5367-2016) | Combines several monitors (self-consistency, ZDR checks, etc.) to track C-band calibration stability over time. | C | moments | — | ARPA Piemonte | Yes |
| Long-term French QC monitoring | Figueras i Ventura et al. 2012, QJRMS 138, 2212 (10.1002/qj.1934) | Long-term monitoring of polarimetric data quality across the French network. | C, S | moments | — | Météo-France | Yes |

### 1.4 Sun-based monitoring of receiver, antenna pointing and ZDR

| Method | Paper (DOI) | What it does | Bands | Inputs | Open source | Operational use | Archived moments? |
|---|---|---|---|---|---|---|---|
| Sun hits for antenna pointing | Huuskonen & Holleman 2007, JTECH 24, 476 (10.1175/JTECH1978.1) | Detects sun "spikes" (full rays of noise-like power) in routine low-elevation scans and fits a 2-D model in azimuth/elevation against the computed sun position. This gives the pointing bias. | All | DBZH or uncorrected power along rays, scan time, site lat/lon | MeteoSwiss Py-ART (`sun_hits`, `sun_retrieval`); [pyrad](https://github.com/MeteoSwiss/pyrad) | OPERA / BALTRAD members, MeteoSwiss, FMI, KNMI | Yes, if the far range is not censored |
| Receiving-chain monitoring via the sun | Holleman et al. 2010a, JTECH 27, 159 (10.1175/2009JTECHA1213.1) | Compares sun power with a reference solar flux to monitor receiver gain. | All | as above plus solar flux | as above | OPERA | Yes |
| ZDR monitoring via the sun | Holleman et al. 2010b, JTECH 27, 881 (10.1175/2010JTECHA1381.1) | The sun is unpolarised, so the H/V power ratio of sun hits measures the receive-chain ZDR bias (not the transmit part). | All | sun hits in H and V | as above | OPERA, KNMI | Yes |
| Mid-range adaptation | Altube et al. 2015, JTECH 32, 927 (10.1175/JTECH-D-14-00116.1) | Adapts the sun method to mid-range scans, where the sun signal is mixed with weather and noise. | C (Catalonia), all | as above | pyrad | SMC Catalonia | Yes |
| Improved solar ZDR analysis | Huuskonen et al. 2016, AMT 9, 3183 (10.5194/amt-9-3183-2016) | Better estimation of solar ZDR from noisy hits. | C | as above | — | FMI | Yes |
| Solar flux at operational radars | Gabella et al. 2014, Atmosphere 6, 50 (10.3390/atmos6010050); Gabella et al. 2016, Atmosphere 7, 76 (10.3390/atmos7060076); Gabella et al. 2017, Adv. Meteorol. (10.1155/2017/4971765) | Uses the slowly varying solar component as an absolute receiver reference. Reports H/V receiver calibration accuracy for the Swiss network and a European comparison. | C | sun hits | pyrad | MeteoSwiss | Yes |

### 1.5 ZDR calibration

| Method | Paper (DOI) | What it does | Bands | Inputs | Open source | Operational use | Archived moments? |
|---|---|---|---|---|---|---|---|
| Vertical pointing / sun / cross-polar power | Hubbert et al. 2003, JTECH 20, 696 (10.1175/1520-0426(2003)20<696:SOTPCM>2.0.CO;2) | Covariance-matrix calibration methodology. Uses the vertical-pointing ("birdbath") ZDR in light rain (expected 0 dB) and solar/cross-polar power. | All | birdbath scan, cross-pol | LROSE | NCAR S-Pol | Partly (needs a birdbath scan) |
| WSR-88D ZDR calibration | Zrnić et al. 2006, JTECH 23, 944 (10.1175/JTECH1893.1) | Combines engineering measurements with weather-based checks for NEXRAD, which cannot point vertically. | S | moments, sun, test signals | — | NEXRAD | Partly |
| Operational ZDR calibration (vertical pointing + light rain) | Bechini et al. 2008, JTECH 25, 1542 (10.1175/2008JTECHA1037.1) | Compares birdbath ZDR with light-rain ZDR for operational C-band radars. | C | birdbath and/or PPI in light rain | — | ARPA Piemonte | Partly / Yes |
| Light rain and dry snow natural targets | Ryzhkov et al. 2005 **[seed]** (see 1.3) | The expected intrinsic ZDR in light rain, or in dry aggregated snow above the melting layer, fixes the offset. | All | DBZH, ZDR, RHOHV, ML height or sounding | MeteoSwiss Py-ART `zdr_precip`, `zdr_snow` | NEXRAD, MeteoSwiss | Yes |
| Bragg scatter as ZDR ≈ 0 target | Richardson et al. 2017, JTECH 34, 479 (10.1175/JTECH-D-16-0031.1) | Detects Bragg scatter (clear-air refractive-index turbulence, intrinsic ZDR = 0) and uses it for ZDR bias. Best suited to S band. | S (C/X limited, because Bragg returns weaken at shorter λ) | DBZH, ZDR, RHOHV, WRADH | — | NEXRAD (ROC) | Yes |
| Birdbath monitoring, DWD | Frech et al. 2017, JTECH 34, 599 (10.1175/JTECH-D-16-0076.1) | Uses the operational DWD birdbath scan for absolute ZDR and Z monitoring. | C | birdbath scan | — | DWD | Partly |
| Birdbath Doppler spectra | Gergely et al. 2022, AMT 15, 7315 (10.5194/amt-15-7315-2022) | Spectral post-processing of birdbath scans for multi-moment profiles. | C | birdbath spectra | — | DWD | No (spectra) |
| Dynamic ZDR from vertical profiles in rain and snow | Ferrone & Berne 2020, Remote Sens. 13, 8 (10.3390/rs13010008) | Estimates the ZDR offset dynamically from vertical profiles in rain and snow. | X (tested), all | DBZH, ZDR, ML | — | EPFL research | Yes |
| QVP-based ZDR calibration | Sanchez-Rivas & Rico-Ramirez 2022, AMT 15, 503 (10.5194/amt-15-503-2022) | Builds quasi-vertical profiles (Ryzhkov et al. 2016, 10.1175/JTECH-D-15-0020.1) from high-elevation PPIs and finds the ZDR offset in light rain / dry snow. Works without birdbath scans. | C (UK), all | high-elevation PPI moments, ML detection | — | UK research | Yes |
| QZdrCal (NEXRAD ORPG update) | Hu et al. 2026, JTECH 43, 673 (10.1175/JTECH-D-25-0123.1) | Latest operational NEXRAD ZDR calibration algorithm, based on natural targets. | S | moments | — | NEXRAD ORPG | Yes |
| ZDR cross-coupling bias (caveat) | Zrnić et al. 2010, JTECH 27, 1624 (10.1175/2010JTECHA1350.1) | Simultaneous-H/V radars have a cross-coupling ZDR bias that depends on the target, which can bias natural-target calibration. | All (SHV radars) | — | — | — | — |

### 1.6 ΦDP system offset

| Method | Paper (DOI) | What it does | Bands | Inputs | Open source | Operational use | Archived moments? |
|---|---|---|---|---|---|---|---|
| Initial ΦDP inside KDP algorithm | Wang & Chandrasekar 2009, JTECH 26, 2565 (10.1175/2009JTECHA1358.1) | Estimates the system ΦDP from the first valid rain gates of each ray before range filtering. | All | PHIDP, RHOHV, DBZH | — | CASA / CSU | Yes |
| **[seed]** ΦDP offset, unfolding and KDP for C-band in mountains | Vulpiani et al. 2012, JAMC 51, 405 (10.1175/JAMC-D-10-05024.1) | Operational chain: ΦDP offset, iterative KDP, and clutter/blockage-aware QC for C-band in complex terrain. | C (adaptable) | PHIDP, RHOHV, DBZH, DEM | wradlib (`phidp_kdp_vulpiani`) | Italian DPC | Yes |
| Linear-programming ΦDP processing | Giangrande et al. 2013, JTECH 30, 1716 (10.1175/JTECH-D-12-00147.1) | Fits a monotonic ΦDP and determines the system phase. | All | PHIDP, DBZH, RHOHV | Py-ART `phase_proc_lp` | ARM | Yes |
| Textbook treatment | Ryzhkov & Zrnić 2019, *Radar Polarimetry for Weather Observations*, Springer (10.1007/978-3-030-05093-1) | Reference for system ΦDP, noise correction, and polarimetric echo classification. | All | — | — | — | — |

### 1.7 Radar-network intercomparison and wet radome

| Method | Paper (DOI) | What it does | Bands | Inputs | Open source | Operational use | Archived moments? |
|---|---|---|---|---|---|---|---|
| Network reconciliation via specific attenuation A | Ryzhkov et al. 2014, JTECH 31, 599 (10.1175/JTECH-D-13-00038.1) | A (from ΦDP) is immune to calibration and to partial blockage. It can be used to reconcile Z between neighbouring radars and to mitigate partial blockage. | S, C, X | DBZH, ZDR, PHIDP | — | Research | Yes |
| OPERA network overview | Huuskonen et al. 2014, BAMS 95, 897 (10.1175/BAMS-D-12-00216.1); Saltikoff et al. 2019, Atmosphere 10, 320 (10.3390/atmos10060320) | European network status and harmonised monitoring (sun, ODIM, composite QC). | C mainly | — | BALTRAD | OPERA | — |
| Collocated S/C long-term biases and wet radome | Loh et al. 2022, IEEE TGRS 60 (10.1109/TGRS.2022.3170609) | Uses collocated operational S and C radars to estimate relative Z biases and the wet-radome effect statistically. | S, C | DBZH from overlapping radars | — | Taiwan | Yes |
| Wet-radome attenuation at X | Frasier et al. 2013, JTECH 30, 917 (10.1175/JTECH-D-12-00148.1) | In-place estimation of radome loss during rain at the site. | X | moments, rain at site | — | Research | Yes |

---

## 2. Stage 2: Quality control

### 2.1 Receiver noise, SNR censoring and noise correction

| Method | Paper (DOI) | What it does | Bands | Inputs | Open source | Operational use | Archived moments? |
|---|---|---|---|---|---|---|---|
| Objective noise level (HS74) | Hildebrand & Sekhon 1974, JAM 13, 808 (10.1175/1520-0450(1974)013<0808:ODOTNL>2.0.CO;2) | Estimates the noise floor statistically from data that contain noise. Originally applied to spectra; Py-ART also applies it to range profiles of power. | All | spectra, or power/DBZH along a ray | Py-ART `estimate_noise_hs74` | Widely used | Partly |
| Coherency-based detection | Ivić et al. 2009, JTECH 26, 2474 (10.1175/2009JTECHA1154.1) | Uses H/V coherency to detect weak signals below the usual power threshold. | All | I/Q | — | NEXRAD | No |
| Radial-based noise for ρhv | Ivić 2014, JTECH 31, 1867 (10.1175/JTECH-D-14-00052.1) | Estimates noise per radial to reduce the noise bias in ρhv. | All | uncensored power per radial | — | NEXRAD | Partly |
| Noise correction of ZDR and ρhv | Ryzhkov et al. 2005 **[seed]**; Ryzhkov & Zrnić 2019 (book) | Applies the standard SNR-dependent corrections: ZDR from SNR_H/SNR_V; ρhv_true = ρhv_meas·[(1+1/SNR_H)(1+1/SNR_V)]^{1/2}. Then censors below an SNR threshold. | All | ZDR, RHOHV, SNRH (or DBZH + noise level + range) | Py-ART `correct_noise_rhohv`, `correct_bias`, `compute_noisedBZ`; wradlib `estimate_snr` | NEXRAD, MeteoSwiss, others | Yes, if SNRH is archived or the noise level is known |
| ρhv-in-rain check | MeteoSwiss Py-ART `est_rhohv_rain` (software, no paper DOI) | Estimates the intrinsic ρhv in rain to check the noise correction. | All | RHOHV, DBZH | MeteoSwiss Py-ART | MeteoSwiss | Yes |

### 2.2 Ground clutter: signal-level filters (processor) and moment-level detectors (radar-wow)

| Method | Paper (DOI) | What it does | Bands | Inputs | Open source | Operational use | Archived moments? |
|---|---|---|---|---|---|---|---|
| GMAP spectral clutter filter | Siggia & Passarelli 2004, Proc. ERAD (*no DOI*) | Removes the Gaussian clutter peak around 0 m/s in the spectrum and rebuilds the weather spectrum underneath it. | All | I/Q / spectra | Vaisala processors (proprietary) | NEXRAD, many Vaisala radars | No |
| Clutter phase alignment and simulation | Hubbert et al. 2009a, JTECH 26, 1165 (10.1175/2009JTECHA1159.1) | Defines clutter phase alignment (CPA), a strong clutter discriminator. | All | I/Q | LROSE | — | No |
| **[seed]** CMD (Clutter Mitigation Decision) | Hubbert, Dixon & Ellis 2009b, JTECH 26, 1181 (10.1175/2009JTECHA1160.1) | Fuzzy logic on CPA plus Z texture and "spin". It applies the clutter filter only where clutter is detected. | All | I/Q (CPA); texture/spin are moment-based | LROSE | NEXRAD | No for full CMD. A moment-only "CMD-lite" (texture + spin) is feasible |
| Autocorrelation spectral density | Torres & Warde 2014, JTECH 31, 2049 (10.1175/JTECH-D-13-00117.1) | Clutter detection and filtering in the autocorrelation spectral domain. | All | I/Q | — | NEXRAD | No |
| Polarimetric spectral filter | Moisseev & Chandrasekar 2009, JTECH 26, 215 (10.1175/2008JTECHA1119.1); Alku et al. 2015, IEEE TGRS 53, 3628 (10.1109/TGRS.2014.2380476) | Classifies each spectral bin with polarimetric spectral densities and removes clutter, noise and biological echoes in the spectrum. | All | spectra | — | FMI research | No |
| Gabella texture filter | Gabella & Notarpietro 2002, ERAD (*no DOI*) | Echo-continuity/texture filter for single-pol Z in mountains. | All | DBZH | wradlib `filter_gabella`, `histo_cut` | — | Yes |
| 3-D reflectivity structure | Steiner & Smith 2002, JTECH 19, 673 (10.1175/1520-0426(2002)019<0673:UOTDRS>2.0.CO;2) | Detects clutter/AP from vertical extent, texture and spin of Z. | All | DBZH volume | — | — | Yes |
| Fuzzy logic, single-pol | Berenguer et al. 2006, JTECH 23, 1157 (10.1175/JTECH1914.1) | Fuzzy logic on 3-D Z texture features. | All | DBZH volume | — | Spain | Yes |
| Fuzzy logic, dual-pol | Gourley et al. 2007, JTECH 24, 1439 (10.1175/JTECH2035.1) | Separates precipitation from non-precipitation using empirical membership functions of ZDR, ρhv, ΦDP texture and Z texture. | C (S/X adaptable) | DBZH, ZDR, RHOHV, PHIDP | wradlib `classify_echo_fuzzy` (related) | Météo-France | Yes |
| Bayesian dual-pol AP/clutter | Rico-Ramirez & Cluckie 2008, IEEE TGRS 46, 1892 (10.1109/TGRS.2008.916979) | Classifies clutter/AP vs rain using texture of ZDR, ΦDP and Z. | C (UK) | DBZH, ZDR, PHIDP | — | UK research | Yes |
| AI clutter identification | Islam et al. 2012, Atmos. Res. 109–110, 95 (10.1016/j.atmosres.2012.02.007) | Compares AI classifiers for clutter on dual-pol features. | C | moments | — | — | Yes |
| Clutter contamination effects | Friedrich et al. 2009, JTECH 26, 251 (10.1175/2008JTECHA1092.1) | Quantifies how residual clutter biases ZDR, ρhv and ΦDP. Useful to set QC thresholds. | C | moments | — | — | — |
| Fuzzy logic UK (dual-pol moments) | Dufton & Collier 2015, AMT 8, 3985 (10.5194/amt-8-3985-2015) | Fuzzy filter of non-met echoes from dual-pol moments. | C | DBZH, ZDR, RHOHV, PHIDP, VRADH | — | UK research | Yes |
| Dual-scan / 3-D discriminant | Golbon-Haghighi et al. 2016, Atmosphere 7, 83 (10.3390/atmos7060083); Golbon-Haghighi & Zhang 2019, JTECH 36, 1285 (10.1175/JTECH-D-18-0147.1) | Clutter detection from scan-to-scan correlation and a 3-D discriminant of dual-pol features. | S | moments (two scans) | — | Research | Yes |
| Simple ρhv/ΦDP-texture met/non-met | Kilambi et al. 2018, JTECH 35, 1415 (10.1175/JTECH-D-17-0175.1) | Uses spatial texture of ΦDP and ρhv to separate met from non-met targets (clutter, biology, etc.). Easy to transfer across bands. | S, C (X with care) | PHIDP, RHOHV, DBZH | — | McGill | Yes |
| Improved fuzzy logic (C-band) | Zhang et al. 2020, AMT 13, 537 (10.5194/amt-13-537-2020) | Improved fuzzy met/non-met classification with C-band dual-pol. | C | moments | — | China research | Yes |
| Physics + ML clutter (phased array) | Li, Zhang & Wu 2023, IEEE TGRS 61 (10.1109/TGRS.2023.3323836) | Physical discriminants plus ML (NBC, MLP, CNN) for clutter detection. The physics features improve ML. | S (PAR) | moments | — | Research | Yes |

### 2.3 Anomalous propagation (AP) and sea clutter

| Method | Paper (DOI) | What it does | Bands | Inputs | Open source | Operational use | Archived moments? |
|---|---|---|---|---|---|---|---|
| Statistical AP detection | Moszkowicz et al. 1994, JTECH 11, 1026 (10.1175/1520-0426(1994)011<1026:SDOAPI>2.0.CO;2) | Statistical (Bayesian) discriminant on Z pattern features. | All | DBZH volume | — | — | Yes |
| NN AP detection | Grecu & Krajewski 2000, JTECH 17, 121 (10.1175/1520-0426(2000)017<0121:AEMFDO>2.0.CO;2) | Neural network on Z features for AP. | S | DBZH volume | — | — | Yes |
| Spurious echo removal using temperature data | Michelson & Sunhede 2004, Met. Apps 11, 1 (10.1017/S1350482703001129) | Uses multisource temperature information to flag spurious echoes that cannot be precipitation. | C | DBZH, NWP/satellite temperature | BALTRAD heritage | SMHI | Partly |
| AP and propagation modelling | Bech et al. 2012, InTech chapter (10.5772/38172); Bech et al. 2007, QJRMS 133, 1191 (10.1002/qj.98) | Links super-refraction/ducting conditions to AP clutter, and models beam propagation and blockage. | All | soundings / NWP refractivity | — | SMC | Partly |
| AP vs inversions in India | Bibraj et al., MAUSAM 71(1), 11–20 (10.54302/mausam.v71i1.2) | IMD analysis of AP clutter intensity vs inversion and refractivity gradient. | S (Visakhapatnam) | radiosonde, DBZH | — | IMD | Partly |
| Sea clutter (S band) | Collier 1998, Met. Apps 5, 263 (10.1017/S1350482798000930) | Characterises sea-clutter echoes from an S-band radar. | S | DBZH | — | UK | Yes |
| Dual-pol AP / sea-clutter separation | Rico-Ramirez & Cluckie 2008 (see 2.2) | Dual-pol features (low ρhv, noisy ZDR/ΦDP) separate AP/sea clutter from rain. | C | moments | — | — | Yes |

### 2.4 Biological echoes (birds, insects, bats, locusts)

| Method | Paper (DOI) | What it does | Bands | Inputs | Open source | Operational use | Archived moments? |
|---|---|---|---|---|---|---|---|
| Polarimetric signatures of insects/birds | Zrnić & Ryzhkov 1998, IEEE TGRS 36, 661 (10.1109/36.662746) | Shows biology has high ZDR, low ρhv and large differential phase. This is the basis for every dual-pol bio filter. | S | moments | — | — | Yes |
| Bird/insect discrimination in clear air | Martin & Shapiro 2007, JTECH 24, 1215 (10.1175/JTECH2038.1) | High-resolution discrimination of birds vs insects. | — | moments | — | — | Yes |
| vol2bird | Dokter et al. 2011, J. R. Soc. Interface 8, 30 (10.1098/rsif.2010.0116) | Separates birds from precipitation in operational C-band volumes and produces vertical profiles of bird density and speed. | C, S | DBZH, VRADH, WRADH, RHOHV if available | [vol2bird](https://github.com/adokter/vol2bird), [bioRad](https://github.com/adokter/bioRad) | ENRAM / OPERA research | Yes |
| Orthogonal-polarisation Doppler velocities | Melnikov et al. 2014, IEEE GRSL 11, 592 (10.1109/LGRS.2013.2272011) | Differences between H and V Doppler velocities from biological scatterers. | — | VRADH, VRADV | — | — | Partly (needs V-channel velocity) |
| Dual-pol products for biology | Stepanian et al. 2016, Ecosphere 7 (10.1002/ecs2.1539) | Biology-oriented dual-pol products and signatures. | S | moments | — | — | Yes |
| ML bird/insect classification | Jatau et al. 2021, JTECH (10.1175/JTECH-D-20-0180.1) | Supervised ML on S-band polarimetric features to separate birds and insects. | S | moments | — | Research | Yes |
| Gaussian mixture birds/insects (single-pol) | Nussbaumer et al. 2021, Remote Sens. 13, 1989 (10.3390/rs13101989) | Gaussian mixture model separating birds and insects without dual-pol. | C | DBZH, VRADH, WRADH | — | Swiss research | Yes |
| bioRad | Dokter et al. 2019, Ecography 42, 852 (10.1111/ecog.04028) | R package for extracting biological echoes and profiles. | All | ODIM volumes | [bioRad](https://github.com/adokter/bioRad) | ENRAM | Yes |
| **[seed]** MistNet | Lin et al. 2019, Methods Ecol. Evol. 10, 1908 (10.1111/2041-210X.13280) | CNN segmentation of rain vs biology on NEXRAD, trained with labels derived from dual-pol. It can run on archives without dual-pol. | S (NEXRAD); C via vol2bird | DBZH, VRADH, WRADH (+ZDR, RHOHV) at several elevations | in [vol2bird](https://github.com/adokter/vol2bird); [wsrlib](https://github.com/darkecology/wsrlib) | BirdCast | Yes |
| Bird roost detection (CNN) | Chilson et al. 2019, Remote Sens. Ecol. Conserv. 5, 20 (10.1002/rse2.92); Cheng et al. 2020, AAAI 34 (10.1609/aaai.v34i01.5373) | CNN detection and tracking of roost rings. | S | DBZH, VRADH | — | Research | Yes |
| Insect vs clutter (archived data) | Rennie et al. 2010, AMT Discuss. 3, 1843 (10.5194/amtd-3-1843-2010) | Separates insects and clutter using archived single-pol data. *Discussion paper*; the final AMT version was not located. | C | DBZH, VRADH | — | UK | Yes |
| Aeroecology review | Shamoun-Baranes et al. 2019, Ecography 42, 847 (10.1111/ecog.04582) | Review and roadmap of biological use of weather radar networks. | All | — | — | — | — |

### 2.5 RLAN/Wi-Fi interference, sun spikes and radar–radar interference

| Method | Paper (DOI) | What it does | Bands | Inputs | Open source | Operational use | Archived moments? |
|---|---|---|---|---|---|---|---|
| **[seed]** Threat from wireless technology | Saltikoff et al. 2016, BAMS 97, 1159 (10.1175/BAMS-D-15-00048.1) | Documents the growth of 5 GHz RLAN interference and its radial "spoke" patterns. Mainly a C-band problem. | C (also S, X) | — | — | OPERA | — |
| ropo anomaly detectors (emitters, sun, ships, speckle) | Peura 2002, ERAD (*no DOI*); implemented in BALTRAD (Michelson et al. 2018, JORS 6, 12, 10.5334/jors.193) | Image-processing detectors of radial emitter lines, sun rays, ships and speckle that output probability-of-anomaly fields. | All | DBZH (PPI) | [bropo](https://github.com/baltrad/bropo) | FMI, SMHI, OPERA members | Yes |
| Sun-hit detection | Huuskonen & Holleman 2007; Holleman et al. 2010a (see 1.4) | Flags full-ray sun spikes, which are then removed and reused for monitoring. | All | DBZH | MeteoSwiss Py-ART `sun_hits` | OPERA | Yes |
| RADVOL-QC spike / RLAN algorithms | Ośródka & Szturc 2022, AMT 15, 261 (10.5194/amt-15-261-2022) | Updated operational QC that includes spike detection, wind-turbine and terrain algorithms, and a quality index. | C | DBZH, other moments | — | IMGW Poland | Yes |
| DWD RFI detection | Schaper et al. 2022, AMT 15, 6625 (10.5194/amt-15-6625-2022) | Operational radio-frequency interference detection and mitigation. | C | moments | — | DWD | Mostly yes |
| Radar–radar interference | Frech et al. 2023, AMT 16, 295 (10.5194/amt-16-295-2023) | Detects and mitigates interference between neighbouring radars. | C | moments | — | DWD | Yes (detection) |
| Wi-Fi interference detection | Rodríguez et al. 2025, Radio Sci. 60 (10.1029/2025RS008232) | Strategy to detect Wi-Fi interference in weather radar data. | C | see paper | — | Research | Not assessed |

### 2.6 Wind-turbine clutter (WTC)

| Method | Paper (DOI) | What it does | Bands | Inputs | Open source | Operational use | Archived moments? |
|---|---|---|---|---|---|---|---|
| WTC signatures | Isom et al. 2009, JTECH 26, 894 (10.1175/2008JTECHA1136.1) | Characterises WTC in Z, V and spectrum width. | S, C | moments | — | — | Yes |
| Automatic WTC detection | Hood et al. 2010, JTECH 27, 1868 (10.1175/2010JTECHA1437.1) | Automatic detection of WTC. | S | moments (+ spectra) | — | Research | Partly |
| WTC impact quantification | Norin 2015, AMT 8, 593 (10.5194/amt-8-593-2015) | Quantifies clutter and blockage by wind farms. Supports a static turbine mask. | C | DBZH, turbine locations | — | SMHI | Yes |
| DWD WTC monitoring | Frech et al. 2026, AMT 19, 1711 (10.5194/amt-19-1711-2026) | Operational monitoring and quantification of WTC in the DWD network. | C | moments, turbine database | — | DWD | Yes |

### 2.7 Second-trip (range-folded) echoes

| Method | Paper (DOI) | What it does | Bands | Inputs | Open source | Operational use | Archived moments? |
|---|---|---|---|---|---|---|---|
| SZ phase coding | Sachidananda & Zrnić 1999, JTECH 16, 1351 (10.1175/1520-0426(1999)016<1351:SPCFRR>2.0.CO;2) | Phase codes separate overlaid 1st- and 2nd-trip signals in the processor. | S (NEXRAD) | I/Q | — | NEXRAD | No |
| Dual-pol artefact recognition | Kumjian 2013, J. Oper. Meteor. 1, 265 (10.15191/nwajom.2013.0121) | Catalogue of dual-pol artefacts, including range-folded echoes (low ρhv, noisy ΦDP, radially elongated shapes). | All | moments | — | NWS training | Yes (heuristic detection) |

### 2.8 Dust/sand, smoke/ash, chaff, locusts

| Method | Paper (DOI) | What it does | Bands | Inputs | Open source | Operational use | Archived moments? |
|---|---|---|---|---|---|---|---|
| Haboob dual-pol case | Dempsey 2014, Adv. Meteorol. (10.1155/2014/904759) | Single case study: dust shows low ρhv. ZDR is inconclusive. | S | DBZH, ZDR, RHOHV | — | — | Yes |
| Delhi dust/thunderstorm events May–June 2018 | Singh et al. 2021, MAUSAM 72, 719 (10.54302/mausam.v72i4.3543) | Delhi C-band dual-pol analysis of three severe events. Reports that dual-pol helps reveal the non-meteorological part of the echo. | C (Delhi) | moments | — | IMD | Yes |
| Smoke plume signatures | Melnikov et al. 2008, GRL 35 (10.1029/2008GL034311); Melnikov et al. 2009, JGR 114 (10.1029/2009JD012647); Jones & Christopher 2010, BAMS 91, 455 (10.1175/2009BAMS2919.1); Zrnić et al. 2020, Atmosphere 11, 363 (10.3390/atmos11040363) | Smoke/debris plumes show low Z, very low ρhv and noisy, often high ZDR. Zrnić et al. (2020) is the synthesis. | S | moments | — | NWS forecasters | Yes |
| Chaff | Zrnić & Ryzhkov 2004, JTECH 21, 1017 (10.1175/1520-0426(2004)021<1017:PPOC>2.0.CO;2) | Polarimetric properties of chaff. Usable as a fuzzy class. | S | moments | — | — | Yes |
| HCA non-met classes | Park et al. 2009, WAF 24, 730 (10.1175/2008WAF2222205.1) | NEXRAD HCA includes ground clutter/AP and biological classes. These can serve as a non-met mask. | S (C/X with retuning) | DBZH, ZDR, RHOHV, KDP, textures | CSU_RadarTools / Py-ART (related HCAs) | NEXRAD | Yes |

No peer-reviewed **dust-echo classifier** for Indian radars was found (see also `04_india_delhi_radar.md`). The practical route is to treat dust as a non-met class with low ρhv and high ΦDP/Z texture (Kilambi 2018 / Gourley 2007 style) and to validate it on Delhi pre-monsoon cases. Searches also surfaced an IMD study of locust-swarm echoes on the Delhi and Lucknow radars (2020), but no DOI was verified for it.

### 2.9 Speckle and isolated gates

| Method | Paper (DOI) | What it does | Bands | Inputs | Open source | Operational use | Archived moments? |
|---|---|---|---|---|---|---|---|
| Despeckling / small-object removal | Lakshmanan et al. 2007, JAMC 46, 288 (10.1175/JAM2460.1) (part of the QC chain); Py-ART `despeckle_field` (software); BALTRAD ropo speckle detectors (Peura 2002) | Removes connected regions smaller than N gates, or isolated pixels. | All | any moment | Py-ART, bropo | MRMS, OPERA | Yes |

### 2.10 Beam blockage (partial/total, DEM-based and polarimetric)

| Method | Paper (DOI) | What it does | Bands | Inputs | Open source | Operational use | Archived moments? |
|---|---|---|---|---|---|---|---|
| DEM beam-blockage fraction (BBF) | Bech et al. 2003, JTECH 20, 845 (10.1175/1520-0426(2003)020<0845:TSOSPW>2.0.CO;2) | Computes partial blockage of the beam by terrain along each ray, and shows its sensitivity to the refractivity gradient. Common practice is to correct Z for moderate blockage and mask heavy blockage. | All | DEM, site, beamwidth, elevation, refractivity | wradlib `beam_block_frac`, `cum_beam_block_frac`; BALTRAD [beamb](https://github.com/baltrad/beamb) | SMC, OPERA | Partly (DEM) |
| GIS-based blockage | Krajewski et al. 2006, Comput. Geosci. 32, 283 (10.1016/j.cageo.2005.06.024) | GIS/DEM blockage assessment in mountains. | S | DEM | — | — | Partly |
| Propagation + blockage at high latitudes | Bech et al. 2007, QJRMS 133, 1191 (10.1002/qj.98) | Adds variable refraction to blockage modelling. | C | DEM, soundings | — | Nordic | Partly |
| Combined clutter + blockage correction | Fornasiero et al. 2006, NHESS 6, 697 (10.5194/nhess-6-697-2006) | Joint clutter and DEM-blockage correction. | C | DEM, DBZH | — | Italy | Partly |
| Polarimetric blockage correction | Giangrande & Ryzhkov 2005, JTECH 22, 1156 (10.1175/JTECH1766.1); Lang et al. 2009, JTECH 26, 943 (10.1175/2008JTECHA1133.1); Zhang et al. 2013, JTECH 30, 861 (10.1175/JTECH-D-12-00075.1) | Uses self-consistency or ΦDP (which blockage does not affect) to estimate and correct the Z loss empirically. | All | DBZH, ZDR, PHIDP | — | NEXRAD research | Yes |
| Specific attenuation A | Ryzhkov et al. 2014 (see 1.7) | Rain rate from A is immune to partial blockage. | S, C, X | PHIDP, DBZH | — | — | Yes |
| **[seed]** BBF as GPM-matching filter | Crisologo et al. 2018 (see 1.1) | — | — | — | wradlib | — | — |
| Orographic visibility and VPR (MeteoSwiss) | Germann et al. 2006, QJRMS 132, 1669 (10.1256/qj.05.190); Germann et al. 2022, Remote Sens. 14, 503 (10.3390/rs14030503) | Visibility maps, clutter elimination and VPR correction for radars in complex orography. The 2022 paper is the review. | C | DEM, moments | pyrad (visibility / GECSX) | MeteoSwiss | Partly |
| DL blockage correction | Tan et al. 2025, AIES 4 (10.1175/AIES-D-24-0111.1) | Deep learning infill of blocked sectors over complex terrain. | S | moments, DEM | — | Research | Partly |

### 2.11 Three-body scatter spike (TBSS) and other hail artefacts

| Method | Paper (DOI) | What it does | Bands | Inputs | Open source | Operational use | Archived moments? |
|---|---|---|---|---|---|---|---|
| TBSS theory | Zrnić 1987, Radio Sci. 22, 76 (10.1029/RS022i001p00076) | Explains the false low-Z echo downrange of hail cores, caused by hail–ground–hail multiple scattering. | All | — | — | — | — |
| TBSS as a hail signature | Lemon 1998, WAF 13, 327 (10.1175/1520-0434(1998)013<0327:TRTBSS>2.0.CO;2) | Operational recognition of TBSS. | S | DBZH, VRADH | — | NWS | Yes (heuristic) |
| ZDR in TBSS | Hubbert & Bringi 2000, JTECH 17, 51 (10.1175/1520-0426(2000)017<0051:TEOTBS>2.0.CO;2) | Explains the anomalous ZDR signatures inside the TBSS. | S | moments | — | — | Yes |
| Artefact catalogue | Kumjian 2013 (see 2.7) | Covers TBSS, NUBF and depolarisation streaks. | All | moments | — | — | Yes |

### 2.12 Operational combined QC systems

| System | Key papers (DOI) | Components | Bands | Open? |
|---|---|---|---|---|
| NOAA MRMS (US) | Lakshmanan et al. 2007 (10.1175/JAM2460.1); Lakshmanan et al. 2014, JTECH 31, 1234 (10.1175/JTECH-D-13-00073.1); Tang et al. 2014, WAF 29, 1106 (10.1175/WAF-D-13-00072.1); Zhang et al. 2016, BAMS 97, 621 (10.1175/BAMS-D-14-00174.1); **Tang et al. 2020, JTECH 37, 1521 (10.1175/JTECH-D-19-0165.1)** | Neural-network reflectivity QC (QCNN), then a physically based dual-pol + environmental (NWP) precip/non-precip classifier. Tang et al. 2020 updates it. | S | Algorithms published; code not open |
| OPERA / BALTRAD (EU) | Huuskonen et al. 2014; Saltikoff et al. 2019; Michelson et al. 2018 (10.5334/jors.193) | ropo (emitters, sun, ships, speckle), beamb (blockage), ODIM quality fields | mostly C | Yes ([github.com/baltrad](https://github.com/baltrad)) |
| RADVOL-QC (Poland) | Ośródka & Szturc 2022 (10.5194/amt-15-261-2022) | spikes, WTC, terrain, quality index | C | No |
| MeteoSwiss | Germann et al. 2006; Germann et al. 2022; Figueras i Ventura et al. 2020, JORS 8, 28 (10.5334/jors.330) | clutter, visibility, sun monitoring, ZDR/self-consistency, birds (`bird_density`) | C | Yes (pyrad + MeteoSwiss Py-ART fork) |
| DWD | Frech et al. 2017; Schaper et al. 2022; Frech et al. 2023; Frech et al. 2026; **Bölz et al. 2026** (DL QC) | birdbath calibration, RFI, radar–radar interference, WTC, DL non-met classification | C | No |
| Météo-France | Gourley et al. 2007; Gourley et al. 2009; Figueras i Ventura et al. 2012 | dual-pol fuzzy QC, self-consistency, long-term monitoring | C, S, X | No |
| Italian DPC | Vulpiani et al. 2012 **[seed]** | ΦDP processing, QC, blockage | C | Partly (wradlib re-implementation) |
| NCAR LROSE | Dixon et al. 2026, JORS (10.5334/jors.630) | CMD, HCA, Radx tools | All | Yes ([lrose-core](https://github.com/NCAR/lrose-core)) |
| Open toolkits | Heistermann et al. 2013 (10.5194/hess-17-863-2013) wradlib; Helmus & Collis 2016 (10.5334/jors.119) Py-ART | building blocks listed per row above | All | Yes |

### 2.13 Machine-learning / deep-learning QC

| Method | Paper (DOI) | What it does | Bands | Inputs | Open source | Archived moments? |
|---|---|---|---|---|---|---|
| NN AP detector | Grecu & Krajewski 2000 (see 2.3) | Early neural network for AP. | S | DBZH | — | Yes |
| QCNN | Lakshmanan et al. 2007 | Neural-network reflectivity QC (MRMS heritage). | S | DBZH, VRADH, WRADH | — | Yes |
| ML clutter (NBC/MLP/CNN + physics) | Li et al. 2023 (see 2.2) | Physics features + CNN. | S | moments | — | Yes |
| **CNN/U-Net trained on synthetic data (DWD)** | Bölz et al. 2026, AMT 19, 6781 (10.5194/amt-19-6781-2026) | Builds training samples by combining clean winter weather with cluttered summer data, then trains a CNN that beats DWD's operational classifier. Avoids hand-labelling. | C | dual-pol moments | not checked | Yes |
| Swin-U-Net vs MLP (Guangzhou) | Yang et al. 2026, EGUsphere preprint (10.5194/egusphere-2026-590), *under review* | Compares pointwise, spatial and temporal DL for non-precipitation echo identification. Finds that spatial context + polarimetry + time works best. | S | dual-pol moments, time sequence | — | Yes |
| MistNet **[seed]**, roost CNNs, bird/insect ML | Lin 2019; Chilson 2019; Jatau 2021 | Biology segmentation (see 2.4). | S (C) | moments | vol2bird | Yes |
| DL beam-blockage infill | Tan et al. 2025 (see 2.10) | — | S | moments, DEM | — | Yes |

**Not found / not verified:**
- **"dpQCNN"**: I found no paper by that name. MRMS dual-pol QC is described in Tang et al. 2014 and 2020, and the neural QC (QCNN) in Lakshmanan et al. 2007/2014.
- **"Pérez Hortal 2023"** (found 2026-11-10, Crossref-verified): Pérez Hortal, A. A., and D. B. Michelson, 2023: Using a continental-scale data quality monitoring framework to evaluate a new nonweather filter for radar observations. *J. Appl. Meteor. Climatol.*, 62(3), 411–425, doi:10.1175/JAMC-D-22-0014.1. ECCC nonweather filter (builds on Michelson et al. 2020), evaluated against METARs over the US and Canada. Candidate QC class next to MRMS dpQC.

---

## 3. Place-dependent problems and the methods that address them

| Place factor | Problem it creates | Where it matters (examples) | Methods (this file) | Archived-only feasible? |
|---|---|---|---|---|
| Mountains / complex terrain | Partial/total beam blockage, strong static clutter, VPR gaps, biased GPM matching | Alps, Apennines, Himalaya (Mukteshwar, Kufri, Surkanda Devi X-band), US West | Bech 2003 BBF, Krajewski 2006, Crisologo 2018, Zhang 2013 / Lang 2009 polarimetric blockage, Ryzhkov 2014 (A), Germann 2006/2022, Vulpiani 2012, Gabella filter, Tan 2025 | Yes (+DEM) |
| Coasts / sea | Sea clutter, frequent ducting/AP over water, ships | Indian east/west coasts (Chennai, Visakhapatnam, Mumbai), North Sea, Baltic | Collier 1998, Rico-Ramirez 2008, Moszkowicz 1994, ropo ship detector, Michelson & Sunhede 2004 | Yes (sounding/NWP helps) |
| Temperature inversions / ducting | AP clutter at night and in winter mornings | Indo-Gangetic Plain in winter (Delhi), deserts, sea | Bech 2007/2012, Bibraj (MAUSAM), Steiner & Smith 2002, dual-pol fuzzy (Gourley 2007) + NWP refractivity | Partly |
| Cities | RLAN/5 GHz Wi-Fi interference, building blockage, near-range clutter | Delhi C-band at Mausam Bhawan (dense city), European cities | Saltikoff 2016, ropo, Ośródka 2022, Schaper 2022, Rodríguez 2025, clutter maps / RCA | Yes |
| Neighbouring radars | Radar–radar interference | Dense networks (Germany; the three Delhi-area radars) | Frech 2023 | Yes |
| Monsoon / heavy rain | Wet radome (esp. X/C), attenuation that looks like calibration loss, TBSS in hail | India monsoon, tropics | Frasier 2013, Loh 2022, Hunzinger 2020, ΦDP-based methods, Ryzhkov 2014 | Yes |
| Dust / sand / haze | Low-ρhv non-met echoes, gust-front dust, AP in dry boundary layer | North India pre-monsoon (Delhi, Rajasthan), Middle East, US Southwest | Dempsey 2014, Singh 2021 (Delhi), Kilambi 2018-style texture, Gourley 2007 fuzzy, HCA non-met class | Yes (needs RHOHV) |
| Fires / smoke / crop burning | Smoke and debris plumes | Punjab/Haryana stubble burning (Oct–Nov, upwind of Delhi), US/Australia wildfires | Melnikov 2008/2009, Jones & Christopher 2010, Zrnić 2020 | Yes |
| Biological migration | Nocturnal bird/insect echoes contaminate summer-night QPE and VPR | Spring/autumn in Europe and the US; insects in tropical summer; locusts in NW India (2020) | vol2bird/bioRad, MistNet, Jatau 2021, Nussbaumer 2021, Kilambi 2018, Stepanian 2016 | Yes |
| Wind farms | Non-stationary WTC and blockage | Germany, North Sea coast, US plains, Indian wind-power states | Isom 2009, Hood 2010, Norin 2015, Frech 2026 | Yes (+turbine database) |
| Military areas | Chaff | Near air-force ranges | Zrnić & Ryzhkov 2004, HCA | Yes |
| High latitude / snow climate | Dry snow is common, so ZDR natural targets differ; sun at low elevation for much of the year | Nordic countries | Huuskonen 2016, Ferrone 2020, Ryzhkov 2005 dry snow | Yes |
| Warm climates with high freezing level | Little dry snow at accessible heights, so ZDR calibration relies on light rain, birdbath or Bragg | India, tropics | Ryzhkov 2005 light rain, Sanchez-Rivas 2022 QVP (rain part), Richardson 2017 Bragg (S band, e.g. Palam) | Yes |
| GPM coverage | GPM DPR covers roughly 65° S–65° N, with more frequent overpasses at mid-latitudes | All IMD and US radars covered; the northernmost sites are not | Warren 2018, Crisologo 2018 | Partly |

---

## 4. Ranked recommendation: what radar-wow should implement next in Stages 1–2

Selection criteria (in order):
1. Works on **archived moments only**.
2. **Band-agnostic** (S/C/X), using band constants as parameters.
3. Produces a **quantity later stages need**: calibrated Z/ZDR, a clean echo mask and a quality index.
4. Has an **open reference implementation** to validate against.
5. Matters for **Delhi/IMD and NEXRAD/OPERA** alike.

1. **`NoiseCorrectionCensoring` (Ryzhkov et al. 2005; Ryzhkov & Zrnić 2019; noise level via Py-ART `compute_noisedBZ` / HS74 on range profiles)**
   - Applies SNR-based censoring and noise correction to ZDR and ρhv.
   - Every ρhv- or ZDR-based QC and calibration step below is biased without it, and the bias is worst at long range and in X-band.
   - Uses SNRH when archived; otherwise derives SNR from DBZH, a noise level and range.
   - Cheap, all bands. Validate against Py-ART `correct_noise_rhohv`.

2. **`DualPolNonMetClassifier`: Kilambi et al. 2018 texture classifier, with a Gourley et al. 2007 / Dufton & Collier 2015 fuzzy-logic variant**
   - One class targets ground clutter, AP, sea clutter, biology, chaff, smoke/dust and second-trip residue, using DBZH, ZDR, RHOHV and PHIDP textures.
   - Membership functions are band-specific config.
   - Validate on the Delhi May–June 2018 cases (Singh et al. 2021).
   - Gives the largest QC benefit for the least code.

3. **`DEMBeamBlockage` (Bech et al. 2003), with refractivity as a parameter and the Crisologo et al. 2018 quality weight**
   - Outputs partial/cumulative blockage fields and a quality index.
   - Needed for the Himalayan X-band radars, for GPM matching (item 4) and for later compositing.
   - Reference: wradlib `beam_block_frac` / `cum_beam_block_frac`.
   - Add Zhang et al. 2013 (ΦDP-based blockage correction) later as a polarimetric refinement.

4. **`GPMVolumeMatchCalibration` (Warren et al. 2018 + Crisologo et al. 2018)**
   - Gives absolute Z offsets that are traceable and global, the same for S, C and X.
   - Indian studies (Saini et al. 2026; Jha et al. 2024) report substantial offsets, so this is a priority for Delhi.
   - References: wradlib GPM tutorial, `gpmmatch`.

5. **`ClutterRCA` (Silberstein et al. 2008 / Wolff et al. 2015, with the Hunzinger et al. 2020 eRCA options for X-band)**
   - Tracks daily relative calibration drift between GPM overpasses (the Louf et al. 2019 integrated scheme).
   - Needs only a dry-day clutter map built from the archive.
   - Caveat: weaker if the processor's clutter filter already removed most clutter. Detect this from the clutter-map statistics.

6. **`ZDROffsetNaturalTargets`: light rain and dry snow (Ryzhkov et al. 2005), with a QVP variant (Sanchez-Rivas & Rico-Ramirez 2022) and an optional birdbath input (Bechini et al. 2008; Frech et al. 2017)**
   - Small ZDR offsets cause large rain-rate errors, so this step is mandatory before polarimetric QPE.
   - Works from archived PPIs. Uses ML height from QVP or a sounding.
   - References: MeteoSwiss Py-ART `zdr_precip` / `zdr_snow`.

7. **`SunHitMonitor` (Huuskonen & Holleman 2007; Holleman et al. 2010a, b; Altube et al. 2015)**
   - Detects sun spikes in the volume data. This *removes* an interference artefact and also *produces* antenna pointing, receiver gain and receive-ZDR bias estimates.
   - Pair it with a ropo-style emitter/RLAN spike detector (Peura 2002; Ośródka & Szturc 2022) in the same class family.
   - Works only if far-range rays are not range-censored.
   - Reference: MeteoSwiss Py-ART `sun_hits`.

8. **`PhidpSystemOffset` + `SelfConsistencyZCheck` (Wang & Chandrasekar 2009 / Vulpiani et al. 2012 offset; Gourley et al. 2009 / Vivekanandan et al. 2003 Z check)**
   - Small and needed for KDP and attenuation correction in later stages.
   - The self-consistency check gives a third, independent Z calibration estimate to cross-check GPM and RCA.
   - The drop-shape assumption limits it to roughly 1 dB accuracy, so use it as a monitor rather than the primary calibration.

**Deferred (next round):**
- **Biology**: vol2bird/MistNet integration. Needed for nocturnal-migration contamination of VPR and of light-rain ZDR calibration.
- **WTC masks** from a turbine database (Norin 2015; Frech 2026).
- **DL non-met classifier** following Bölz et al. 2026. Its synthetic-training idea suits a multi-network project without labels. Build it after items 1–2, which can generate baseline labels.
- **Second-trip and TBSS** heuristics (Kumjian 2013; Hubbert & Bringi 2000).
- **I/Q-level methods** (GMAP, CMD-CPA, SZ, spectral polarimetric filters) are out of scope for archived data. Record which processor filter was applied (e.g. from ODIM `how` attributes) as metadata.

---

## 5. References (DOIs verified via Crossref on 2026-11-03)

### 5.1 Calibration
- Altube, P., Bech, J., Argemí, O., Rigo, T., et al., 2015. Quality control of antenna alignment and receiver calibration using the sun: adaptation to midrange weather radar observations. JTECH 32, 927–942. https://doi.org/10.1175/JTECH-D-14-00116.1
- Bechini, R., Baldini, L., Cremonini, R., Gorgucci, E., 2008. Differential reflectivity calibration for operational radars. JTECH 25, 1542–1555. https://doi.org/10.1175/2008JTECHA1037.1
- Ferrone, A., Berne, A., 2020. Dynamic differential reflectivity calibration using vertical profiles in rain and snow. Remote Sens. 13, 8. https://doi.org/10.3390/rs13010008
- Figueras i Ventura, J., Boumahmoud, A.-A., Fradon, B., Dupuy, P., et al., 2012. Long-term monitoring of French polarimetric radar data quality and evaluation of several polarimetric quantitative precipitation estimators in ideal conditions for operational implementation at C-band. QJRMS 138, 2212–2228. https://doi.org/10.1002/qj.1934
- Frasier, S. J., Kabeche, F., Figueras i Ventura, J., Al-Sakka, H., et al., 2013. In-place estimation of wet radome attenuation at X band. JTECH 30, 917–928. https://doi.org/10.1175/JTECH-D-12-00148.1
- Frech, M., Hagen, M., Mammen, T., 2017. Monitoring the absolute calibration of a polarimetric weather radar. JTECH 34, 599–615. https://doi.org/10.1175/JTECH-D-16-0076.1
- Gabella, M., Sartori, M., Boscacci, M., Germann, U., 2014. Vertical and horizontal polarization observations of slowly varying solar emissions from operational Swiss weather radars. Atmosphere 6, 50–59. https://doi.org/10.3390/atmos6010050
- Gabella, M., Boscacci, M., Sartori, M., Germann, U., 2016. Calibration accuracy of the dual-polarization receivers of the C-band Swiss weather radar network. Atmosphere 7, 76. https://doi.org/10.3390/atmos7060076
- Gabella, M., Huuskonen, A., Sartori, M., Holleman, I., et al., 2017. Evaluating the solar slowly varying component at C-band using dual- and single-polarization weather radars in Europe. Adv. Meteorol. 2017. https://doi.org/10.1155/2017/4971765
- Gergely, M., Schaper, M., Toussaint, M., Frech, M., 2022. Doppler spectra from DWD's operational C-band radar birdbath scan: sampling strategy, spectral postprocessing, and multimodal analysis. AMT 15, 7315–7335. https://doi.org/10.5194/amt-15-7315-2022
- Giangrande, S. E., McGraw, R., Lei, L., 2013. An application of linear programming to polarimetric radar differential phase processing. JTECH 30, 1716–1729. https://doi.org/10.1175/JTECH-D-12-00147.1
- Gorgucci, E., Scarchilli, G., Chandrasekar, V., 1992. Calibration of radars using polarimetric techniques. IEEE TGRS 30, 853–858. https://doi.org/10.1109/36.175319
- Gorgucci, E., Scarchilli, G., Chandrasekar, V., 1999. A procedure to calibrate multiparameter weather radar using properties of the rain medium. IEEE TGRS 37, 269–276. https://doi.org/10.1109/36.739161
- Gourley, J. J., Illingworth, A. J., Tabary, P., 2009. Absolute calibration of radar reflectivity using redundancy of the polarization observations and implied constraints on drop shapes. JTECH 26, 689–703. https://doi.org/10.1175/2008JTECHA1152.1
- Holleman, I., Huuskonen, A., Kurri, M., Beekhuis, H., 2010a. Operational monitoring of weather radar receiving chain using the sun. JTECH 27, 159–166. https://doi.org/10.1175/2009JTECHA1213.1
- Holleman, I., Huuskonen, A., Gill, R., Tabary, P., 2010b. Operational monitoring of radar differential reflectivity using the sun. JTECH 27, 881–887. https://doi.org/10.1175/2010JTECHA1381.1
- Hu, J., Zhang, P., Krause, J., Ryzhkov, A., et al., 2026. Calibrating differential reflectivity with QZdrCal: an Open System Radar Product Generator (ORPG) update. JTECH 43, 673–686. https://doi.org/10.1175/JTECH-D-25-0123.1
- Hubbert, J. C., Bringi, V. N., Brunkow, D., 2003. Studies of the polarimetric covariance matrix. Part I: Calibration methodology. JTECH 20, 696–706. https://doi.org/10.1175/1520-0426(2003)20<696:SOTPCM>2.0.CO;2
- Hunzinger, A., Hardin, J. C., Bharadwaj, N., Varble, A., et al., 2020. An extended radar relative calibration adjustment (eRCA) technique for higher-frequency radars and range–height indicator scans. AMT 13, 3147. https://doi.org/10.5194/amt-13-3147-2020
- Huuskonen, A., Holleman, I., 2007. Determining weather radar antenna pointing using signals detected from the sun at low antenna elevations. JTECH 24, 476–483. https://doi.org/10.1175/JTECH1978.1
- Huuskonen, A., Kurri, M., Holleman, I., 2016. Improved analysis of solar signals for differential reflectivity monitoring. AMT 9, 3183–3192. https://doi.org/10.5194/amt-9-3183-2016
- Huuskonen, A., Saltikoff, E., Holleman, I., 2014. The operational weather radar network in Europe. BAMS 95, 897–907. https://doi.org/10.1175/BAMS-D-12-00216.1
- Jha, A. K., Bhat, G. S., Kalapureddy, M. C. R., Pandithurai, G., 2024. Bias correction of an X-band radar reflectivity data to improve spatial rainfall estimation. J. Earth Syst. Sci. 133. https://doi.org/10.1007/s12040-024-02271-w
- Keem, M., Seo, B.-C., Krajewski, W. F., Morris, K. R., 2019. Inter-comparison of reflectivity measurements between GPM DPR and NEXRAD radars. Atmos. Res. 226, 49–65. https://doi.org/10.1016/j.atmosres.2019.04.010
- Loh, J. L., Chang, W.-Y., Hsu, H.-W., Lin, P.-F., et al., 2022. Long-term assessment of the reflectivity biases and wet-radome effect using collocated operational S- and C-band dual-polarization radars. IEEE TGRS 60. https://doi.org/10.1109/TGRS.2022.3170609
- Louf, V., Protat, A., Warren, R. A., Collis, S. M., et al., 2019. An integrated approach to weather radar calibration and monitoring using ground clutter and satellite comparisons. JTECH 36, 17–39. https://doi.org/10.1175/JTECH-D-18-0007.1
- Louf, V., Protat, A., 2023. Real-time monitoring of weather radar network calibration and antenna pointing. JTECH 40, 823–844. https://doi.org/10.1175/JTECH-D-22-0118.1
- Loulli, E., Michaelides, S., Bühl, J., Loukas, A., et al., 2025. Calibration of two X-band ground radars against GPM DPR Ku-band. Remote Sens. 17, 1712. https://doi.org/10.3390/rs17101712
- Richardson, L. M., Zittel, W. D., Lee, R. R., Melnikov, V. M., et al., 2017. Bragg scatter detection by the WSR-88D. Part II: Assessment of ZDR bias estimation. JTECH 34, 479–493. https://doi.org/10.1175/JTECH-D-16-0031.1
- Ryzhkov, A. V., Giangrande, S. E., Melnikov, V. M., Schuur, T. J., 2005. Calibration issues of dual-polarization radar measurements. JTECH 22, 1138–1155. https://doi.org/10.1175/JTECH1772.1 **[seed]**
- Ryzhkov, A., Diederich, M., Zhang, P., Simmer, C., 2014. Potential utilization of specific attenuation for rainfall estimation, mitigation of partial beam blockage, and radar networking. JTECH 31, 599–619. https://doi.org/10.1175/JTECH-D-13-00038.1
- Ryzhkov, A., Zhang, P., Reeves, H., Kumjian, M., et al., 2016. Quasi-vertical profiles: a new way to look at polarimetric radar data. JTECH 33, 551–562. https://doi.org/10.1175/JTECH-D-15-0020.1
- Ryzhkov, A. V., Zrnić, D. S., 2019. Radar Polarimetry for Weather Observations. Springer Atmospheric Sciences. https://doi.org/10.1007/978-3-030-05093-1
- Saini, S., Das, S. K., Jha, A. K., Kolte, Y. K., et al., 2026. Calibration bias evaluation and correction of S-band ground-based radar reflectivity using Ku-band space-borne radar observations along the east coast of India. Radio Sci. 61. https://doi.org/10.1029/2025RS008484
- Saltikoff, E., Haase, G., Delobbe, L., Gaussiat, N., et al., 2019. OPERA the radar project. Atmosphere 10, 320. https://doi.org/10.3390/atmos10060320
- Sanchez-Rivas, D., Rico-Ramirez, M. A., 2022. Calibration of radar differential reflectivity using quasi-vertical profiles. AMT 15, 503–520. https://doi.org/10.5194/amt-15-503-2022
- Schwaller, M. R., Morris, K. R., 2011. A ground validation network for the Global Precipitation Measurement mission. JTECH 28, 301–319. https://doi.org/10.1175/2010JTECHA1403.1
- Silberstein, D. S., Wolff, D. B., Marks, D. A., Atlas, D., et al., 2008. Ground clutter as a monitor of radar stability at Kwajalein, RMI. JTECH 25, 2037–2045. https://doi.org/10.1175/2008JTECHA1063.1
- Vaccarono, M., Bechini, R., Chandrasekar, C. V., Cremonini, R., et al., 2016. An integrated approach to monitoring the calibration stability of operational dual-polarization radars. AMT 9, 5367–5383. https://doi.org/10.5194/amt-9-5367-2016
- Vivekanandan, J., Zhang, G., Ellis, S. M., Rajopadhyaya, D., et al., 2003. Radar reflectivity calibration using differential propagation phase measurement. Radio Sci. 38. https://doi.org/10.1029/2002RS002676
- Vulpiani, G., Montopoli, M., Passeri, L. D., Gioia, A. G., et al., 2012. On the use of dual-polarized C-band radar for operational rainfall retrieval in mountainous areas. JAMC 51, 405–425. https://doi.org/10.1175/JAMC-D-10-05024.1 **[seed]**
- Wang, Y., Chandrasekar, V., 2009. Algorithm for estimation of the specific differential phase. JTECH 26, 2565–2578. https://doi.org/10.1175/2009JTECHA1358.1
- Warren, R. A., Protat, A., Siems, S. T., Ramsay, H. A., et al., 2018. Calibrating ground-based radars against TRMM and GPM. JTECH 35, 323–346. https://doi.org/10.1175/JTECH-D-17-0128.1 **[seed]**
- Wolff, D. B., Marks, D. A., Petersen, W. A., 2015. General application of the relative calibration adjustment (RCA) technique for monitoring and correcting radar reflectivity calibration. JTECH 32, 496–506. https://doi.org/10.1175/JTECH-D-13-00185.1
- Zrnić, D. S., Melnikov, V. M., Carter, J. K., 2006. Calibrating differential reflectivity on the WSR-88D. JTECH 23, 944–951. https://doi.org/10.1175/JTECH1893.1
- Zrnić, D. S., Doviak, R. J., Zhang, G., Ryzhkov, A., 2010. Bias in differential reflectivity due to cross coupling through the radiation patterns of polarimetric weather radars. JTECH 27, 1624–1637. https://doi.org/10.1175/2010JTECHA1350.1

### 5.2 Quality control
- Alku, L., Moisseev, D., Aittomäki, T., Chandrasekar, V., 2015. Identification and suppression of nonmeteorological echoes using spectral polarimetric processing. IEEE TGRS 53, 3628–3638. https://doi.org/10.1109/TGRS.2014.2380476
- Bech, J., Codina, B., Lorente, J., Bebbington, D., 2003. The sensitivity of single polarization weather radar beam blockage correction to variability in the vertical refractivity gradient. JTECH 20, 845–855. https://doi.org/10.1175/1520-0426(2003)020<0845:TSOSPW>2.0.CO;2
- Bech, J., Gjertsen, U., Haase, G., 2007. Modelling weather radar beam propagation and topographical blockage at northern high latitudes. QJRMS 133, 1191–1204. https://doi.org/10.1002/qj.98
- Bech, J., Magaldi, A., Codina, B., Lorente, J., 2012. Effects of anomalous propagation conditions on weather radar observations. In: Doppler Radar Observations, InTech. https://doi.org/10.5772/38172
- Berenguer, M., Sempere-Torres, D., Corral, C., Sánchez-Diezma, R., 2006. A fuzzy logic technique for identifying nonprecipitating echoes in radar scans. JTECH 23, 1157–1180. https://doi.org/10.1175/JTECH1914.1
- Bibraj, R., Arul Malar, B., Ramachandra Rao, K., Sai Krishnan, K. C. An analysis of anomalous propagation parameters and its effect on the intensity of clutter in weather radars. MAUSAM 71(1), 11–20 (Crossref issue date 2021). https://doi.org/10.54302/mausam.v71i1.2
- Bölz, R., Kirstein, T., Fuchs, L., Josipović, L., et al., 2026. Enhancing weather radar data by removing non-meteorological echoes, using neural networks trained on synthetic weather data. AMT 19, 6781–6803. https://doi.org/10.5194/amt-19-6781-2026
- Cheng, Z., Gabriel, S., Bhambhani, P., Sheldon, D., et al., 2020. Detecting and tracking communal bird roosts in weather radar data. Proc. AAAI 34. https://doi.org/10.1609/aaai.v34i01.5373
- Chilson, C., Avery, K., McGovern, A., Bridge, E., et al., 2019 (online 2018). Automated detection of bird roosts using NEXRAD radar data and convolutional neural networks. Remote Sens. Ecol. Conserv. 5, 20–32. https://doi.org/10.1002/rse2.92
- Collier, C. G., 1998. Observations of sea clutter using an S-band weather radar. Meteorol. Appl. 5, 263–270. https://doi.org/10.1017/S1350482798000930
- Dempsey, M., 2014. Forecasting strategies for haboobs: an underreported weather phenomenon. Adv. Meteorol. 2014. https://doi.org/10.1155/2014/904759
- Dixon, M., DeHart, B., Javornik, B., Cha, T.-Y., et al., 2026. The Lidar Radar Open Software Environment (LROSE): an end-to-end suite of applications for radar and lidar processing. JORS. https://doi.org/10.5334/jors.630
- Dokter, A. M., Liechti, F., Stark, H., Delobbe, L., et al., 2011 (online 2010). Bird migration flight altitudes studied by a network of operational weather radars. J. R. Soc. Interface 8, 30–43. https://doi.org/10.1098/rsif.2010.0116
- Dokter, A. M., Desmet, P., Spaaks, J. H., van Hoey, S., et al., 2019 (online 2018). bioRad: biological analysis and visualization of weather radar data. Ecography 42, 852–860. https://doi.org/10.1111/ecog.04028
- Dufton, D. R. L., Collier, C. G., 2015. Fuzzy logic filtering of radar reflectivity to remove non-meteorological echoes using dual polarization radar moments. AMT 8, 3985–4000. https://doi.org/10.5194/amt-8-3985-2015
- Figueras i Ventura, J., Lainer, M., Schauwecker, Z., Grazioli, J., et al., 2020. Pyrad: a real-time weather radar data processing framework based on Py-ART. JORS 8, 28. https://doi.org/10.5334/jors.330
- Fornasiero, A., Bech, J., Alberoni, P. P., 2006. Enhanced radar precipitation estimates using a combined clutter and beam blockage correction technique. NHESS 6, 697. https://doi.org/10.5194/nhess-6-697-2006
- Frech, M., Hald, C., Schaper, M., Lange, B., et al., 2023. Assessing and mitigating the radar–radar interference in the German C-band weather radar network. AMT 16, 295–309. https://doi.org/10.5194/amt-16-295-2023
- Frech, M., Boehm, A. M., Tracksdorf, P., 2026. Monitoring and quantifying wind turbine clutter in DWD weather radar measurements. AMT 19, 1711–1727. https://doi.org/10.5194/amt-19-1711-2026
- Friedrich, K., Germann, U., Tabary, P., 2009. Influence of ground clutter contamination on polarimetric radar parameters. JTECH 26, 251. https://doi.org/10.1175/2008JTECHA1092.1
- Germann, U., Galli, G., Boscacci, M., Bolliger, M., 2006. Radar precipitation measurement in a mountainous region. QJRMS 132, 1669–1692. https://doi.org/10.1256/qj.05.190
- Germann, U., Boscacci, M., Clementi, L., Gabella, M., et al., 2022. Weather radar in complex orography. Remote Sens. 14, 503. https://doi.org/10.3390/rs14030503
- Giangrande, S. E., Ryzhkov, A. V., 2005. Calibration of dual-polarization radar in the presence of partial beam blockage. JTECH 22, 1156–1166. https://doi.org/10.1175/JTECH1766.1
- Golbon-Haghighi, M.-H., Zhang, G., Li, Y., Doviak, R. J., 2016. Detection of ground clutter from weather radar using a dual-polarization and dual-scan method. Atmosphere 7, 83. https://doi.org/10.3390/atmos7060083
- Golbon-Haghighi, M.-H., Zhang, G., 2019. Detection of ground clutter for dual-polarization weather radar using a novel 3D discriminant function. JTECH 36, 1285–1296. https://doi.org/10.1175/JTECH-D-18-0147.1
- Gourley, J. J., Tabary, P., Parent du Chatelet, J., 2007. A fuzzy logic algorithm for the separation of precipitating from nonprecipitating echoes using polarimetric radar observations. JTECH 24, 1439–1451. https://doi.org/10.1175/JTECH2035.1
- Grecu, M., Krajewski, W. F., 2000. An efficient methodology for detection of anomalous propagation echoes in radar reflectivity data using neural networks. JTECH 17, 121–129. https://doi.org/10.1175/1520-0426(2000)017<0121:AEMFDO>2.0.CO;2
- Heistermann, M., Jacobi, S., Pfaff, T., 2013. Technical note: an open source library for processing weather radar data (wradlib). HESS 17, 863–871. https://doi.org/10.5194/hess-17-863-2013
- Helmus, J. J., Collis, S. M., 2016. The Python ARM Radar Toolkit (Py-ART), a library for working with weather radar data in the Python programming language. JORS 4, 25. https://doi.org/10.5334/jors.119
- Hildebrand, P. H., Sekhon, R. S., 1974. Objective determination of the noise level in Doppler spectra. JAM 13, 808–811. https://doi.org/10.1175/1520-0450(1974)013<0808:ODOTNL>2.0.CO;2
- Hood, K., Torres, S., Palmer, R., 2010. Automatic detection of wind turbine clutter for weather radars. JTECH 27, 1868–1880. https://doi.org/10.1175/2010JTECHA1437.1
- Hubbert, J. C., Bringi, V. N., 2000. The effects of three-body scattering on differential reflectivity signatures. JTECH 17, 51–61. https://doi.org/10.1175/1520-0426(2000)017<0051:TEOTBS>2.0.CO;2
- Hubbert, J. C., Dixon, M., Ellis, S. M., Meymaris, G., 2009a. Weather radar ground clutter. Part I: Identification, modeling, and simulation. JTECH 26, 1165–1180. https://doi.org/10.1175/2009JTECHA1159.1
- Hubbert, J. C., Dixon, M., Ellis, S. M., 2009b. Weather radar ground clutter. Part II: Real-time identification and filtering. JTECH 26, 1181–1197. https://doi.org/10.1175/2009JTECHA1160.1 **[seed]**
- Isom, B. M., Palmer, R. D., Secrest, G. S., Rhoton, R. D., et al., 2009. Detailed observations of wind turbine clutter with scanning weather radars. JTECH 26, 894–910. https://doi.org/10.1175/2008JTECHA1136.1
- Islam, T., Rico-Ramirez, M. A., Han, D., Srivastava, P. K., 2012. Artificial intelligence techniques for clutter identification with polarimetric radar signatures. Atmos. Res. 109–110, 95–113. https://doi.org/10.1016/j.atmosres.2012.02.007
- Ivić, I. R., Zrnić, D. S., Yu, T.-Y., 2009. The use of coherency to improve signal detection in dual-polarization weather radars. JTECH 26, 2474–2487. https://doi.org/10.1175/2009JTECHA1154.1
- Ivić, I. R., 2014. On the use of a radial-based noise power estimation technique to improve estimates of the correlation coefficient on dual-polarization weather radars. JTECH 31, 1867–1880. https://doi.org/10.1175/JTECH-D-14-00052.1
- Jatau, P., Melnikov, V., Yu, T.-Y., 2021. A machine learning approach for classifying bird and insect radar echoes with S-band polarimetric weather radar. JTECH. https://doi.org/10.1175/JTECH-D-20-0180.1
- Jones, T. A., Christopher, S. A., 2010. Satellite and radar observations of the 9 April 2009 Texas and Oklahoma grassfires. BAMS 91, 455. https://doi.org/10.1175/2009BAMS2919.1
- Kilambi, A., Fabry, F., Meunier, V., 2018. A simple and effective method for separating meteorological from nonmeteorological targets using dual-polarization data. JTECH 35, 1415–1424. https://doi.org/10.1175/JTECH-D-17-0175.1
- Krajewski, W. F., Ntelekos, A. A., Goska, R., 2006. A GIS-based methodology for the assessment of weather radar beam blockage in mountainous regions: two examples from the US NEXRAD network. Comput. Geosci. 32, 283–302. https://doi.org/10.1016/j.cageo.2005.06.024
- Kumjian, M. R., 2013. Principles and applications of dual-polarization weather radar. Part III: Artifacts. J. Oper. Meteor. 1, 265–274. https://doi.org/10.15191/nwajom.2013.0121
- Lakshmanan, V., Fritz, A., Smith, T., Hondl, K., et al., 2007. An automated technique to quality control radar reflectivity data. JAMC 46, 288–305. https://doi.org/10.1175/JAM2460.1
- Lakshmanan, V., Karstens, C., Krause, J., Tang, L., 2014. Quality control of weather radar data using polarimetric variables. JTECH 31, 1234–1249. https://doi.org/10.1175/JTECH-D-13-00073.1
- Lang, T. J., Nesbitt, S. W., Carey, L. D., 2009. On the correction of partial beam blockage in polarimetric radar data. JTECH 26, 943–957. https://doi.org/10.1175/2008JTECHA1133.1
- Lemon, L. R., 1998. The radar "three-body scatter spike": an operational large-hail signature. WAF 13, 327–340. https://doi.org/10.1175/1520-0434(1998)013<0327:TRTBSS>2.0.CO;2
- Li, Z., Zhang, G., Wu, Y., 2023. Detection and mitigation of ground clutter in polarimetric phased array radar measurements using machine learning and physics-based discriminants. IEEE TGRS 61. https://doi.org/10.1109/TGRS.2023.3323836
- Lin, T.-Y., Winner, K., Bernstein, G., Mittal, A., et al., 2019. MistNet: measuring historical bird migration in the US using archived weather radar data and convolutional neural networks. Methods Ecol. Evol. 10, 1908–1922. https://doi.org/10.1111/2041-210X.13280 **[seed]**
- Martin, W. J., Shapiro, A., 2007. Discrimination of bird and insect radar echoes in clear air using high-resolution radars. JTECH 24, 1215. https://doi.org/10.1175/JTECH2038.1
- Melnikov, V. M., Zrnić, D. S., Rabin, R. M., Zhang, P., 2008. Radar polarimetric signatures of fire plumes in Oklahoma. GRL 35. https://doi.org/10.1029/2008GL034311
- Melnikov, V. M., Zrnić, D. S., Rabin, R. M., 2009. Polarimetric radar properties of smoke plumes: a model. JGR Atmos. 114. https://doi.org/10.1029/2009JD012647
- Melnikov, V., Leskinen, M., Koistinen, J., 2014. Doppler velocities at orthogonal polarizations in radar echoes from insects and birds. IEEE GRSL 11, 592–596. https://doi.org/10.1109/LGRS.2013.2272011
- Michelson, D. B., Sunhede, D., 2004. Spurious weather radar echo identification and removal using multisource temperature information. Meteorol. Appl. 11, 1–14. https://doi.org/10.1017/S1350482703001129
- Michelson, D., Henja, A., Ernes, S., Haase, G., et al., 2018. BALTRAD advanced weather radar networking. JORS 6, 12. https://doi.org/10.5334/jors.193
- Moisseev, D. N., Chandrasekar, V., 2009. Polarimetric spectral filter for adaptive clutter and noise suppression. JTECH 26, 215–228. https://doi.org/10.1175/2008JTECHA1119.1
- Moszkowicz, S., Ciach, G. J., Krajewski, W. F., 1994. Statistical detection of anomalous propagation in radar reflectivity patterns. JTECH 11, 1026–1034. https://doi.org/10.1175/1520-0426(1994)011<1026:SDOAPI>2.0.CO;2
- Norin, L., 2015. A quantitative analysis of the impact of wind turbines on operational Doppler weather radar data. AMT 8, 593–609. https://doi.org/10.5194/amt-8-593-2015
- Nussbaumer, R., Schmid, B., Bauer, S., Liechti, F., 2021. A Gaussian mixture model to separate birds and insects in single-polarization weather radar data. Remote Sens. 13, 1989. https://doi.org/10.3390/rs13101989
- Ośródka, K., Szturc, J., 2022. Improvement in algorithms for quality control of weather radar data (RADVOL-QC system). AMT 15, 261–277. https://doi.org/10.5194/amt-15-261-2022
- Park, H. S., Ryzhkov, A. V., Zrnić, D. S., Kim, K.-E., 2009. The hydrometeor classification algorithm for the polarimetric WSR-88D: description and application to an MCS. WAF 24, 730–748. https://doi.org/10.1175/2008WAF2222205.1
- Rennie, S. J., Illingworth, A. J., Dance, S. L., 2010. On differentiating ground clutter and insect echoes from Doppler weather radars using archived data. AMT Discuss. 3, 1843. https://doi.org/10.5194/amtd-3-1843-2010 (discussion paper)
- Rico-Ramirez, M. A., Cluckie, I. D., 2008. Classification of ground clutter and anomalous propagation using dual-polarization weather radar. IEEE TGRS 46, 1892. https://doi.org/10.1109/TGRS.2008.916979
- Rodríguez, A. M., Cogo, J., Pascual, J. P., 2025. Strategy for WiFi interference detection in weather radar applications. Radio Sci. 60. https://doi.org/10.1029/2025RS008232
- Sachidananda, M., Zrnić, D. S., 1999. Systematic phase codes for resolving range overlaid signals in a Doppler weather radar. JTECH 16, 1351–1363. https://doi.org/10.1175/1520-0426(1999)016<1351:SPCFRR>2.0.CO;2
- Saltikoff, E., Cho, J. Y. N., Tristant, P., Huuskonen, A., et al., 2016. The threat to weather radars by wireless technology. BAMS 97, 1159–1167. https://doi.org/10.1175/BAMS-D-15-00048.1 **[seed]**
- Schaper, M., Frech, M., Michaelis, D., Hald, C., et al., 2022. Radio frequency interference detection and mitigation in the DWD C-band weather radar network. AMT 15, 6625–6642. https://doi.org/10.5194/amt-15-6625-2022
- Shamoun-Baranes, J., Nilsson, C., Bauer, S., Chapman, J., 2019. Taking radar aeroecology into the 21st century. Ecography 42, 847–851. https://doi.org/10.1111/ecog.04582
- Singh, D. K., Yadav, R., Sai Krishnan, K. C., Rawat, N., 2021. Analysis of three unusual severe weather events over Delhi during May–June, 2018 using dual-pol Doppler weather radar and GNSS data. MAUSAM 72, 719–738. https://doi.org/10.54302/mausam.v72i4.3543
- Stepanian, P. M., Horton, K. G., Melnikov, V. M., Zrnić, D. S., et al., 2016. Dual-polarization radar products for biological applications. Ecosphere 7. https://doi.org/10.1002/ecs2.1539
- Steiner, M., Smith, J. A., 2002. Use of three-dimensional reflectivity structure for automated detection and removal of nonprecipitating echoes in radar data. JTECH 19, 673–686. https://doi.org/10.1175/1520-0426(2002)019<0673:UOTDRS>2.0.CO;2
- Tan, S., Chen, H., Lee, W.-C., 2025. Deep learning for weather radar beam blockage correction: potential impacts on QPE over complex terrain in northern California. AIES 4. https://doi.org/10.1175/AIES-D-24-0111.1
- Tang, L., Zhang, J., Langston, C., Krause, J., et al., 2014. A physically based precipitation–nonprecipitation radar echo classifier using polarimetric and environmental data in a real-time national system. WAF 29, 1106–1119. https://doi.org/10.1175/WAF-D-13-00072.1
- Tang, L., Zhang, J., Simpson, M., Arthur, A., et al., 2020. Updates on the radar data quality control in the MRMS quantitative precipitation estimation system. JTECH 37, 1521–1537. https://doi.org/10.1175/JTECH-D-19-0165.1
- Torres, S. M., Warde, D. A., 2014. Ground clutter mitigation for weather radars using the autocorrelation spectral density. JTECH 31, 2049–2066. https://doi.org/10.1175/JTECH-D-13-00117.1
- Yang, R., Wei, C., Pan, X., Zhao, K., et al., 2026. Deep learning for non-precipitation radar echo identification: comparative evaluation of polarimetric, spatial, and temporal information. EGUsphere preprint (under review). https://doi.org/10.5194/egusphere-2026-590
- Zhang, P., Zrnić, D., Ryzhkov, A., 2013. Partial beam blockage correction using polarimetric radar measurements. JTECH 30, 861–872. https://doi.org/10.1175/JTECH-D-12-00075.1
- Zhang, J., Howard, K., Langston, C., Kaney, B., et al., 2016. Multi-Radar Multi-Sensor (MRMS) quantitative precipitation estimation: initial operating capabilities. BAMS 97, 621–638. https://doi.org/10.1175/BAMS-D-14-00174.1
- Zhang, S., Huang, X., Min, J., Chu, Z., et al., 2020. Improved fuzzy logic method to distinguish between meteorological and non-meteorological echoes using C-band polarimetric radar data. AMT 13, 537–551. https://doi.org/10.5194/amt-13-537-2020
- Zrnić, D. S., 1987. Three-body scattering produces precipitation signature of special diagnostic value. Radio Sci. 22, 76–86. https://doi.org/10.1029/RS022i001p00076
- Zrnić, D. S., Ryzhkov, A. V., 1998. Observations of insects and birds with a polarimetric radar. IEEE TGRS 36, 661–668. https://doi.org/10.1109/36.662746
- Zrnić, D. S., Ryzhkov, A. V., 2004. Polarimetric properties of chaff. JTECH 21, 1017–1024. https://doi.org/10.1175/1520-0426(2004)021<1017:PPOC>2.0.CO;2
- Zrnić, D., Zhang, P., Melnikov, V., Mirkovic, D., 2020. Of fire and smoke plumes, polarimetric radar characteristics. Atmosphere 11, 363. https://doi.org/10.3390/atmos11040363

### 5.3 Items without DOI, or not found
- Siggia, A., Passarelli, R., 2004. Gaussian model adaptive processing (GMAP) for improved ground clutter cancellation and moment calculation. Proc. ERAD 2004. *No DOI.* https://www.copernicus.org/erad/2004/online/ERAD04_P_67.pdf
- Gabella, M., Notarpietro, R., 2002. Ground clutter characterization and elimination in mountainous terrain. Proc. ERAD 2002. *No DOI.* https://www.copernicus.org/erad/online/erad-305.pdf
- Peura, M., 2002. Computer vision methods for anomaly removal. Proc. ERAD 2002. *No DOI.* https://www.copernicus.org/erad/online/erad-312.pdf
- **Resolved 2026-11-10:** "dpQCNN" = Lakshmanan et al. 2014 dual-pol QCNN (10.1175/JTECH-D-13-00073.1; the name itself is not used in the literature). "Pérez Hortal 2023" = Pérez Hortal, A. A., and D. B. Michelson, 2023: Using a continental-scale data quality monitoring framework to evaluate a new nonweather filter for radar observations. *J. Appl. Meteor. Climatol.*, 62(3), 411–425, doi:10.1175/JAMC-D-22-0014.1.
- **DOI unverified:** the 2020 study of locust echoes on the Delhi and Lucknow radars (seen in search results, no DOI confirmed).

Software referenced:
- [Py-ART](https://github.com/ARM-DOE/pyart): `correct_noise_rhohv`, `correct_bias`, `calc_zdr_offset`, `compute_noisedBZ`, `estimate_noise_hs74`, `despeckle_field`, `phase_proc_lp`. All confirmed present in the current source.
- [MeteoSwiss Py-ART fork](https://github.com/MeteoSwiss/pyart): `sun_hits`, `sun_retrieval`, `selfconsistency_bias`, `zdr_precip`, `zdr_snow`, `est_rhohv_rain`, `bird_density`, `visibility`. All confirmed present.
- [pyrad](https://github.com/MeteoSwiss/pyrad)
- [wradlib](https://github.com/wradlib/wradlib): `filter_gabella`, `histo_cut`, `classify_echo_fuzzy`, `beam_block_frac`, `cum_beam_block_frac`, `estimate_snr`. All confirmed present.
- BALTRAD [bropo](https://github.com/baltrad/bropo) and [beamb](https://github.com/baltrad/beamb)
- [vol2bird](https://github.com/adokter/vol2bird) and [bioRad](https://github.com/adokter/bioRad)
- [wsrlib](https://github.com/darkecology/wsrlib)
- [gpmmatch](https://github.com/vlouf/gpmmatch)
- [LROSE](https://github.com/NCAR/lrose-core)
- [xradar](https://github.com/openradar/xradar)
