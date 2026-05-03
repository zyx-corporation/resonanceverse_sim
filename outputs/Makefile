# Makefile

FILENAME = resonanceverse_en
FILENAME_JA = resonanceverse_ja

LATEX = xelatex
LATEXFLAGS = -interaction=nonstopmode

.PHONY: all clean pdf

all: pdf pdf_ja

pdf_ja:
	$(LATEX) $(LATEXFLAGS) $(FILENAME_JA).tex
	$(LATEX) $(LATEXFLAGS) $(FILENAME_JA).tex

pdf:
	$(LATEX) $(LATEXFLAGS) $(FILENAME).tex
	$(LATEX) $(LATEXFLAGS) $(FILENAME).tex

clean:
	rm -f $(FILENAME).pdf $(FILENAME).aux $(FILENAME).log $(FILENAME).out
	rm -f $(FILENAME).toc $(FILENAME).bbl $(FILENAME).blg
	rm -f $(FILENAME_JA).pdf $(FILENAME_JA).aux $(FILENAME_JA).log $(FILENAME_JA).out
	rm -f $(FILENAME_JA).toc $(FILENAME_JA).bbl $(FILENAME_JA).blg

view: pdf
	open $(FILENAME).pdf
