# radar-wow

A generalised radar quantitative precipitation estimation (QPE) system for S, C and X band radars, built from one repo per processing stage. Each repo implements published algorithms (one class per paper) and an executed notebook that runs them on free data from NEXRAD, ARM and IMD.

| stage | repo | what | implemented |
|---|---|---|---|
| - | [radarwow-core](https://github.com/manmeet3591/radarwow-core) | Core | 4/4 |
| 1 | [radarwow-calibration](https://github.com/manmeet3591/radarwow-calibration) | Calibration | 3/5 |
| 2 | [radarwow-qc](https://github.com/manmeet3591/radarwow-qc) | Quality control | 5/7 |
| 3 | [radarwow-kdp](https://github.com/manmeet3591/radarwow-kdp) | PHIDP processing and KDP | 4/4 |
| 4 | [radarwow-attenuation](https://github.com/manmeet3591/radarwow-attenuation) | Attenuation correction | 4/6 |
| 5 | [radarwow-classification](https://github.com/manmeet3591/radarwow-classification) | Hydrometeor classification and melting layer | 3/7 |
| 6 | [radarwow-estimation](https://github.com/manmeet3591/radarwow-estimation) | Rain-rate estimators, VPR, blockage, hybrid scan | 11/12 |
| 7 | [radarwow-merging](https://github.com/manmeet3591/radarwow-merging) | Gauge merging and uncertainty | 3/5 |
| 8 | [radarwow-mosaic](https://github.com/manmeet3591/radarwow-mosaic) | Compositing, mosaics and accumulation | 2/5 |
| 9 | [radarwow-ml](https://github.com/manmeet3591/radarwow-ml) | Machine-learning QPE | 0/8 |
| - | [radarwow-verify](https://github.com/manmeet3591/radarwow-verify) | Verification | 9/10 |
| 10 | [radarwow-pipeline](https://github.com/manmeet3591/radarwow-pipeline) | End-to-end pipeline | 1/5 |

Different radars bring different problems (code values, stored noise, reversed PHIDP sign, mislabelled fields, missing moments). `radarwow.core.diagnose` measures them on any file before the algorithms run.
