# CV

LaTeX source for the CV linked from the website (`assets/files/Boyang_Cheng_s_CV.pdf`).

## Update the CV

```sh
cd cv
make
```

`make` does three things:

1. Reads the publication record in `../assets/data/publications.json` and writes it both into `publications.tex` (the CV's publication section) and into the Reference chapter of `../index.html`.
2. Compiles `Boyang_Cheng_CV.tex` with `latexmk` (pdflatex, TeX Live).
3. Copies the PDF to `../assets/files/Boyang_Cheng_s_CV.pdf`, the file the website links to.

Commit and push afterwards to put the new CV online.

## Files

| File | What it is |
|---|---|
| `Boyang_Cheng_CV.tex` | The CV content. Edit experience, education, skills and awards here. |
| `jobcv.sty` | The layout: a clean, ATS-friendly one-column resume style. |
| `publications.tex` | Generated. Do not edit by hand. |
| `sync_publications.py` | Generates the publication lists for the CV and the website. |
| `Makefile` | Runs the steps above. `make clean` removes build files. |

## Adding a publication

Add an entry to `../assets/data/publications.json` (newest first), then run `make`. Fields:

```json
{
  "title": "…",
  "authors": "First Author, Boyang Cheng, …",
  "venue": "IEEE Journal of Solid-State Circuits",
  "year": 2026,
  "scholar_url": "optional link",
  "arxiv": "optional arXiv id, for preprints",
  "doi": "optional DOI",
  "note": "optional, e.g. Best Paper Award Nominee"
}
```

The script decides the group from the venue: names containing *arXiv* are preprints, *Patent* is a patent, *Journal / Transactions / Letters* are journal articles, anything else is a conference paper. Venue abbreviations for the CV (IEEE JSSC, DAC, …) are listed at the top of `sync_publications.py`.
