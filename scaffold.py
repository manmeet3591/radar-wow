"""Generate the radar-wow repos' boilerplate (README, pyproject, LICENSE, .gitignore, package stubs).

Implemented repos (core, qc, kdp) keep their code; only README/LICENSE/.gitignore are (re)written.
Every paper listed here is in the radar_wow literature review (papers.json); "talk" = cited in the
original talk; "to review" = candidate not yet read.
"""

from pathlib import Path

ROOT = Path(__file__).parent
ORG = "manmeet3591"  # GitHub account the repos are published under
YEAR = 2026

LICENSE = f"""MIT License

Copyright (c) {YEAR} Manmeet Singh and radar-wow contributors

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

GITIGNORE = """__pycache__/
*.egg-info/
.pytest_cache/
.ipynb_checkpoints/
.venv/
build/
dist/
*.nc
*.h5
*.gz
*.pptx
*.pdf
"""

# repo -> (stage number(s), title, description, [(sub-component, algorithm, paper, doi, status)], extra notes)
DONE, PLAN, REVIEW, STUB = "implemented + notebook", "planned", "to review", "stub"
STAGES = {
    "core": ("-", "Core", "shared I/O (NEXRAD, ODIM, CfRadial, IRIS, IMD FSL), canonical moment names, band configs (S/C/X), algorithm interface, free sample data, health checks", [
        ("I/O + names", "`open_volume`, `standardize`", "xradar DataTree; CF metadata before variable names", "", DONE),
        ("band configs", "`load_band('S'|'C'|'X')`", "every parameter cites its source", "", DONE),
        ("free data", "`load_sample`, `nexrad_aws`", "open-radar-data + NEXRAD on AWS", "", DONE),
        ("health checks", "`diagnose`", "measures each radar's problems, names the stage that fixes them", "", DONE),
    ], "notebooks/00_free_data_and_health_checks.ipynb"),
    "calibration": ("1", "Calibration", "absolute Z calibration and ZDR bias", [
        ("Z: spaceborne radar matching", "`Warren2018GPMMatch`", "Warren et al. 2018, JTECH", "10.1175/JTECH-D-17-0128.1", PLAN),
        ("Z: relative calibration adjustment + GPM", "`Crisologo2018`", "Crisologo et al. 2018, AMT", "10.5194/amt-11-5223-2018", PLAN),
        ("ZDR: light rain / dry snow / vertical pointing", "`Ryzhkov2005ZDR`", "Ryzhkov et al. 2005, JTECH", "10.1175/JTECH1772.1", PLAN),
        ("Z: self-consistency Z-ZDR-KDP", "`SelfConsistencyZ`", "Ryzhkov et al. 2005, JTECH", "10.1175/JTECH1772.1", PLAN),
    ], ""),
    "qc": ("2", "Quality control", "noise, ground clutter, biological echo, interference, speckle", [
        ("noise", "`SignalMask`", "SNR/SQI, else measured noise floor", "", DONE),
        ("ground clutter", "`Hubbert2009CMD`", "Hubbert, Dixon & Ellis 2009, JTECH", "10.1175/2009JTECHA1160.1", DONE),
        ("non-meteorological echo", "`Vulpiani2012QualityMap`", "Vulpiani et al. 2012, JAMC", "10.1175/JAMC-D-10-05024.1", DONE),
        ("RLAN / sun / emitters", "`InterferenceSpikes`", "Saltikoff et al. 2016, BAMS", "10.1175/BAMS-D-15-00048.1", DONE),
        ("speckle", "`Despeckle`", "connected-component size filter", "", DONE),
        ("birds / insects", "`MistNet`", "Lin et al. 2019, Methods Ecol. Evol.", "10.1111/2041-210X.13280", STUB),
        ("dual-pol QC (operational)", "`MRMSdpQC`", "Tang et al. 2014 (talk)", "", REVIEW),
    ], "notebooks/01_qc_chain_s_c_x.ipynb"),
    "kdp": ("3", "PHIDP processing and KDP", "unfolding, sign convention, system offset, KDP estimation", [
        ("PHIDP preparation", "`radarwow.kdp.phase.prepare`", "unfold, sign, offset, rain mask", "", DONE),
        ("iterative window derivative", "`Vulpiani2012KDP`", "Vulpiani et al. 2012, JAMC", "10.1175/JAMC-D-10-05024.1", DONE),
        ("linear programming", "`Giangrande2013LP`", "Giangrande, McGraw & Lei 2013, JTECH", "10.1175/JTECH-D-12-00147.1", DONE),
        ("moving regression", "`MovingRegressionKDP`", "Wolfensberger et al. 2021, AMT (App. A)", "10.5194/amt-14-3169-2021", DONE),
    ], "notebooks/01_kdp_methods_s_c_x.ipynb"),
    "attenuation": ("4", "Attenuation correction", "path-integrated and differential attenuation in rain (critical at C and X band)", [
        ("linear A = alpha KDP", "`LinearPhiAttenuation`", "baseline: PIA = alpha PHIDP, alpha per band in `core/bands/*.toml`", "", DONE),
        ("ZPHI (PHIDP-constrained)", "`Testud2000ZPHI`", "Testud et al. 2000, JTECH", "10.1175/1520-0426(2000)017<0332:TRPAAT>2.0.CO;2", DONE),
        ("self-consistent alpha per ray", "`Bringi2001SelfConsistent`", "Bringi, Keenan & Chandrasekar 2001, IEEE TGRS", "10.1109/36.951081", DONE),
        ("ZDR constraint for beta", "-", "Bringi, Keenan & Chandrasekar 2001", "10.1109/36.951081", PLAN),
        ("hail / melting-layer attenuation, wet radome", "-", "see survey/02", "", REVIEW),
    ], "notebooks/01_attenuation_s_c_x.ipynb"),
    "classification": ("5", "Hydrometeor classification and melting layer", "melting-layer detection from QVPs, fuzzy-logic / clustering classes", [
        ("quasi-vertical profiles", "`quasi_vertical_profile`", "Ryzhkov et al. 2016, JTECH", "10.1175/JTECH-D-15-0020.1", DONE),
        ("melting layer from QVPs", "`detect_melting_layer`", "Sanchez-Rivas & Rico-Ramirez 2021, AMT", "10.5194/amt-14-2873-2021", DONE),
        ("temporal consistency", "`MeltingLayerTracker`", "radar-wow: rejects jumps > 0.5 km, optional model prior", "", DONE),
        ("NEXRAD MLDA", "`Giangrande2008ML`", "Giangrande, Krause & Ryzhkov 2008, JAMC", "10.1175/2007JAMC1634.1", PLAN),
        ("fuzzy-logic HCA", "`Park2009HCA`", "Park et al. 2009, Wea. Forecasting", "10.1175/2008WAF2222205.1", PLAN),
        ("semi-supervised clustering", "`Besic2016`", "Besic et al. 2016, AMT", "10.5194/amt-9-4425-2016", PLAN),
        ("non-meteorological echo (dust, bio)", "`DualPolNonMetClassifier`", "Kilambi et al. 2018; Gourley et al. 2007 (see survey/01)", "", PLAN),
    ], "../radarwow-verify/notebooks/01_ktlx_20220505_vs_mrms.ipynb"),
    "estimation": ("6", "Rain-rate estimators, VPR, blockage, hybrid scan", "R(Z), R(KDP), R(A), R(Z,ZDR) and a synthetic blend; vertical profile correction; beam blockage; lowest-usable-tilt selection", [
        ("R(Z) presets", "`ZRRelation`", "Marshall & Palmer 1948; Fulton et al. 1998; Suresh et al. 2005 (Chennai)", "10.1175/1520-0434(1998)013<0377:TWRA>2.0.CO;2", DONE),
        ("R(KDP)", "`RainRateKDP`", "Ryzhkov & Zrnic 1996; band defaults as documented in Py-ART", "10.1175/1520-0450(1996)035<2080:AORMTU>2.0.CO;2", DONE),
        ("R(A)", "`RainRateA`", "Ryzhkov, Diederich, Zhang & Simmer 2014, JTECH", "10.1175/JTECH-D-13-00038.1", DONE),
        ("R(Z,ZDR) (S band)", "`RainRateZZDR`", "Ryzhkov, Giangrande & Schuur 2005; NEXRAD DP-QPE coefficients", "10.1175/JAM2213.1", DONE),
        ("synthetic blend", "`SyntheticRainRate`", "Zhang et al. 2020, J. Hydrometeor. (MRMS logic)", "10.1175/JHM-D-19-0194.1", DONE),
        ("HCA-driven rate", "`HCADrivenRainRate`", "Giangrande & Ryzhkov 2008; NEXRAD Build 18/19 table (Grams et al. 2019)", "10.1175/2008JAMC1753.1", PLAN),
        ("VPR correction", "`ZhangQi2010VPR`", "Zhang & Qi 2010, J. Hydrometeor.", "10.1175/2010JHM1201.1", DONE),
        ("beam blockage", "`Bech2003BeamBlockage`", "Bech et al. 2003, JTECH; Copernicus GLO-90 terrain", "10.1175/1520-0426(2003)020<0845:TSOSPW>2.0.CO;2", DONE),
        ("hybrid scan + NEXRAD dB correction", "`hybrid_scan`, `fulton1998_correction_db`", "Fulton et al. 1998 (WSR-88D)", "10.1175/1520-0434(1998)013<0377:TWRA>2.0.CO;2", DONE),
        ("accumulation (no advection)", "`accumulate`", "scan-hold accumulation", "", DONE),
        ("advection-corrected accumulation", "`advection_accumulate`", "Anagnostou & Krajewski 1999, JTECH; pysteps Lucas-Kanade (Pulkkinen et al. 2019)", "10.1175/1520-0426(1999)016<0189:RTRREP>2.0.CO;2", DONE),
    ], ["notebooks/01_rain_rate_s_c_x.ipynb", "../radarwow-verify/notebooks/02_ktlx_20220505_vpr.ipynb", "../radarwow-verify/notebooks/03_ktlx_20220505_advection.ipynb", "../radarwow-verify/notebooks/04_kdax_20211024_blockage.ipynb"]),
    "merging": ("7", "Gauge merging and uncertainty", "radar-gauge bias adjustment, merging, ensembles", [
        ("merging methods compared", "`MeanFieldBias`, `KrigingWithExternalDrift`", "Goudenhoofdt & Delobbe 2009, HESS", "10.5194/hess-13-195-2009", PLAN),
        ("RRBF / KMA, KNMI, UK schemes", "-", "talk", "", REVIEW),
        ("commercial microwave links", "-", "talk (2 papers)", "", REVIEW),
    ], ""),
    "mosaic": ("8", "Compositing, mosaics and accumulation", "multi-radar mosaics, advection-corrected accumulation; national systems as references", [
        ("Swiss operational chain", "reference design", "Germann et al. 2022, Remote Sens.", "10.3390/rs14030503", REVIEW),
        ("MRMS, KMA, KNMI, UK, JMA, RADOLAN, CMPAS", "reference designs", "talk + review (Zhang et al. 2025, Remote Sens.)", "10.3390/rs17213619", REVIEW),
        ("mosaic", "`MaxQualityMosaic`", "quality-weighted compositing", "", PLAN),
        ("accumulation", "`AdvectionAccumulation`", "motion-corrected sums", "", PLAN),
    ], ""),
    "ml": ("9", "Machine-learning QPE", "learned estimators, with physics-based stages as inputs and baselines", [
        ("RainForest (random forest)", "`RainForest`", "Wolfensberger et al. 2021, AMT", "10.5194/amt-14-3169-2021", PLAN),
        ("deep learning QPE", "-", "Chen et al. 2019, GRL", "10.1029/2019GL084771", PLAN),
        ("satellite-to-radar", "-", "Hilburn et al. 2021, JAMC", "10.1175/JAMC-D-20-0084.1", PLAN),
        ("deep learning QPE", "-", "Li, Chen & Han 2023, IEEE TGRS", "10.1109/TGRS.2023.3280799", PLAN),
        ("deep learning QPE", "-", "Yo et al. 2021, Earth Space Sci.", "10.1029/2020EA001340", PLAN),
        ("deep learning QPE", "-", "Osborne et al. 2023, AIES", "10.1175/AIES-D-22-0053.1", PLAN),
        ("radar + humidity fusion QPE (MCB-Net)", "-", "Cui et al. 2025, IEEE TGRS (talk)", "10.1109/TGRS.2025.3585737", REVIEW),
        ("cGAN beam-blockage infill", "-", "Tan & Chen 2023, IEEE TGRS (talk)", "10.1109/TGRS.2023.3286181", REVIEW),
    ], ""),
    "verify": ("-", "Verification", "matching radar estimates to references (MRMS, gauges), scores stratified by range and hour", [
        ("MRMS reference from AWS", "`fetch_mrms`", "Zhang et al. 2016, BAMS (MRMS)", "10.1175/BAMS-D-14-00174.1", DONE),
        ("polar-to-grid matching", "`gate_latlon`, `to_mrms_grid`", "4/3-Earth beam geometry, cell averaging", "", DONE),
        ("model freezing level", "`hrrr_freezing_level`", "HRRR analysis on AWS (byte-range GRIB2)", "", DONE),
        ("continuous scores", "`scores`", "bias ratio, RMSE, correlation, MAE", "", DONE),
        ("gauge matching", "`match_gauges`", "radar-gauge pairs in space and time", "", PLAN),
        ("neighbourhood / categorical scores", "-", "use the `scores` library and pysteps (survey/04)", "", PLAN),
    ], ["notebooks/01_ktlx_20220505_vs_mrms.ipynb", "notebooks/02_ktlx_20220505_vpr.ipynb", "notebooks/03_ktlx_20220505_advection.ipynb", "notebooks/04_kdax_20211024_blockage.ipynb"]),
    "pipeline": ("10", "End-to-end pipeline", "chains the stages per radar from a config; India / Delhi (IMD C-band, ISRO S-band) first", [
        ("config-driven chain", "`Pipeline.from_toml`", "checks bands and moments before running", "", PLAN),
        ("India radar review", "-", "Bhat, Vivekanandan & Pradhan 2025, MAUSAM", "10.54302/mausam.v76i1.6497", REVIEW),
        ("India QPE", "-", "Sharma et al. 2025, Phys. Chem. Earth", "10.1016/j.pce.2025.104182", REVIEW),
        ("India dual-pol QPE", "-", "Saini et al. 2026, Radio Science", "10.1029/2025RS008484", REVIEW),
    ], ""),
}

ORDER = ["core", "calibration", "qc", "kdp", "attenuation", "classification", "estimation", "merging", "mosaic", "ml", "verify", "pipeline"]


def doi_link(doi):
    return f"[doi:{doi}](https://doi.org/{doi})" if doi else ""


def readme(key):
    num, title, desc, rows, nb = STAGES[key]
    repo = f"radarwow-{key}"
    lines = [f"# {repo}", "", f"**radar-wow{'' if num == '-' else f' stage {num}'}: {title}.** {desc[0].upper() + desc[1:]}.", "",
             "Part of [radar-wow](https://github.com/{0}/radar-wow), a set of repos that together build a radar QPE system that works for S, C and X band radars.".format(ORG),
             "Every algorithm is one class implementing one paper, with the same interface: it takes an xradar sweep or volume with canonical moment names, "
             "declares the bands and moments it needs, and records provenance.", "",
             "## Sub-components", "", "| sub-component | algorithm | source | DOI | status |", "|---|---|---|---|---|"]
    lines += [f"| {a} | {b} | {c} | {doi_link(d)} | {s} |" for a, b, c, d, s in rows]
    lines += ["", "## Install", "", "```bash",
              f"pip install git+https://github.com/{ORG}/radarwow-core" + ("" if key == "core" else f" git+https://github.com/{ORG}/{repo}"), "```", ""]
    nbs = [nb] if isinstance(nb, str) and nb else list(nb or [])
    own = [n for n in nbs if not n.startswith("../")]
    if nbs:
        lines += ["## Notebooks (free data, S / C / X band)" if own else "## Notebooks", ""]
    for n in nbs:
        if n.startswith("../"):
            other, path = n[3:].split("/", 1)
            lines.append(f"- Used and checked in the [{other} notebook `{path.split('/')[-1]}`](https://github.com/{ORG}/{other}/blob/main/{path})")
        else:
            lines.append(f"- [`{n}`]({n}): open in Colab via `https://colab.research.google.com/github/{ORG}/{repo}/blob/main/{n}`")
    if nbs:
        lines.append("")
    if own:
        figs = sorted((ROOT / repo / "docs" / "figures").glob("*.png"))
        if figs:
            lines += ["## Results", ""] + [f"![{f.stem}](docs/figures/{f.name})" for f in figs] + [""]
    if key != "core":
        lines += ["## Usage", "", "```python", "from radarwow.core import load_sample", f"from radarwow.{key} import *  # see table above", "",
                  "vol = load_sample('arm_csapr2_c')        # or open_volume('my_file')", "# out = SomeAlgorithm()(vol)            # band read from the file, or band='S'|'C'|'X'", "```", ""]
    lines += ["## Status legend", "", f"*{DONE}*: code, tests, executed notebook. *{PLAN}*: interface fixed, code to write. "
              f"*{STUB}*: class exists, raises `NotImplementedError`. *{REVIEW}*: paper to read before deciding.", "",
              "## License", "", "MIT. Data used in the notebooks comes from public archives (NEXRAD on AWS, ARM, IMD via open-radar-data) under their own terms.", ""]
    return "\n".join(lines)


def scaffold(key):
    repo = ROOT / f"radarwow-{key}"
    num, title, desc, rows, _ = STAGES[key]
    new = not repo.exists()
    for d in ("notebooks", "docs/figures", "tests", f"src/radarwow/{key}"):
        (repo / d).mkdir(parents=True, exist_ok=True)
    if new:
        (repo / "pyproject.toml").write_text(f"""[build-system]
