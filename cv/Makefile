# Build the CV and publish it where the website links to it.
#   make        sync publications from the website data, compile, copy the PDF to assets/files/
#   make clean  remove LaTeX build files
CV   := Boyang_Cheng_CV
OUT  := ../assets/files/Boyang_Cheng_s_CV.pdf
DATA := ../assets/data/publications.json

all: $(OUT)

publications.tex: $(DATA) sync_publications.py
	python3 sync_publications.py

build/$(CV).pdf: $(CV).tex jobcv.sty publications.tex
	latexmk -pdf -interaction=nonstopmode -halt-on-error -outdir=build $(CV).tex

$(OUT): build/$(CV).pdf
	cp $< $@
	@echo "CV updated: $(OUT)"

clean:
	latexmk -C -outdir=build $(CV).tex
	rm -rf build

.PHONY: all clean
