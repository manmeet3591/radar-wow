# radar-wow

A generalised radar quantitative precipitation estimation (QPE) system for S, C and X band radars, built from one repo per processing stage. Each repo implements published algorithms (one class per paper) and an executed notebook that runs them on free data from NEXRAD, ARM and IMD.

| stage | repo | what | implemented |
|---|---|---|---|
| - | [radarwow-core](https://github.com/radar-wow/radarwow-core) | Core | 4/4 |
| 1 | [radarwow-calibration](https://github.com/radar-wow/radarwow-calibration) | Calibration | 0/4 |
| 2 | [radarwow-qc](https://github.com/radar-wow/radarwow-qc) | Quality control | 5/7 |
| 3 | [radarwow-kdp](https://github.com/radar-wow/radarwow-kdp) | PHIDP processing and KDP | 4/4 |
| 4 | [radarwow-attenuation](https://github.com/radar-wow/radarwow-attenuation) | Attenuation correction | 0/3 |
| 5 | [radarwow-classification](https://github.com/radar-wow/radarwow-classification) | Hydrometeor classification and melting layer | 0/4 |
| 6 | [radarwow-estimation](https://github.com/radar-wow/radarwow-estimation) | Rain-rate estimators, VPR, blockage, hybrid scan | 0/4 |
| 7 | [radarwow-merging](https://github.com/radar-wow/radarwow-merging) | Gauge merging and uncertainty | 0/3 |
| 8 | [radarwow-mosaic](https://github.com/radar-wow/radarwow-mosaic) | Compositing, mosaics and accumulation | 0/4 |
| 9 | [radarwow-ml](https://github.com/radar-wow/radarwow-ml) | Machine-learning QPE | 0/7 |
| - | [radarwow-verify](https://github.com/radar-wow/radarwow-verify) | Verification | 0/2 |
| 10 | [radarwow-pipeline](https://github.com/radar-wow/radarwow-pipeline) | End-to-end pipeline | 0/4 |

Different radars bring different problems (code values, stored noise, reversed PHIDP sign, mislabelled fields, missing moments). `radarwow.core.diagnose` measures them on any file before the algorithms run.