requires = ["setuptools>=68"]
build-backend = "setuptools.build_meta"

[project]
name = "radarwow-{key}"
version = "0.0.1"
description = "radar-wow{'' if num == '-' else f' stage {num}'}: {title}"
readme = "README.md"
license = {{text = "MIT"}}
requires-python = ">=3.10"
dependencies = ["radarwow-core @ git+https://github.com/manmeet3591/radarwow-core", "numpy", "scipy", "xarray"]

[tool.setuptools.packages.find]
where = ["src"]
namespaces = true
""")
        planned = [r[1].strip("`") for r in rows if r[4] in (PLAN, STUB) and r[1].startswith("`") and "," not in r[1] and "." not in r[1]]
        (repo / f"src/radarwow/{key}/__init__.py").write_text(
            f'"""radar-wow{"" if num == "-" else f" stage {num}"}: {title.lower()}.\n\nPlanned algorithms (see README): {", ".join(planned) or "-"}.\n"""\n\n'
            f"PLANNED = {planned!r}\n__all__: list[str] = []\n")
        (repo / "tests/test_import.py").write_text(f"import radarwow.{key} as m\n\n\ndef test_import():\n    assert isinstance(m.PLANNED, list)\n")
        (repo / "notebooks/.gitkeep").write_text("")
        (repo / "docs/figures/.gitkeep").write_text("")
    (repo / "README.md").write_text(readme(key))
    (repo / "LICENSE").write_text(LICENSE)
    (repo / ".gitignore").write_text(GITIGNORE)


def umbrella():
    lines = ["# radar-wow", "", "A generalised radar quantitative precipitation estimation (QPE) system for S, C and X band radars, "
             "built from one repo per processing stage. Each repo implements published algorithms (one class per paper) "
             "and an executed notebook that runs them on free data from NEXRAD, ARM and IMD.", "",
             "| stage | repo | what | implemented |", "|---|---|---|---|"]
    for k in ORDER:
        num, title, desc, rows, _ = STAGES[k]
        done = sum(r[4] == DONE for r in rows)
        lines.append(f"| {num} | [radarwow-{k}](https://github.com/{ORG}/radarwow-{k}) | {title} | {done}/{len(rows)} |")
    lines += ["", "Different radars bring different problems (code values, stored noise, reversed PHIDP sign, mislabelled fields, "
              "missing moments). `radarwow.core.diagnose` measures them on any file before the algorithms run.", ""]
    (ROOT / "README.md").write_text("\n".join(lines))


if __name__ == "__main__":
    for k in ORDER:
        scaffold(k)
    umbrella()
    print("ok:", ", ".join(ORDER))
