SVGS := kit_os_poc_work_conserving \
	kit_os_poc_blocking \
	cohort_and_steps \
	$(addprefix mig,0 1 2 3 4) \
	state_chart_pre_spread \
	state_chart_post_spread

DOTS := sched_state_diag_upstream \
	sched_state_diag_spread

.DEFAULT_GOAL := all

## impl
FIG :=

TMP := $(addprefix fig_build/,$(SVGS))
FIG_SVG_PDF := $(addsuffix .pdf,$(TMP))
FIG_SVG_PNG := $(addsuffix .png,$(TMP))
FIG += $(FIG_SVG_PDF) $(FIG_SVG_PNG)

TMP := $(addprefix fig_build/,$(DOTS))
#FIG_DOT_TEX := $(addsuffix .tex,$(TMP))
FIG_DOT_PDF := $(addsuffix .pdf,$(TMP))
FIG += $(FIG_DOT_TEX) $(FIG_DOT_PDF)

#SVGS := $(addsuffix .svg,$(addprefix fig/,$(SVGS)))
#DOTS := $(addsuffix .dot,$(addprefix fig/,$(DOTS)))

fig_build:
	mkdir -p $@

$(FIG_SVG_PDF): fig_build/%.pdf: fig_build fig/%.svg
	rsvg-convert -f pdf -d 300 -p 300 fig/$*.svg > $@

$(FIG_SVG_PNG): fig_build/%.png: fig_build fig/%.svg
	rsvg-convert -f png -d 300 -p 300  fig/$*.svg > $@

$(FIG_DOT_TEX): fig_build/%.tex: fig_build fig/%.dot
	dot2tex --figonly fig/$*.dot > $@

$(FIG_DOT_PDF): fig_build/%.pdf: fig_build fig/%.dot
	dot -Tpdf fig/$*.dot > $@

## targets

.PHONY: copyevaluation
copyevaluation: fig_build
	rsync -a evaluation/processed/ fig_build/evaluation/

all: $(FIG) copyevaluation
    #nop

clean:
	rm -rf fig_build/*.{pdf,png}
