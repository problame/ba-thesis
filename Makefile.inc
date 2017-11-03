# Specify the following variables in your makefile before including this one
#
# Required: 
#
#   DOCNAME     name of the document, $(DOCNAME).tex -> $(DOCNAME).pdf
#
# Optional:
#
#   DEPS        list of other dependencies  (not cleaned)
#   SVGS        list of PDF targets produces from SVG files (SVG2PDF)
#   ...
#   see below

LATEX ?= pdflatex -file-line-error -interaction batchmode
BIBER ?= biber
INKSCAPE_BIN ?= `which inkscape`
SVG2PDF = $(INKSCAPE_BIN) -A $(2) $(1)
UMLET_JAR ?= /usr/share/umlet/umlet.jar
UMLET_CONVERT = java -jar $(UMLET_JAR) -action=convert -format=pdf -filename=$(1) -output=$(2)

ifndef DOCNAME
$(error DOCNAME is not set)
endif

.DEFAULT_GOAL = $(DOCNAME).pdf

# GENERIC GOALS

$(DOCNAME).pdf: $(DOCNAME).tex $(DEPS) $(SVGS) $(UMLET_PDFS)
	${LATEX} $(DOCNAME)
	${BIBER} $(DOCNAME)
	${LATEX} $(DOCNAME)
	${LATEX} $(DOCNAME)

$(SVGS): %.pdf: %.svg
	$(call SVG2PDF,$<,$@)

$(UMLET_PDFS): %.pdf: %.uxf
	$(call UMLET_CONVERT,$<,$@)

.PHONY: clean
clean:
	# remember to update .gitignore
	rm -f *.nav *.aux *.toc *.out *.log *.vrb *.snm \
		$(SVGS) \
		$(UMLET_PDFS) \
		$(DOCNAME).pdf

